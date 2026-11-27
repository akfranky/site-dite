"""Audit des points mesurables avant publication (bibliotheque standard + Pillow).

Usage (depuis le dossier du site) : python outils/audit.py

Controles, page par page :
- lang="fr", <title>, meta description, un seul <h1>, hierarchie de titres sans saut,
  lien d'evitement, fil d'Ariane (sauf accueil) ;
- chaque <img> : alt present, width et height presents, format WebP (ou SVG pour les icones),
  poids < 150 Ko (< 100 Ko pour les portraits), loading="lazy" conseille hors premier ecran ;
- aucune ressource chargee depuis un domaine externe (link, script, img, source, iframe, CSS url()) ;
- poids total de la page : HTML + CSS + JS + polices + images referencees (premier chargement) ;
Controles globaux :
- aucun emoji dans les fichiers du depot (hors lib/) ;
- contrastes WCAG des couples de couleurs de la charte.
Code de sortie 1 si un controle bloquant echoue.
"""
import pathlib
import re
import sys
from html.parser import HTMLParser

try:
    from PIL import Image
except ImportError:  # Pillow facultatif : dimensions non verifiees
    Image = None

RACINE = pathlib.Path(__file__).resolve().parent.parent
LIMITE_ACCUEIL = 1024 * 1024
# Plages Unicode des emojis et pictogrammes (codes numeriques, pour garder ce fichier en ASCII)
PLAGES_EMOJI = [(0x1F300, 0x1FAFF), (0x2600, 0x27BF), (0x1F000, 0x1F2FF), (0xFE0F, 0xFE0F)]
EMOJI = re.compile("[" + "".join(chr(a) + "-" + chr(b) for a, b in PLAGES_EMOJI) + "]")

# Couples (texte, fond, usage, seuil) : 4,5 pour le texte courant, 3 pour le grand texte et les icones
CONTRASTES = [
    ("#A63D24", "#FFFFFF", "liens et boutons secondaires sur blanc", 4.5),
    ("#A63D24", "#F6F1EA", "liens sur fond sable", 4.5),
    ("#FFFFFF", "#A63D24", "bouton principal", 4.5),
    ("#FFFFFF", "#852F1A", "bouton principal survole", 4.5),
    ("#1E1A17", "#E8B04B", "bouton d'appel et badge Nouveau", 4.5),
    ("#E8B04B", "#1E1A17", "surtitre ocre sur ebene", 4.5),
    ("#FFFFFF", "#1E1A17", "titres et pied de page", 4.5),
    ("#E1E1E0", "#1E1A17", "liens de navigation (blanc 88 %)", 4.5),
    ("#C7C6C5", "#1E1A17", "bas de pied de page (blanc 75 %)", 4.5),
    ("#212529", "#FFFFFF", "corps de texte", 4.5),
    ("#212529", "#F6F1EA", "corps de texte sur sable", 4.5),
    ("#6B5E55", "#FFFFFF", "texte secondaire", 4.5),
    ("#6B5E55", "#F6F1EA", "texte secondaire sur sable", 4.5),
    ("#852F1A", "#F6E4DD", "etiquettes Enseigne et categories", 4.5),
    ("#6B4A0F", "#FBEFD6", "etiquettes Recherche", 4.5),
    ("#5A4512", "#FBF3E2", "bandeau de version de travail", 4.5),
    ("#FFFFFF", "#146C43", "badge Oui", 4.5),
    ("#1E1A17", "#EADFD1", "badge Non", 4.5),
    ("#A63D24", "#F6E4DD", "icones sur carre latérite clair", 3.0),
    ("#FFFFFF", "#6A2D1E", "texte du bandeau, zone la plus claire du degrade", 4.5),
]


