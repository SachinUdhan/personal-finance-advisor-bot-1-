/**
 * Dashboard Analytics & Chart.js Integration
 */

document.addEventListener('DOMContentLoaded', () => {
  const categoryCanvas = document.getElementById('categoryChart');
  const cashflowCanvas = document.getElementById('cashflowChart');
  const categoryFallback = document.getElementById('categoryChartFallback');

  if (!categoryCanvas || !cashflowCanvas) return;

  // Format number as INR for chart tooltips
  const formatInrJs = (num) => {
    return '₹' + Number(num).toLocaleString('en-IN', { maximumFractionDigits: 0 });
  };

  // Fetch live chart dataset from API
  fetch('/api/dashboard/chart-data')
    .then(res => res.json())
    .then(data => {
      // 1. Expense Category Doughnut Chart
      const catLabels = data.categories.labels || [];
      const catValues = data.categories.values || [];

      if (catValues.length === 0 || catValues.every(v => v === 0)) {
        categoryCanvas.style.display = 'none';
        if (categoryFallback) categoryFallback.style.display = 'block';
      } else {
        const vibrantColors = [
          '#10b981', '#06b6d4', '#6366f1', '#8b5cf6',
          '#f59e0b', '#ec4899', '#3b82f6', '#f97316', '#14b8a6'
        ];

        new Chart(categoryCanvas.getContext('2d'), {
          type: 'doughnut',
          data: {
            labels: catLabels,
            datasets: [{
              data: catValues,
              backgroundColor: vibrantColors.slice(0, catLabels.length),
              borderWidth: 2,
              borderColor: '#111827',
              hoverOffset: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'right',
                labels: {
                  color: '#94a3b8',
                  font: { family: 'Inter', size: 11 },
                  boxWidth: 12,
                  padding: 10
                }
              },
              tooltip: {
                callbacks: {
                  label: function (ctx) {
                    const val = ctx.raw || 0;
                    const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                    const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                    return ` ${ctx.label}: ${formatInrJs(val)} (${pct}%)`;
                  }
                }
              }
            },
            cutout: '65%'
          }
        });
      }

      // 2. Cash Flow Comparison Bar Chart
      const compLabels = data.comparison.labels || ['Monthly Income', 'Total Expenses', 'Net Savings'];
      const compValues = data.comparison.values || [0, 0, 0];

      new Chart(cashflowCanvas.getContext('2d'), {
        type: 'bar',
        data: {
          labels: compLabels,
          datasets: [{
            data: compValues,
            backgroundColor: [
              'rgba(16, 185, 129, 0.8)',
              'rgba(239, 68, 68, 0.8)',
              'rgba(6, 182, 212, 0.8)'
            ],
            borderColor: ['#10b981', '#ef4444', '#06b6d4'],
            borderWidth: 1,
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: function (ctx) {
                  return ` ${ctx.label}: ${formatInrJs(ctx.raw)}`;
                }
              }
            }
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: '#94a3b8', font: { family: 'Inter', size: 12 } }
            },
            y: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: {
                color: '#64748b',
                callback: function (val) {
                  return formatInrJs(val);
                }
              }
            }
          }
        }
      });
    })
    .catch(err => {
      console.warn("Chart data load warning:", err);
    });
});
