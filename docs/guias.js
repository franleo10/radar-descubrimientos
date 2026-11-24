// Guías: filtro por capítulo, contadores del 100 %, listas para tildar y buscador de trucos.
// Todo se guarda solo en este navegador (localStorage). Si no se puede guardar, igual funciona.
(() => {
  const LANG = document.documentElement.lang.slice(0, 2);
  const PT = LANG === "pt", EN = LANG === "en";
  const tx = (es, pt, en) => EN ? en : PT ? pt : es;
  const load = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } };
  const store = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} };

  // ---- ¿Por qué capítulo vas? (0 = ver todo)
  const bars = document.querySelectorAll("[data-capbar]");
  const capItems = document.querySelectorAll("[data-cap]");
  function applyCap(v) {
    let hidden = 0;
    capItems.forEach(el => {
      const off = v > 0 && v < 5 && +el.dataset.cap > v;
      el.classList.toggle("cap-off", off);
      if (off && !el.matches(".g-group")) hidden++;
    });
    bars.forEach(b => {
      b.querySelectorAll("button").forEach(x => x.classList.toggle("on", +x.dataset.v === v));
      const s = b.querySelector("[data-caphidden]");
      s.hidden = !hidden;
      s.textContent = !hidden ? "" : tx(
        `Ocultamos ${hidden} ${hidden === 1 ? "cosa" : "cosas"} de capítulos que todavía no jugaste.`,
        `Ocultamos ${hidden} ${hidden === 1 ? "item" : "itens"} de capítulos que você ainda não jogou.`,
        `Hiding ${hidden} ${hidden === 1 ? "item" : "items"} from chapters you haven't played yet.`);
    });
    if (window.wmFilter) window.wmFilter();
  }
  if (bars.length) {
    let cap = +load("wm-cap", 0) || 0;
    bars.forEach(b => b.addEventListener("click", ev => {
      const x = ev.target.closest("button"); if (!x) return;
      cap = +x.dataset.v; store("wm-cap", cap); applyCap(cap);
    }));
    applyCap(cap);
  }

  // ---- Listas para tildar (trofeos, cartas)
  const groups = {};
  document.querySelectorAll("input[data-ck]").forEach(b => (groups[b.dataset.ck] ||= []).push(b));
  Object.entries(groups).forEach(([key, boxes]) => {
    const done = new Set(load(key, []));
    const paint = () => {
      boxes.forEach(b => { b.checked = done.has(b.dataset.id); b.closest("li").classList.toggle("is-done", b.checked); });
      const out = document.getElementById(key === "wm-trofeos" ? "tr-done" : "");
      if (out) out.textContent = boxes.filter(b => b.checked).length;
    };
    boxes.forEach(b => b.addEventListener("change", () => {
      b.checked ? done.add(b.dataset.id) : done.delete(b.dataset.id);
      store(key, [...done]); paint();
      if (b.checked && window.wmToast) {
        const n = boxes.filter(x => x.checked).length;
        key === "wm-trofeos" ? wmToast(tx("¡Trofeo desbloqueado!", "Troféu desbloqueado!", "Trophy unlocked!"), `${n} ${tx("de", "de", "of")} ${boxes.length}`)
                             : wmToast(tx("¡Colección completa!", "Coleção completa!", "Collection complete!"), `${n} ${tx("de", "de", "of")} ${boxes.length} ${tx("colecciones", "coleções", "collections")}`);
      }
    }));
    paint();
  });

  // ---- Trofeos: filtro por tipo y ocultar los conseguidos
  const trList = document.querySelector(".tr-list");
  if (trList) {
    let grade = "";
    const rows = [...trList.children];
    window.wmFilter = () => rows.forEach(r => r.classList.toggle("grade-off", !!grade && r.dataset.grade !== grade));
    document.querySelector(".tr-filter").addEventListener("click", ev => {
      const x = ev.target.closest("button"); if (!x) return;
      grade = x.dataset.grade;
      document.querySelectorAll(".tr-filter button").forEach(y => y.classList.toggle("on", y === x));
      window.wmFilter();
    });
    document.getElementById("tr-hide").addEventListener("change", ev => document.body.classList.toggle("ck-hiding", ev.target.checked));
  }

  // ---- 100 %: contadores
  const hRows = [...document.querySelectorAll(".h-row")];
  if (hRows.length) {
    const have = load("wm-100", {});
    const paint = () => {
      let sum = 0, n = 0;
      hRows.forEach(r => {
        const inp = r.querySelector("input"), need = +r.dataset.need;
        const v = Math.max(0, +inp.value || 0), k = Math.min(1, v / need);
        r.querySelector(".ck-bar i").style.width = (k * 100) + "%";
        r.classList.toggle("is-done", k >= 1);
        if (!r.classList.contains("cap-off")) { sum += k; n++; }
      });
      const pct = n ? Math.floor(100 * sum / n) : 0;
      document.getElementById("h-pct").textContent = pct;
      document.getElementById("h-all").style.width = pct + "%";
    };
    hRows.forEach(r => {
      const inp = r.querySelector("input"), key = inp.dataset.key, step = +inp.step || 1, need = +r.dataset.need;
      inp.value = have[key] || 0;
      const set = v => {
        const before = +inp.value || 0;
        inp.value = Math.max(0, v); have[key] = +inp.value; store("wm-100", have); paint();
        if (before < need && +inp.value >= need && window.wmToast) wmToast(tx("¡Objetivo cumplido!", "Objetivo cumprido!", "Goal complete!"), r.querySelector("b").textContent);
      };
      r.querySelector(".h-minus").addEventListener("click", () => set((+inp.value || 0) - step));
      r.querySelector(".h-plus").addEventListener("click", () => set((+inp.value || 0) + step));
      inp.addEventListener("change", () => set(+inp.value || 0));
    });
    document.getElementById("h-reset").addEventListener("click", () => {
      if (!confirm(tx("¿Borrar todo tu progreso del 100 %? No se puede deshacer.", "Apagar todo o seu progresso dos 100 %? Não dá para desfazer.", "Clear all your 100% progress? This can't be undone."))) return;
      hRows.forEach(r => { r.querySelector("input").value = 0; });
      Object.keys(have).forEach(k => delete have[k]); store("wm-100", have); paint();
    });
    const prev = window.wmFilter;
    window.wmFilter = () => { if (prev) prev(); paint(); };
    paint();
  }

  // ---- Trucos: buscador
  const q = document.getElementById("tk-q");
  if (q) {
    const rows = [...document.querySelectorAll(".tk-row")];
    const norm = s => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
    q.addEventListener("input", () => {
      const t = norm(q.value.trim());
      let shown = 0;
      rows.forEach(r => { const ok = !t || norm(r.dataset.q).includes(t); r.hidden = !ok; if (ok) shown++; });
      document.querySelectorAll(".tk-list").forEach(l => { l.closest(".g-group").hidden = ![...l.children].some(r => !r.hidden); });
      document.getElementById("tk-empty").hidden = shown > 0;
    });
  }
})();
