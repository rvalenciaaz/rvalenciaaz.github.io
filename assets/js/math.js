const prose = document.querySelector('.prose');

if (prose) {
  renderMathInElement(prose, {
    delimiters: [
      { left: '\\[', right: '\\]', display: true },
      { left: '$$', right: '$$', display: true },
      { left: '\\(', right: '\\)', display: false },
      { left: '$', right: '$', display: false }
    ],
    throwOnError: false,
    trust: false
  });
}
