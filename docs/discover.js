// Listado de descubrimientos: búsqueda, filtro por categoría y "ver más".
// La página ya trae las primeras tarjetas en el HTML; esto toma el control al cargar data.json.
(() => {
  const CATS = {
    easter_egg: ["Easter eggs", "easter-eggs"], ubicacion_secreta: ["Lugares secretos", "lugares-secretos"],
    coleccionable: ["Coleccionables", "coleccionables"], vehiculo: ["Vehículos", "vehiculos"],
    arma: ["Armas", "armas"], dinero: ["Dinero", "dinero"], mision: ["Misiones", "misiones"],
    mecanica_truco: ["Mecánicas y tips", "mecanicas-y-tips"], otro: ["Otros", "otros"],
  };
  const PAGE = 24;
  const grid = document.getElementById("grid");
  const more = document.getElementById("more");
  const meta = document.getElementById("meta");
  const input = document.getElementById("q");
  const chips = document.getElementById("chips");
  const params = new URLSearchParams(location.search);
  let all = [], cat = params.get("cat") || "todos", q = params.get("q") || "", shown = PAGE;
  const colors = {};
  chips.querySelectorAll(".chip").forEach(b => { colors[b.dataset.cat] = b.style.getPropertyValue("--c"); });

  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const thumb = e => e.thumbnail || (e.video_id ? `https://i.ytimg.com/vi/${encodeURIComponent(e.video_id)}/hqdefault.jpg` : "");
  const date = iso => iso ? `${iso.slice(8, 10)}/${iso.slice(5, 7)}/${iso.slice(0, 4)}` : "";
  const cat0 = e => CATS[e.categoria] ? e.categoria : "otro";

  function card(e) {
    const k = cat0(e), href = `../d/${esc(e.slug)}/`, t = thumb(e), place = e.macro || e.region;
    return `<article class="card${e.spoiler ? " is-spoiler" : ""}"><a class="thumb" href="${href}" tabindex="-1" aria-hidden="true">${t ? `<img loading="lazy" src="${esc(t)}" alt="">` : ""}</a>
      <div class="card-body"><div class="meta"><a class="m-cat" style="--c:${colors[k] || ""}" href="../c/${CATS[k][1]}/">${CATS[k][0]}</a>${place ? `<span>${esc(place)}</span>` : ""}</div>
      <h3><a href="${href}">${esc(e.titulo)}</a></h3><p>${esc(e.resumen)}</p>
      <div class="card-foot"><span>${esc(e.author)}</span><time datetime="${esc(e.published_at)}" data-ago>${date(e.published_at)}</time>${e.confianza === "media" ? '<span class="flag">Sin confirmar</span>' : ""}</div></div></article>`;
  }

  function render() {
    const needle = q.trim().toLowerCase();
    const list = all.filter(e => (cat === "todos" || cat0(e) === cat) &&
      (!needle || [e.titulo, e.resumen, e.zona, e.region, e.macro, e.como_conseguirlo, e.title_original].join(" ").toLowerCase().includes(needle)));
    grid.innerHTML = list.length ? list.slice(0, shown).map(card).join("")
      : `<p class="empty">No encontramos nada con ese filtro todavía. Revisamos videos nuevos varias veces por día.</p>`;
    more.hidden = list.length <= shown;
    meta.textContent = needle || cat !== "todos" ? `${list.length} resultado${list.length === 1 ? "" : "s"}` : `${list.length} descubrimientos`;
    chips.querySelectorAll(".chip").forEach(b => b.setAttribute("aria-pressed", b.dataset.cat === cat));
    window.wmAgo && window.wmAgo(grid);
    const u = new URL(location.href);
    q ? u.searchParams.set("q", q) : u.searchParams.delete("q");
    cat !== "todos" ? u.searchParams.set("cat", cat) : u.searchParams.delete("cat");
    history.replaceState(null, "", u);
  }

  input.value = q;
  chips.addEventListener("click", ev => {
    const b = ev.target.closest(".chip"); if (!b) return;
    cat = b.dataset.cat; shown = PAGE; render();
  });
  input.addEventListener("input", () => { q = input.value; shown = PAGE; render(); });
  more.addEventListener("click", () => { shown += PAGE; render(); });

  fetch("../data.json", { cache: "no-store" }).then(r => r.json()).then(d => {
    all = (d.entries || []).slice().sort((a, b) => (b.published_at || "").localeCompare(a.published_at || ""));
    render();
  }).catch(() => {});
})();
