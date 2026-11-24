"""Guías fijas de GTA 6: trucos, lista del 100 %, trofeos, cosas que se pierden y cómo ganar plata.

Los datos están cruzados entre varias guías publicadas (ver FUENTES) y redactados con
palabras propias. Cuando las fuentes no coinciden, se dice. Cuando solo lo dice una, también.
Revisado el 24/11/2026: si algo cambia, se corrige acá y el bot regenera las páginas.
"""
from __future__ import annotations

from html import escape

from . import config

REVISADO = "24 de noviembre de 2026"

FUENTES = {
    "infobae": ("Infobae", "https://www.infobae.com/tecno/2026/11/19/todos-los-trucos-de-gta-6-codigos-para-conseguir-dinero-armas-vehiculos-y-municion-infinita/"),
    "levelup": ("LevelUp", "https://www.levelup.com/noticias/lista-completa-con-todos-los-cheats-oficiales-de-gta-6-como-desbloquear-e-introducir-los-trucos-para-conseguir-municion-infinita-dinero-y-mucho-mas/"),
    "vidaextra": ("VidaExtra", "https://www.vidaextra.com/guias-y-trucos/trucos-gta-6-para-ps5-xbox-series"),
    "powerpyx": ("PowerPyx", "https://www.powerpyx.com/gta-6-grand-theft-auto-vi/"),
    "keengamer": ("KeenGamer", "https://www.keengamer.com/articles/guides/gta-6-trophy-guide-platinum-roadmap-all-55-trophies/"),
    "bloxodes": ("Bloxodes", "https://bloxodes.com/articles/gta-6-missable-trophies-and-missions"),
    "vchq": ("The Vice City HQ", "https://thevicecityhq.com/collectibles/gta-6-collectibles-and-100-percent-checklist"),
    "gc": ("Game Checklists", "https://game-checklists.com/gta6/"),
    "mpg": ("Mission Passed Guides", "https://missionpassedguides.com/map/gta-6-collectibles/"),
    "technerdiness": ("Technerdiness", "https://www.technerdiness.com/gta/gta-6-make-money-fast/"),
    "egamers": ("eGamers", "https://egamers.io/how-to-get-rich-fast-in-gta-6-every-money-method-ranked-by-payout/"),
    "fandomwire": ("FandomWire", "https://fandomwire.com/best-ways-to-make-money-quickly-in-gta-6-ranked/"),
}

GUIAS = [
    ("trucos", "Trucos de GTA 6", "Los 61 trucos, cómo se activan y qué hay que hacer para desbloquear cada uno."),
    ("100-por-ciento", "Lista del 100 %", "Todo lo que pide el 100 %, con contadores para llevar tu progreso."),
    ("trofeos", "Trofeos de GTA 6", "Los 55 trofeos en español, cuáles son de historia y cuáles hay que buscar."),
    ("no-te-lo-pierdas", "Lo que se pierde", "Cosas que desaparecen si avanzás la historia, capítulo por capítulo."),
    ("ganar-dinero", "Cómo ganar plata rápido", "Las formas de hacer plata ordenadas por cuánto pagan y desde cuándo."),
]

# --------------------------------------------------------------------------- trucos
# code: secuencia con U/D/L/R (arriba/abajo/izquierda/derecha) o None si ninguna guía la confirma.
TRUCOS = [
    ("Personaje", [
        ("250.000 dólares al instante", "Terminar la historia", "URDLULDR", "En las tres guías, con el mismo código."),
        ("Más atención policial en todo el mapa", "Perder 3 estrellas de búsqueda 25 veces", "LDRDUDU", ""),
        ("Subir el nivel de búsqueda", "Perder 3 estrellas de búsqueda 50 veces", None, ""),
        ("Concentración infinita", "Terminar la historia", "DUUDUDUDUR", ""),
        ("Blindaje (chaleco)", "Completar 100 entrenamientos", "DULUUUUUDD", ""),
        ("Borracho (vos y tu pareja)", "Gastar 2.500 dólares en alcohol", None, ""),
        ("Sin daño por caídas", "Sobrevivir 20 veces a una caída de más de 12 metros", None, ""),
        ("Paracaídas", "Hacer 50 saltos en paracaídas o uno desde 92 metros o más", None, ""),
        ("Reparar el vehículo", "Ganar 10 carreras en Gellhorn Raceway, Thrillbilly Mud Club o Boone Speedway", None, ""),
        ("Nitro infinito", "Hacer 50 saltos con vehículo", None, "Dos guías dicen que también da combustible infinito; otra, que solo nitro."),
    ]),
    ("Armas y combate", [
        ("Recargar toda la munición", "25 medallas de bronce en las galerías de tiro", "DURDLLUUDL", ""),
        ("Munición infinita", "25 medallas de plata en las galerías de tiro", "DURDLLUDDD", "En las tres guías, con el mismo código."),
        ("Sin recarga", "25 medallas de oro en las galerías de tiro", "DURDLLUDDU", ""),
        ("Fuerza de ataque (los golpes y balas empujan más)", "Terminar la historia", "DULLRDDUD", ""),
        ("Pelotas explosivas", "Eliminar 20 enemigos con explosivos", "DULLRDDUR", ""),
        ("Fuerza vehicular (los choques empujan más)", "Eliminar 25 personas con un vehículo", "DULLRDLUD", ""),
        ("Todas las armas explosivas", "Lanzar 100 granadas", None, ""),
        ("Munición incendiaria", "Quemar a 100 enemigos", None, ""),
        ("Botellas explosivas", "Lanzar 100 molotov", None, ""),
        ("Escopeta explosiva", "Alcanzar a 100 enemigos con daño explosivo", None, "Solo aparece en una de las guías."),
        ("Lanzacohetes Hauners H-AT", "Destruir 100 vehículos", None, ""),
    ]),
    ("Clima y hora", [
        ("Cambiar el clima", "Terminar la historia", "DRUDRUR", "Una guía dice que se desbloquea al descubrir todo el mapa."),
        ("Adelantar la hora", "Juntar 10 relojes coleccionables", None, ""),
        ("Detener la hora", "Juntar 20 relojes coleccionables", None, ""),
    ]),
    ("Vehículos", [
        ("Maibatsu Boomazoom", "5 desafíos de compras", "LURDLLUL", ""),
        ("Camión de bomberos MTL Pumper", "Descubrirlo (aparece en Progreso)", "LURDLRRU", ""),
        ("Topadora HVY Bulldozer", "Descubrirla (aparece en Progreso)", "LURDLRRD", ""),
        ("Ambulancia Interstate", "Descubrirla (aparece en Progreso)", None, ""),
        ("Lancha de aire Airboat 09", "5 desafíos de supervivencia", None, ""),
        ("Bravado Banshee", "Todos los desafíos de combate", None, ""),
        ("Bicicleta Tuff BMX", "5 desafíos de estado físico", None, ""),
        ("Nagasaki Carbon RS", "Todos los desafíos de exploración", None, ""),
        ("Vapid Dominator '65", "Todos los desafíos de estado físico", None, ""),
        ("Progen Emerus", "Todos los desafíos de vehículos", None, ""),
        ("Flamenco inflable", "Destruir 50 flamencos", None, ""),
        ("Taxi Vapid Stanier G2", "5 desafíos deportivos", None, ""),
        ("Avión Hauners P-996 Lazer", "Todos los desafíos", None, ""),
        ("Lapwing Mallard", "5 desafíos de vehículos", None, ""),
        ("Carrito de golf Brimstone Golfer", "Todos los desafíos deportivos", None, ""),
        ("Tanque Hauners Rhino", "Todos los desafíos de supervivencia", None, ""),
        ("Moto Maibatsu Sanchez", "5 desafíos criminales", None, ""),
        ("Helicóptero Nagasaki Sea Sparrow", "5 desafíos de exploración", None, ""),
        ("Lancha Speeder 700 GT", "5 desafíos de combate", None, ""),
        ("Truffade Thrax", "Todos los desafíos de compras", None, ""),
        ("Moto Western Zombie Bobber", "Todos los desafíos criminales", None, ""),
    ]),
    ("Filtros de imagen", [
        ("Cataclysm", "Descubrir el Vamos de Martha (aparece en Progreso)", "DDURRULLRR", ""),
        ("Dollhouse", "Pasar 8 horas con tu pareja", "DDURRULLDR", ""),
        ("Faded Glory (TV de tubo a color)", "Robar 50 negocios con tu pareja", "DDURRULLLR", ""),
        ("Golden Hour", "Pasar 4 horas de la mano con tu pareja", None, ""),
        ("Powdered Sugar", "Escanear toda la basura espacial con WAiNK", None, ""),
        ("Pinhole", "Hacer 25 operaciones de bandas con tu pareja", None, ""),
        ("Neon Jungle", "Descubrir 16 vehículos Girlypop", None, ""),
        ("Yesteryear (blanco y negro)", "Descubrir Ridgeway", None, ""),
        ("Videotape", "Hacer 50 actividades con tu pareja", None, ""),
        ("Dark Mirror", "Ganar 500.000 dólares vendiendo vehículos", None, ""),
        ("Migraine", "Sobrevivir 6 minutos con 6 estrellas", None, ""),
        ("Bubblegum", "Juntar las 24 cartas de los Vice City Flamingos", None, ""),
        ("Fast Forward", "Hacer 50 meditaciones", None, ""),
        ("Fisheye", "Pescar 100 peces", None, ""),
        ("Pixel Art", "Ganar 250.000 dólares vendiendo coleccionables", None, ""),
        ("Hellscape", "Robar 100 patrulleros", None, ""),
    ]),
]

