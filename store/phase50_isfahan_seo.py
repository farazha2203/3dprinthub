from django.shortcuts import render


ISFAHAN_PAGE_TITLE = "چاپ سه‌بعدی و مهندسی معکوس در اصفهان | 3DprintHub"
ISFAHAN_PAGE_DESCRIPTION = (
    "طراحی سه‌بعدی، بازسازی قطعات از روی نمونه و چاپ سه‌بعدی صنعتی برای پروژه‌های اصفهان. "
    "فایل، عکس، ابعاد و کاربرد قطعه را بفرستید تا امکان‌سنجی و برآورد پس از بررسی فنی اعلام شود."
)


def isfahan_service_landing_view(request):
    return render(
        request,
        "store/isfahan_service_landing.html",
        {
            "isfahan_page_title": ISFAHAN_PAGE_TITLE,
            "isfahan_page_description": ISFAHAN_PAGE_DESCRIPTION,
        },
    )
