import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Crash Game Bot", layout="centered")

st.title("🚀 Crash Game Predictor Bot")

st.write("""
قم بتحميل ملف CSV يحتوي على نتائج اللعبة أو أدخل النتائج يدويًا لتحليلها.
""")

# تحميل ملف CSV
uploaded_file = st.file_uploader("📁 حمّل ملف CSV", type=["csv"])

# قراءة البيانات
df = None
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ تم تحميل البيانات بنجاح!")
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء قراءة الملف: {e}")

# إدخال يدوي
if df is None:
    st.write("أو أدخل البيانات يدويًا:")
    manual_data = st.text_area("📋 أدخل القيم مفصولة بفواصل (مثال: 1.5, 2.1, 3.0):")
    if manual_data:
        try:
            values = [float(x.strip()) for x in manual_data.split(",")]
            df = pd.DataFrame(values, columns=["Crash Multipliers"])
            st.success("✅ تم إنشاء البيانات من الإدخال اليدوي!")
        except:
            st.error("❌ تأكد من أن البيانات مدخلة بشكل صحيح.")

# تحليل البيانات
if df is not None:
    st.subheader("📊 تحليل النتائج")
    st.write(df.describe())

    st.subheader("📈 رسم بياني للقيم")
    fig, ax = plt.subplots()
    df.plot(kind="line", ax=ax)
    st.pyplot(fig)

    st.subheader("✅ اقتراح آمن")
    avg = df.mean().values[0]
    st.info(f"🔎 المتوسط الحسابي للجولات: **{avg:.2f}** - يمكنك استخدامه كمرجع لقرارك.")
