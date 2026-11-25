// Votos, "me funcionó" y comentarios de cada guía (usa las funciones de /api).
(() => {
  const box = document.getElementById("community");
  if (!box) return;
  const slug = box.dataset.slug;
  const sitekey = box.dataset.sitekey;
  const $ = (s) => box.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const when = (ms) => {
    const m = (Date.now() - ms) / 6e4;
    if (m < 1) return "recién";
    if (m < 60) return `hace ${Math.floor(m)} min`;
    if (m < 1440) return `hace ${Math.floor(m / 60)} h`;
    const d = Math.floor(m / 1440);
    return d === 1 ? "ayer" : `hace ${d} días`;
  };
  let state = { likes: 0, dislikes: 0, confirms: 0, mine: null, confirmed: false };

  function paint() {
    $("[data-n=likes]").textContent = state.likes;
    $("[data-n=dislikes]").textContent = state.dislikes;
    $("[data-n=confirms]").textContent = state.confirms;
    $("[data-act=like]").setAttribute("aria-pressed", state.mine === "like");
    $("[data-act=dislike]").setAttribute("aria-pressed", state.mine === "dislike");
    const c = $("[data-act=confirm]");
    c.setAttribute("aria-pressed", state.confirmed);
    c.disabled = state.confirmed;
  }

  function paintComments(list) {
    $(".c-count").textContent = list.length ? `(${list.length})` : "";
    $(".c-list").innerHTML = list.length
      ? list.map((c) => `<li data-id="${Number(c.id) || ""}"><div class="c-head"><b>${esc(c.name)}</b><span>${when(c.created)}</span></div>`
          + `<p>${esc(c.body)}</p>${c.id ? '<button type="button" class="c-report">Reportar</button>' : ""}</li>`).join("")
      : `<li class="c-empty">Todavía no hay comentarios. ¡Sé el primero en contar si te funcionó!</li>`;
  }

  async function api(path, body) {
    const r = await fetch(path, body ? { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) } : {});
    const data = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(data.error || "Algo falló. Probá de nuevo.");
    return data;
  }

  api(`/api/stats?slug=${encodeURIComponent(slug)}`)
    .then((d) => { state = { ...state, ...d }; paint(); paintComments(d.comments || []); box.hidden = false; })
    .catch(() => { box.hidden = true; });

  // Reportar un comentario: primero se elige el motivo, después se manda.
  const REASONS = [["spam", "Spam"], ["ofensivo", "Ofensivo"], ["sexual", "Sexual"], ["otro", "Otro"]];
  $(".c-list").addEventListener("click", async (ev) => {
    const li = ev.target.closest("li[data-id]");
    if (!li) return;
    if (ev.target.closest(".c-report")) {
      if (li.querySelector(".c-why")) return;
      const why = document.createElement("div");
      why.className = "c-why";
      why.innerHTML = `<span>¿Por qué lo reportás?</span>` +
        REASONS.map(([k, t]) => `<button type="button" data-why="${k}">${t}</button>`).join("") +
        `<button type="button" class="c-cancel">Cancelar</button>`;
      li.appendChild(why);
      return;
    }
    if (ev.target.closest(".c-cancel")) { li.querySelector(".c-why")?.remove(); return; }
    const w = ev.target.closest("[data-why]");
    if (!w) return;
    li.querySelectorAll(".c-why button").forEach((x) => (x.disabled = true));
    try {
      await api("/api/report", { id: Number(li.dataset.id), reason: w.dataset.why });
      li.classList.add("c-reported");
      li.querySelector(".c-why").outerHTML = '<p class="c-thanks">Gracias por avisar. Lo vamos a revisar.</p>';
      li.querySelector(".c-report")?.remove();
    } catch (e) {
      li.querySelector(".c-why").outerHTML = `<p class="c-thanks err">${esc(e.message)}</p>`;
    }
  });

  box.addEventListener("click", async (ev) => {
    const b = ev.target.closest("[data-act]");
    if (!b || b.disabled) return;
    const act = b.dataset.act;
    const body = act === "confirm" ? { slug, confirm: true } : { slug, kind: state.mine === act ? "none" : act };
    b.disabled = true;
    try {
      const c = await api("/api/react", body);
      state = { ...state, ...c };
      if (act === "confirm") state.confirmed = true;
      else state.mine = body.kind === "none" ? null : body.kind;
    } catch (e) { alert(e.message); }
    b.disabled = false;
    paint();
  });

  // Turnstile se carga recién cuando alguien va a comentar.
  let widget = null;
  function loadTurnstile() {
    if (widget !== null || !sitekey) return;
    widget = "loading";
    window.onTurnstileLoad = () => { widget = window.turnstile.render($(".c-captcha"), { sitekey, theme: "dark", language: "es" }); };
    const s = document.createElement("script");
    s.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=onTurnstileLoad";
    s.async = true;
    document.head.appendChild(s);
  }
  const form = $(".c-form");
  form.addEventListener("focusin", loadTurnstile);
  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const msg = $(".c-msg");
    const token = window.turnstile && typeof widget === "string" && widget !== "loading" ? window.turnstile.getResponse(widget) : "";
    if (!token) { msg.className = "c-msg err"; msg.textContent = "Esperá un segundo a que termine la verificación anti-robots."; return; }
    const btn = form.querySelector("button");
    btn.disabled = true; msg.className = "c-msg"; msg.textContent = "Revisando tu comentario…";
    try {
      const f = new FormData(form);
      const r = await api("/api/comment", { slug, name: f.get("name"), email: f.get("email"), body: f.get("body"), token });
      const list = [...$(".c-list").querySelectorAll("li:not(.c-empty)")].length;
      const li = document.createElement("li");
      li.innerHTML = `<div class="c-head"><b>${esc(r.comment.name)}</b><span>recién</span></div><p>${esc(r.comment.body)}</p>`;
      if (!list) $(".c-list").innerHTML = "";
      $(".c-list").prepend(li);
      $(".c-count").textContent = `(${list + 1})`;
      form.querySelector("textarea").value = "";
      msg.className = "c-msg ok"; msg.textContent = "¡Listo! Tu comentario ya está publicado.";
    } catch (e) {
      msg.className = "c-msg err"; msg.textContent = e.message;
    }
    if (window.turnstile && widget) window.turnstile.reset(widget);
    btn.disabled = false;
  });
})();
