// Panel de administración de WastedMap. Habla con /api/admin/* usando la contraseña que se
// guarda en este navegador. Los títulos de los descubrimientos salen de /data.json.
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const KEY = "wm-admin";
  const REPO = "franleo10/radar-descubrimientos";
  let token = "";
  try { token = localStorage.getItem(KEY) || ""; } catch {}

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const num = (n) => Number(n || 0).toLocaleString("es-AR");
  const when = (ms) => {
    const d = new Date(ms), mins = (Date.now() - d) / 60000;
    if (mins < 1) return "recién";
    if (mins < 60) return `hace ${Math.round(mins)} min`;
    if (mins < 1440) return `hace ${Math.round(mins / 60)} h`;
    return d.toLocaleString("es-AR", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
  };
  // Saca un elemento de una lista y, si queda vacía, lo avisa.
  const drop = (li, empty) => {
    const ul = li.parentElement; li.remove();
    if (!ul.querySelector(".it")) ul.innerHTML = `<li class="empty">${empty}</li>`;
  };
  const toast = (msg) => {
    document.querySelectorAll(".toast").forEach((t) => t.remove());
    const t = Object.assign(document.createElement("div"), { className: "toast", textContent: msg });
    t.setAttribute("role", "status");
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2600);
  };

  async function api(path, body) {
    const r = await fetch(`/api/admin/${path}`, {
      method: body ? "POST" : "GET",
      headers: { authorization: `Bearer ${token}`, ...(body ? { "content-type": "application/json" } : {}) },
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await r.json().catch(() => ({ error: "Respuesta inválida del servidor." }));
    if (r.status === 401) { logout(data.error); throw new Error(data.error); }
    if (!r.ok) { toast(data.error || "Algo falló."); throw new Error(data.error); }
    return data;
  }

  // ---------------------------------------------------------------- datos públicos del sitio
  let site = null; // { entries, bySlug, updated_at }
  async function loadSite() {
    if (site) return site;
    const d = await fetch(`/data.json?t=${Date.now()}`).then((r) => r.json());
    site = { ...d, bySlug: Object.fromEntries(d.entries.map((e) => [e.slug, e])) };
    return site;
  }
  const title = (slug) => site?.bySlug[slug]?.titulo || slug;
  const link = (slug) => `<a href="/d/${esc(slug)}/" target="_blank" rel="noopener">${esc(title(slug))}</a>`;

  // ---------------------------------------------------------------- pestañas
  let current = "resumen";
  const loaded = {};
  function show(tab) {
    current = tab;
    document.querySelectorAll("#tabs button").forEach((b) => b.classList.toggle("on", b.dataset.tab === tab));
    document.querySelectorAll("[data-panel]").forEach((p) => (p.hidden = p.dataset.panel !== tab));
    if (!loaded[tab]) { loaded[tab] = true; LOADERS[tab](); }
  }
  $("#tabs").addEventListener("click", (ev) => { const b = ev.target.closest("button"); if (b) show(b.dataset.tab); });

  // ---------------------------------------------------------------- resumen
  let overview = null;
  async function loadResumen() {
    const [o] = await Promise.all([api("overview"), loadSite()]);
    overview = o;
    const t = o.totals;
    $("#n-com").textContent = t.comments_24h || "";
    $("#n-rej").textContent = t.rejected_7d || "";
    const kpi = (label, v, sub = "", warn = false) =>
      `<div class="kpi${warn ? " warn" : ""}"><span>${label}</span><b>${num(v)}</b><small>${sub}</small></div>`;
    $("#kpis").innerHTML = [
      kpi("Online ahora", t.online, "últimos 2 minutos"),
      kpi("Comentarios", t.comments_24h, `en 24 h · ${num(t.comments_7d)} en 7 días · ${num(t.comments)} en total`),
      kpi("Rechazados", t.rejected_7d, `en 7 días · ${num(t.rejected_24h)} en 24 h`, t.rejected_24h > 0),
      kpi("Votos", t.votes_24h, `en 24 h · ${num(t.votes_7d)} en 7 días · ${num(t.votes)} en total`),
      kpi("«Me funcionó»", t.confirms_7d, `en 7 días · ${num(t.confirms)} en total`),
      kpi("Personas activas", t.people_7d, "votaron o comentaron en 7 días"),
      kpi("Bloqueados", t.bans, "no pueden comentar"),
    ].join("");

    // Barras de 14 días (los días sin actividad también se muestran).
    const byDay = Object.fromEntries(o.perDay.map((d) => [d.day, d]));
    const days = [...Array(14)].map((_, i) => new Date(Date.now() - (13 - i) * 864e5).toISOString().slice(0, 10));
    const max = Math.max(1, ...days.map((d) => (byDay[d]?.comments || 0) + (byDay[d]?.votes || 0)));
    $("#bars").innerHTML = days.map((d) => {
      const x = byDay[d] || {};
      return `<div title="${d}: ${x.comments || 0} comentarios, ${x.votes || 0} votos, ${x.rejected || 0} rechazados">
        <i style="height:${(100 * (x.comments || 0)) / max}%"></i><i class="v" style="height:${(100 * (x.votes || 0)) / max}%"></i>
        <small>${d.slice(8)}/${d.slice(5, 7)}</small></div>`;
    }).join("");

    const row = (r, extra) => `<li>${link(r.slug)}<span>${extra}</span></li>`;
    $("#top").innerHTML = o.top.length
      ? o.top.map((r) => row(r, `👍 ${r.likes} · 👎 ${r.dislikes} · ✔ ${r.confirms} · 💬 ${r.comments}`)).join("")
      : `<li class="empty">Sin actividad esta semana.</li>`;
    $("#disliked").innerHTML = o.disliked.length
      ? o.disliked.map((r) => row(r, `👍 ${r.likes} · 👎 ${r.dislikes}`)).join("")
      : `<li class="empty">Ninguno. 👌</li>`;

    const E = site.entries;
    const n = (f) => E.filter(f).length;
    const up = site.updated_at ? when(Date.parse(site.updated_at)) : "—";
    $("#site").innerHTML = [
      ["Descubrimientos publicados", num(E.length)],
      ["Confirmados / sin confirmar", `${n((e) => e.confianza === "alta")} / ${n((e) => e.confianza !== "alta")}`],
      ["Traducidos al portugués", `${n((e) => e.pt?.titulo)} de ${E.length}`],
      ["Traducidos al inglés", `${n((e) => e.en?.titulo)} de ${E.length}`],
      ["Última actualización de datos", up],
    ].map(([a, b]) => `<li><span style="color:var(--ink)">${a}</span><span>${b}</span></li>`).join("");
    loadRuns();
  }

  // Corridas del bot en GitHub Actions (el repo es público, no hace falta clave).
  async function loadRuns() {
    try {
      const d = await fetch(`https://api.github.com/repos/${REPO}/actions/runs?per_page=6`).then((r) => r.json());
      const label = { success: ["ok", "Bien"], failure: ["no", "Falló"], cancelled: ["", "Cancelada"] };
      $("#runs").innerHTML = (d.workflow_runs || []).map((r) => {
        const [cls, txt] = r.status !== "completed" ? ["", "Corriendo…"] : label[r.conclusion] || ["", r.conclusion];
        return `<li><a href="${esc(r.html_url)}" target="_blank" rel="noopener">${esc(r.name)}</a>
          <span>${when(Date.parse(r.created_at))} <span class="pill ${cls}">${txt}</span></span></li>`;
      }).join("") || `<li class="empty">Sin datos.</li>`;
    } catch {
      $("#runs").innerHTML = `<li class="empty">No se pudo consultar GitHub.</li>`;
    }
  }

  // ---------------------------------------------------------------- comentarios
  const cState = { before: 0, q: "", slug: "", voter: "", label: "" };
  async function loadComments(append = false) {
    await loadSite();
    if (!append) cState.before = 0;
    const p = new URLSearchParams();
    if (cState.before) p.set("before", cState.before);
    for (const k of ["q", "slug", "voter"]) if (cState[k]) p.set(k, cState[k]);
    const d = await api(`comments?${p}`);
    const html = d.comments.map((c) => `<li class="it" data-id="${c.id}">
      <div class="it-h"><b>${esc(c.name)}</b>${c.banned ? '<span class="tag-b">Bloqueado</span>' : ""}
        <span>${when(c.created)}</span><span>en ${link(c.slug)}</span>
        <button class="btn-s" type="button" data-f="voter" data-v="${esc(c.voter)}" data-l="${esc(c.name)}">${c.by_voter} ${c.by_voter == 1 ? "comentario" : "comentarios"} de esta persona</button>
        <button class="btn-s" type="button" data-f="slug" data-v="${esc(c.slug)}" data-l="${esc(title(c.slug))}">Todos los de esta guía</button></div>
      <p>${esc(c.body)}</p>
      <div class="acts"><button type="button" class="danger" data-a="delete">Borrar</button>
        ${c.by_voter > 1 ? `<button type="button" class="danger" data-a="delete_author">Borrar sus ${c.by_voter} comentarios</button>` : ""}
        ${c.banned ? "" : '<button type="button" class="danger" data-a="ban">Bloquear a esta persona</button>'}</div></li>`).join("");
    if (append) $("#c-list").insertAdjacentHTML("beforeend", html);
    else $("#c-list").innerHTML = html || `<li class="empty">No hay comentarios${cState.q || cState.slug || cState.voter ? " con ese filtro" : " todavía"}.</li>`;
    cState.before = d.comments.length ? d.comments[d.comments.length - 1].created : cState.before;
    $("#c-more").hidden = !d.more;
  }
  let qTimer;
  $("#c-q").addEventListener("input", (ev) => {
    clearTimeout(qTimer);
    qTimer = setTimeout(() => { cState.q = ev.target.value.trim(); loadComments(); }, 300);
  });
  $("#c-more").addEventListener("click", () => loadComments(true));
  $("#c-filter button").addEventListener("click", () => {
    cState.slug = cState.voter = ""; $("#c-filter").hidden = true; loadComments();
  });
  $("#c-list").addEventListener("click", async (ev) => {
    const f = ev.target.closest("[data-f]");
    if (f) {
      cState.slug = cState.voter = "";
      cState[f.dataset.f] = f.dataset.v;
      $("#c-filter span").textContent = f.dataset.f === "voter" ? `Persona: ${f.dataset.l}` : `Guía: ${f.dataset.l}`;
      $("#c-filter").hidden = false;
      return loadComments();
    }
    const a = ev.target.closest("[data-a]"); if (!a) return;
    const li = a.closest("[data-id]"), id = +li.dataset.id;
    if (a.dataset.a === "delete") {
      if (!confirm("¿Borrar este comentario? No se puede deshacer.")) return;
      await api("comments", { action: "delete", id }); drop(li, "No quedan comentarios en esta lista."); toast("Comentario borrado.");
    } else if (a.dataset.a === "delete_author") {
      if (!confirm("¿Borrar todos los comentarios de esta persona? No se puede deshacer.")) return;
      const r = await api("comments", { action: "delete_author", id }); toast(`${r.deleted} comentarios borrados.`); loadComments();
    } else if (a.dataset.a === "ban") {
      const reason = prompt("¿Por qué la bloqueás? (opcional, solo lo ves vos)");
      if (reason === null) return;
      await api("bans", { action: "ban", id, reason }); toast("Persona bloqueada: ya no puede comentar."); loadComments(); loaded.bloqueados = false;
    }
  });

  // ---------------------------------------------------------------- rechazados
  let rBefore = 0;
  async function loadRejected(append = false) {
    await loadSite();
    if (!append) rBefore = 0;
    const d = await api(`rejected${rBefore ? `?before=${rBefore}` : ""}`);
    const html = d.rejected.map((c) => `<li class="it" data-id="${c.id}">
      <div class="it-h"><b>${esc(c.name)}</b>${c.banned ? '<span class="tag-b">Bloqueado</span>' : ""}<span>${when(c.created)}</span><span>en ${link(c.slug)}</span></div>
      <div class="why">Motivo: ${esc(c.reason || "no cumple las reglas")}</div>
      <p>${esc(c.body)}</p>
      <div class="acts"><button type="button" data-a="approve">Publicar igual</button><button type="button" data-a="dismiss">Descartar</button>
        ${c.banned ? "" : '<button type="button" class="danger" data-a="ban">Bloquear a esta persona</button>'}</div></li>`).join("");
    if (append) $("#r-list").insertAdjacentHTML("beforeend", html);
    else $("#r-list").innerHTML = html || `<li class="empty">No hay comentarios rechazados.</li>`;
    if (d.rejected.length) rBefore = d.rejected[d.rejected.length - 1].created;
    $("#r-more").hidden = !d.more;
  }
  $("#r-more").addEventListener("click", () => loadRejected(true));
  $("#r-list").addEventListener("click", async (ev) => {
    const a = ev.target.closest("[data-a]"); if (!a) return;
    const li = a.closest("[data-id]"), id = +li.dataset.id;
    if (a.dataset.a === "approve") {
      if (!confirm("¿Publicar este comentario en la página?")) return;
      await api("rejected", { action: "approve", id }); drop(li, "No hay comentarios rechazados."); toast("Publicado."); loaded.comentarios = false;
    } else if (a.dataset.a === "dismiss") {
      await api("rejected", { action: "dismiss", id }); drop(li, "No hay comentarios rechazados."); toast("Descartado.");
    } else if (a.dataset.a === "ban") {
      const reason = prompt("¿Por qué la bloqueás? (opcional, solo lo ves vos)");
      if (reason === null) return;
      await api("bans", { action: "ban_rejected", id, reason }); toast("Persona bloqueada."); loadRejected(); loaded.bloqueados = false;
    }
  });

  // ---------------------------------------------------------------- bloqueados
  async function loadBans() {
    const d = await api("bans");
    $("#b-list").innerHTML = d.bans.map((b) => `<li class="it" data-key="${esc(b.key)}" data-email="${esc(b.email_key || "")}">
      <div class="it-h"><b>${esc(b.name || "Sin nombre")}</b><span>bloqueado ${when(b.created)}</span><span>huella ${esc(b.key.slice(0, 10))}…</span></div>
      ${b.reason ? `<p>${esc(b.reason)}</p>` : ""}
      <div class="acts"><button type="button" data-a="unban">Desbloquear</button></div></li>`).join("")
      || `<li class="empty">No hay nadie bloqueado.</li>`;
  }
  $("#b-list").addEventListener("click", async (ev) => {
    const a = ev.target.closest("[data-a=unban]"); if (!a) return;
    const li = a.closest("[data-key]");
    if (!confirm("¿Desbloquear a esta persona? Va a poder comentar de nuevo.")) return;
    await api("bans", { action: "unban", key: li.dataset.key, email_key: li.dataset.email }); drop(li, "No hay nadie bloqueado."); toast("Desbloqueada.");
  });

  // ---------------------------------------------------------------- descubrimientos
  // Quitar: la página deja de verse al instante y el bot lo saca de los datos en su próxima corrida.
  let sortKey = "published_at", sortDir = -1;
  let removed = new Map(); // slug -> {title, reason, created}
  async function loadDiscoveries() {
    await loadSite();
    const [o, r] = await Promise.all([overview ? overview : api("overview"), api("discoveries")]);
    overview = o;
    removed = new Map(r.removed.map((x) => [x.slug, x]));
    renderDiscoveries();
  }
  function renderDiscoveries() {
    const q = $("#d-q").value.trim().toLowerCase(), f = $("#d-f").value;
    const per = overview?.perSlug || {};
    let rows = site.entries.map((e) => ({ ...e, likes: 0, dislikes: 0, confirms: 0, comments: 0, ...per[e.slug] }));
    // Los que el bot ya sacó de los datos solo aparecen en el filtro "Quitados".
    const gone = [...removed.entries()].filter(([slug]) => !site.bySlug[slug])
      .map(([slug, x]) => ({ slug, titulo: x.title || slug, likes: 0, dislikes: 0, confirms: 0, comments: 0, ...per[slug], gone: true }));
    if (f === "removed") rows = [...rows.filter((e) => removed.has(e.slug)), ...gone];
    else if (f !== "") rows = rows.filter((e) => !removed.has(e.slug));
    if (q) rows = rows.filter((e) => `${e.titulo} ${e.author || ""} ${e.zona || ""}`.toLowerCase().includes(q));
    if (f === "media" || f === "alta") rows = rows.filter((e) => (e.confianza === "alta") === (f === "alta"));
    if (f === "bad") rows = rows.filter((e) => e.dislikes > 0 && e.dislikes >= e.likes);
    if (f === "nopt") rows = rows.filter((e) => !e.pt?.titulo);
    if (f === "noen") rows = rows.filter((e) => !e.en?.titulo);
    rows.sort((a, b) => {
      const x = a[sortKey] ?? "", y = b[sortKey] ?? "";
      return (typeof x === "number" ? x - y : String(x).localeCompare(String(y))) * sortDir;
    });
    $("#d-n").textContent = `${rows.length} de ${site.entries.length}${removed.size ? ` · ${removed.size} quitados` : ""}`;
    $("#d-body").innerHTML = rows.map((e) => {
      const off = removed.get(e.slug);
      const state = off
        ? `<span class="pill no">${e.gone ? "Quitado" : "Quitado · el bot lo borra en su próxima corrida"}</span>${off.reason ? `<br><small class="note">${esc(off.reason)}</small>` : ""}`
        : `<span class="pill ${e.confianza === "alta" ? "ok" : ""}">${e.confianza === "alta" ? "Confirmado" : "Sin confirmar"}</span>
           ${e.pt?.titulo ? '<span class="pill">PT</span>' : ""}${e.en?.titulo ? '<span class="pill">EN</span>' : ""}`;
      return `<tr data-slug="${esc(e.slug)}"${off ? ' class="is-off"' : ""}>
      <td>${e.gone ? esc(e.titulo) : `<a href="/d/${esc(e.slug)}/" target="_blank" rel="noopener">${esc(e.titulo)}</a>`}<br>
        <small class="note">${esc(e.author || "")}${e.url ? ` · <a href="${esc(e.url)}" target="_blank" rel="noopener">video</a>` : ""}</small></td>
      <td class="n">${e.published_at ? new Date(e.published_at).toLocaleDateString("es-AR") : "—"}</td>
      <td class="n">${e.likes}</td><td class="n">${e.dislikes}</td><td class="n">${e.confirms}</td><td class="n">${e.comments}</td>
      <td>${state}</td>
      <td class="acts">${off ? '<button type="button" data-a="restore">Restaurar</button>' : '<button type="button" class="danger" data-a="remove">Quitar</button>'}</td></tr>`;
    }).join("") || `<tr><td colspan="8" class="empty">Nada con ese filtro.</td></tr>`;
  }
  $("#d-q").addEventListener("input", renderDiscoveries);
  $("#d-f").addEventListener("change", renderDiscoveries);
  document.querySelector(".dt thead").addEventListener("click", (ev) => {
    const th = ev.target.closest("th[data-k]"); if (!th) return;
    sortDir = sortKey === th.dataset.k ? -sortDir : -1; sortKey = th.dataset.k; renderDiscoveries();
  });
  $("#d-body").addEventListener("click", async (ev) => {
    const a = ev.target.closest("[data-a]"); if (!a) return;
    const slug = a.closest("[data-slug]").dataset.slug;
    if (a.dataset.a === "remove") {
      const reason = prompt(`¿Quitar «${title(slug)}» del sitio?\n\nLa página deja de verse ahora y desaparece de la portada, el mapa y las listas en la próxima corrida del bot. Podés restaurarlo cuando quieras.\n\nMotivo (opcional, solo lo ves vos):`);
      if (reason === null) return;
      await api("discoveries", { action: "remove", slug, title: title(slug), reason });
      removed.set(slug, { title: title(slug), reason, created: Date.now() });
      toast("Quitado. Su página ya no se ve.");
    } else {
      await api("discoveries", { action: "restore", slug });
      removed.delete(slug);
      toast(site.bySlug[slug] ? "Restaurado." : "Restaurado: vuelve a publicarse en la próxima corrida del bot.");
    }
    renderDiscoveries();
  });

  const LOADERS = { resumen: loadResumen, comentarios: () => loadComments(), rechazados: () => loadRejected(), bloqueados: loadBans, descubrimientos: loadDiscoveries };

  // ---------------------------------------------------------------- entrar y salir
  function logout(msg = "") {
    token = "";
    try { localStorage.removeItem(KEY); } catch {}
    $("#app").hidden = true; $("#login").hidden = false;
    $("#login-err").textContent = msg && msg !== "Contraseña incorrecta." ? msg : msg ? "Contraseña incorrecta." : "";
    $("#pw").focus();
  }
  async function start() {
    $("#login").hidden = true; $("#app").hidden = false;
    Object.keys(loaded).forEach((k) => (loaded[k] = false));
    overview = null; site = null;
    try { await LOADERS[current](); loaded[current] = true; } catch {}
  }
  $("#login").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    token = $("#pw").value.trim();
    try {
      await api("overview");
      try { localStorage.setItem(KEY, token); } catch {}
      $("#pw").value = "";
      start();
    } catch (e) { $("#login-err").textContent = e.message || "No se pudo entrar."; }
  });
  $("#logout").addEventListener("click", () => logout());
  $("#refresh").addEventListener("click", () => { start(); toast("Actualizado."); });

  if (token) start(); else logout();
})();