ARROW = {"U": "↑", "D": "↓", "L": "←", "R": "→"}
ARROW_NAME = {"U": "arriba", "D": "abajo", "L": "izquierda", "R": "derecha"}

# --------------------------------------------------------------------------- 100 %
# (clave, nombre, necesitás, existen, nota, fuentes que coinciden, capítulo desde el que se puede)
CIEN = [
    ("Historia y misiones", [
        ("mis", "Misiones de la historia", 91, 91, "Terminar la historia completa.", "gc", 1),
        ("opt", "Tareas opcionales", 100, None, "Misiones secundarias y encargos de contactos.", "gc, keengamer", 1),
    ]),
    ("Robos", [
        ("gang", "Operaciones de bandas", 39, 39, "Escondites de las bandas; se encuentran escuchando a la gente o siguiendo autos sospechosos.", "gc, keengamer, fandomwire", 1),
        ("bank", "Trabajos de banco", 22, 22, "14 bancos chicos (desde «Credit Check», capítulo 3) y 8 bóvedas grandes (desde «That's Where the Money Is», capítulo 4).", "gc, keengamer", 3),
        ("payday", "Locales de préstamos (Payday Loans)", 7, 7, "Desde «Credit Check», capítulo 3.", "gc, keengamer", 3),
        ("smash", "Smash 'n' Grab", 34, 35, "Robá también la caja fuerte del fondo o el local puede no contar.", "gc", 2),
        ("stick", "Asaltos a negocios", 50, None, "Game Checklists dice 50 de 91, pero su propia lista muestra más locales.", "gc", 1),
    ]),
    ("Coleccionables y exploración", [
        ("cards", "Colecciones de cartas completas", 15, 18, "480 cartas en 18 colecciones. Las repetidas no suman; las variantes de color sí.", "vchq, gc, mpg", 1),
        ("waink", "Escaneos WAiNK", 100, None, "Las guías no coinciden en cuántos hay: 100, 102 o más de 110.", "vchq, gc, mpg", 1),
        ("flam", "Flamencos de cocaína destruidos", 100, 125, "Que haya 125 lo dice una sola fuente.", "vchq, gc, mpg", 1),
        ("under", "Hallazgos bajo el agua", 33, 33, "Hacen falta todos. Las inmersiones de Kenton se pausan al final del capítulo 1 pero vuelven.", "vchq, gc, mpg", 1),
        ("mags", "Revistas, libros y cómics", 30, 34, "Tres solo están en la casa de Jason durante el capítulo 1.", "vchq, gc, mpg", 1),
        ("medit", "Meditaciones", 15, 18, "Con Jason y con Lucía en el mismo lugar cuenta doble.", "vchq, gc, mpg", 1),
        ("kenton", "Colecciones de Kenton (tesoros)", 5, 7, "Desde la misión «Island Dreams», capítulo 1.", "vchq, gc", 1),
        ("styles", "Estilos descubiertos", 70, 79, "Revistas de peinados, de tatuajes y relojes de lujo.", "vchq, gc", 1),
        ("playlists", "Listas de música únicas", 2, 2, "Se desbloquean con 5 afiches en Vice City.", "gc, mpg", 1),
    ]),
    ("Carreras, acrobacias y desafíos", [
        ("races", "Carreras distintas ganadas", 30, 40, "", "gc", 1),
        ("racech", "Desafíos de carrera con oro", 10, 13, "Seis están en el Thrillbilly Mud Club, en el norte de Kelly County.", "gc", 1),
        ("stunts", "Acrobacias", 300, 397, "Saltos, pasar bajo puentes, vuelos rasantes y saltos base: cualquier combinación.", "gc, keengamer", 1),
        ("chall", "Desafíos", 70, 80, "", "gc, keengamer", 1),
        ("decks", "Target decks", 15, 15, "", "gc, keengamer", 1),
        ("range", "Oros en las galerías de tiro", 42, 42, "Hay que comprar un pase de 5 dólares para que aparezcan en el mapa.", "gc, keengamer", 1),
        ("drone", "Contrarreloj con dron", 42, 42, "", "gc, keengamer", 1),
    ]),
    ("Actividades", [
        ("hoops", "Aros de básquet", 90, 100, "", "gc", 1),
        ("pool", "Rivales de pool", 5, 7, "El rival del Delights Cabaret desaparece con «Checking Out» hasta que reabre el club.", "gc", 1),
        ("arcade", "Videojuegos", 4, 4, "", "gc", 1),
        ("golf", "Canchas de minigolf", 2, 3, "", "gc", 1),
    ]),
    ("Escanear y estudiar", [
        ("cars", "Vehículos escaneados", 200, 277, "", "gc, keengamer", 1),
        ("animals", "Animales estudiados", 100, 255, "Con binoculares: no hace falta cazar.", "gc, keengamer", 1),
        ("weapons", "Armas", 50, 66, "Las 12 herramientas no cuentan.", "gc, keengamer", 1),
    ]),
    ("Ventas a reducidores (en dólares)", [
        ("f_bills", "Billetes marcados", 250000, None, "Hace falta el Dye Pack Jammer, que se consigue con «Credit Check».", "gc", 3),
        ("f_cars", "Vehículos", 200000, None, "", "gc", 1),
        ("f_jewel", "Joyas", 100000, None, "", "gc", 2),
        ("f_drugs", "Narcóticos", 100000, None, "Algunos reducidores cierran para siempre: vendé antes de la misión que los cierra.", "gc", 1),
    ]),
]

