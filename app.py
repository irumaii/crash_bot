// استدعاء المكتبة
const fetch = require('node-fetch');

// نُعرف الاستعلام:
const query = `
  query CrashGameListHistory($limit: Int!, $offset: Int!) {
    crashGameList(limit: $limit, offset: $offset) {
      id
      startTime
      crashpoint
      hash {
        hash
      }
    }
  }
`;

// دالة لجلب البيانات دفعات:
async function fetchCrashHistory(limit = 100, offset = 0) {
  const res = await fetch('https://stake.com/_api/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'origin': 'https://stake.com',
      'user-agent': 'Mozilla/5.0',
    },
    body: JSON.stringify({
      query,
      variables: { limit, offset },
      operationName: 'CrashGameListHistory'
    })
  });

  const json = await res.json();
  return json.data.crashGameList;
}

// مثال لجلب وتحليل أول ٢٠ ألف نتيجة:
(async () => {
  const batchSize = 1000;
  let allGames = [];
  for (let offset = 0; offset < 20000; offset += batchSize) {
    const chunk = await fetchCrashHistory(batchSize, offset);
    if (!chunk || chunk.length === 0) break;
    allGames = allGames.concat(chunk);
  }
  
  console.log(`تم جلب ${allGames.length} جولة`);
  
  // أمثلة تحليل حسب الحالات المطلوبة:
  let case1 = 0, case2 = 0, case3 = 0;
  for (let i = 0; i < allGames.length; i++) {
    const cp = parseFloat(allGames[i].crashpoint);
    // الحالة 1: ثلاث مرات <1.20 دون ظهور 1.05 بعدها
    if (i >= 2) {
      if (
        parseFloat(allGames[i].crashpoint) < 1.20 &&
        parseFloat(allGames[i - 1].crashpoint) < 1.20 &&
        parseFloat(allGames[i - 2].crashpoint) < 1.20
      ) case1++;
    }
    // الحالة 2: رقم = 1.00 مرتين متتاليتين
    if (i >= 1) {
      if (
        parseFloat(allGames[i].crashpoint) === 1.00 &&
        parseFloat(allGames[i - 1].crashpoint) === 1.00
      ) case2++;
    }
    // الحالة 3: أقل من 0.50 ست مرات متواصلة
    if (i >= 5) {
      const slice = allGames.slice(i - 5, i + 1).map(g => parseFloat(g.crashpoint));
      if (slice.every(v => v < 0.50)) case3++;
    }
  }

  console.log('التحليلات:');
  console.log('✅ ثلاث مرات متتالية <1.20:', case1);
  console.log('✅ رقم 1.00 مرتين:', case2);
  console.log('✅ ست مرات <0.50:', case3);
})();
