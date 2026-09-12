"""Browser regression for the real selector + mature cart listener, with isolated API data.

Run with a development Playwright install; no live server, database or external requests.
"""
from pathlib import Path
import json
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]


def row(pk, size, color, material, quality, **extra):
    return dict(product_id=1, profile_key=str(pk), profile_label=f"Build {pk}",
                size_label=size, color_name=color, color=color, material=material,
                material_id=material, quality=quality, quality_id=quality,
                unit_price=pk * 100000, final_weight_grams=pk * 100,
                print_time_minutes=pk * 60, orderable=True, stock_status="in_stock", **extra)


BASE = {
    "1": row(1, "20", "Red", "PLA", "Normal"),
    "2": row(2, "20", "Red", "PETG", "Fine"),
    "3": row(3, "20", "Blue", "PLA", "Normal"),
    "4": row(4, "30", "Blue", "PETG", "Fine"),
    "5": {**row(5, "30", "Green", "PLA", "Normal"), "orderable": False},
    "6": row(6, "40", "Red", "PLA", "Normal", filament_brand_name="Brand A"),
    "7": row(7, "40", "Red", "PLA", "Normal", filament_brand_name="Brand B"),
}


def fixture(data):
    options = ''.join(f'<option value="{key}" data-total="{value["unit_price"]}">Build {key}</option>'
                      for key, value in data.items())
    return f'''<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <link rel="stylesheet" href="/selector.css">
    <style>body{{font-family:Arial;margin:20px;background:#f1f5f9}}main{{max-width:650px;margin:auto}}
    .hidden{{display:none}}select,input,button{{font:inherit}}form{{display:flex;gap:12px;margin-top:20px}}
    input{{width:65px}}#order-variant-button{{padding:14px;background:#0b2238;color:white;border:0;border-radius:12px}}
    #order-variant-button:disabled{{opacity:.4}}</style><main>
    <label for="variant-select">انتخاب پروفایل و مشخصات سفارش</label>
    <select id="variant-select"><option value="">انتخاب کنید</option>{options}</select>
    <div id="price-breakdown" class="hidden"><span id="price-total"></span></div>
    <form method="post" action="/cart" class="store-order-cart-bar"><input name="variant_id" id="cart-variant-id" type="hidden">
    <input name="quantity" value="1"><button id="order-variant-button" disabled>افزودن به سبد خرید</button></form>
    </main><script src="/store.js"></script><script src="/selector.js"></script></html>'''


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 1000})
        errors, posts, batches = [], [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        data = dict(BASE)
        fail_api = False

        def route(request):
            path = urlparse(request.request.url).path
            if path == "/":
                request.fulfill(content_type="text/html", body=fixture(data))
            elif path in ("/store.js", "/selector.js", "/selector.css"):
                file = {"/store.js": "static/store/js/store.js",
                        "/selector.js": "static/store/js/phase50-profile-selector.js",
                        "/selector.css": "static/store/css/phase50-profile-selector.css"}[path]
                request.fulfill(content_type="text/css" if path.endswith('css') else "application/javascript",
                                body=(ROOT / file).read_text(encoding="utf-8"))
            elif path == "/store/api/variant-commerce-options/":
                if fail_api:
                    request.fulfill(status=503, body="Unavailable")
                    return
                ids = parse_qs(urlparse(request.request.url).query)["ids"][0].split(',')[:100]
                batches.append(ids)
                request.fulfill(json={"products": {"1": {}}, "variants": {key: data[key] for key in ids}})
            elif path == "/cart":
                posts.append(parse_qs(request.request.post_data))
                request.fulfill(body="Cart received")
            else:
                request.abort()

        page.route("**/*", route)
        page.goto('https://configurator.test/')
        expect(page.locator('.store-profile-selector.is-ready')).to_be_visible()
        expect(page.locator('#order-variant-button')).to_be_disabled()
        assert page.locator('[data-step]').evaluate_all('(nodes) => nodes.map(n => n.dataset.step)') == ['size', 'color', 'material', 'quality']
        assert page.locator('[data-step="color"] button').count() == 0
        page.locator('[data-step="size"] button', has_text='20').click()
        page.locator('[data-step="color"] button', has_text='Red').click()
        assert page.locator('[data-step="material"] button').all_text_contents() == ['PLA', 'PETG']
        page.locator('[data-step="material"] button', has_text='PETG').click()
        expect(page.locator('#cart-variant-id')).to_have_value('2')
        expect(page.locator('#order-variant-button')).to_be_enabled()
        expect(page.locator('[data-profile-summary]')).to_contain_text('۲۰۰٬۰۰۰')
        expect(page.locator('[data-profile-summary]')).to_contain_text('۱۲۰ دقیقه')
        page.locator('[data-step="size"] button', has_text='20').click()
        expect(page.locator('#cart-variant-id')).to_have_value('')
        expect(page.locator('#order-variant-button')).to_be_disabled()
        assert page.locator('[data-profile-summary]').locator('strong').count() == 0
        assert page.evaluate('document.activeElement.dataset.dimension') == 'size'
        page.locator('[data-step="size"] button', has_text='30').click()
        expect(page.locator('[data-step="color"] button', has_text='Green')).to_be_disabled()
        expect(page.locator('#cart-variant-id')).to_have_value('4')
        page.locator('[data-step="size"] button', has_text='40').click()
        expect(page.locator('#order-variant-button')).to_be_disabled()
        page.locator('[data-step="variant"] button', has_text='Brand B').click()
        expect(page.locator('#cart-variant-id')).to_have_value('7')
        page.locator('.store-profile-native-fallback summary').click()
        page.locator('#variant-select').select_option('1')
        expect(page.locator('#cart-variant-id')).to_have_value('1')
        expect(page.locator('[data-step="material"] button[aria-pressed="true"]')).to_have_text('PLA')
        page.locator('.store-profile-native-fallback summary').click()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert page.locator('.store-order-cart-bar').evaluate('(node) => getComputedStyle(node).position') == 'sticky'
        expect(page.locator('.store-profile-selector__head')).to_contain_text('۴ مرحله ساده')
        expect(page.locator('[data-step="size"] .store-profile-control__label')).to_contain_text('سایز قطعه')
        output = ROOT / '.local-qa'
        output.mkdir(exist_ok=True)
        page.screenshot(path=str(output / 'configurator-mobile.png'), full_page=True)
        page.set_viewport_size({"width": 1280, "height": 1000})
        page.screenshot(path=str(output / 'configurator-desktop.png'), full_page=True)
        page.locator('#order-variant-button').click()
        page.wait_for_url('**/cart')
        assert posts == [{"variant_id": ["1"], "quantity": ["1"]}]

        data = {str(pk): row(pk, str(pk), 'Red', 'PLA', 'Normal') for pk in range(1, 106)}
        page.goto('https://configurator.test/')
        expect(page.locator('.store-profile-selector.is-ready')).to_be_visible()
        page.locator('[data-step="size"] button', has_text='105').click()
        expect(page.locator('#cart-variant-id')).to_have_value('105')
        assert any('105' in batch for batch in batches)

        data = {"5": BASE['5']}
        page.goto('https://configurator.test/')
        expect(page.locator('.store-profile-selector.is-ready')).to_be_visible()
        expect(page.locator('#order-variant-button')).to_be_disabled()
        expect(page.locator('[data-profile-summary]')).to_contain_text('هیچ گزینه')

        data, fail_api = dict(BASE), True
        page.goto('https://configurator.test/')
        page.locator('#variant-select').select_option('2')
        expect(page.locator('#cart-variant-id')).to_have_value('2')
        expect(page.locator('#order-variant-button')).to_be_enabled()
        assert page.locator('.store-profile-selector').count() == 0
        assert not errors, errors
        browser.close()
        print('GUIDED_CONFIGURATOR_BROWSER=PASS (desktop/mobile, cart, fallback, stock, ambiguity, >100)')


if __name__ == '__main__':
    main()