def luminance(hexa):
    r, g, b = (int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.titre = ""
        self.dans_titre = False
        self.description = None
        self.titres = []
        self.imgs = []
        self.ressources = []
        self.liens_evitement = False
        self.fil = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title":
            self.dans_titre = True
        elif tag == "meta" and a.get("name") == "description":
            self.description = a.get("content")
        elif re.fullmatch(r"h[1-6]", tag):
            self.titres.append(int(tag[1]))
        elif tag == "img":
            self.imgs.append((a, self.getpos()[0]))
            self.ressources.append(a.get("src", ""))
            for m in (a.get("srcset") or "").split(","):
                if m.strip():
                    self.ressources.append(m.strip().split()[0])
        elif tag == "link" and a.get("rel") in ("stylesheet", "icon", "apple-touch-icon", "preload"):
            self.ressources.append(a.get("href", ""))
        elif tag in ("script", "source", "iframe", "video", "audio", "embed"):
            if a.get("src"):
                self.ressources.append(a["src"])
        elif tag == "a" and a.get("href") == "#contenu" and "lien-evitement" in a.get("class", ""):
            self.liens_evitement = True
        elif tag == "nav" and a.get("aria-label") == "Fil d'Ariane":
            self.fil = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.dans_titre = False

    def handle_data(self, data):
        if self.dans_titre:
            self.titre += data


def taille(base, chemin):
    p = (base / chemin).resolve()
    return p.stat().st_size if p.exists() else 0


def main():
    bloquant = []
    print("== Pages ==")
    css_communs = ["lib/bootstrap/css/bootstrap.min.css", "lib/bootstrap-icons/bootstrap-icons.min.css",
                   "assets/css/style.css", "lib/bootstrap-icons/fonts/bootstrap-icons.woff2"]
    polices = [str(p.relative_to(RACINE)).replace("\\", "/") for p in (RACINE / "assets/fonts").glob("*.woff2")]
    for fichier in sorted(RACINE.glob("*.html")) + sorted((RACINE / "pages").glob("*.html")):
        base = fichier.parent
        texte = fichier.read_text(encoding="utf-8")
        p = Page()
        p.feed(texte)
        nom = fichier.relative_to(RACINE).as_posix()
        pb = []
        if p.lang != "fr":
            pb.append("lang absent ou different de fr")
        if not p.titre.strip():
            pb.append("title vide")
        if not p.description:
            pb.append("meta description absente")
        if p.titres.count(1) != 1:
            pb.append(f"{p.titres.count(1)} h1")
        for avant, apres in zip(p.titres, p.titres[1:]):
            if apres > avant + 1:
                pb.append(f"saut de titre h{avant} -> h{apres}")
                break
        if not p.liens_evitement:
            pb.append("lien d'evitement absent")
        if nom != "index.html" and not p.fil:
            pb.append("fil d'Ariane absent")
        for a, ligne in p.imgs:
            src = a.get("src", "")
            if "alt" not in a:
                pb.append(f"img sans alt ligne {ligne}")
            if not a.get("width") or not a.get("height"):
                pb.append(f"img sans width/height ligne {ligne} ({src})")
            if not src.endswith((".webp", ".svg")):
                pb.append(f"image non WebP ligne {ligne} ({src})")
            limite = 100 if "/enseignants/" in src else 150
            if taille(base, src) > limite * 1024:
                pb.append(f"image de plus de {limite} Ko : {src}")
        externes = [r for r in p.ressources if re.match(r"^(https?:)?//", r)]
        if externes:
            pb.append(f"ressources externes : {externes}")
        # Poids du premier chargement : les images differees sont comptees a part
        imgs_immediates, imgs_differees = set(), set()
        for a, _ in p.imgs:
            cible = imgs_differees if a.get("loading") == "lazy" else imgs_immediates
            srcset = [m.strip().split()[0] for m in (a.get("srcset") or "").split(",") if m.strip()]
            cible.add(srcset[-1] if srcset else a.get("src", ""))  # variante la plus lourde
        fixes = len(texte.encode()) + sum(taille(RACINE, c) for c in css_communs) + sum(taille(RACINE, c) for c in polices)
        fixes += taille(RACINE, "lib/bootstrap/js/bootstrap.bundle.min.js") + taille(RACINE, "assets/js/main.js")
        fixes += taille(RACINE, "assets/img/logo/favicon-32.png")
        immediat = fixes + sum(taille(base, i) for i in imgs_immediates)
        total = immediat + sum(taille(base, i) for i in imgs_differees)
        etat = "OK" if not pb else "A CORRIGER"
        print(f"{nom:30} {etat:10} h1={p.titres.count(1)} titres={''.join(map(str, p.titres))[:40]:40} "
              f"premier chargement {immediat / 1024:6.0f} Ko, total {total / 1024:6.0f} Ko")
        for x in pb:
            print("    -", x)
        bloquant += [f"{nom} : {x}" for x in pb]
        if nom == "index.html" and total > LIMITE_ACCUEIL:
            bloquant.append(f"accueil trop lourde : {total / 1024:.0f} Ko")

    print("\n== Images du dossier assets/img ==")
    for img in sorted((RACINE / "assets/img").rglob("*")):
        if img.is_file() and img.suffix in (".webp", ".png", ".svg"):
            dims = ""
            if Image and img.suffix != ".svg":
                with Image.open(img) as im:
                    dims = f"{im.size[0]}x{im.size[1]} {im.format}"
            print(f"  {str(img.relative_to(RACINE)):48} {img.stat().st_size / 1024:6.1f} Ko  {dims}")

    print("\n== Feuilles de style : url() externes ==")
    for css in (RACINE / "assets/css").glob("*.css"):
        ext = re.findall(r"url\(\s*[\"']?(https?:)?//", css.read_text(encoding="utf-8"))
        print(f"  {css.name} : {'aucune' if not ext else ext}")
        if ext:
            bloquant.append(f"{css.name} : url() externe")
    for fichier in [RACINE / "assets/js/main.js"]:
        if re.search(r"fetch\(|XMLHttpRequest|https?://", fichier.read_text(encoding="utf-8")):
            bloquant.append("main.js charge une ressource externe")

    print("\n== Emojis (hors lib/ et .git/) ==")
    trouves = []
    for f in RACINE.rglob("*"):
        if f.is_file() and ".git" not in f.parts and "lib" not in f.parts and f.suffix in (
                ".html", ".css", ".js", ".md", ".py", ".svg", ".txt", ".json", ".yml"):
            for n, ligne in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if EMOJI.search(ligne):
                    trouves.append(f"{f.relative_to(RACINE)}:{n}")
    print("  aucun" if not trouves else "\n".join("  " + t for t in trouves))
    bloquant += [f"emoji : {t}" for t in trouves]

    print("\n== Contrastes (WCAG 2.1) ==")
    for texte, fond, usage, seuil in CONTRASTES:
        r = ratio(texte, fond)
        ok = r >= seuil
        print(f"  {texte} sur {fond}  {r:5.2f}:1  (min {seuil})  {'OK' if ok else 'INSUFFISANT'}  {usage}")
        if not ok:
            bloquant.append(f"contraste {texte}/{fond} = {r:.2f}")

    print()
    if bloquant:
        print(f"{len(bloquant)} point(s) bloquant(s).")
        return 1
    print("Tous les controles mesurables sont satisfaits.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
