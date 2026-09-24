/**
 * Expense & Income Modal Controls and Dynamic Behavior
 */

function openExpenseModal() {
  const modal = document.getElementById('expenseModal');
  if (modal) {
    modal.classList.add('active');
    const titleInput = document.getElementById('add-title');
    if (titleInput) titleInput.focus();
  }
}

function closeExpenseModal() {
  const modal = document.getElementById('expenseModal');
  if (modal) modal.classList.remove('active');
}

function openIncomeModal() {
  const modal = document.getElementById('incomeModal');
  if (modal) {
    modal.classList.add('active');
    const sourceInput = document.getElementById('inc-source');
    if (sourceInput) sourceInput.focus();
  }
}

function closeIncomeModal() {
  const modal = document.getElementById('incomeModal');
  if (modal) modal.classList.remove('active');
}

function openEditExpenseModal(id, title, amount, category, date, description) {
  const modal = document.getElementById('editExpenseModal');
  const form = document.getElementById('editExpenseForm');
  if (!modal || !form) return;

  form.action = `/expenses/edit/${id}`;
  document.getElementById('edit-title').value = title;
  document.getElementById('edit-amount').value = amount;
  document.getElementById('edit-category').value = category;
  document.getElementById('edit-date').value = date;
  document.getElementById('edit-desc').value = description || '';

  modal.classList.add('active');
}

function closeEditExpenseModal() {
  const modal = document.getElementById('editExpenseModal');
  if (modal) modal.classList.remove('active');
}

// Close modals when clicking backdrop
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('active');
  }
});

// ESC key to close open modals
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
  }
});
