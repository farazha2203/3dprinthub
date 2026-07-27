from __future__ import annotations

from collections import defaultdict

from django.apps import apps

from django_smartbase_admin.admin.site import sb_admin_site
from django_smartbase_admin.engine.configuration import (
    SBAdminConfigurationBase,
    SBAdminRoleConfiguration,
)
from django_smartbase_admin.engine.menu_item import SBAdminMenuItem
from django_smartbase_admin.messaging.config import (
    AllUsersAudience,
    GroupsAudience,
    NotificationStyle,
    SBAdminMessageType,
    SBAdminMessagingConfig,
    UsersAudience,
)
from django_smartbase_admin.messaging.services import SBAdminMessagingService
from django_smartbase_admin.views.dashboard_view import SBAdminDashboardView

from smartbase_admin_bridge.dashboard import AdminOverviewWidget
from smartbase_admin_bridge.utils import app_group_icon, app_group_label


DASHBOARD_VIEW_ID = "dashboard"
MESSAGE_INBOX_VIEW_ID = "sb_admin_messaging_messagerecipient"


class ProjectDashboardView(SBAdminDashboardView):
    view_id = DASHBOARD_VIEW_ID
    label = "میز کار"
    title = "میز کار مدیریت 3DPrintHub"
    widgets = [AdminOverviewWidget()]


def _menu_items_from_registry() -> list[SBAdminMenuItem]:
    grouped: dict[str, list[SBAdminMenuItem]] = defaultdict(list)

    for model, view in sorted(
        sb_admin_site._registry.items(),
        key=lambda pair: (
            pair[0]._meta.app_label,
            str(pair[0]._meta.verbose_name_plural),
        ),
    ):
        if not hasattr(view, "get_id"):
            continue

        view_id = view.get_id()
        badge = None
        if view_id == MESSAGE_INBOX_VIEW_ID:
            badge = SBAdminMessagingService.get_unread_count

        grouped[model._meta.app_label].append(
            SBAdminMenuItem(
                view_id=view_id,
                label=str(model._meta.verbose_name_plural),
                badge=badge,
            )
        )

    menu_items = [
        SBAdminMenuItem(
            view_id=DASHBOARD_VIEW_ID,
            label="میز کار",
            icon="All-application",
        )
    ]

    for app_label, sub_items in grouped.items():
        try:
            verbose_name = str(apps.get_app_config(app_label).verbose_name)
        except LookupError:
            verbose_name = app_label

        menu_items.append(
            SBAdminMenuItem(
                label=app_group_label(app_label, verbose_name),
                icon=app_group_icon(app_label),
                sub_items=sub_items,
            )
        )

    return menu_items


class ProjectRoleConfiguration(SBAdminRoleConfiguration):
    def __init__(self):
        dashboard = ProjectDashboardView()
        messaging = SBAdminMessagingConfig(
            message_types=[
                SBAdminMessageType(
                    key="info",
                    label="اطلاع",
                    notification_style=NotificationStyle.TOAST,
                    icon="Info",
                    color="notice",
                ),
                SBAdminMessageType(
                    key="success",
                    label="موفق",
                    notification_style=NotificationStyle.TOAST,
                    icon="Check-one",
                    color="success",
                ),
                SBAdminMessageType(
                    key="warning",
                    label="هشدار",
                    notification_style=NotificationStyle.MODAL,
                    icon="Attention",
                    color="warning",
                    require_acknowledge=True,
                ),
                SBAdminMessageType(
                    key="critical",
                    label="فوری",
                    notification_style=NotificationStyle.MODAL,
                    icon="Caution",
                    color="negative",
                    require_acknowledge=True,
                ),
            ],
            audiences=[
                UsersAudience(),
                GroupsAudience(),
                AllUsersAudience(),
            ],
            poll_interval_seconds=30,
            scope_by_author=False,
        )

        super().__init__(
            default_view=SBAdminMenuItem(view_id=DASHBOARD_VIEW_ID),
            registered_views=[dashboard],
            menu_items=_menu_items_from_registry(),
            admin_title="مدیریت 3DPrintHub",
            messaging_config=messaging,
            link_history_to_audit=True,
            default_list_sticky_header_and_footer=True,
            list_pagination_page_input_min_pages=20,
        )


class SBAdminConfiguration(SBAdminConfigurationBase):
    def get_configuration_for_roles(self, user_roles):
        return ProjectRoleConfiguration()
