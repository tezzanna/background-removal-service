"""Собирает demo.gif для README из реальных результатов research/outputs.
Честно: это не запись экрана интерфейса, а анимация "исходник -> результат"
на нескольких тестовых фото, чтобы сразу было видно качество и прозрачность фона.
"""
from PIL import Image, ImageDraw, ImageFont

TARGET_W, TARGET_H = 480, 320
CANVAS_W, CANVAS_H = 520, 380
CHECKER = 16

def make_checkerboard(w, h, size=CHECKER):
    bg = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(bg)
    c1, c2 = (235, 235, 235), (255, 255, 255)
    for y in range(0, h, size):
        for x in range(0, w, size):
            color = c1 if ((x // size) + (y // size)) % 2 == 0 else c2
            draw.rectangle([x, y, x + size, y + size], fill=color)
    return bg

def fit(img, w, h):
    img = img.copy()
    img.thumbnail((w, h), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ox = (w - img.width) // 2
    oy = (h - img.height) // 2
    canvas.paste(img, (ox, oy), img if img.mode == "RGBA" else None)
    return canvas

def make_frame(original_path, result_path, label):
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (255, 255, 255))

    orig = Image.open(original_path).convert("RGB")
    orig_fit = fit(orig, TARGET_W, TARGET_H).convert("RGB")
    canvas.paste(orig_fit, (20, 40))

    checker = make_checkerboard(TARGET_W, TARGET_H)
    result = Image.open(result_path).convert("RGBA")
    result_fit = fit(result, TARGET_W, TARGET_H)
    checker.paste(result_fit, (0, 0), result_fit)
    canvas.paste(checker, (20, 40))

    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
    draw.text((20, 12), label, fill=(30, 30, 30), font=font)
    return canvas

pairs = [
    ("research/sample_images/animal.jpg", "research/outputs/animal__isnet-general-use.png", "Удаление фона — пример 1/3 (тигр)"),
    ("research/sample_images/car.jpg", "research/outputs/car__isnet-general-use.png", "Удаление фона — пример 2/3 (объект)"),
    ("research/sample_images/girl.jpg", "research/outputs/girl__isnet-general-use.png", "Удаление фона — пример 3/3 (портрет)"),
]

frames = []
for orig_path, result_path, label in pairs:
    frame_before = make_frame(orig_path, orig_path, label + " — исходное")
    frame_after = make_frame(orig_path, result_path, label + " — результат")
    frames.extend([frame_before] * 12 + [frame_after] * 18)

frames[0].save(
    "docs/assets/demo.gif",
    save_all=True,
    append_images=frames[1:],
    duration=90,
    loop=0,
)
print("Готово:", len(frames), "кадров")