CARTAS = [
    ("Vice City Flamingos", 24), ("Vice City Narcos", 24), ("Vice City Manatees", 24),
    ("Vice City Club De Fútbol", 30), ("Liberty City Swingers", 24), ("Liberty City Penetrators", 24),
    ("Liberty City Wrath", 24), ("Los Santos Corkers", 24), ("Los Santos Panic", 24),
    ("Los Santos Pounders", 24), ("Backyard Wrestling", 12), ("America's Next Top Hooker", 24),
    ("Delights Dancers", 18), ("Jack of Hearts Dancers", 36), ("Nine1Nine Dancers", 36),
    ("The Legends of Ratface", 36), ("Right Wing: America's Hero", 36), ("Ed Comics Universe", 36),
]

# --------------------------------------------------------------------------- trofeos
# (nombre, grado, requisito, tipo, capítulo desde el que se ve sin spoilers, nota)
# grado: p platino, o oro, a plata (argent), b bronce. tipo: h historia, o opcional.
TROFEOS = [
    ("Vice Got a Price!", "p", "Conseguir todos los demás trofeos.", "o", 1, ""),
    ("Just Like Paradise", "b", "Terminar la primera misión.", "h", 1, ""),
    ("Paradise Lost", "b", "Terminar el capítulo 1.", "h", 1, ""),
    ("T**s Ass Drug Money", "b", "Terminar el capítulo 2.", "h", 2, ""),
    ("Vice City, Baby!", "b", "Terminar el capítulo 3.", "h", 3, ""),
    ("Top Of The World, Ma", "b", "Terminar el capítulo 4.", "h", 4, ""),
    ("You Gotta Know When to Get Off", "o", "Terminar la última misión de la historia.", "h", 5, ""),
    ("Trust", "b", "Completar la misión «Breakfast Run».", "h", 5, ""),
    ("Break the Bank", "b", "Completar la misión «The Cartel Heist».", "h", 5, ""),
    ("Family Matters", "b", "Completar la misión «Child's Play».", "h", 5, ""),
    ("DWNFALL", "b", "Completar la misión «Headliners».", "h", 5, ""),
    ("Hi-Jacked", "b", "Completar la misión «VCIA Takedown».", "h", 5, ""),
    ("Snow Storm", "b", "Completar la misión «Operation Savage Glory».", "h", 5, ""),
    ("A Long Road", "o", "Llegar al 100 % de la lista que aparece al terminar la historia.", "o", 5, "El más difícil. Nada de la lista se pierde."),
    ("Cunning Stunts", "a", "Hacer 250 acrobacias.", "o", 1, ""),
    ("Master of None", "b", "Probar una vez cada uno de los 9 tipos de actividad.", "o", 1, ""),
    ("The Shootist", "a", "Sacar oro en los 42 desafíos de las galerías de tiro.", "o", 1, ""),
    ("Top Fun", "b", "Ganar una carrera de drones en los 14 lugares.", "o", 1, ""),
    ("Earn Cash, Not Kudos", "b", "Ganar 20 carreras distintas.", "o", 1, ""),
    ("Baited My Tackle", "b", "Ganarle a Cal un desafío de pesca (te escribe después de «Feng Shui»).", "o", 1, ""),
    ("Stick Fiddler", "b", "Llegar al final de un juego de arcade.", "o", 1, ""),
    ("Road to Rehabilitation", "b", "Completar la última misión de Andy (con Lucía).", "o", 1, ""),
    ("This Was No Boat Accident", "b", "Completar la última misión de Kenton: los 7 naufragios.", "o", 1, "Kenton se pausa al terminar el capítulo 1 y vuelve después."),
    ("The Lone Rider", "b", "Completar la última misión de Billy.", "o", 1, ""),
    ("Strangers & Freaks", "a", "Completar 8 historias de desconocidos.", "o", 1, "Una guía avisa que saltearse «Race Against Yago» (capítulo 3) podría trabarlo."),
    ("Supply & Demand", "b", "Completar la última misión de Randy (lista de 16 autos).", "o", 3, ""),
    ("Spin On This!", "b", "Completar la última misión de Tyrone (solo Jason).", "o", 1, ""),
    ("Positive Mental Attitude", "b", "Meditar en los 18 lugares (Jason y Lucía en el mismo lugar cuentan como 2).", "o", 1, "Ojo: la meditación del balcón de Jason solo está en el capítulo 1. Las guías no se ponen de acuerdo en si hace falta: hacela por las dudas."),
    ("Fair Game", "b", "Cazar un animal único para Bret (solo Jason).", "o", 1, "Cuál es el animal todavía no está confirmado."),
    ("Don't Touch My Deck", "a", "Completar 3 colecciones de cartas.", "o", 1, ""),
    ("You WAiNKer!", "a", "Escanear 100 lugares con WAiNK.", "o", 1, ""),
    ("One Last Thing", "b", "Completar 50 de los 80 desafíos.", "o", 1, ""),
    ("Hot Together", "b", "Escapar de 4 estrellas con tu pareja.", "o", 1, ""),
    ("Retail Therapy", "b", "Robar 3 negocios seguidos con tu pareja sin perder el nivel de búsqueda.", "o", 1, ""),
    ("Whip It Good", "b", "Descubrir 100 vehículos.", "o", 1, ""),
    ("Gunslinger", "b", "Eliminar 5 enemigos en un solo uso de Concentración de combate.", "o", 1, ""),
    ("Catch Me If You Can", "b", "Robar un avión de pasajeros en el aeropuerto VCIA.", "o", 1, "Una guía agrega que hay que alejarse 1 km."),
    ("Challenging Tank", "b", "Robar el tanque militar Rhino y usarlo en combate.", "o", 1, ""),
    ("Sneakthief", "b", "Robar una joyería sin que te detecten.", "o", 3, ""),
    ("Maximum Withdrawal", "a", "Robar 5 bóvedas de banco y escapar.", "o", 4, ""),
    ("A Classic Blitz Play", "b", "Robar un camión blindado y escapar.", "o", 4, ""),
    ("The Goodtime State", "b", "Descubrir todo el mapa de Leonida.", "o", 1, ""),
    ("Pest Control", "b", "Robar una operación de cada una de las 9 bandas.", "o", 1, ""),
    ("In The Beginning…", "b", "Tomar un cóctel en el bar de la terraza de Ocean View.", "o", 1, "Una guía dice que es un Apple Martini; otra, que no está confirmado."),
    ("Capital Offense", "b", "Atravesar la vidriera de una concesionaria con el Banshee azul.", "o", 3, "Método sin confirmar en una de las guías."),
    ("Let's Go Bowling", "b", "Robar los 3 objetos valiosos del bowling y escapar.", "o", 2, "No se pierde: se puede volver."),
    ("Personal Best", "b", "Llevar la Fuerza al máximo con Jason y con Lucía.", "o", 2, ""),
    ("Actions Speak Louder", "b", "Hacer 500 acciones que cambien tu perfil criminal.", "o", 1, ""),
    ("Bad Luck, I Guess", "b", "Trofeo oculto. Una guía dice: robar otra vez el Payday Loans de Little Cuba con Lucía y escapar a pie.", "o", 3, "Método sin confirmar."),
    ("The Truth Is Out There", "b", "Trofeo oculto. Una guía lo relaciona con un ovni cerca del Starlet Motel que aparece al azar.", "o", 1, "Método sin confirmar."),
    ("Ten Pin", "b", "Trofeo oculto. Una guía dice: tirar a 10 peatones desde una moto en 60 segundos.", "o", 1, "Método sin confirmar."),
    ("Dime on the Dollar", "b", "Lavar 250.000 dólares en billetes marcados con un reducidor.", "o", 3, ""),
    ("Treat Yo Self", "b", "Gastar 100.000 dólares en tiendas.", "o", 1, ""),
    ("Little Boxes", "b", "Comprar los 8 garajes (unos 160.000 dólares).", "o", 2, ""),
    ("On the Spot", "b", "Registrar 10 vehículos en la app Scooter Bros.", "o", 2, ""),
]
GRADOS = {"p": "Platino", "o": "Oro", "a": "Plata", "b": "Bronce"}

