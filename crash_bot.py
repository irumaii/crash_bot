
import requests
import time
from colorama import Fore, Style

# ========== إعدادات الاتصال بـ Stake ==========
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'origin': 'https://stake.com/',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'cookie': '__cf_bm=YOUR_COOKIE; cf_clearance=YOUR_CLEARANCE',
    'x-access-token': 'YOUR_API_KEY'
}

GRAPHQL_URL = 'https://stake.com/_api/graphql'

QUERY = """
  query CrashGameListHistory($limit: Int, $offset: Int) {
    crashGameList(limit: $limit, offset: $offset) {
      id
      startTime
      crashpoint
    }
  }
"""

def fetch_crash_data(limit=50, offset=0):
    variables = {"limit": limit, "offset": offset}
    payload = {
        "query": QUERY,
        "variables": variables,
        "operationName": "CrashGameListHistory"
    }

    response = requests.post(GRAPHQL_URL, headers=HEADERS, json=payload)
    data = response.json()
    
    if "data" in data and "crashGameList" in data["data"]:
        return [float(game['crashpoint']) for game in data["data"]["crashGameList"]]
    else:
        print("فشل في جلب البيانات:", data)
        return []

# ========== منطق التحليل والتوقع ==========
def analyze_and_predict(crash_data):
    low_threshold = 2.0
    safe_prediction_threshold = 3.0
    safe_streak = 0

    print(f"\nآخر {len(crash_data)} نتائج (الأحدث أولاً):")
    print(", ".join([f"{x:.2f}" for x in crash_data]))

    for result in crash_data:
        if result < low_threshold:
            safe_streak += 1
        else:
            safe_streak = 0

    # عرض التوقع بناءً على التحليل
    print("\nتحليل النتائج:")
    if safe_streak >= 3:
        print(Fore.GREEN + f"🚨 يوجد احتمال كبير لتوقع آمن في الجولة القادمة! عدد النتائج الخطيرة المتتالية: {safe_streak}" + Style.RESET_ALL)
        print(f"🎯 التوقع: على الأرجح ستكون النتيجة القادمة فوق {safe_prediction_threshold}x")
    else:
        print(Fore.YELLOW + f"⚠️ لا يوجد نمط واضح حالياً. النتائج الخطيرة المتتالية: {safe_streak}" + Style.RESET_ALL)
        print("🔄 التوصية: الانتظار حتى يتكرر نمط آمن أكثر.")

# ========== التنفيذ التلقائي ==========
if __name__ == "__main__":
    while True:
        print("\nجاري جلب النتائج من Stake ...")
        crash_data = fetch_crash_data(limit=30)
        if crash_data:
            analyze_and_predict(crash_data)
        else:
            print("⚠️ لم يتم العثور على نتائج، تحقق من صحة الاتصال.")

        time.sleep(60)  # انتظر دقيقة قبل التحديث التالي
