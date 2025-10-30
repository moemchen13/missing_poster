from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import random
from pathlib import Path
from typing import List, Tuple
import pandas as pd


def load_csv_row(df:pd.DataFrame,irow:int)->Tuple[str,str,str,Path,List[Tuple[str,str]]]:
    if irow is None:
        raise Exception("Row index must be provided")
    record = df.iloc[irow]

    name = record["Name"]
    classification = record["Classification"]
    file_number = record["File Number"]
    image_path = record["Image Path"]

    description_lines = []
    n_attributes = (len(record) - 4) // 2
    for i in range(n_attributes):
        attr_name = record[f"Attributename {i}"]
        attr_value = record[f"Attribute {i}"]
        description_lines.append((attr_name,attr_value))
    return name,classification,file_number,image_path,description_lines


# ---------- Font helpers ----------
def _load_font(size, bold=False, fallback_ratio=1.0):
    candidates = []
    if bold:
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
        ]
    else:
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/Library/Fonts/Arial.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
        ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, int(size * fallback_ratio))
    return ImageFont.load_default()

def _text_size(draw, text, font):
    try:
        w = font.getlength(text)
        _, _, _, h = draw.textbbox((0, 0), text, font=font)
        return w, h
    except Exception:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2]-bbox[0], bbox[3]-bbox[1]


def crop_to_square_special(img: Image.Image) -> Image.Image:
    """
    If the image is approximately DIN A4 portrait (~1.414 aspect),
    crop equally from TOP and BOTTOM to make a square (side = width).
    Otherwise, center-crop to a square using the shorter side.
    """
    w, h = img.size
    aspect = h / w if w else 1
    tolerance = 0.05
    if 1.4142 * (1-tolerance) <= aspect <= 1.4142 * (1+tolerance):
        side = w
        if h > side:
            excess = h - side
            top = int(excess / 2)
            bottom = top + side
            return img.crop((0, top, w, bottom))
        else:
            return img
    else:
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        return img.crop((left, top, left + side, top + side))


def draw_labeled_wrap(draw, x, y, max_width, label, value, label_font, text_font, line_height_factor=1.2):
    """
    Draws: [BOLD LABEL]: [wrapped regular value]
    Wrapped lines after the first align to the value (hanging indent).
    Returns the new y position after drawing.
    """
    label_text = f"{label}: "
    label_w, label_h = _text_size(draw, label_text, label_font)

    first_line_width = max(0, max_width - label_w)

    words = value.split()
    lines = []
    curr = ""
    for w in words:
        trial = f"{curr} {w}".strip()
        trial_w, _ = _text_size(draw, trial, text_font)
        limit = first_line_width if not lines else max_width
        if trial_w <= limit:
            curr = trial
        else:
            if curr:
                lines.append(curr)
            curr = w
    if curr:
        lines.append(curr)

    lh = int(max(label_h, _text_size(draw, "Ag", text_font)[1]) * line_height_factor)
    draw.text((x, y), label_text, fill="black", font=label_font)
    if lines:
        draw.text((x + label_w, y), lines[0], fill="black", font=text_font)

    y += lh

    for line in lines[1:]:
        draw.text((x, y), line, fill="black", font=text_font)
        y += lh

    return y

def measure_labeled_height(draw, max_width, label, value, label_font, text_font, line_height_factor=1.2):
    label_txt = f"{label}: "
    label_w, label_h = _text_size(draw, label_txt, label_font)
    text_h = _text_size(draw, "Ag", text_font)[1]
    line_h = int(max(label_h, text_h) * line_height_factor)

    first_line_width = max(0, max_width - label_w)
    words = str(value).split()
    lines, curr = [], ""
    for w in words:
        trial = (curr + " " + w).strip()
        limit = first_line_width if not lines else max_width
        if _text_size(draw, trial, text_font)[0] <= limit:
            curr = trial
        else:
            if curr:
                lines.append(curr)
            curr = w
    if curr:
        lines.append(curr)

    num_lines = max(1, len(lines))
    return num_lines * line_h


