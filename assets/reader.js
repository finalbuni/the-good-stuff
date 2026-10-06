document.querySelectorAll('[data-chapters]').forEach(select => {
  select.addEventListener('change', () => { window.location.href = select.value; });
});
document.querySelectorAll('.panels img').forEach(img => {
  img.addEventListener('error', () => {
    const note = document.createElement('p');
    note.className = 'notice';
    note.textContent = img.alt + ' could not load. Try refreshing the page.';
    img.replaceWith(note);
  });
});
