/**
 * Savings Goals Modal Controls & Progress Tracking
 */

function openGoalModal() {
  const modal = document.getElementById('goalModal');
  if (modal) {
    modal.classList.add('active');
    const nameInput = document.getElementById('goal-name');
    if (nameInput) nameInput.focus();
  }
}

function closeGoalModal() {
  const modal = document.getElementById('goalModal');
  if (modal) modal.classList.remove('active');
}

function openUpdateGoalModal(goalId, goalName, currentAmount) {
  const modal = document.getElementById('updateGoalModal');
  const form = document.getElementById('updateGoalForm');
  const title = document.getElementById('updateGoalTitle');
  const balanceDisplay = document.getElementById('currentSavedDisplay');

  if (!modal || !form) return;

  form.action = `/goals/update-progress/${goalId}`;
  if (title) title.innerText = `Add Funds: ${goalName}`;
  if (balanceDisplay) {
    balanceDisplay.innerText = '₹' + Number(currentAmount).toLocaleString('en-IN');
  }

  // Clear inputs
  const addInput = document.getElementById('add-amount-input');
  const setInput = document.getElementById('set-amount-input');
  if (addInput) addInput.value = '';
  if (setInput) setInput.value = '';

  modal.classList.add('active');
  if (addInput) addInput.focus();
}

function closeUpdateGoalModal() {
  const modal = document.getElementById('updateGoalModal');
  if (modal) modal.classList.remove('active');
}

// Global modal backdrop close
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('active');
  }
});
