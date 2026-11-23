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
