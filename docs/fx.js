// Animaciones de WastedMap. Si falla o la persona pidió menos movimiento, la página se ve igual, quieta.
(() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const root = document.documentElement;
  if (reduce) { root.classList.remove("fx"); }

  // Barra superior: sombra al bajar.
  const bar = document.querySelector(".topbar");
  const onScroll = () => bar && bar.classList.toggle("scrolled", scrollY > 8);
  addEventListener("scroll", onScroll, { passive: true }); onScroll();

  // Escalonado: cada hijo de [data-stagger] entra un poquito después del anterior.
  document.querySelectorAll("[data-stagger]").forEach(list => {
    [...list.children].forEach((el, i) => el.style.setProperty("--d", `${Math.min(i, 12) * 70}ms`));
  });

  // Números que cuentan hasta su valor.
  const count = el => {
    const to = +el.dataset.count; if (!to || reduce) return;
    const t0 = performance.now(), dur = 1100;
    const step = t => {
      const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      el.textContent = Math.round(to * e);
      if (k < 1) requestAnimationFrame(step);
    };
    el.textContent = "0"; requestAnimationFrame(step);
  };

  // Aparecer al entrar en pantalla.
  const targets = document.querySelectorAll("[data-reveal]");
  if (!("IntersectionObserver" in window) || reduce) {
    targets.forEach(el => el.classList.add("in"));
  } else {
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (!en.isIntersecting) return;
      en.target.classList.add("in");
      en.target.querySelectorAll("[data-count]").forEach(count);
      io.unobserve(en.target);
    }), { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    targets.forEach(el => io.observe(el));
  }
  document.querySelectorAll(".facts [data-count]").forEach(count);

  // Cartel de "¡Secreto encontrado!" (estilo videojuego, diseño propio).
  window.wmToast = (title, sub = "") => {
    document.querySelectorAll(".wm-toast").forEach(t => t.remove());
    const t = document.createElement("div");
    t.className = "wm-toast"; t.setAttribute("role", "status");
    t.innerHTML = `<div class="wt-band"><b></b><span></span></div>`;
    t.querySelector("b").textContent = title;
    t.querySelector("span").textContent = sub;
    document.body.appendChild(t);
    setTimeout(() => t.classList.add("out"), 2300);
    setTimeout(() => t.remove(), 2900);
  };

  // Tarjetas: brillo que sigue al mouse.
  document.addEventListener("pointermove", ev => {
    const c = ev.target.closest && ev.target.closest(".thumb, .r-row img, .cats a");
    if (!c) return;
    const r = c.getBoundingClientRect();
    c.style.setProperty("--mx", `${ev.clientX - r.left}px`);
    c.style.setProperty("--my", `${ev.clientY - r.top}px`);
  }, { passive: true });
})();