# --------------------------------------------------------------------------- lo que se pierde
# (capítulo, qué, por qué importa, qué hacer, fuentes)
PERDIBLES = [
    (1, "Meditación en el balcón de Jason", "Puede hacer falta para el trofeo Positive Mental Attitude. Las guías no coinciden.",
     "Después de «Down to Earth», a la mañana hablá con Lucía en la cocina, seguila al balcón y aceptá meditar.", "keengamer, bloxodes, powerpyx"),
    (1, "Revistas y libros de la casa de Jason", "Tres títulos (Ashes of Glory, Lethal By Design y Body Copy) solo están ahí. Cuentan para el 100 % (hacen falta 30 de 34).",
     "Leelos antes de empezar «Tourist Trap».", "mpg, gc"),
    (1, "La plata que juntás en el capítulo 1", "Al terminar el capítulo solo se conserva lo que está en Family Savings.",
     "Antes de cerrar el capítulo, gastá o guardá lo que tengas.", "gc, mpg"),
    (1, "Encargos de Shirley (el ron y el scooter)", "No cuentan para trofeos ni para el 100 %.",
     "Si los querés hacer, hacelos antes de «Tourist Trap».", "bloxodes, gc"),
    (2, "Cartas 1 y 2 de la colección Maravilla, en el Starlet Motel", "Desaparecen con la misión «Checking Out». Lo dice una sola guía.",
     "Agarralas antes de «Checking Out».", "mpg"),
    (2, "Refugio del Starlet Motel y rival de pool del Delights Cabaret", "«Checking Out» los saca. El rival vuelve cuando reabre el club.",
     "No hace falta apurarse por el 100 %: alcanzan 5 de 7 rivales.", "gc"),
    (2, "Final del capítulo 2", "Pide haber terminado los demás trabajos del capítulo y tener al menos 15.000 dólares.",
     "Juntá esa plata antes.", "gc"),
    (3, "«Race Against Yago» (misión con reloj de arena)", "Si no la hacés a tiempo puede trabar las misiones de Yago y, según una guía, el trofeo Strangers & Freaks.",
     "Hacela apenas aparezca.", "gc, bloxodes"),
]

GENERALES = [
    ("No hay repetición de misiones", "Guardá en varias ranuras: hay 15 manuales y 1 automática. Una buena idea es guardar al empezar cada capítulo."),
    ("Algunos reducidores cierran para siempre", "Vendé lo que tengas antes de la misión que los cierra."),
    ("Los trucos desactivan trofeos y guardado", "Durante esa sesión no ganás trofeos ni se guarda. Guardá antes de usarlos."),
    ("El 100 % no se pierde", "Todo lo que pide la lista sigue disponible después de los créditos, en juego libre."),
    ("Los trofeos de historia no se pierden", "Se desbloquean solos al avanzar. Tampoco importa la relación entre Jason y Lucía."),
]

# --------------------------------------------------------------------------- plata
# (método, pago, desde, capítulo, riesgo 1-3, nota, fuentes)
PLATA = [
    ("Bóvedas de banco grandes", "Hasta 205.000 dólares cada una", "«That's Where the Money Is», capítulo 4", 4, 3,
     "Empiezan con 4 estrellas. Pagan en billetes marcados: hay que lavarlos con un reducidor antes de gastarlos. Son 8.", "fandomwire, egamers, technerdiness"),
    ("Autos para Randy (Wish List)", "Unos 30.000 a 35.000 dólares por auto impecable", "Mitad del capítulo 3, después de «Key Cloner»", 3, 2,
     "Son 16 o 18 autos, según la guía. Los rastreadores avanzados avisan a la policía si frenás. Los choques bajan el precio.", "fandomwire, egamers"),
    ("Entregas de Pilot Pete (en avión)", "12.000 dólares la primera, 20.000 las siguientes", "Capítulo 4", 4, 1,
     "Solo con Jason. Tienen tiempo límite y tienen que llegar todos los paquetes.", "fandomwire, egamers"),
    ("Bancos chicos", "Entre 5.000 y 45.000 dólares", "«Credit Check», capítulo 3", 3, 2,
     "Son 14. Llevate la caja y la caja fuerte, si no, no cuenta para el 100 %.", "fandomwire, egamers"),
    ("Joyerías", "Entre 10.000 y 25.000 dólares", "Trabajos de Yasmani, capítulo 3", 3, 3,
     "Cortá la alarma primero. Las joyas se venden a un reducidor.", "fandomwire, egamers, technerdiness"),
    ("Locales de préstamos (Payday Loans)", "Entre 2.000 y 25.000 dólares", "«Credit Check», capítulo 3", 3, 2,
     "Son 7. El monto depende del local.", "egamers"),
    ("Smash 'n' Grab en casas de empeño", "Entre 1.000 y 25.000 dólares", "«Coffee Break», capítulo 2", 2, 2,
     "El personal puede defenderse.", "egamers"),
    ("Operaciones de bandas", "Variable", "Desde el principio", 1, 2,
     "Son 39 escondites y se vuelven a llenar con el tiempo. Las cajas fuertes tienen el código cerca. Lo que saques va a un reducidor.", "fandomwire, egamers, technerdiness"),
    ("Robar negocios", "Unos miles de dólares", "Desde el principio", 1, 2,
     "Cortá la alarma y borrá las grabaciones de seguridad para que no den tu descripción.", "technerdiness, egamers"),
    ("Autos para Moses (garaje de Port Gellhorn)", "Unos 1.000 dólares por auto", "Capítulo 2", 2, 1,
     "No acepta autos con rastreador. Hay que esperar unos 2 minutos entre ventas y no robar cerca del garaje.", "fandomwire, egamers"),
    ("Pay 'n' Spray", "Un par de miles por auto", "Capítulo 3 según dos guías; otra dice que desde el principio", 3, 1,
     "Revisá si el auto tiene rastreador antes de robarlo (estacionado, no del tráfico).", "technerdiness, fandomwire, egamers"),
    ("Baúles de autos", "Poco: efectivo, armas o cosas para vender", "Desde el principio", 1, 1,
     "Casi sin riesgo.", "technerdiness"),
]

CONSEJOS_PLATA = [
    "Lo que llevás encima se pierde si morís o te detienen. Una guía dice que el tope en efectivo es de 20.000 dólares: depositá seguido en un cajero o en BuckMe.",
    "Cada reducidor compra un solo tipo de cosa y paga menos si está dañada.",
    "Scooter Bros. Premium cuesta unos 12.500 dólares y da tres entregas de autos gratis por día del juego: según una guía, conviene apenas puedas.",
    "Al terminar el capítulo 1 solo se conserva lo que está en Family Savings.",
]


# =========================================================================== páginas
# Las mismas páginas salen en español (/trucos/...) y en portugués (/pt/truques/...).
# Los datos en portugués están en guias_pt.py; los textos fijos de la página, en TXT.

