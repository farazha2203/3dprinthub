from pathlib import Path
from PIL import Image, ImageOps


BASE_DIR = Path(__file__).resolve().parent.parent

SOURCE = BASE_DIR / "static" / "source" / "logo-sheet.png"

BRAND_DIR = BASE_DIR / "static" / "img" / "brand"
FAVICON_DIR = BASE_DIR / "static" / "favicon"

BRAND_DIR.mkdir(parents=True, exist_ok=True)
FAVICON_DIR.mkdir(parents=True, exist_ok=True)


def crop_by_ratio(image, box_ratio):
    width, height = image.size

    left = int(width * box_ratio[0])
    top = int(height * box_ratio[1])
    right = int(width * box_ratio[2])
    bottom = int(height * box_ratio[3])

    return image.crop((left, top, right, bottom))


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Source logo image not found: {SOURCE}")

    image = Image.open(SOURCE).convert("RGBA")

    # برش لوگوی اصلی از بخش بالای عکس
    # اگر کمی جابه‌جا بود، عددها را خیلی کم تغییر می‌دهیم
    full_logo = crop_by_ratio(
        image,
        (
            0.28,  # left
            0.04,  # top
            0.74,  # right
            0.50,  # bottom
        )
    )

    full_logo.save(BRAND_DIR / "logo-full.png")

    # نسخه مناسب هدر، کمی عریض‌تر
    header_logo = ImageOps.contain(full_logo, (520, 220), Image.Resampling.LANCZOS)
    header_logo.save(BRAND_DIR / "logo-header.png")

    # برش آیکن 3D برای favicon
    icon_crop = crop_by_ratio(
        image,
        (
            0.34,  # left
            0.04,  # top
            0.66,  # right
            0.34,  # bottom
        )
    )

    square_icon = ImageOps.fit(
        icon_crop,
        (512, 512),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.45),
    )

    square_icon.save(BRAND_DIR / "logo-icon-512.png")
    square_icon.save(FAVICON_DIR / "android-chrome-512x512.png")

    for size in [16, 32, 48, 64, 128, 180, 192, 256]:
        resized = square_icon.resize((size, size), Image.Resampling.LANCZOS)

        if size == 180:
            resized.save(FAVICON_DIR / "apple-touch-icon.png")
        elif size == 192:
            resized.save(FAVICON_DIR / "android-chrome-192x192.png")
        else:
            resized.save(FAVICON_DIR / f"favicon-{size}x{size}.png")

    ico_image = square_icon.convert("RGBA")
    ico_image.save(
        FAVICON_DIR / "favicon.ico",
        sizes=[
            (16, 16),
            (32, 32),
            (48, 48),
            (64, 64),
            (128, 128),
            (256, 256),
        ],
    )

    print("Brand assets generated successfully:")
    print(BRAND_DIR / "logo-full.png")
    print(BRAND_DIR / "logo-header.png")
    print(BRAND_DIR / "logo-icon-512.png")
    print(FAVICON_DIR / "favicon.ico")


if __name__ == "__main__":
    main()