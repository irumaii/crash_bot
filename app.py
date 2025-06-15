import streamlit as st
import requests
import pandas as pd
import time

st.markdown("### 👋 هذا الإصدار الجديد من البوت ✅")
st.set_page_config(page_title="تحليل نتائج Crash", layout="centered")
st.markdown("## 📊 تحليل نتائج Crash - Stake")
st.markdown("### 📩 جاري تحميل آخر 50,000 نتيجة...")

@st.cache_data(show_spinner=False)
def fetch_crash_data(max_rounds=50000, batch_size=100):
    url = "https://api.stake.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://stake.com/"
    }

    query_str = """
    query CrashRounds($first: Int, $orderBy: String, $orderDirection: String) {
      crashRounds(first: $first, orderBy: $orderBy, orderDirection: $orderDirection) {
        id
        multiplier
      }
    }
    """

    all_data = []
    variables = {
        "first": batch_size,
        "orderBy": "id",
        "orderDirection": "desc"
    }

    while len(all_data) < max_rounds:
        payload = {
            "operationName": "CrashRounds",
            "variables": variables,
            "query": query_str
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                break
            json_data = response.json()
            rounds = json_data.get("data", {}).get("crashRounds", [])
            if not rounds:
                break
            all_data.extend(rounds)
            variables["cursor"] = rounds[-1]["id"]
        except Exception:
            break
        time.sleep(0.3)
    return pd.DataFrame(all_data)

def check_conditions(data):
    values = data["multiplier"].tolist()
    results = {
        "1.00 مرتين": [],
        "<1.05 مرتين": [],
        "<1.05 ثلاث مرات": [],
        "<1.20 ثلاث مرات": [],
        "<1.20 أربع مرات": [],
        "<2.00 أحد عشر مرة": [],
        "نقطة تحقق زرقاء": []
    }

    for i in range(len(values) - 11):
        segment = values[i:i+12]

        if segment[0] == 1.00 and segment[1] == 1.00:
            results["1.00 مرتين"].append(i)

        if segment[0] < 1.05 and segment[1] < 1.05:
            results["<1.05 مرتين"].append(i)

        if segment[0] < 1.05 and segment[1] < 1.05 and segment[2] < 1.05:
            results["<1.05 ثلاث مرات"].append(i)

        if segment[0] < 1.20 and segment[1] < 1.20 and segment[2] < 1.20:
            results["<1.20 ثلاث مرات"].append(i)

        if segment[0] < 1.20 and segment[1] < 1.20 and segment[2] < 1.20 and segment[3] < 1.20:
            results["<1.20 أربع مرات"].append(i)

        if all(x < 2.00 for x in segment[:11]):
            results["<2.00 أحد عشر مرة"].append(i)

        # التحقق من نقطة زرقاء (تحقق شرط ثم ظهور 1.05 خلال 140 بدون خسارة <1.05)
        for key in list(results.keys())[:-1]:
            for idx in results[key]:
                future = values[idx+len(key.split())+1: idx+140]
                if 1.05 in future and all(x >= 1.05 for x in future):
                    results["نقطة تحقق زرقاء"].append((key, idx))
    return results

def display_results(results, values):
    st.markdown("---")
    st.markdown("### ✅ النتائج:")

    for key, indices in results.items():
        if key == "نقطة تحقق زرقاء":
            for condition, idx in indices:
                st.markdown(f"<span style='color:blue'>🔵 تحقق الشرط [{condition}] ثم ظهرت 1.05 بعده خلال 140 لعبة دون أي خسارة</span>", unsafe_allow_html=True)
        else:
            for idx in indices:
                segment = values[idx:idx+12]
                if any(x == 1.05 for x in segment):
                    color = "green"
                    result = "✅ مع ظهور 1.05"
                else:
                    color = "red"
                    result = "❌ بدون ظهور 1.05"
                st.markdown(f"<span style='color:{color}'>🔹 {key}: {result} (من الجولة {idx})</span>", unsafe_allow_html=True)

    # الإحصائيات العامة بالأبيض
    st.markdown("### ⚪️ الإحصائيات العامة:")
    for key in results:
        if key != "نقطة تحقق زرقاء":
            st.markdown(f"<span style='color:white'>• {key}: {len(results[key])} مرة</span>", unsafe_allow_html=True)

try:
    df = fetch_crash_data()
    if df.empty:
        st.error("❌ فشل في تحميل البيانات.")
    else:
        df["multiplier"] = df["multiplier"].astype(float)
        st.success(f"✅ تم تحميل {len(df)} نتيجة.")
        results = check_conditions(df)
        display_results(results, df["multiplier"].tolist())
except Exception as e:
    st.error(f"❌ حدث خطأ: {str(e)}")
