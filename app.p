import streamlit as st
import requests

st.set_page_config(page_title="Crash Analyzer for Stake", layout="wide")
st.title("📊 تحليل لعبة Crash على Stake")
st.markdown(
    """
البوت يحسب فقط عدد مرّات تحقّق الشروط التالية **دون** ظهور ‎1.05 بعدها:

1. أقل من **1.20** ثلاث مرّات متتالية  
2. **1.00** مرّتين متتاليتين  
3. أقل من **0.50** ستّ مرّات متتالية
"""
)

# عدد النتائج المطلوب تحليلها
limit = st.number_input("عدد الجولات المراد تحليلها", 1000, 50000, 20000, 1000)

# بيانات المصادَقة (تُلصق من المتصفّح أو HTTP Catcher)
st.subheader("🔐 بيانات المصادَقة من Stake")
access_token   = st.text_input("x-access-token", type="password")
cf_bm          = st.text_input("__cf_bm",        type="password")
cf_clearance   = st.text_input("cf_clearance",    type="password")

if st.button("ابدأ التحليل"):
    if not (access_token and cf_bm and cf_clearance):
        st.error("يرجى ملء الحقول الثلاثة كلها.")
        st.stop()

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-access-token": access_token,
        "cookie": f"__cf_bm={cf_bm}; cf_clearance={cf_clearance}",
        "origin": "https://stake.com",
        "user-agent": "Mozilla/5.0",
    }

    query = """
    query CrashGameListHistory($limit: Int, $offset: Int) {
      crashGameList(limit: $limit, offset: $offset) {
        crashpoint
      }
    }
    """

    all_points = []
    step = 500                         # نسحب على دفعات كيلا يتجاوز الطلب الحدّ
    with st.spinner("جلب البيانات …"):
        for offset in range(0, limit, step):
            payload = {
                "query"        : query,
                "variables"    : {"limit": step, "offset": offset},
                "operationName": "CrashGameListHistory",
            }
            r = requests.post("https://stake.com/_api/graphql",
                              json=payload, headers=headers)
            if r.status_code != 200:
                st.error(f"فشل عند offset {offset} – كود {r.status_code}")
                st.stop()
            data = r.json()["data"]["crashGameList"]
            all_points.extend(float(item["crashpoint"]) for item in data)

    st.success(f"تم جلب {len(all_points)} نتيجة ✅")

    # العدّ
    c1 = c2 = c3 = 0
    n   = len(all_points)

    for i in range(n):
        # شرط 1
        if i + 3 < n and all(p < 1.20 for p in all_points[i:i+3]) \
           and all_points[i+3] != 1.05:
            c1 += 1
        # شرط 2
        if i + 2 < n and all_points[i] == all_points[i+1] == 1.00 \
           and all_points[i+2] != 1.05:
            c2 += 1
        # شرط 3
        if i + 6 < n and all(p < 0.50 for p in all_points[i:i+6]) \
           and all_points[i+6] != 1.05:
            c3 += 1

    st.header("🔢 النتائج")
    st.write(f"‎**شرط 1** (< 1.20 × 3)      → `{c1}` مرّة")
    st.write(f"‎**شرط 2** (1.00 × 2)        → `{c2}` مرّة")
    st.write(f"‎**شرط 3** (< 0.50 × 6)      → `{c3}` مرّة")
