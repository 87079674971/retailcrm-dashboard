const currency = new Intl.NumberFormat("ru-RU");
const dateFormatter = new Intl.DateTimeFormat("ru-RU", {
  dateStyle: "medium",
  timeStyle: "short"
});

function formatMoney(value) {
  return `${currency.format(Math.round(Number(value || 0)))} ₸`;
}

function renderSummary(summary) {
  const grid = document.getElementById("summary-grid");
  const cards = [
    ["Всего заказов", summary.totalOrders],
    ["Выручка", formatMoney(summary.totalRevenue)],
    ["Средний чек", formatMoney(summary.averageCheck)],
    ["Чек > 50 000 ₸", summary.highValueOrders]
  ];

  grid.innerHTML = cards
    .map(
      ([label, value]) => `
        <article class="metric">
          <span>${label}</span>
          <strong>${value}</strong>
        </article>
      `
    )
    .join("");
}

function renderChart(series) {
  const chart = document.getElementById("chart");
  const maxOrders = Math.max(...series.map((item) => item.orders), 1);

  chart.innerHTML = series
    .map((item) => {
      const height = Math.max(10, (item.orders / maxOrders) * 180);

      return `
        <div class="chart-col">
          <div class="chart-bar-wrap">
            <div class="chart-bar" style="height:${height}px"></div>
          </div>
          <strong>${item.orders}</strong>
          <span>${item.label}</span>
        </div>
      `;
    })
    .join("");
}

function renderCities(cities) {
  const container = document.getElementById("cities");
  container.innerHTML = cities.length
    ? cities
        .map(
          (item) => `
            <div class="chip">
              <strong>${item.city}</strong>
              <span>${item.ordersCount} заказов</span>
            </div>
          `
        )
        .join("")
    : '<p class="muted">Нет данных по городам.</p>';
}

function renderRecentOrders(orders) {
  const container = document.getElementById("recent-orders");
  container.innerHTML = orders.length
    ? orders
        .map(
          (order) => `
            <article class="order-row">
              <div>
                <strong>Заказ ${order.order_number || order.retailcrm_id}</strong>
                <p>${[order.first_name, order.last_name].filter(Boolean).join(" ") || "Без имени"}</p>
              </div>
              <div>
                <strong>${formatMoney(order.order_total)}</strong>
                <p>${order.city || "Город не указан"}</p>
              </div>
              <div>
                <strong>${order.status || "без статуса"}</strong>
                <p>${order.retailcrm_created_at ? dateFormatter.format(new Date(order.retailcrm_created_at)) : "дата не указана"}</p>
              </div>
            </article>
          `
        )
        .join("")
    : '<p class="muted">Нет данных по заказам.</p>';
}

async function loadDashboard() {
  const response = await fetch("./api/dashboard");
  const data = await response.json();

  if (!response.ok || !data.ok) {
    throw new Error(data.error || "Не удалось загрузить дашборд");
  }

  document.getElementById("generated-at").textContent = `Обновлено ${dateFormatter.format(new Date(data.generatedAt))}`;
  renderSummary(data.summary);
  renderChart(data.series);
  renderCities(data.topCities);
  renderRecentOrders(data.recentOrders);
}

loadDashboard().catch((error) => {
  document.getElementById("summary-grid").innerHTML = `<p class="error">${error.message}</p>`;
});