TXT = {
    "es": dict(
        home="Inicio", guias="Guías", overline="Guía · revisada el {r}",
        src_h="De dónde sale esto",
        src_p="Cruzamos estas guías y lo escribimos con nuestras palabras. Cuando no coinciden, lo aclaramos. "
              "Revisado el {r}. Si en tu partida ves algo distinto, <a href=\"{root}contacto/\">avisanos</a>.",
        segun="Según", capq="¿Por qué capítulo vas?", cap_aria="Capítulo", cap_done="Terminé", cap_all="Ver todo",
        code_none="Código sin confirmar", unlock="Se desbloquea",
        tk_h1="Trucos de GTA 6: todos los códigos",
        tk_lead="Los {n} trucos de GTA 6, qué hace cada uno y qué hay que hacer para desbloquearlo. "
                "De {c} hay código confirmado por dos guías distintas.",
        tk_how="""<section class="g-how">
  <h2>Cómo se activan</h2>
  <ol class="g-steps">
    <li>Terminá la historia: recién ahí aparece la sección de trucos en el menú Progreso.</li>
    <li>Cumplí el requisito de cada truco. Cuando lo cumplís, el juego te muestra el código en Progreso.</li>
    <li>Sacá el teléfono (flecha arriba de la cruceta), mantené <b>L1 + R1</b> en PS5 o <b>LB + RB</b> en Xbox y marcá la secuencia.</li>
  </ol>
  <p class="g-warn"><b>Antes de usarlos:</b> mientras haya un truco activo no ganás trofeos ni logros y el juego no guarda. Guardá antes.</p>
  <p class="note">Los códigos son iguales en PS5 y Xbox. Las flechas son de la cruceta.</p>
</section>""",
        tk_search_l="Buscar un truco", tk_search_ph="Buscar: munición, Banshee, clima…", tk_empty="No hay trucos con esa búsqueda.",
        h_need="Necesitás", h_of="de", h_minus="Restar", h_plus="Sumar", h_aria="Cuántos llevás de {x}",
        h_h1="Lista del 100 % de GTA 6",
        h_lead="Todo lo que pide el 100 % y cuánto te falta. Anotá lo que llevás: se guarda en este navegador, sin registrarte.",
        h_sum="""<div class="ck-summary"><p>Vas por el <b id="h-pct">0</b>% de la lista</p><div class="ck-bar big"><i id="h-all"></i></div>
<div class="ck-actions"><span class="note">Es un promedio de cada fila. El porcentaje real lo ves en el juego, en Progreso.</span><button class="btn sm ghost" id="h-reset" type="button">Borrar mi progreso</button></div></div>
<section class="g-how"><h2>Antes de empezar</h2><ul class="g-facts">
<li>El 100 % da el trofeo de oro <b>A Long Road</b>. Las guías calculan unas 200 horas, contra 65 a 70 de la historia sola.</li>
<li>El progreso de cada cosa se ve en el juego, en <b>Mapa › Progreso › Colecciones</b>. Algunas categorías aparecen recién cuando encontrás la primera.</li>
<li>Nada de la lista se pierde: todo sigue disponible después de los créditos. Igual hay cosas cómodas de hacer antes: mirá <a href="{lost}">lo que se pierde</a>.</li>
</ul></section>""",
        cards_h="Colecciones de cartas <small>hacen falta 15 de 18</small>", cards_n="cartas",
        cards_note="Los nombres y cantidades salen de una sola guía (Mission Passed Guides), pero suman exactamente las 480 cartas que confirman las demás.",
        tr_h1="Trofeos de GTA 6: la lista completa",
        tr_lead="Los {n} trofeos de GTA 6 en español: {p} platino, {o} de oro, {a} de plata y {b} de bronce. Tildá los que ya tenés.",
        tr_how="""<section class="g-how"><h2>Lo que tenés que saber</h2><ul class="g-facts">
<li><b>Platino en una sola partida.</b> No hay niveles de dificultad ni trofeos online. Las guías lo ponen en 4 de 10 de dificultad y unas 200 horas.</li>
<li><b>No hay repetición de misiones ni partida nueva+.</b> El juego libre sigue después de la historia.</li>
<li><b>El único que podría perderse</b> es Positive Mental Attitude, por una meditación del capítulo 1. <a href="{lost}">Mirá cómo hacerla</a>.</li>
<li><b>Los trucos desactivan los trofeos</b> mientras estén activos.</li>
</ul></section>""",
        tr_story="Historia: sale solo", tr_opt="Hay que buscarlo", tr_filter="Filtrar por tipo", tr_all="Todos",
        tr_hide="Ocultar los que ya tengo", tr_count="de {n} conseguidos",
        ml_h1="GTA 6: lo que se pierde si avanzás la historia",
        ml_lead="Lo que desaparece al pasar de capítulo, ordenado para que lo hagas a tiempo. Spoilers mínimos: elegí por qué capítulo vas.",
        ml_gen="Reglas generales", chapter="Capítulo",
        mn_h1="Cómo ganar plata rápido en GTA 6",
        mn_lead="Las formas de hacer plata ordenadas de la que más paga a la que menos, con el capítulo desde el que se pueden hacer.",
        mn_from="Desde", risk={1: "Riesgo bajo", 2: "Riesgo medio", 3: "Riesgo alto"},
        mn_note="Los montos son los que reportaron las primeras guías después del lanzamiento y pueden cambiar con actualizaciones.",
        mn_tips="Para no perder lo que ganaste",
        mn_cat='También tenés la categoría <a href="{root}c/dinero/">Dinero</a>, con los métodos que va encontrando la comunidad en video.',
        hub_lead="Lo esencial para jugar y completar GTA 6, en español y revisado con varias fuentes.",
        hub_list="<b>Mi lista de secretos</b><span>Tildá los secretos de WastedMap que ya encontraste.</span>",
        home_over="Guías", home_h="Lo que más se busca de GTA 6", home_more="Ver todas →",
    ),
    "pt": dict(
        home="Início", guias="Guias", overline="Guia · revisado em {r}",
        src_h="De onde vem isto",
        src_p="Cruzamos estes guias e escrevemos com nossas palavras. Quando eles não concordam, avisamos. "
              "Revisado em {r}. Se no seu jogo aparecer algo diferente, <a href=\"{root}contacto/\">avise a gente</a>.",
        segun="Segundo", capq="Em que capítulo você está?", cap_aria="Capítulo", cap_done="Terminei", cap_all="Ver tudo",
        code_none="Código não confirmado", unlock="Desbloqueia com",
        tk_h1="Truques de GTA 6: todos os códigos",
        tk_lead="Os {n} truques de GTA 6, o que cada um faz e o que é preciso fazer para desbloqueá-lo. "
                "{c} têm o código confirmado por dois guias diferentes.",
        tk_how="""<section class="g-how">
  <h2>Como ativar</h2>
  <ol class="g-steps">
    <li>Termine a história: só então aparece a seção de truques no menu Progresso.</li>
    <li>Cumpra o requisito de cada truque. Quando você cumpre, o jogo mostra o código em Progresso.</li>
    <li>Pegue o celular (seta para cima no direcional), segure <b>L1 + R1</b> no PS5 ou <b>LB + RB</b> no Xbox e digite a sequência.</li>
  </ol>
  <p class="g-warn"><b>Antes de usar:</b> enquanto houver um truque ativo você não ganha troféus nem conquistas e o jogo não salva. Salve antes.</p>
  <p class="note">Os códigos são iguais no PS5 e no Xbox. As setas são do direcional.</p>
</section>""",
        tk_search_l="Buscar um truque", tk_search_ph="Buscar: munição, Banshee, clima…", tk_empty="Nenhum truque com essa busca.",
        h_need="Precisa de", h_of="de", h_minus="Diminuir", h_plus="Aumentar", h_aria="Quantos você tem de {x}",
        h_h1="Lista dos 100 % de GTA 6",
        h_lead="Tudo o que os 100 % pedem e quanto falta. Anote o que você já tem: fica salvo neste navegador, sem cadastro.",
        h_sum="""<div class="ck-summary"><p>Você está em <b id="h-pct">0</b>% da lista</p><div class="ck-bar big"><i id="h-all"></i></div>
<div class="ck-actions"><span class="note">É uma média de cada linha. A porcentagem real aparece no jogo, em Progresso.</span><button class="btn sm ghost" id="h-reset" type="button">Apagar meu progresso</button></div></div>
<section class="g-how"><h2>Antes de começar</h2><ul class="g-facts">
<li>Os 100 % dão o troféu de ouro <b>A Long Road</b>. Os guias calculam umas 200 horas, contra 65 a 70 só da história.</li>
<li>O progresso de cada coisa aparece no jogo, em <b>Mapa › Progresso › Coleções</b>. Algumas categorias só aparecem quando você encontra a primeira.</li>
<li>Nada da lista se perde: tudo continua disponível depois dos créditos. Mesmo assim, há coisas que convém fazer antes: veja <a href="{lost}">o que dá para perder</a>.</li>
</ul></section>""",
        cards_h="Coleções de cartas <small>precisa de 15 de 18</small>", cards_n="cartas",
        cards_note="Os nomes e quantidades vêm de um único guia (Mission Passed Guides), mas somam exatamente as 480 cartas que os outros confirmam.",
        tr_h1="Troféus de GTA 6: a lista completa",
        tr_lead="Os {n} troféus de GTA 6 em português: {p} platina, {o} de ouro, {a} de prata e {b} de bronze. Marque os que você já tem.",
        tr_how="""<section class="g-how"><h2>O que você precisa saber</h2><ul class="g-facts">
<li><b>Platina num único save.</b> Não há níveis de dificuldade nem troféus online. Os guias dão dificuldade 4 de 10 e umas 200 horas.</li>
<li><b>Não dá para repetir missões nem há novo jogo+.</b> O jogo livre continua depois da história.</li>
<li><b>O único que poderia ser perdido</b> é Positive Mental Attitude, por causa de uma meditação do capítulo 1. <a href="{lost}">Veja como fazer</a>.</li>
<li><b>Os truques desativam os troféus</b> enquanto estiverem ativos.</li>
</ul></section>""",
        tr_story="História: vem sozinho", tr_opt="É preciso buscar", tr_filter="Filtrar por tipo", tr_all="Todos",
        tr_hide="Ocultar os que já tenho", tr_count="de {n} conquistados",
        ml_h1="GTA 6: o que dá para perder se você avançar a história",
        ml_lead="O que some ao passar de capítulo, em ordem para você fazer a tempo. Spoilers mínimos: escolha em que capítulo você está.",
        ml_gen="Regras gerais", chapter="Capítulo",
        mn_h1="Como ganhar dinheiro rápido no GTA 6",
        mn_lead="As formas de fazer dinheiro ordenadas da que mais paga para a que menos, com o capítulo a partir do qual dá para fazer.",
        mn_from="A partir de", risk={1: "Risco baixo", 2: "Risco médio", 3: "Risco alto"},
        mn_note="Os valores são os que os primeiros guias publicaram depois do lançamento e podem mudar com atualizações.",
        mn_tips="Para não perder o que você ganhou",
        mn_cat='Veja também a categoria <a href="{root}pt/c/dinheiro/">Dinheiro</a>, com os métodos que a comunidade vai encontrando em vídeo.',
        hub_lead="O essencial para jogar e completar GTA 6, em português e revisado com várias fontes.",
        hub_list="<b>Minha lista de segredos</b><span>Marque os segredos do WastedMap que você já encontrou (em espanhol).</span>",
        home_over="Guias", home_h="O mais buscado de GTA 6", home_more="Ver todos →",
    ),
}


