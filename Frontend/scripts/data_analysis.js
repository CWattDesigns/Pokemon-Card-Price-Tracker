document.addEventListener("DOMContentLoaded", () => {
  // Set your backend URL here (e.g., "http://your-server:5000")
  const BACKEND_BASE_URL = "<INSERT_YOUR_BACKEND_URL_HERE>";

  // Utility functions
  const formatNumber = (val, decimals = 2) => {
    const num = Number(val);
    return isNaN(num) ? "N/A" : num.toFixed(decimals);
  };

  const formatDate = (rawDate) => {
    const date = new Date(rawDate);
    return date.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric"
    }).replace(",", " -");
  };

  const formatWithCommas = (num) => Number(num).toLocaleString();

  const getCardImage = async (id) => {
    const res = await fetch(`https://api.pokemontcg.io/v2/cards/${id}`);
    const data = await res.json();
    return data?.data?.images?.small || "";
  };

  // 1. Volatility List
  fetch(`${BACKEND_BASE_URL}/analysis/volatility`)
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById("volatileList");
      list.innerHTML = "";
      data.forEach(card => {
        const li = document.createElement("li");
        li.innerHTML = `<span><strong>${card.name}</strong> (${card.unique_id})</span><span>${formatNumber(card.change)}%</span>`;
        list.appendChild(li);
      });
    })
    .catch(err => console.error("Error loading volatility:", err));

  // 2. Rarity Changes
  fetch(`${BACKEND_BASE_URL}/analysis/rarity_changes`)
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById("rarityChangeList");
      list.innerHTML = "";
      data.forEach(item => {
        const color = item.change >= 0 ? "green" : "red";
        const sign = item.change >= 0 ? "+" : "";
        const li = document.createElement("li");
        li.innerHTML = `${item.rarity}: <strong style="color: ${color};">${sign}${formatNumber(item.change)}%</strong>`;
        list.appendChild(li);
      });
    })
    .catch(err => console.error("Error loading rarity changes:", err));

  // 3. Summary + Most/Least Expensive Cards
  fetch(`${BACKEND_BASE_URL}/analysis/full_summary`)
    .then(res => res.json())
    .then(async data => {
      const summary = document.getElementById("cardVolumeSummary");
      const [startDate, endDate] = data.timeframe.split(" to ");

      summary.innerHTML = `
        <p><strong>Average Cards Tracked:</strong> ${formatWithCommas(Math.round(data.total_rows / 12))}</p>
        <p><strong>Data Pulls:</strong> 12</p>
        <p><strong>Timeframe:</strong> ${formatDate(startDate)} to ${formatDate(endDate)}</p>
        <p><strong>Total Rows:</strong> ${formatWithCommas(data.total_rows)}</p>
        <p><strong>Total Data Points:</strong> ${formatWithCommas(data.total_datapoints)}</p>
      `;

      const mostImage = await getCardImage(data.most_expensive.id);
      const leastImage = await getCardImage(data.least_expensive.id);
      const expensive = document.getElementById("mostExpensiveCard");

      expensive.innerHTML = `
        <div style="text-align: center;">
          <img src="${mostImage}" alt="Most Expensive Card" style="max-height: 100px; margin-bottom: 8px;" />
          <p><strong>Most Expensive:</strong><br>${data.most_expensive.name} (${data.most_expensive.id})<br>$${formatNumber(data.most_expensive.price)}</p>
        </div>
        <div style="height: 15px;"></div>
        <div style="text-align: center;">
          <img src="${leastImage}" alt="Least Expensive Card" style="max-height: 100px; margin-bottom: 8px;" />
          <p><strong>Least Expensive:</strong><br>${data.least_expensive.name} (${data.least_expensive.id})<br>$${formatNumber(data.least_expensive.price)}</p>
        </div>
      `;
    })
    .catch(err => console.error("Error loading full summary:", err));

  // 4. Top Cards by Rarity (Scatterplot)
  fetch(`${BACKEND_BASE_URL}/analysis/top_by_rarity`)
    .then(res => res.json())
    .then(data => {
      const canvas = document.createElement("canvas");
      canvas.id = "rarityScatterPlot";
      canvas.width = 1400;
      canvas.height = 700;
      document.getElementById("topByRarityContainer").appendChild(canvas);

      const rarities = Object.keys(data);
      const colors = [
        "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
        "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe",
        "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000"
      ];

      const datasets = rarities.map((rarity, idx) => ({
        label: rarity,
        data: data[rarity].map(card => ({
          x: rarity,
          y: card.price,
          name: card.name,
          id: card.unique_id
        })),
        backgroundColor: colors[idx % colors.length]
      }));

      new Chart(canvas, {
        type: "scatter",
        data: { datasets },
        options: {
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: context => {
                  const { name, id, y } = context.raw;
                  return [`${name} (${id})`, `Price: $${formatNumber(y)}`];
                }
              }
            }
          },
          scales: {
            x: {
              type: "category",
              labels: rarities,
              title: { display: true, text: "Rarity" }
            },
            y: {
              beginAtZero: true,
              title: { display: true, text: "Market Price ($)" }
            }
          }
        }
      });
    })
    .catch(err => console.error("Error loading top cards by rarity:", err));
});
