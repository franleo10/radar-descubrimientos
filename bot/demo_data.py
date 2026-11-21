"""Datos INVENTADOS para probar la web sin claves. No son descubrimientos reales."""

CANDIDATES = [
    {"id": "demo:1", "source": "youtube", "url": "#", "video_id": "", "author": "Canal de ejemplo",
     "published_at": "2026-11-21T14:00:00Z", "title_original": "EXAMPLE secret room under the pier!!",
     "text": "", "popularity": 184000, "thumbnail": ""},
    {"id": "demo:2", "source": "reddit", "url": "#", "video_id": "", "author": "u/ejemplo · r/GTA6",
     "published_at": "2026-11-21T11:30:00Z", "title_original": "Found a rare car spawn near the airport (example)",
     "text": "", "popularity": 3400, "thumbnail": ""},
    {"id": "demo:3", "source": "youtube", "url": "#", "video_id": "", "author": "Otro canal de ejemplo",
     "published_at": "2026-11-21T09:10:00Z", "title_original": "Easy money early game (example)",
     "text": "", "popularity": 92000, "thumbnail": ""},
    {"id": "demo:4", "source": "reddit", "url": "#", "video_id": "", "author": "u/prueba · r/GTAVI",
     "published_at": "2026-11-20T22:45:00Z", "title_original": "Hidden mural easter egg (example)",
     "text": "", "popularity": 1250, "thumbnail": ""},
    {"id": "demo:5", "source": "youtube", "url": "#", "video_id": "", "author": "Canal de ejemplo",
     "published_at": "2026-11-20T18:00:00Z", "title_original": "Is GTA 6 worth it? (example)",
     "text": "", "popularity": 500000, "thumbnail": ""},
]

_base = {"zona": "", "como_conseguirlo": "", "spoiler": False, "confianza": "alta"}
CLASSIFICATIONS = {
    "demo:1": {**_base, "id": "demo:1", "relevante": True, "categoria": "ubicacion_secreta",
               "titulo": "[Ejemplo] Sala oculta debajo del muelle",
               "resumen": "Texto de ejemplo: así se va a ver un lugar secreto resumido por el bot.",
               "zona": "Zona de ejemplo", "como_conseguirlo": "Paso 1 de ejemplo. Paso 2 de ejemplo."},
    "demo:2": {**_base, "id": "demo:2", "relevante": True, "categoria": "vehiculo",
               "titulo": "[Ejemplo] Auto raro cerca del aeropuerto",
               "resumen": "Texto de ejemplo para un vehículo poco común.", "confianza": "media"},
    "demo:3": {**_base, "id": "demo:3", "relevante": True, "categoria": "dinero",
               "titulo": "[Ejemplo] Plata fácil al principio del juego",
               "resumen": "Texto de ejemplo para una guía de dinero.",
               "como_conseguirlo": "Pasos de ejemplo."},
    "demo:4": {**_base, "id": "demo:4", "relevante": True, "categoria": "easter_egg",
               "titulo": "[Ejemplo] Mural escondido con referencia",
               "resumen": "Texto de ejemplo para un easter egg.", "spoiler": True},
    # Este lo descarta el filtro: es opinión, no un descubrimiento.
    "demo:5": {**_base, "id": "demo:5", "relevante": False, "categoria": "otro",
               "titulo": "Opinión sobre el juego", "resumen": "No es un descubrimiento."},
}
