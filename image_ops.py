"""عمليات OpenCV: فلاتر، قص، تغيير ألوان. كل الدوال بتاخد صورة BGR (numpy) وبترجّع صورة BGR."""
import cv2
import numpy as np

FILTERS = ["رمادي", "تغبيش (Blur)", "حواف (Edges)", "حدة (Sharpen)", "سيبيا (Sepia)", "سالب (Negative)"]
COLOR_MODES = ["RGB → BGR (تبديل القنوات)", "HSV", "تعديل السطوع والتباين", "تغيير تدرج اللون (Hue)"]


def apply_filter(img, name, strength=5):
    k = int(strength) * 2 + 1  # رقم فردي
    if name == "رمادي":
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    if name == "تغبيش (Blur)":
        return cv2.GaussianBlur(img, (k, k), 0)
    if name == "حواف (Edges)":
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(cv2.Canny(g, 100, 200), cv2.COLOR_GRAY2BGR)
    if name == "حدة (Sharpen)":
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        return cv2.filter2D(img, -1, kernel)
    if name == "سيبيا (Sepia)":
        m = np.array([[0.272, 0.534, 0.131],
                      [0.349, 0.686, 0.168],
                      [0.393, 0.769, 0.189]])  # صفوف B,G,R
        return np.clip(cv2.transform(img, m), 0, 255).astype(np.uint8)
    if name == "سالب (Negative)":
        return cv2.bitwise_not(img)
    raise ValueError(f"فلتر غير معروف: {name}")


def crop(img, x, y, w, h):
    H, W = img.shape[:2]
    x, y = max(0, int(x)), max(0, int(y))
    x2, y2 = min(W, x + int(w)), min(H, y + int(h))
    if x2 <= x or y2 <= y:
        raise ValueError("منطقة القص خارج الصورة")
    return img[y:y2, x:x2].copy()


def change_color(img, mode, a=0, b=0):
    """a,b حسب الوضع: للسطوع/التباين a=سطوع(-100..100) b=تباين(0.5..3)، للـ Hue a=زاوية(0..179)"""
    if mode == COLOR_MODES[0]:
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if mode == COLOR_MODES[1]:
        return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    if mode == COLOR_MODES[2]:
        return cv2.convertScaleAbs(img, alpha=float(b) if b else 1.0, beta=float(a))
    if mode == COLOR_MODES[3]:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv[..., 0] = (hsv[..., 0].astype(int) + int(a)) % 180
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    raise ValueError(f"وضع غير معروف: {mode}")
