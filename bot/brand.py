"""Piezas de marca compartidas entre el inicio y las páginas generadas."""


def logo_svg(gid: str = "lg") -> str:
    """Isotipo: pin de mapa con un destello (el 'descubrimiento')."""
    return (
        f'<svg viewBox="0 0 30 38" aria-hidden="true"><defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="#ff3d8b"/><stop offset="1" stop-color="#ffb547"/></linearGradient></defs>'
        f'<path d="M15 1C7.3 1 1 7.1 1 14.7 1 24.9 15 37 15 37s14-12.1 14-22.3C29 7.1 22.7 1 15 1z" fill="url(#{gid})"/>'
        f'<circle cx="15" cy="14.5" r="7.2" fill="#0b0912"/>'
        f'<path d="M15 9.2l1.4 3.9 3.9 1.4-3.9 1.4-1.4 3.9-1.4-3.9-3.9-1.4 3.9-1.4z" fill="#fff"/></svg>'
    )


def logo(href: str, gid: str = "lg") -> str:
    return (f'<a class="logo" href="{href}" aria-label="WastedMap, inicio">{logo_svg(gid)}'
            f'<span class="wordmark"><b>Wasted</b><i>Map</i></span></a>')


TELEGRAM_URL = "https://t.me/wastedmap"

# Avión de papel (dibujo propio, genérico).
PLANE = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M21.4 3.6 2.9 10.7c-1.2.5-1.2 '
         '1.3-.2 1.6l4.7 1.5 1.8 5.6c.2.6.4.8.9.8.4 0 .6-.2.9-.5l2.3-2.2 4.7 3.5c.9.5 1.5.2 1.7-.8l3.1-14.6c.3-1.3-.5-1.9-1.4-1.5z'
         'M9.3 13.9l8.6-5.4c.4-.3.8-.1.5.2l-7.1 6.4-.3 3.2-1.7-4.4z"/></svg>')


def tg_link(cls: str = "tg", text: str = "Telegram") -> str:
    return (f'<a class="{cls}" href="{TELEGRAM_URL}" target="_blank" rel="noopener" '
            f'aria-label="Canal de Telegram de WastedMap">{PLANE}<span>{text}</span></a>')


def tg_cta(title: str = "¿Te sirvió? Enterate primero de cada secreto nuevo") -> str:
    return (f'<aside class="cta-tg">{PLANE}<div><b>{title}</b>'
            f'<span>Publicamos los hallazgos confirmados apenas aparecen, sin spoilers.</span></div>'
            f'<a class="btn tgbtn" href="{TELEGRAM_URL}" target="_blank" rel="noopener">Unirme al canal</a></aside>')