def generate_missing_poster(
    name: str,
    classification: str,
    file_number: str,
    image_path: str,
    description_lines: list[tuple[str, str]],
    out_path: str,
    dpi: int = 300,
    phone_numbers:list[str]=["017621663536", "01629567590"]
):
    A4_W, A4_H = 2480, 3508

    margin = int(0.25 * dpi)         
    x0, y0 = margin, margin
    usable_w = A4_W - 2 * margin

    # Canvas
    img = Image.new("RGB", (A4_W, A4_H), "white")
    draw = ImageDraw.Draw(img)

    # Fonts
    header_font = _load_font(size=int(1.5 * dpi), bold=True)
    name_font   = _load_font(size=int(0.5 * dpi), bold=True)
    label_font  = _load_font(size=int(0.20 * dpi), bold=True)
    number_font = _load_font(size=int(0.30 * dpi), bold=True)
    text_font   = _load_font(size=int(0.20 * dpi), bold=False)
    call_font   = _load_font(size=int(0.4 * dpi), bold=True)
    class_font  = _load_font(size=int(0.6 * dpi), bold=True)

    # 1) Header: MISSING
    header_text = "MISSING"
    header_w, header_h = _text_size(draw, header_text, header_font)
    header_x = (A4_W - header_w) // 2
    draw.text((header_x, y0), header_text, fill=(200, 0, 0), font=header_font)
    header_w, header_h = _text_size(draw, header_text, header_font)
    underline_y = y0 + header_h + int(0.02 * dpi)
    draw.line(
        (x0, underline_y, x0 + usable_w, underline_y),
        fill=(200, 0, 0),
        width=max(3, int(0.01 * dpi))
    )
    y = underline_y + int(0.04 * dpi)

    # 2) Image and crop
    with Image.open(image_path) as pic:
        pic = pic.convert("RGB")
        enhancer = ImageEnhance.Color(pic)
        pic = enhancer.enhance(0.0)  # grayscale
        sq = crop_to_square_special(pic)

    target_w = usable_w
    target_h = target_w
    max_img_height = int(A4_H * 0.60)
    if target_h > max_img_height:
        target_h = max_img_height
        target_w = target_h

    sq_resized = sq.resize((target_w, target_h), Image.LANCZOS)

    img_x = x0 + (usable_w - target_w) // 2
    img_y = y
    img.paste(sq_resized, (img_x, img_y))

    # CLASSIFICATION
    txt = str(classification)
    tw, th = _text_size(draw, txt, class_font)
    pad = int(0.02 * dpi)

    text_rgba = Image.new("RGBA", (int(tw + 2 * pad), int(th + 2 * pad)), (0, 0, 0, 0))
    td = ImageDraw.Draw(text_rgba)
    if classification != "X":
        td.text((pad, pad), txt, font=class_font, fill=(50, 50, 50, 200))
    else:
        td.text((pad, pad), txt, font=class_font, fill=(0, 0, 0, 0))

    # Rotate it
    text_rot = text_rgba.rotate(270, expand=True, resample=Image.BICUBIC)

    side_gap = int(0.05 * dpi)  
    right_margin = x0 + usable_w*2
    placed = False

    tx_right = img_x + target_w + side_gap
    ty = img_y + (target_h - text_rot.height) // 2
    if tx_right + text_rot.width <= right_margin:
        img.paste(text_rot, (tx_right, ty), text_rot)
        placed = True

    if not placed:
        tx_left = img_x - side_gap - text_rot.width
        if tx_left >= x0:
            img.paste(text_rot, (tx_left, ty), text_rot)
            placed = True

    if not placed:
        tx = min(max(x0, tx_right), right_margin - text_rot.width)
        img.paste(text_rot, (tx, ty), text_rot)


    y = img_y + target_h + int(0.04 * dpi)  # continue layout below image

    # 3) Name — centered
    name_w, name_h = _text_size(draw, name, name_font)
    name_x = (A4_W - name_w) // 2
    draw.text((name_x, y), name, fill="black", font=name_font)
    _, name_h = _text_size(draw, name, name_font)
    y += name_h + int(0.015 * dpi)

    # 4) Footer
    #telefonnummer Jasper und Lea
    #print(phone_numbers)
    mobile_number = random.choice(phone_numbers)
    footer_text = f"PLEASE CALL - {mobile_number}!"
    fw, fh = _text_size(draw, footer_text, call_font)
    footer_x = (A4_W - fw) // 2
    footer_y = max(y, A4_H - margin - fh)

    file_text = f"#{file_number}"
    file_w, file_h = _text_size(draw, file_text, number_font)
    file_x = (A4_W - file_w) // 2
    draw.text((file_x, y), file_text, fill="black", font=number_font)
    y += file_h + int(0.02 * dpi)

    # 5) Descriptions bracketed by black lines
    items = list(description_lines[:4])
    top_y = y + int(0.015 * dpi)          
    bottom_y = footer_y - int(0.02 * dpi)

    # Thin black lines
    rule_w = max(2, int(0.006 * dpi))
    top_rule_y = top_y
    bottom_rule_y = bottom_y

    draw.line((x0, top_rule_y, x0 + usable_w, top_rule_y), fill="black", width=rule_w)
    draw.line((x0, bottom_rule_y, x0 + usable_w, bottom_rule_y), fill="black", width=rule_w)

    inset = int(0.015 * dpi)   # keep text off the lines a bit
    top_y = top_rule_y + inset
    bottom_y = bottom_rule_y - inset

    available_h = max(0, bottom_y - top_y)

    heights = [
        measure_labeled_height(draw, usable_w, lbl, val, label_font, text_font)
        for (lbl, val) in items
    ]
    content_h = sum(heights)
    n = len(items)
    gap = max(0, (available_h - content_h) / (n + 1))

    curr_y = top_y + gap
    for (lbl, val), h in zip(items, heights):
        curr_y = draw_labeled_wrap(
            draw, x=x0, y=int(curr_y), max_width=usable_w,
            label=str(lbl), value=str(val),
            label_font=label_font, text_font=text_font
        )
        curr_y += gap

    # 6) Footer
    draw.text((footer_x, footer_y), footer_text, fill="red", font=call_font)

    # Save
    out_path = str(out_path)
    ext = Path(out_path).suffix.lower()
    if ext == ".pdf":
        img.save(out_path, "PDF", resolution=dpi)
    else:
        img.save(out_path, quality=95)

    return out_path



def csv_to_posters(df:pd.DataFrame,out_dir:Path,phone_numbers:list[str]=["017621663536", "01629567590"]):
    out_dir = Path(out_dir)
    for i in range(df.shape[0]):
        person = load_csv_row(df=df,irow=i)
        person_name = person[0].replace(" ", "_")
        filename = person_name +"_missing_poster.pdf"
        generate_missing_poster(*person,out_path = out_dir/filename,phone_numbers=phone_numbers)
        print(f"Saved: {filename}")
    print("Finished all Missing posters")


def read_csv(path:str)->pd.DataFrame:
    return pd.read_csv(Path(path),sep=";")