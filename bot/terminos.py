"""Términos del servicio de WastedMap (sitio y app de Android) en español, portugués e inglés.

Se publican en /terminos/, /pt/termos/ y /en/terms/, enlazadas entre sí. Play Console pide esta URL.
"""
from __future__ import annotations

from . import config

UPDATED = {"es": "25 de noviembre de 2026", "pt": "25 de novembro de 2026", "en": "November 25, 2026"}
MAIL = "contacto@wastedmap.com"
M = f'<a href="mailto:{MAIL}">{MAIL}</a>'

PAGES = {
    "es": ("terminos", "Términos del servicio", "Condiciones de uso del sitio y de la app de WastedMap, una guía no oficial de GTA 6.",
           "Inicio", f"""<h1>Términos del servicio</h1>
<p class="note">Última actualización: {UPDATED["es"]}.</p>
<p class="lead">Estos términos se aplican a wastedmap.com y a la app de WastedMap para Android. Al usarlos, los aceptás. Si no estás de acuerdo, no los uses.</p>
<h2>Qué es WastedMap</h2>
<p>WastedMap es una guía gratuita y <b>no oficial</b> hecha por fans de GTA 6. Reúne secretos, trucos y guías que encuentra la comunidad. No tiene relación con Rockstar Games ni con Take-Two Interactive. GTA, Grand Theft Auto y los nombres del juego son marcas de sus dueños y se mencionan solo para explicar de qué trata cada guía.</p>
<h2>El contenido</h2>
<p>Los resúmenes de las guías se escriben en parte de forma automática, con inteligencia artificial, a partir de videos de otras personas. Hacemos lo posible para que sean correctos, pero <b>pueden tener errores o quedar desactualizados</b> cuando el juego cambia. Usalos bajo tu propia responsabilidad. Las guías marcadas como "sin confirmar" todavía no fueron comprobadas por la comunidad.</p>
<p>Los videos pertenecen a sus autores y se muestran con el reproductor original de YouTube, que tiene sus propias condiciones. Si sos autor de un video y no querés que aparezca, escribinos a {M} y lo sacamos.</p>
<h2>Comentarios y votos</h2>
<p>Podés comentar y votar las guías. Al comentar, sos responsable de lo que escribís y nos das permiso para mostrarlo en el sitio y en la app. No se permiten insultos ni acoso, contenido sexual, discriminación, amenazas, datos personales de otras personas, spam, publicidad, estafas ni trampas para el modo online.</p>
<p>Los comentarios pasan por una revisión automática antes de publicarse. Podemos rechazar, borrar o editar comentarios, y bloquear a quien no respete estas reglas, sin previo aviso. Si ves un comentario que no cumple las reglas, tocá "Reportar" debajo del comentario o escribinos a {M} y lo revisamos.</p>
<h2>Anuncios</h2>
<p>La app para Android muestra anuncios de Google AdMob para cubrir los costos. No respondemos por el contenido de los anuncios ni por los productos de terceros que se promocionan. Cómo se usan los datos para los anuncios lo explica la <a href="../privacidad/">política de privacidad</a>.</p>
<h2>Uso aceptable</h2>
<p>No uses el sitio ni la app para fines ilegales, para intentar dañar o sobrecargar el servicio, ni para copiar masivamente su contenido de forma automática.</p>
<h2>Sin garantías</h2>
<p>El servicio se ofrece "tal cual", gratis y sin garantías de ningún tipo. Puede tener interrupciones o cambiar en cualquier momento. En la medida que lo permita la ley, no somos responsables por daños que surjan del uso del sitio, de la app o de la información que contienen.</p>
<h2>Cambios</h2>
<p>Podemos actualizar estos términos. La fecha de arriba indica la última versión; si seguís usando el servicio después de un cambio, aceptás los términos nuevos.</p>
<h2>Contacto</h2>
<p>Por cualquier consulta sobre estos términos, escribinos a {M}.</p>"""),
    "pt": ("termos", "Termos de serviço", "Condições de uso do site e do app do WastedMap, um guia não oficial de GTA 6.",
           "Início", f"""<h1>Termos de serviço</h1>
<p class="note">Última atualização: {UPDATED["pt"]}.</p>
<p class="lead">Estes termos valem para wastedmap.com e para o app do WastedMap para Android. Ao usá-los, você concorda com eles. Se não concordar, não os use.</p>
<h2>O que é o WastedMap</h2>
<p>O WastedMap é um guia gratuito e <b>não oficial</b> feito por fãs de GTA 6. Reúne segredos, truques e guias que a comunidade encontra. Não tem relação com a Rockstar Games nem com a Take-Two Interactive. GTA, Grand Theft Auto e os nomes do jogo são marcas de seus donos e são citados só para explicar do que trata cada guia.</p>
<h2>O conteúdo</h2>
<p>Os resumos dos guias são escritos em parte de forma automática, com inteligência artificial, a partir de vídeos de outras pessoas. Fazemos o possível para que estejam corretos, mas <b>podem ter erros ou ficar desatualizados</b> quando o jogo muda. Use por sua conta e risco. Os guias marcados como "não confirmado" ainda não foram verificados pela comunidade.</p>
<p>Os vídeos pertencem aos seus autores e aparecem com o player original do YouTube, que tem suas próprias condições. Se você é autor de um vídeo e não quer que ele apareça, escreva para {M} e nós o retiramos.</p>
<h2>Comentários e votos</h2>
<p>Você pode comentar e votar nos guias. Ao comentar, você é responsável pelo que escreve e nos autoriza a mostrar o comentário no site e no app. Não são permitidos insultos ou assédio, conteúdo sexual, discriminação, ameaças, dados pessoais de outras pessoas, spam, publicidade, golpes nem trapaças para o modo online.</p>
<p>Os comentários passam por uma revisão automática antes de serem publicados. Podemos recusar, apagar ou editar comentários e bloquear quem não respeitar estas regras, sem aviso prévio. Se você vir um comentário que não cumpre as regras, toque em "Reportar" abaixo do comentário ou escreva para {M} e nós vamos revisar.</p>
<h2>Anúncios</h2>
<p>O app para Android mostra anúncios do Google AdMob para cobrir os custos. Não respondemos pelo conteúdo dos anúncios nem pelos produtos de terceiros anunciados. Como os dados são usados para os anúncios está explicado na <a href="../../privacidad/">política de privacidade</a> (em espanhol).</p>
<h2>Uso aceitável</h2>
<p>Não use o site nem o app para fins ilegais, para tentar danificar ou sobrecarregar o serviço, nem para copiar seu conteúdo em massa de forma automática.</p>
<h2>Sem garantias</h2>
<p>O serviço é oferecido "no estado em que se encontra", grátis e sem garantias de nenhum tipo. Pode ter interrupções ou mudar a qualquer momento. Na medida permitida pela lei, não somos responsáveis por danos decorrentes do uso do site, do app ou das informações que contêm.</p>
<h2>Mudanças</h2>
<p>Podemos atualizar estes termos. A data acima indica a última versão; se você continuar usando o serviço depois de uma mudança, aceita os novos termos.</p>
<h2>Contato</h2>
<p>Para qualquer dúvida sobre estes termos, escreva para {M}.</p>"""),
    "en": ("terms", "Terms of service", "Terms of use for the WastedMap website and app, an unofficial GTA 6 guide.",
           "Home", f"""<h1>Terms of service</h1>
<p class="note">Last updated: {UPDATED["en"]}.</p>
<p class="lead">These terms apply to wastedmap.com and to the WastedMap app for Android. By using them, you agree to these terms. If you don't agree, please don't use them.</p>
<h2>What WastedMap is</h2>
<p>WastedMap is a free, <b>unofficial</b> guide made by GTA 6 fans. It gathers secrets, cheats and guides found by the community. It is not affiliated with Rockstar Games or Take-Two Interactive. GTA, Grand Theft Auto and the game's names are trademarks of their owners and are mentioned only to describe what each guide is about.</p>
<h2>The content</h2>
<p>Guide summaries are partly written automatically, with artificial intelligence, from other people's videos. We do our best to keep them accurate, but <b>they may contain mistakes or become outdated</b> when the game changes. Use them at your own risk. Guides marked as "unconfirmed" have not been verified by the community yet.</p>
<p>Videos belong to their creators and play in YouTube's original player, which has its own terms. If you made a video and don't want it to appear here, email {M} and we'll take it down.</p>
<h2>Comments and votes</h2>
<p>You can comment on and vote for guides. When you comment, you are responsible for what you write and you allow us to show it on the website and in the app. Insults or harassment, sexual content, discrimination, threats, other people's personal data, spam, advertising, scams and online-mode cheats are not allowed.</p>
<p>Comments are checked automatically before they are published. We may reject, delete or edit comments and block anyone who breaks these rules, without notice. If you see a comment that breaks the rules, tap "Reportar" (Report) under the comment or email {M} and we'll review it.</p>
<h2>Ads</h2>
<p>The Android app shows Google AdMob ads to cover its costs. We are not responsible for ad content or for third-party products being advertised. How data is used for ads is explained in the <a href="../../privacidad/">privacy policy</a> (in Spanish).</p>
<h2>Acceptable use</h2>
<p>Don't use the website or the app for illegal purposes, to try to harm or overload the service, or to scrape its content in bulk.</p>
<h2>No warranties</h2>
<p>The service is provided "as is", free of charge and without warranties of any kind. It may have interruptions or change at any time. To the extent permitted by law, we are not liable for any damage arising from the use of the website, the app or the information they contain.</p>
<h2>Changes</h2>
<p>We may update these terms. The date above shows the latest version; if you keep using the service after a change, you accept the new terms.</p>
<h2>Contact</h2>
<p>For any question about these terms, email {M}.</p>"""),
}


def build(P) -> list[tuple[str, str]]:
    from .idiomas import HREFLANG
    site = config.SITE_URL
    url = {lang: f"{site}/{slug}/" if lang == "es" else f"{site}/{lang}/{slug}/" for lang, (slug, *_ ) in PAGES.items()}
    alternates = [(HREFLANG[l], url[l]) for l in ("es", "pt", "en")]
    urls = []
    for lang, (slug, title, desc, home, body) in PAGES.items():
        root = "../" if lang == "es" else "../../"
        home_href = root if lang == "es" else f"{root}{lang}/"
        out = config.DOCS_DIR / (slug if lang == "es" else f"{lang}/{slug}") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(P._layout(title=f"{title} | {config.SITE_NAME}", description=desc, canonical=url[lang], root=root,
                                 body=f'<nav class="crumbs"><a href="{home_href}">{home}</a> › {title}</nav>\n{body}',
                                 lang=lang, alternates=alternates), encoding="utf-8")
        urls.append((url[lang], "2026-11-25"))
    return urls
