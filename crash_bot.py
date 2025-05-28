
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Crash Predictor", layout="centered")

# ---------------------- العنوان ----------------------
st.title("🎯 بوت توقع نتائج لعبة Crash")
st.markdown("أدخل النتائج السابقة يدويًا أو من ملف CSV، وستحصل على التوقع القادم مع تحليل مبسط.")

# ---------------------- تحميل ملف CSV ----------------------
st.subheader("📂 تحميل ملف CSV")
uploaded_file = st.file_uploader("ارفع ملف النتائج هنا", type="csv")

all_data = []

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    if df.shape[1] == 1:
        all_data = df.iloc[:, 0].tolist()
        st.success("✅ تم تحميل البيانات من CSV.")
    else:
        st.error("❌ الملف يجب أن يحتوي على عمود واحد فقط.")

# ---------------------- إدخال يدوي جماعي ----------------------
st.subheader("✍️ إدخال النتائج يدويًا (افصل القيم بفاصلة أو سطر جديد)")
manual_input = st.text_area("مثال: 1.23, 2.45, 3.67")

if manual_input:
    try:
        entries = [float(x.strip()) for x in manual_input.replace('\n', ',').split(',') if x.strip()]
        all_data.extend(entries)
        st.success(f"✅ تمت إضافة {len(entries)} نتيجة.")
    except:
        st.error("❌ الرجاء إدخال أرقام فقط مفصولة بفواصل أو أسطر.")

# ---------------------- إدخال نتيجة جديدة مباشرة ----------------------
st.subheader("➕ أضف نتيجة جديدة مباشرة")
new_result = st.text_input("أدخل النتيجة الأخيرة (مثال: 2.45):")

if st.button("أضف النتيجة"):
    try:
        value = float(new_result)
        all_data.append(value)
        st.success(f"✅ تمت إضافة {value} بنجاح.")
    except:
        st.error("❌ الرجاء إدخال رقم صالح.")

# ---------------------- تحليل إحصائي ----------------------
if len(all_data) > 0:
    st.markdown("---")
    st.subheader("📊 تحليل النتائج")

    max_val = max(all_data)
    min_val = min(all_data)
    avg_val = np.mean(all_data)

    col1, col2, col3 = st.columns(3)
    col1.metric("🔼 أعلى نتيجة", f"{max_val:.2f}")
    col2.metric("🔽 أقل نتيجة", f"{min_val:.2f}")
    col3.metric("📉 المتوسط", f"{avg_val:.2f}")

# ---------------------- التوقع القادم ----------------------
    st.markdown("---")
    st.subheader("🔮 التوقع القادم")

    def predict_next(data):
        # نموذج بسيط: المتوسط مع بعض الوزن للنتائج الأخيرة
        recent = data[-10:] if len(data) >= 10 else data
        return round(np.mean(recent) * 0.95, 2)

    prediction = predict_next(all_data)

    # تحديد درجة الأمان
    if prediction >= 3.0:
        color = "🟢"
        risk = "فرصة آمنة"
    elif prediction >= 2.0:
        color = "🟡"
        risk = "فرصة متوسطة"
    else:
        color = "🔴"
        risk = "خطر عالي"

    st.markdown(f"### {color} التوقع: **{prediction}x** — {risk}")

# ---------------------- رسم بياني ----------------------
    st.markdown("---")
    st.subheader("📈 عرض النتائج")

    fig, ax = plt.subplots()
    ax.plot(all_data[-50:], marker='o', linestyle='-', label="النتائج")
    ax.axhline(prediction, color='orange', linestyle='--', label="التوقع التالي")
    ax.set_title("آخر 50 نتيجة")
    ax.legend()
    st.pyplot(fig)
else:
    st.info("👈 الرجاء إدخال بعض النتائج أولاً.")
