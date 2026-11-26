import cv2
import numpy as np
import streamlit as st
import image_ops as ops
import sheet_db

st.set_page_config(page_title="Multimedia Project", layout="wide")
st.title("🖼️ تعديل الصور - Streamlit + OpenCV")

tab_edit, tab_db = st.tabs(["تعديل الصور", "قاعدة البيانات (الشيت)"])

with tab_edit:
    up = st.file_uploader("ارفع صورة", type=["png", "jpg", "jpeg", "bmp"])
    if up:
        img = cv2.imdecode(np.frombuffer(up.read(), np.uint8), cv2.IMREAD_COLOR)
        H, W = img.shape[:2]
        op = st.radio("العملية", ["فلتر", "قص", "تغيير ألوان"], horizontal=True)
        settings, out = {}, None
        try:
            if op == "فلتر":
                name = st.selectbox("الفلتر", ops.FILTERS)
                strength = st.slider("القوة (للتغبيش)", 1, 20, 5)
                out, settings = ops.apply_filter(img, name, strength), {"filter": name, "strength": strength}
            elif op == "قص":
                c1, c2 = st.columns(2)
                x = c1.number_input("x", 0, W - 1, 0)
                y = c2.number_input("y", 0, H - 1, 0)
                w = c1.number_input("العرض", 1, W, W // 2)
                h = c2.number_input("الارتفاع", 1, H, H // 2)
                out, settings = ops.crop(img, x, y, w, h), {"x": x, "y": y, "w": w, "h": h}
            else:
                mode = st.selectbox("الوضع", ops.COLOR_MODES)
                a = st.slider("السطوع / زاوية الـ Hue", -100, 179, 0)
                b = st.slider("التباين", 0.5, 3.0, 1.0)
                out, settings = ops.change_color(img, mode, a, b), {"mode": mode, "a": a, "b": b}
        except ValueError as e:
            st.error(str(e))
        if out is not None:
            c1, c2 = st.columns(2)
            c1.subheader("الأصلية")
            c1.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            c2.subheader("بعد التعديل")
            c2.image(cv2.cvtColor(out, cv2.COLOR_BGR2RGB) if out.ndim == 3 else out)
            if st.button("💾 احفظ في الداتا بيز"):
                new_id = sheet_db.save_image(out, up.name, op, settings)
                st.success(f"اتحفظت برقم {new_id} في database.xlsx")

with tab_db:
    recs = sheet_db.list_records()
    if recs:
        st.dataframe(recs, use_container_width=True)
        for r in recs[-6:]:
            st.image(r["ملف الصورة"], caption=f'#{r["ID"]} - {r["العملية"]}', width=200)
    else:
        st.info("لسه مفيش صور محفوظة.")
