function startTyping(phrases) {
  const el = document.getElementById('typingText');
  if (!el || !phrases.length) return;

  let pi = 0, ci = 0, deleting = false;

  function tick() {
    const phrase = phrases[pi];
    el.textContent = phrase.slice(0, ci);

    if (!deleting && ci === phrase.length) {
      setTimeout(() => { deleting = true; tick(); }, 1800);
      return;
    }
    if (deleting && ci === 0) {
      deleting = false;
      pi = (pi + 1) % phrases.length;
    }
    ci += deleting ? -1 : 1;
    setTimeout(tick, deleting ? 40 : 80);
  }

  tick();
}
