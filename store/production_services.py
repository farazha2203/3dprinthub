from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone

from .models import (
    CostEntry,
    FilamentMovement,
    FilamentPurchase,
    FilamentPurchaseItem,
    FilamentSpool,
    MaterialUsage,
    ProductionJob,
    StoreOrder,
)


def _money(value: Decimal | int | float) -> int:
    return int(Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def receive_filament_purchase(purchase: FilamentPurchase, *, actor=None) -> int:
    """Generate one physical spool row for every purchased roll.

    The operation is idempotent at purchase-item level. Re-running it will not
    duplicate spools that were already generated.
    """
    if purchase.status == "cancelled":
        raise ValidationError("خرید لغوشده را نمی‌توان وارد انبار کرد.")

    generated = 0
    with transaction.atomic():
        purchase = FilamentPurchase.objects.select_for_update().get(pk=purchase.pk)
        items = list(
            FilamentPurchaseItem.objects.select_for_update()
            .select_related("material")
            .filter(purchase=purchase)
        )
        if not items:
            raise ValidationError("برای این خرید هیچ ردیف فیلامنتی ثبت نشده است.")

        # هزینه حمل و هزینه‌های عمومی خرید به‌صورت متناسب بین ردیف‌های
        # تولیدنشده توزیع می‌شود. مقدار دستی allocated_extra_cost حفظ می‌شود.
        pending_items = [item for item in items if not item.generated_spools]
        header_extra = int(purchase.shipping_cost) + int(purchase.other_cost)
        already_allocated = sum(int(item.allocated_extra_cost) for item in items)
        remaining_extra = max(0, header_extra - already_allocated)
        basis_total = sum(int(item.total_purchase_amount) for item in pending_items)
        distributed = 0
        if remaining_extra and pending_items:
            for index, item in enumerate(pending_items):
                if index == len(pending_items) - 1:
                    share = remaining_extra - distributed
                elif basis_total:
                    share = int(Decimal(remaining_extra) * Decimal(item.total_purchase_amount) / Decimal(basis_total))
                    distributed += share
                else:
                    share = remaining_extra // len(pending_items)
                    distributed += share
                if share:
                    item.allocated_extra_cost = int(item.allocated_extra_cost) + share
                    item.save(update_fields=["allocated_extra_cost"])

        for item in items:
            if item.generated_spools:
                continue
            if item.quantity_rolls < 1:
                raise ValidationError("تعداد رول باید حداقل یک باشد.")
            if Decimal(item.net_weight_per_roll_grams or 0) <= 0:
                raise ValidationError("وزن هر رول باید بیشتر از صفر باشد.")

            landed_per_roll = Decimal(item.landed_cost) / Decimal(item.quantity_rolls)
            cost_per_gram = Decimal(item.cost_per_gram)
            sale_per_gram = int(item.sale_price_per_gram or item.material.sale_price_per_gram or 0)

            for _ in range(item.quantity_rolls):
                spool = FilamentSpool.objects.create(
                    purchase_item=item,
                    material=item.material,
                    brand=item.brand,
                    color_name=item.color_name,
                    color_hex=item.color_hex,
                    nominal_weight_grams=item.net_weight_per_roll_grams,
                    remaining_weight_grams=item.net_weight_per_roll_grams,
                    purchase_price=_money(landed_per_roll),
                    cost_per_gram_snapshot=cost_per_gram,
                    sale_price_per_gram_snapshot=sale_per_gram,
                    status="sealed",
                    purchased_at=purchase.purchased_at,
                )
                FilamentMovement.objects.create(
                    spool=spool,
                    material=item.material,
                    movement_type="purchase",
                    grams=spool.nominal_weight_grams,
                    balance_after=spool.remaining_weight_grams,
                    unit_cost_snapshot=spool.cost_per_gram_snapshot,
                    total_cost=spool.purchase_price,
                    note=f"ورود خرید {purchase.purchase_number}",
                    created_by=actor,
                )
                generated += 1

            item.generated_spools = True
            item.save(update_fields=["generated_spools"])

            material = item.material
            material.default_roll_weight_grams = item.net_weight_per_roll_grams
            material.default_purchase_price_per_roll = _money(landed_per_roll)
            material.price_per_kg = _money(cost_per_gram * Decimal("1000"))
            if item.sale_price_per_gram:
                material.sale_price_per_gram = item.sale_price_per_gram
            material.track_filament_inventory = True
            material.save(
                update_fields=[
                    "default_roll_weight_grams",
                    "default_purchase_price_per_roll",
                    "price_per_kg",
                    "sale_price_per_gram",
                    "track_filament_inventory",
                ]
            )

        purchase.status = "received"
        purchase.received_at = purchase.received_at or timezone.now()
        purchase.save(update_fields=["status", "received_at", "updated_at"])
    return generated


def create_job_for_store_order(order: StoreOrder) -> ProductionJob:
    revenue = max(0, int(order.total_amount) - int(order.tax_amount))
    job, created = ProductionJob.objects.get_or_create(
        store_order=order,
        defaults={
            "title": f"سفارش فروشگاه {order.order_number}",
            "revenue_snapshot": revenue,
            "tax_snapshot": order.tax_amount,
        },
    )
    if not created:
        changed = False
        if not job.revenue_snapshot and revenue:
            job.revenue_snapshot = revenue
            changed = True
        if job.tax_snapshot != order.tax_amount:
            job.tax_snapshot = order.tax_amount
            changed = True
        if changed:
            job.save(update_fields=["revenue_snapshot", "tax_snapshot", "updated_at"])

    existing = {
        (usage.material_id, usage.color_name): usage
        for usage in job.material_usages.all()
    }
    aggregated: dict[tuple[int, str], Decimal] = {}
    for item in order.items.select_related("variant__material").all():
        variant = item.variant
        if not variant or not variant.material_id:
            continue
        grams = Decimal(variant.material_weight_grams or 0) * Decimal(item.quantity)
        key = (variant.material_id, "")
        aggregated[key] = aggregated.get(key, Decimal("0")) + grams

    for (material_id, color_name), grams in aggregated.items():
        usage = existing.get((material_id, color_name))
        if usage and usage.posted_at:
            continue
        if usage:
            usage.planned_grams = grams
            if not usage.sale_price_per_gram_snapshot:
                usage.sale_price_per_gram_snapshot = usage.material.effective_sale_price_per_gram
            usage.material_charge_snapshot = _money(
                Decimal(usage.sale_price_per_gram_snapshot or 0) * grams
            )
            usage.save(
                update_fields=[
                    "planned_grams",
                    "sale_price_per_gram_snapshot",
                    "material_charge_snapshot",
                ]
            )
        else:
            from website.models import Material

            material = Material.objects.get(pk=material_id)
            sale = int(material.effective_sale_price_per_gram or 0)
            MaterialUsage.objects.create(
                job=job,
                material=material,
                color_name=color_name,
                planned_grams=grams,
                sale_price_per_gram_snapshot=sale,
                material_charge_snapshot=_money(Decimal(sale) * grams),
            )

    _seed_store_order_cost_lines(job, order)
    return job


def _seed_store_order_cost_lines(job: ProductionJob, order: StoreOrder) -> None:
    rows = [
        ("shipping", "هزینه ارسال دریافت‌شده", 0, int(order.shipping_fee)),
        ("packaging", "هزینه بسته‌بندی دریافت‌شده", 0, int(order.packaging_fee)),
    ]
    for category, description, actual_cost, customer_charge in rows:
        if not customer_charge:
            continue
        CostEntry.objects.get_or_create(
            job=job,
            category=category,
            description=description,
            defaults={
                "actual_cost": actual_cost,
                "customer_charge": customer_charge,
                "included_in_order_total": True,
            },
        )


def create_job_for_custom_order(order) -> ProductionJob:
    try:
        quote = order.quote
    except Exception:
        quote = None
    revenue = int(getattr(quote, "total_price", 0) or 0)
    job, created = ProductionJob.objects.get_or_create(
        custom_order=order,
        defaults={
            "title": f"سفارش ساخت #{order.pk} - {order.first_name} {order.last_name}",
            "revenue_snapshot": revenue,
        },
    )
    if not created and revenue and not job.revenue_snapshot:
        job.revenue_snapshot = revenue
        job.save(update_fields=["revenue_snapshot", "updated_at"])

    material = getattr(quote, "selected_material", None) if quote else order.material
    grams = Decimal(getattr(quote, "weight_grams", 0) or 0) * Decimal(order.quantity or 1)
    if material and grams > 0 and not job.material_usages.exists():
        sale = int(material.effective_sale_price_per_gram or 0)
        MaterialUsage.objects.create(
            job=job,
            material=material,
            color_name=order.color,
            planned_grams=grams,
            sale_price_per_gram_snapshot=sale,
            material_charge_snapshot=_money(Decimal(sale) * grams),
        )

    if quote:
        cost_lines = [
            ("design", "هزینه طراحی یا مهندسی معکوس", quote.design_fee),
            ("labor", "دستمزد ساخت و اپراتوری", quote.labor_fee),
            ("post_processing", "پرداخت‌کاری یا مونتاژ", quote.post_processing_fee),
            ("shipping", "هزینه ارسال", quote.shipping_fee),
            ("machine", "کارکرد دستگاه", quote.machine_cost),
        ]
        for category, description, charge in cost_lines:
            if not charge:
                continue
            CostEntry.objects.get_or_create(
                job=job,
                category=category,
                description=description,
                defaults={
                    "actual_cost": 0,
                    "customer_charge": int(charge),
                    "included_in_order_total": True,
                },
            )
    return job


@transaction.atomic
def consume_material_fifo(usage: MaterialUsage, *, actor=None) -> MaterialUsage:
    usage = MaterialUsage.objects.select_for_update().select_related("material", "job").get(pk=usage.pk)
    if usage.posted_at:
        return usage

    grams_needed = Decimal(usage.consumption_grams)
    if grams_needed <= 0:
        usage.posted_at = timezone.now()
        usage.save(update_fields=["posted_at"])
        return usage

    material = usage.material
    if not material.track_filament_inventory:
        fallback_cost = Decimal(material.purchase_cost_per_gram or 0)
        usage.cost_per_gram_snapshot = fallback_cost
        usage.material_cost_snapshot = _money(fallback_cost * grams_needed)
        usage.posted_at = timezone.now()
        usage.save(
            update_fields=["cost_per_gram_snapshot", "material_cost_snapshot", "posted_at"]
        )
        return usage

    spools = list(
        FilamentSpool.objects.select_for_update()
        .filter(material=material, remaining_weight_grams__gt=0, status__in=["open", "sealed"])
        .order_by("status", "purchased_at", "id")
    )
    available = sum((Decimal(spool.remaining_weight_grams) for spool in spools), Decimal("0"))
    if available < grams_needed:
        raise ValidationError(
            f"موجودی {material.name} کافی نیست. نیاز: {grams_needed} گرم، موجودی: {available} گرم."
        )

    remaining = grams_needed
    total_cost_decimal = Decimal("0")
    for spool in spools:
        if remaining <= 0:
            break
        take = min(remaining, Decimal(spool.remaining_weight_grams))
        spool.remaining_weight_grams = Decimal(spool.remaining_weight_grams) - take
        if spool.status == "sealed":
            spool.status = "open"
            spool.opened_at = spool.opened_at or timezone.now()
        if spool.remaining_weight_grams <= 0:
            spool.remaining_weight_grams = Decimal("0")
            spool.status = "empty"
        spool.save(update_fields=["remaining_weight_grams", "status", "opened_at", "updated_at"])

        line_cost = Decimal(spool.cost_per_gram_snapshot) * take
        total_cost_decimal += line_cost
        FilamentMovement.objects.create(
            spool=spool,
            material=material,
            job=usage.job,
            usage=usage,
            movement_type="consume",
            grams=-take,
            balance_after=spool.remaining_weight_grams,
            unit_cost_snapshot=spool.cost_per_gram_snapshot,
            total_cost=_money(line_cost),
            note=f"مصرف پروژه {usage.job.job_number}",
            created_by=actor,
        )
        remaining -= take

    average_cost = total_cost_decimal / grams_needed if grams_needed else Decimal("0")
    usage.cost_per_gram_snapshot = average_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    usage.material_cost_snapshot = _money(total_cost_decimal)
    billable_grams = Decimal(usage.actual_grams or 0) if Decimal(usage.actual_grams or 0) > 0 else Decimal(usage.planned_grams or 0)
    usage.material_charge_snapshot = _money(Decimal(usage.sale_price_per_gram_snapshot or 0) * billable_grams)
    usage.posted_at = timezone.now()
    usage.save(
        update_fields=[
            "cost_per_gram_snapshot", "material_cost_snapshot",
            "material_charge_snapshot", "posted_at",
        ]
    )
    return usage


@transaction.atomic
def finalize_production_job(job: ProductionJob, *, actor=None) -> ProductionJob:
    job = ProductionJob.objects.select_for_update().get(pk=job.pk)
    if job.status == "completed" and not job.material_usages.filter(posted_at__isnull=True).exists():
        return job
    for usage in job.material_usages.select_related("material").all():
        consume_material_fifo(usage, actor=actor)
    job.status = "completed"
    job.completed_at = job.completed_at or timezone.now()
    job.save(update_fields=["status", "completed_at", "updated_at"])
    return job


def finalize_store_order_job(order: StoreOrder, *, actor=None) -> ProductionJob:
    job = create_job_for_store_order(order)
    return finalize_production_job(job, actor=actor)


def finalize_custom_order_job(order, *, actor=None) -> ProductionJob:
    job = create_job_for_custom_order(order)
    return finalize_production_job(job, actor=actor)


def inventory_summary():
    from website.models import Material

    rows = []
    for material in Material.objects.filter(is_active=True).order_by("sort_order", "name"):
        grams = material.current_stock_grams
        rows.append(
            {
                "material": material,
                "grams": grams,
                "rolls": material.current_roll_count,
                "needs_reorder": material.needs_reorder,
            }
        )
    return rows


def finance_summary(*, since=None):
    jobs = ProductionJob.objects.exclude(status="cancelled")
    if since:
        jobs = jobs.filter(created_at__gte=since)
    revenue = sum(job.total_revenue for job in jobs)
    project_cost = sum(job.total_cost for job in jobs)
    general_expense_qs = CostEntry.objects.filter(job__isnull=True)
    if since:
        general_expense_qs = general_expense_qs.filter(incurred_at__gte=since.date())
    general_expenses = int(general_expense_qs.aggregate(value=Sum("actual_cost"))["value"] or 0)
    return {
        "revenue": revenue,
        "project_cost": project_cost,
        "general_expenses": general_expenses,
        "net_profit": revenue - project_cost - general_expenses,
    }
