
import streamlit as st
import requests

st.set_page_config(page_title="Stake Crash Analyzer", layout="centered")
st.title("📊 Crash Analyzer - Stake.com")

st.markdown("""
يعتمد هذا البوت على تحليل آخر آلاف النتائج من لعبة Crash في موقع Stake ويعرض عدد مرات تحقق الشروط التالية:

1. **ثلاثة نتائج متتالية أقل من 1.20**، مع أو بدون ظهور 1.05 بعدهم.
2. **ظهور 1.00 مرتين متتاليتين**، مع أو بدون ظهور 1.05 بعدهم.
3. **ستة نتائج متتالية أقل من 0.50**، مع أو بدون ظهور 1.05 بعدهم.
""")

def fetch_crash_data(limit=20000):
    url = "https://stake.com/_api/graphql"
    headers = {
        "Content-Type": "application/json"
    }
    query = {
        "operationName": "CrashRounds",
        "variables": {
            "limit": limit,
            "cursor": None
        },
        "query": "query CrashRounds($limit: Int!, $cursor: String) { crashRounds(limit: $limit, cursor: $cursor) { edges { node { id multiplier } } } }"
    }

    response = requests.post(url, json=query, headers=headers)
    if response.status_code == 200:
        raw_data = response.json()
        return [float(edge["node"]["multiplier"]) for edge in raw_data["data"]["crashRounds"]["edges"]]
    else:
        st.error("❌ فشل في جلب البيانات من Stake.")
        return []

def analyze_conditions(data):
    condition_1_no_105 = 0
    condition_1_yes_105 = 0
    condition_2_no_105 = 0
    condition_2_yes_105 = 0
    condition_3_no_105 = 0
    condition_3_yes_105 = 0

    for i in range(len(data) - 7):
        # شرط 1: 3 مرات < 1.20
        if data[i] < 1.2 and data[i+1] < 1.2 and data[i+2] < 1.2:
            if 1.05 in data[i+3:i+6]:
                condition_1_yes_105 += 1
            else:
                condition_1_no_105 += 1

        # شرط 2: 1.00 مرتين
        if data[i] == 1.00 and data[i+1] == 1.00:
            if 1.05 in data[i+2:i+5]:
                condition_2_yes_105 += 1
            else:
                condition_2_no_105 += 1

        # شرط 3: 6 مرات < 0.50
        if all(x < 0.5 for x in data[i:i+6]):
            if 1.05 in data[i+6:i+9]:
                condition_3_yes_105 += 1
            else:
                condition_3_no_105 += 1

    return {
        "c1_no_105": condition_1_no_105,
        "c1_yes_105": condition_1_yes_105,
        "c2_no_105": condition_2_no_105,
        "c2_yes_105": condition_2_yes_105,
        "c3_no_105": condition_3_no_105,
        "c3_yes_105": condition_3_yes_105
    }

if st.button("🚀 تحليل آخر 20,000 نتيجة"):
    with st.spinner("⏳ جاري تحميل وتحليل النتائج..."):
        data = fetch_crash_data(limit=20000)
        if data:
            results = analyze_conditions(data)

            st.success("✅ تم التحليل بنجاح!")
            st.subheader("🔹 الشرط 1 (3 مرات < 1.20):")
            st.write(f"- بدون ظهور 1.05: **{results['c1_no_105']}** مرة")
            st.write(f"- مع ظهور 1.05: **{results['c1_yes_105']}** مرة")

            st.subheader("🔹 الشرط 2 (1.00 مرتين):")
            st.write(f"- بدون ظهور 1.05: **{results['c2_no_105']}** مرة")
            st.write(f"- مع ظهور 1.05: **{results['c2_yes_105']}** مرة")

            st.subheader("🔹 الشرط 3 (6 مرات < 0.50):")
            st.write(f"- بدون ظهور 1.05: **{results['c3_no_105']}** مرة")
            st.write(f"- مع ظهور 1.05: **{results['c3_yes_105']}** مرة")
