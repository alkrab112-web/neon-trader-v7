// assistant.js
function generateMockPlan(date) {
  return {
    dailyPlan: {
      summary: "خطة اليوم: التركيز على البيتكوين والإيثريوم بسبب حجم تداول مرتفع.",
      notes: ["مراقبة مستويات الدعم", "الحذر من الأخبار الاقتصادية"]
    },
    opportunities: [
      {
        id: "btc-1",
        symbol: "BTC/USDT",
        side: "LONG",
        confidence: "GREEN",
        entry: 40000,
        stop: 39200,
        takeProfit: 42000,
        riskPct: 1,
        rationale: "اختراق مقاومة قوية.",
        status: "PENDING"
      },
      {
        id: "eth-1",
        symbol: "ETH/USDT",
        side: "SHORT",
        confidence: "YELLOW",
        entry: 2500,
        stop: 2600,
        takeProfit: 2300,
        riskPct: 1,
        rationale: "ارتداد من مقاومة أسبوعية.",
        status: "PENDING"
      },
      {
        id: "sol-1",
        symbol: "SOL/USDT",
        side: "LONG",
        confidence: "RED",
        entry: 150,
        stop: 140,
        takeProfit: 170,
        riskPct: 2,
        rationale: "إشارة ضعيفة لكن محتملة.",
        status: "PENDING"
      }
    ],
    log: []
  };
}

function renderPlan(plan) {
  const container = document.getElementById("assistant-plan");
  if (!container) return;
  container.innerHTML = `
    <div class="card">
      <h3>خطة اليوم</h3>
      <p>${plan.summary}</p>
      <ul>${plan.notes.map(n => `<li>${n}</li>`).join("")}</ul>
    </div>
  `;
}

function renderOpportunities(opps) {
  const container = document.getElementById("assistant-opps");
  if (!container) return;
  container.innerHTML = opps.map(o => `
    <div class="card">
      <h4>${o.symbol} (${o.side})</h4>
      <p>الثقة: ${o.confidence}</p>
      <p>Entry: ${o.entry} | SL: ${o.stop} | TP: ${o.takeProfit}</p>
      <p>${o.rationale}</p>
      <button onclick="approveOpportunity('${o.id}')">✅ موافقة</button>
      <button onclick="rejectOpportunity('${o.id}')">❌ رفض</button>
    </div>
  `).join("");
}

function renderLog(log) {
  const container = document.getElementById("assistant-log");
  if (!container) return;
  container.innerHTML = `
    <h3>سجل الإجراءات</h3>
    <ul>
      ${log.map(l => `<li>${new Date(l.ts).toLocaleTimeString()} - ${l.action} - ${l.symbol}</li>`).join("")}
    </ul>
  `;
}

function approveOpportunity(id) {
  addLog("APPROVED", id);
}

function rejectOpportunity(id) {
  addLog("REJECTED", id);
}

function addLog(action, id) {
  const log = JSON.parse(localStorage.getItem("assistant-log") || "[]");
  log.push({ ts: Date.now(), action, symbol: id });
  localStorage.setItem("assistant-log", JSON.stringify(log));
  renderLog(log);
}

function initAssistantView() {
  const today = new Date().toISOString().slice(0, 10);
  let state = generateMockPlan(today);
  renderPlan(state.dailyPlan);
  renderOpportunities(state.opportunities);

  const log = JSON.parse(localStorage.getItem("assistant-log") || "[]");
  renderLog(log);
}

// 🚀 شغل المساعد عند فتح الصفحة
document.addEventListener("DOMContentLoaded", () => {
  initAssistantView();
});