def _data(lang: str) -> dict:
    """Datos de las guías en el idioma pedido. En portugués se toman los textos de guias_pt.py
    y los números, códigos y capítulos de acá, así no hay que mantenerlos dos veces."""
    if lang == "es":
        return dict(trucos=TRUCOS, cien=CIEN, trofeos=TROFEOS, perdibles=PERDIBLES, generales=GENERALES,
                    plata=PLATA, consejos=CONSEJOS_PLATA, grados=GRADOS, arrow_name=ARROW_NAME, revisado=REVISADO,
                    guias=[(s, s, t, d) for s, t, d in GUIAS])
    from . import guias_pt as X

    def same(a, b, what):
        if len(a) != len(b):
            raise ValueError(f"guias_pt.{what} no coincide con guias.{what}")
    same(X.TRUCOS, TRUCOS, "TRUCOS"); same(X.CIEN, CIEN, "CIEN"); same(X.TROFEOS, TROFEOS, "TROFEOS")
    same(X.PERDIBLES, PERDIBLES, "PERDIBLES"); same(X.PLATA, PLATA, "PLATA")
    trucos = []
    for (g, rows), (_, es) in zip(X.TRUCOS, TRUCOS):
        same(rows, es, "TRUCOS")
        trucos.append((g, [(ef, req, e[2], nota) for (ef, req, nota), e in zip(rows, es)]))
    cien = []
    for (g, rows), (_, es) in zip(X.CIEN, CIEN):
        same(rows, es, "CIEN")
        cien.append((g, [(e[0], lab, e[2], e[3], nota, e[5], e[6]) for (lab, nota), e in zip(rows, es)]))
    return dict(
        trucos=trucos, cien=cien,
        trofeos=[(e[0], e[1], req, e[3], e[4], nota) for (req, nota), e in zip(X.TROFEOS, TROFEOS)],
        perdibles=[(e[0], q, por, hacer, e[4]) for (q, por, hacer), e in zip(X.PERDIBLES, PERDIBLES)],
        generales=X.GENERALES,
        plata=[(m, pago, desde, e[3], e[4], nota, e[6]) for (m, pago, desde, nota), e in zip(X.PLATA, PLATA)],
        consejos=X.CONSEJOS_PLATA, grados=X.GRADOS, arrow_name=X.ARROW_NAME, revisado=X.REVISADO, guias=X.GUIAS)


def _url(lang: str, root: str, es_slug: str) -> str:
    """Enlace a una guía en el mismo idioma."""
    if lang == "es":
        return f"{root}{es_slug}/"
    pt = next(s for s, e, _, _ in _data("pt")["guias"] if e == es_slug)
    return f"{root}pt/{pt}/"


def _src_links(keys: str) -> str:
    return " · ".join(FUENTES[k.strip()][0] for k in keys.split(",") if k.strip())


def _fuentes_html(keys: list[str], root: str, lang: str) -> str:
    t, d = TXT[lang], _data(lang)
    items = "".join(f'<li><a href="{escape(FUENTES[k][1])}" rel="noopener nofollow">{escape(FUENTES[k][0])}</a></li>' for k in keys)
    return (f'<section class="g-sources"><h2>{t["src_h"]}</h2>'
            f'<p>{t["src_p"].format(r=d["revisado"], root=root)}</p><ul>{items}</ul></section>')


