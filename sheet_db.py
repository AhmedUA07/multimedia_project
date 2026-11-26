"""قاعدة البيانات = ملف شيت (database.xlsx). كل صف = صورة معدّلة.
الصور نفسها بتتحفظ في فولدر edited_images، والشيت فيه بياناتها + صورة مصغرة جوه الخلية.
الملف بيتفتح في Excel أو Google Sheets (File > Import)."""
import os
from datetime import datetime
import cv2
from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image as XLImage

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "database.xlsx")
IMG_DIR = os.path.join(BASE, "edited_images")
HEADERS = ["ID", "التاريخ", "اسم الصورة الأصلية", "العملية", "الإعدادات", "ملف الصورة", "معاينة"]


def _open(db_path):
    if os.path.exists(db_path):
        return load_workbook(db_path)
    wb = Workbook()
    ws = wb.active
    ws.title = "images"
    ws.append(HEADERS)
    for col, w in zip("ABCDEFG", [6, 20, 24, 18, 36, 34, 18]):
        ws.column_dimensions[col].width = w
    return wb


def save_image(img, original_name, operation, settings, db_path=DB_PATH, img_dir=IMG_DIR):
    """يحفظ الصورة في الفولدر ويضيف صف في الشيت. بيرجّع رقم الـ ID."""
    os.makedirs(img_dir, exist_ok=True)
    wb = _open(db_path)
    ws = wb["images"]
    new_id = ws.max_row  # الصف الأول عناوين، فالـ ID = عدد الصفوف الحالي
    fname = f"{new_id:04d}.png"
    fpath = os.path.join(img_dir, fname)
    if not cv2.imwrite(fpath, img):
        raise IOError("فشل حفظ الصورة")
    thumb = img.copy()
    h, w = thumb.shape[:2]
    s = 80 / max(h, w)
    thumb = cv2.resize(thumb, (max(1, int(w * s)), max(1, int(h * s))))
    tpath = os.path.join(img_dir, f"thumb_{new_id:04d}.png")
    cv2.imwrite(tpath, thumb)
    ws.append([new_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), original_name,
               operation, str(settings), os.path.relpath(fpath, os.path.dirname(db_path)), None])
    row = ws.max_row
    ws.row_dimensions[row].height = 65
    ws.add_image(XLImage(tpath), f"G{row}")
    wb.save(db_path)
    return new_id


def list_records(db_path=DB_PATH):
    if not os.path.exists(db_path):
        return []
    ws = load_workbook(db_path)["images"]
    return [dict(zip(HEADERS[:-1], r[:-1])) for r in ws.iter_rows(min_row=2, values_only=True)]
