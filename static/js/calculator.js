/**
 * Interactive Real-Time EMI Loan Calculator
 */

document.addEventListener('DOMContentLoaded', () => {
  const principalInput = document.getElementById('calc-principal');
  const principalSlider = document.getElementById('slider-principal');
  const rateInput = document.getElementById('calc-rate');
  const rateSlider = document.getElementById('slider-rate');
  const tenureInput = document.getElementById('calc-tenure');
  const tenureSlider = document.getElementById('slider-tenure');

  const displayPrincipal = document.getElementById('display-principal');
  const displayRate = document.getElementById('display-rate');
  const displayTenure = document.getElementById('display-tenure');

  const emiAmount = document.getElementById('emi-amount');
  const tenureSummary = document.getElementById('tenure-summary');
  const summaryPrincipal = document.getElementById('summary-principal');
  const summaryInterest = document.getElementById('summary-interest');
  const summaryTotal = document.getElementById('summary-total');

  const principalPctLabel = document.getElementById('principal-pct-label');
  const interestPctLabel = document.getElementById('interest-pct-label');
  const ratioBarPrincipal = document.getElementById('ratio-bar-principal');

  if (!principalInput || !rateInput || !tenureInput) return;

  function formatInr(num) {
    const val = Math.round(Number(num) || 0);
    return '₹' + val.toLocaleString('en-IN');
  }

  function calculateAndRender() {
    const p = parseFloat(principalInput.value) || 0;
    const annualRate = parseFloat(rateInput.value) || 0;
    const n = parseInt(tenureInput.value, 10) || 1;

    displayPrincipal.textContent = formatInr(p);
    displayRate.textContent = annualRate + '%';
    displayTenure.textContent = n + ' Months';
    tenureSummary.textContent = n;

    if (p <= 0 || n <= 0) {
      emiAmount.textContent = '₹0';
      summaryInterest.textContent = '₹0';
      summaryTotal.textContent = '₹0';
      return;
    }

    let monthlyEmi = 0;
    let totalPayment = 0;
    let totalInterest = 0;

    if (annualRate === 0) {
      // Zero-interest loan calculation
      monthlyEmi = p / n;
      totalPayment = p;
      totalInterest = 0;
    } else {
      const r = (annualRate / 12) / 100;
      const factor = Math.pow(1 + r, n);
      monthlyEmi = (p * r * factor) / (factor - 1);
      totalPayment = monthlyEmi * n;
      totalInterest = totalPayment - p;
    }

    emiAmount.textContent = formatInr(monthlyEmi);
    summaryPrincipal.textContent = formatInr(p);
    summaryInterest.textContent = formatInr(totalInterest);
    summaryTotal.textContent = formatInr(totalPayment);

    // Percentage ratio
    const principalPct = totalPayment > 0 ? ((p / totalPayment) * 100).toFixed(1) : 100;
    const interestPct = totalPayment > 0 ? ((totalInterest / totalPayment) * 100).toFixed(1) : 0;

    principalPctLabel.textContent = `Principal: ${principalPct}%`;
    interestPctLabel.textContent = `Interest: ${interestPct}%`;
    if (ratioBarPrincipal) {
      ratioBarPrincipal.style.width = `${principalPct}%`;
    }
  }

  // Bind input and slider dual events
  principalInput.addEventListener('input', () => {
    principalSlider.value = principalInput.value;
    calculateAndRender();
  });
  principalSlider.addEventListener('input', () => {
    principalInput.value = principalSlider.value;
    calculateAndRender();
  });

  rateInput.addEventListener('input', () => {
    rateSlider.value = rateInput.value;
    calculateAndRender();
  });
  rateSlider.addEventListener('input', () => {
    rateInput.value = rateSlider.value;
    calculateAndRender();
  });

  tenureInput.addEventListener('input', () => {
    tenureSlider.value = tenureInput.value;
    calculateAndRender();
  });
  tenureSlider.addEventListener('input', () => {
    tenureInput.value = tenureSlider.value;
    calculateAndRender();
  });

  // Run initial calculation
  calculateAndRender();
});