def _capbar(lang: str) -> str:
    t = TXT[lang]
    btns = "".join(f'<button type="button" data-v="{v}">{x}</button>' for v, x in
                   [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", t["cap_done"])])
    return (f'<div class="capbar" data-capbar><span>{t["capq"]}</span>'
            f'<div class="capbtns" role="group" aria-label="{t["cap_aria"]}">{btns}<button type="button" data-v="0">{t["cap_all"]}</button></div>'
            '<small data-caphidden hidden></small></div>')


def _head(root: str, lang: str, title: str, lead: str) -> str:
    t, d = TXT[lang], _data(lang)
    home, hub = (f"{root}", f"{root}guias/") if lang == "es" else (f"{root}pt/", f"{root}pt/guias/")
    return (f'<nav class="crumbs"><a href="{home}">{t["home"]}</a> › <a href="{hub}">{t["guias"]}</a> › {escape(title)}</nav>'
            f'<header class="page-head"><p class="overline">{t["overline"].format(r=d["revisado"])}</p><h1>{escape(title)}</h1>'
            f'<p class="lead">{lead}</p></header>')


def _code(seq: str | None, lang: str) -> str:
    if not seq:
        return f'<span class="tag">{TXT[lang]["code_none"]}</span>'
    names = _data(lang)["arrow_name"]
    label = ", ".join(names[c] for c in seq)
    keys = "".join(f"<kbd>{ARROW[c]}</kbd>" for c in seq)
    return f'<span class="code" aria-label="{label}">{keys}</span>'


def _num(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def trucos_body(root: str, lang: str = "es") -> str:
    t, d = TXT[lang], _data(lang)
    n = sum(len(v) for _, v in d["trucos"])
    n_code = sum(1 for _, v in d["trucos"] for x in v if x[2])
    groups = []
    for name, rows in d["trucos"]:
        lis = "".join(
            f'<li class="tk-row" data-q="{escape((efecto + " " + req).lower())}">'
            f'<div class="tk-main"><b>{escape(efecto)}</b><span class="tk-req">{t["unlock"]}: {escape(req)}</span>'
            + (f'<span class="tk-note">{escape(nota)}</span>' if nota else "") +
            f'</div><div class="tk-code">{_code(code, lang)}</div></li>'
            for efecto, req, code, nota in rows)
        groups.append(f'<section class="g-group"><h2>{escape(name)} <small>{len(rows)}</small></h2><ul class="tk-list">{lis}</ul></section>')
    return (_head(root, lang, t["tk_h1"], t["tk_lead"].format(n=n, c=n_code))
            + t["tk_how"]
            + f'<label class="g-search"><span class="sr">{t["tk_search_l"]}</span><input type="search" id="tk-q" placeholder="{t["tk_search_ph"]}" autocomplete="off"></label>'
            + "".join(groups)
            + f'<p class="g-empty" id="tk-empty" hidden>{t["tk_empty"]}</p>'
            + _fuentes_html(["levelup", "vidaextra", "infobae"], root, lang))


def cien_body(root: str, lang: str = "es") -> str:
    t, d = TXT[lang], _data(lang)
    sections = []
    for name, rows in d["cien"]:
        lis = []
        for key, label, need, total, nota, src, cap in rows:
            money = key.startswith("f_")
            tot = f' {t["h_of"]} {_num(total)}' if total else ""
            step = 5000 if money else 1
            lis.append(
                f'<li class="h-row" data-cap="{cap}" data-need="{need}">'
                f'<div class="h-info"><b>{escape(label)}</b>'
                f'<span class="h-need">{t["h_need"]} {"$" if money else ""}{_num(need)}{tot}</span>'
                + (f'<span class="h-note">{escape(nota)}</span>' if nota else "")
                + f'<span class="h-src">{t["segun"]} {escape(_src_links(src))}</span></div>'
                f'<div class="h-ctrl"><button type="button" class="h-minus" aria-label="{t["h_minus"]}">−</button>'
                f'<input type="number" inputmode="numeric" min="0" step="{step}" value="0" data-key="{key}" aria-label="{escape(t["h_aria"].format(x=label))}">'
                f'<button type="button" class="h-plus" aria-label="{t["h_plus"]}">+</button></div>'
                f'<div class="ck-bar"><i></i></div></li>')
        sections.append(f'<section class="g-group"><h2>{escape(name)}</h2><ul class="h-list">{"".join(lis)}</ul></section>')
    cards = "".join(f'<li><label><input type="checkbox" data-ck="wm-cartas" data-id="{escape(n)}">'
                    f'<span class="ck-t">{escape(n)}<small>{c} {t["cards_n"]}</small></span></label></li>' for n, c in CARTAS)
    return (_head(root, lang, t["h_h1"], t["h_lead"])
            + _capbar(lang)
            + t["h_sum"].format(lost=_url(lang, root, "no-te-lo-pierdas"))
            + "".join(sections)
            + f'<section class="g-group"><h2>{t["cards_h"]}</h2><p class="note">{t["cards_note"]}</p><ul class="ck-list">{cards}</ul></section>'
            + _fuentes_html(["gc", "vchq", "mpg", "keengamer"], root, lang))


def trofeos_body(root: str, lang: str = "es") -> str:
    t, d = TXT[lang], _data(lang)
    grados, trofeos = d["grados"], d["trofeos"]
    counts = {g: sum(1 for x in trofeos if x[1] == g) for g in grados}
    rows = "".join(
        f'<li class="tr-row" data-cap="{cap}" data-grade="{g}" data-type="{tipo}"><label>'
        f'<input type="checkbox" data-ck="wm-trofeos" data-id="{escape(name)}">'
        f'<span class="tr-badge g-{g}" title="{grados[g]}">{grados[g][0]}</span>'
        f'<span class="ck-t"><b>{escape(name)}</b><span>{escape(req)}</span>'
        + (f'<small class="tr-note">{escape(nota)}</small>' if nota else "")
        + f'<small>{t["tr_story"] if tipo == "h" else t["tr_opt"]}</small></span></label></li>'
        for name, g, req, tipo, cap, nota in trofeos)
    filt = "".join(f'<button type="button" data-grade="{g}">{grados[g]} <small>{counts[g]}</small></button>' for g in grados)
    return (_head(root, lang, t["tr_h1"], t["tr_lead"].format(n=len(trofeos), **counts))
            + t["tr_how"].format(lost=_url(lang, root, "no-te-lo-pierdas"))
            + _capbar(lang)
            + f'<div class="tr-filter" role="group" aria-label="{t["tr_filter"]}"><button type="button" data-grade="" class="on">{t["tr_all"]}</button>{filt}'
              f'<label class="ck-hide"><input type="checkbox" id="tr-hide"> {t["tr_hide"]}</label></div>'
            + f'<p class="tr-count"><b id="tr-done">0</b> {t["tr_count"].format(n=len(trofeos))}</p>'
            + f'<ul class="ck-list tr-list">{rows}</ul>'
            + _fuentes_html(["powerpyx", "keengamer", "bloxodes"], root, lang))


def perdibles_body(root: str, lang: str = "es") -> str:
    t, d = TXT[lang], _data(lang)
    rows = []
    for cap in sorted({p[0] for p in d["perdibles"]}):
        items = "".join(
            f'<li data-cap="{c}"><b>{escape(q)}</b><p>{escape(por)}</p><p class="ml-do">{escape(hacer)}</p>'
            f'<small>{t["segun"]} {escape(_src_links(src))}</small></li>'
            for c, q, por, hacer, src in d["perdibles"] if c == cap)
        rows.append(f'<section class="g-group" data-cap="{cap}"><h2>{t["chapter"]} {cap}</h2><ul class="ml-list">{items}</ul></section>')
    gen = "".join(f"<li><b>{escape(a)}.</b> {escape(b)}</li>" for a, b in d["generales"])
    return (_head(root, lang, t["ml_h1"], t["ml_lead"])
            + _capbar(lang)
            + f'<section class="g-how"><h2>{t["ml_gen"]}</h2><ul class="g-facts">{gen}</ul></section>'
            + "".join(rows)
            + _fuentes_html(["powerpyx", "keengamer", "bloxodes", "gc", "mpg"], root, lang))


def plata_body(root: str, lang: str = "es") -> str:
    t, d = TXT[lang], _data(lang)
    rows = "".join(
        f'<li class="mn-row" data-cap="{cap}"><span class="mn-n">{i:02d}</span>'
        f'<div class="mn-main"><b>{escape(m)}</b><span class="mn-pay">{escape(pago)}</span>'
        f'<span class="mn-meta"><span>{t["mn_from"]}: {escape(desde)}</span><span class="mn-risk r{r}">{t["risk"][r]}</span></span>'
        f'<p>{escape(nota)}</p><small>{t["segun"]} {escape(_src_links(src))}</small></div></li>'
        for i, (m, pago, desde, cap, r, nota, src) in enumerate(d["plata"], 1))
    tips = "".join(f"<li>{escape(x)}</li>" for x in d["consejos"])
    return (_head(root, lang, t["mn_h1"], t["mn_lead"])
            + _capbar(lang)
            + f'<p class="note">{t["mn_note"]}</p>'
            + f'<ol class="mn-list">{rows}</ol>'
            + f'<section class="g-how"><h2>{t["mn_tips"]}</h2><ul class="g-facts">{tips}</ul></section>'
            + f'<p class="note">{t["mn_cat"].format(root=root)}</p>'
            + _fuentes_html(["fandomwire", "egamers", "technerdiness"], root, lang))


def _cards(root: str, lang: str) -> str:
    return "".join(f'<li><a href="{_url(lang, root, es)}"><b>{escape(ti)}</b><span>{escape(de)}</span><i aria-hidden="true">→</i></a></li>'
                   for _, es, ti, de in _data(lang)["guias"])


def hub_body(root: str, lang: str = "es") -> str:
    t = TXT[lang]
    home = root if lang == "es" else f"{root}pt/"
    h1 = "Guías de GTA 6" if lang == "es" else "Guias de GTA 6"
    return (f'<nav class="crumbs"><a href="{home}">{t["home"]}</a> › {t["guias"]}</nav>'
            f'<header class="page-head"><h1>{h1}</h1><p class="lead">{t["hub_lead"]}</p></header>'
            f'<ul class="g-hub">{_cards(root, lang)}<li><a href="{root}lista/">{t["hub_list"]}<i aria-hidden="true">→</i></a></li></ul>')


def home_section(root: str = "", lang: str = "es") -> str:
    """Bloque de la portada con las guías."""
    t = TXT[lang]
    hub = f"{root}guias/" if lang == "es" else f"{root}pt/guias/"
    head = (f'<div class="sec-head" data-reveal><div><p class="overline">{t["home_over"]}</p>'
            f'<h2>{t["home_h"]}</h2></div><a class="more-link" href="{hub}">{t["home_more"]}</a></div>'
            f'<ul class="g-hub" data-reveal data-stagger>{_cards(root, lang)}</ul>')
    if lang == "es":
        return f'<section class="sec guides-home"><div class="wrap">{head}</div></section>'
    return f'<section class="guides-pt">{head}</section>'


# slug en español -> (título, descripción, función) por idioma
PAGES = {
    "trucos": ("Trucos de GTA 6: todos los códigos y cómo activarlos",
               "Los 61 trucos de GTA 6 en español: códigos para PS5 y Xbox, cómo se activan y qué hay que hacer para desbloquear cada uno.",
               trucos_body),
    "100-por-ciento": ("Lista del 100 % de GTA 6 con contador de progreso",
                       "Todo lo que pide el 100 % de GTA 6: cartas, flamencos, WAiNK, robos, acrobacias y más. Anotá tu progreso sin registrarte.",
                       cien_body),
    "trofeos": ("Trofeos de GTA 6: lista completa en español",
                "Los 55 trofeos de GTA 6 en español, con requisitos, cuáles son de historia y cuál se puede perder. Tildá los que ya tenés.",
                trofeos_body),
    "no-te-lo-pierdas": ("GTA 6: lo que se pierde si avanzás la historia",
                         "Coleccionables, meditaciones y misiones de GTA 6 que desaparecen al pasar de capítulo, y qué hacer antes.",
                         perdibles_body),
    "ganar-dinero": ("Cómo ganar plata rápido en GTA 6: todos los métodos",
                     "Las mejores formas de ganar dinero en GTA 6, ordenadas por cuánto pagan y desde qué capítulo se pueden hacer.",
                     plata_body),
}
PAGES_PT = {
    "trucos": ("Truques de GTA 6: todos os códigos e como ativar",
               "Os 61 truques de GTA 6 em português: códigos para PS5 e Xbox, como ativar e o que fazer para desbloquear cada um."),
    "100-por-ciento": ("Lista dos 100 % de GTA 6 com contador de progresso",
                       "Tudo o que os 100 % de GTA 6 pedem: cartas, flamingos, WAiNK, roubos, acrobacias e mais. Anote seu progresso sem cadastro."),
    "trofeos": ("Troféus de GTA 6: lista completa em português",
                "Os 55 troféus de GTA 6 em português, com requisitos, quais vêm da história e qual dá para perder. Marque os que você já tem."),
    "no-te-lo-pierdas": ("GTA 6: o que dá para perder se você avançar a história",
                         "Colecionáveis, meditações e missões de GTA 6 que somem ao passar de capítulo, e o que fazer antes."),
    "ganar-dinero": ("Como ganhar dinheiro rápido no GTA 6: todos os métodos",
                     "As melhores formas de ganhar dinheiro no GTA 6, ordenadas por quanto pagam e a partir de qual capítulo dá para fazer."),
}
HUB = {"es": ("Guías de GTA 6 en español", "Trucos, lista del 100 %, trofeos, lo que se pierde y cómo ganar plata en GTA 6."),
       "pt": ("Guias de GTA 6 em português", "Truques, lista dos 100 %, troféus, o que dá para perder e como ganhar dinheiro no GTA 6.")}


def build(P) -> list[tuple[str, str]]:
    """Escribe las guías y el índice en los dos idiomas. Devuelve las URLs para el sitemap."""
    docs, site = config.DOCS_DIR, config.SITE_URL
    ver = P._ver("guias.js")
    pt_slug = {es: pt for pt, es, _, _ in _data("pt")["guias"]}
    pages = [("guias", "guias", HUB["es"], HUB["pt"], hub_body)]
    pages += [(es, pt_slug[es], (ti, de), PAGES_PT[es], fn) for es, (ti, de, fn) in PAGES.items()]
    urls = []
    for es, pt, (ti_es, de_es), (ti_pt, de_pt), fn in pages:
        es_url, pt_url = f"{site}/{es}/", f"{site}/pt/{pt}/"
        alternates = [("es", es_url), ("pt-BR", pt_url)]
        for lang, rel, title, desc, root, url in [("es", es, ti_es, de_es, "../", es_url),
                                                  ("pt", f"pt/{pt}", ti_pt, de_pt, "../../", pt_url)]:
            out = docs / rel / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            body = fn(root, lang) + f'<script src="{root}guias.js?v={ver}" defer></script>'
            out.write_text(P._layout(title=f"{title} | {config.SITE_NAME}", description=desc, canonical=url, root=root,
                                     body=body, lang=lang, alternates=alternates), encoding="utf-8")
            urls.append((url, "2026-11-24"))
    print(f"[web] {len(urls)} páginas de guías (español y portugués)")
    return urls
