"""Turn the source brand images into web-ready files for one preview site.

Usage: python3 prep_images.py <brand> <out_dir>
Reads ./src/<brand>/ and writes <out_dir>/assets/img/.
"""
import shutil
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent


def webp(src, dst, width=None, quality=78):
    im = Image.open(src)
    im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
    if width and im.width > width:
        h = round(im.height * width / im.width)
        im = im.resize((width, h), Image.LANCZOS)
    im.save(dst, "WEBP", quality=quality, method=6)
    return im.size


def main(brand, out):
    src = HERE / "src" / brand
    img = Path(out) / "assets" / "img"
    img.mkdir(parents=True, exist_ok=True)
    sizes = {}
    for icon in ["car", "motorcycle", "ship", "rv", "caravan"]:
        shutil.copy(src / f"{icon}-duotone.svg", img / f"{icon}.svg")
    if brand == "vfv":
        sizes["logo"] = webp(src / "vfv-logo-horizontal.png", img / "logo.webp", 400, 90)
        Image.open(src / "vfv-logo-horizontal.png").save(img / "logo.png")
        sizes["hero-480"] = webp(src / "disabled_vet.jpg", img / "hero-480.webp", 480)
        sizes["hero-856"] = webp(src / "disabled_vet.jpg", img / "hero-856.webp", 856)
        sizes["photo"] = webp(src / "should_know.jpg", img / "veterans-photo.webp", 1200)
        sizes["badge"] = webp(src / "vfv-badge-200m-2026-08.png", img / "badge.webp", 226, 90)
        Image.open(src / "vfv-social-default-2026-08.png").convert("RGB").save(img / "og.png", optimize=True)
        shutil.copy(src / "vfv-social-x-square-2026-08.png", img / "icon-512.png")
    else:
        shutil.copy(src / "Wheels-For-Wishes-Logo-2021-sq.svg", img / "logo.svg")
        sizes["maw"] = webp(src / "benefiting-make-a-wish.png", img / "make-a-wish.webp", 267, 92)
        for w in (640, 1280, 1920):
            sizes[f"hero-{w}"] = webp(src / "wfw-maw-hero-clara-01.jpg", img / f"hero-{w}.webp", w)
        sizes["check"] = webp(src / "wfw-maw-check-02.jpg", img / "check.webp", 900)
        sizes["slide"] = webp(src / "wfw-maw-slide-01.jpg", img / "slide.webp", 1200)
        for kid in ["Ethan-6-cystic-fibrosis-garbageman", "Chloe-8-leukemia-duderanch",
                    "Areice-5-cancer-pirate", "Jack-14-cancer-skiing-in-Aspen"]:
            name = kid.split("-")[0].lower()
            sizes[name] = webp(src / f"wfw-maw-{kid}.jpg", img / f"wish-{name}.webp", 300)
        sizes["badge"] = webp(src / "car-donation-foundation-badge-200m-2026-08.png", img / "badge.webp", 260, 90)
        Image.open(src / "wfw-social-default-2026-08.png").convert("RGB").save(img / "og.png", optimize=True)
        shutil.copy(src / "wfw-social-x-square-2026-08.png", img / "icon-512.png")
    for k, v in sizes.items():
        print(f"{k}: {v[0]}x{v[1]}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
