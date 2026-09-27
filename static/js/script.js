document.querySelectorAll('[data-confirm]').forEach((form) => {
  form.addEventListener('submit', (event) => {
    if (!window.confirm(form.dataset.confirm)) event.preventDefault();
  });
});

document.querySelectorAll('.flash-dismiss').forEach((button) => {
  button.addEventListener('click', () => button.closest('.flash').remove());
});

document.querySelectorAll('.filter-bar select').forEach((select) => {
  select.addEventListener('change', () => select.form.requestSubmit());
});