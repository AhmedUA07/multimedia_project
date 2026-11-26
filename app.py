import cv2
import numpy as np
import streamlit as st
import image_ops as ops
import sheet_db

st.set_page_config(page_title="Multimedia Project", layout="wide")
st.title("🖼️ تعديل الصور - Streamlit + OpenCV")

# ---------- الشريط الجانبي (Sidebar) ----------
with st.sidebar:
    st.header("⚙️ الإعدادات")
    user_name = st.text_input("اسمك", placeholder="اكتب اسمك")
    theme_choice = st.selectbox("نوع المستخدم", ["طالب", "مدرس", "زائر"])
    show_tips = st.checkbox("اعرض نصائح الاستخدام", value=True)
    st.date_input("تاريخ اليوم")
    if user_name:
        st.success(f"أهلاً {user_name} ({theme_choice})")
    else:
        st.info("اكتب اسمك في الشريط الجانبي")
    if show_tips:
        st.caption("ارفع صورة، اختار العملية، وبعدين احفظ أو حمّل النتيجة.")

tab_edit, tab_db, tab_form = st.tabs(["تعديل الصور", "قاعدة البيانات (الشيت)", "فورم الرأي"])

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
            ok, buf = cv2.imencode(".png", out)
            if ok:
                st.download_button("⬇️ حمّل الصورة المعدلة", buf.tobytes(),
                                   file_name="edited.png", mime="image/png")
            if st.button("💾 احفظ في الداتا بيز"):
                new_id = sheet_db.save_image(out, up.name, op, settings)
                st.success(f"اتحفظت برقم {new_id} في database.xlsx")

with tab_db:
    recs = sheet_db.list_records()
    if recs:
        st.dataframe(recs, use_container_width=True)
        with open(sheet_db.DB_PATH, "rb") as f:
            st.download_button("⬇️ حمّل ملف الداتا بيز (xlsx)", f.read(), file_name="database.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        for r in recs[-6:]:
            st.image(r["ملف الصورة"], caption=f'#{r["ID"]} - {r["العملية"]}', width=200)
    else:
        st.info("لسه مفيش صور محفوظة.")

with tab_form:
    st.subheader("📝 فورم الرأي")
    with st.form("feedback_form", clear_on_submit=False):
        f_name = st.text_input("الاسم", value=user_name)
        f_email = st.text_input("الإيميل")
        f_rate = st.slider("تقييمك للتطبيق", 1, 5, 4)
        f_like = st.multiselect("أكتر حاجة عجبتك", ["الفلاتر", "القص", "الألوان", "الداتا بيز"])
        f_type = st.radio("نوع الملاحظة", ["اقتراح", "مشكلة", "إعجاب"], horizontal=True)
        f_text = st.text_area("ملاحظاتك")
        f_agree = st.checkbox("أوافق على حفظ ردي")
        submitted = st.form_submit_button("إرسال")
    if submitted:
        if not f_name.strip():
            st.error("لازم تكتب الاسم")
        elif not f_agree:
            st.warning("لازم توافق على حفظ الرد")
        else:
            st.success(f"شكراً {f_name}! تم إرسال رأيك ✅")
            st.info(f"تقييمك: {'⭐' * f_rate} ({f_rate}/5) - النوع: {f_type}")
            if f_like:
                st.write("عجبك:", "، ".join(f_like))
            st.balloons()
