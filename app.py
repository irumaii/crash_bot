import streamlit as st
import requests

# ---------------------------
# استدعاء بيانات Crash بشكل متدرج (آمن)
# ---------------------------
def fetch_crash_data(limit=50000):
    url = "https://api.stake.com/graphql"
    headers = {"Content-Type": "application/json"}
    query = """
    query crashHistory($first: Int, $after: String) {
      crashHistory(first: $first, after: $after) {
        edges {
          cursor
          node {
            multiplier
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """

    results = []
    cursor = None

    while len(results) < limit:
        variables = {"first": min(500, limit - len(results))}
        if cursor:
            variables["after"] = cursor

        try:
            response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
            data = response.json()
            edges = data["data"]["crashHistory"]["edges"]
            page_info = data["data"]["crashHistory"]["pageInfo"]
        except Exception as e:
            st.error(f"فشل في جلب البيانات: {e}")
            break

        for edge in edges:
            results.append(float(edge["node"]["multiplier"]))
        if not page_info["hasNextPage"]:
            break
        cursor = page_info["endCursor"]

    return results

# ---------------------------
# تحليل الأنماط المطلوبة
# ---------------------------
def analyze_patterns(results):
    stats = {
        "1.00 x2": 0,
        "<1.05 x2": 0,
        "<1.05 x3": 0,
        "<1.20 x3": 0,
        "<1.20 x4": 0,
        "<2.00 x11": 0
    }

    green_alerts = []
    red_alerts = []
    blue_alerts = []

    for i in range(len(results)):
        conds = {
            "1.00 x2": i+1 < len(results) and results[i]==1.00 and results[i+1]==1.00,
            "<1.05 x2": i+1 < len(results) and results[i]<1.05 and results[i+1]<1.05,
            "<1.05 x3": i+2 < len(results) and all(r<1.05 for r in results[i:i+3]),
            "<1.20 x3": i+2 < len(results) and all(r<1.20 for r in results[i:i+3]),
            "<1.20 x4": i+3 < len(results) and all(r<1.20 for r in results[i:i+4]),
            "<2.00 x11": i+10 < len(results) and all(r<2.00 for r in results[i:i+11]),
        }

        # إجمالي تحقق الشروط (أبيض)
        for key, condition in conds.items():
            if condition:
                stats[key] += 1

        # تحقق شرط + ظهور 1.05 بعده (أخضر) أو لا (أحمر)
        for key, condition in conds.items():
            if condition and i+1 < len(results):
                next_result = results[i + int(key.split('x')[-1])]
                if next_result >= 1.05:
                    green_alerts.append((i, key))
                else:
                    red_alerts.append((i, key))

        # تحقق شرط أو أكثر + 1.05 بعده + لا خسارة أقل من 1.05 خلال 140 (أزرق)
        matched_keys = [k for k, v in conds.items() if v]
        if matched_keys and i+1 < len(results):
            next_result = results[i + 1]
            if next_result >= 1.05:
                future = results[i+2:i+142]  # 140 محاولة
                if len(future) == 140 and all(r >= 1.05 for r in future):
                    blue_alerts.append((i, matched_keys))

    return stats, green_alerts, red_alerts, blue_alerts

# ---------------------------
# واجهة Streamlit
# ---------------------------
st.set_page_config(page_title="تحليل Crash", layout="wide")
st.title("📊 تحليل نتائج Crash - Stake")

with st.spinner("📥 جاري تحميل آخر 50,000 نتيجة..."):
    data = fetch_crash_data()
    if len(data) < 100:
        st.error("❌ فشل في جلب كمية كافية من البيانات.")
        st.stop()

st.success("✅ تم التحميل بنجاح!")

# تحليل النتائج
stats, green, red, blue = analyze_patterns(data)

# عرض الإحصائيات
st.header("⚪ إجمالي تحقق كل شرط")
for k, v in stats.items():
    st.markdown(f"<span style='color:white;font-weight:bold'>{k}: {v}</span>", unsafe_allow_html=True)

st.header("🟩 تحقق + ظهور 1.05 بعده")
for i, k in green:
    st.markdown(f"<span style='color:green'>Index {i} - {k}</span>", unsafe_allow_html=True)

st.header("🟥 تحقق + لم يظهر 1.05 بعده")
for i, k in red:
    st.markdown(f"<span style='color:red'>Index {i} - {k}</span>", unsafe_allow_html=True)

st.header("🔵 تحقق شرط/شروط + ظهر 1.05 + لا خسارة <1.05 خلال 140 لعبة")
for i, keys in blue:
    joined = ", ".join(keys)
    st.markdown(f"<span style='color:blue'>Index {i} - شروط: {joined}</span>", unsafe_allow_html=True)
