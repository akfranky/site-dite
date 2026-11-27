"""Verifie les liens internes et les ancres de toutes les pages du site.

Usage (depuis le dossier du site) :
    python outils/verifier_liens.py            liens internes et ancres
    python outils/verifier_liens.py --externes liste aussi les liens externes (sans les tester)

Controles :
- chaque href/src local (pages, images, CSS, JS, PDF) pointe vers un fichier existant ;
- chaque ancre (#id), sur la meme page ou sur une autre page, existe ;
- chaque cible de data-bs-target / aria-controls existe dans la page ;
- aucun identifiant n'est en double dans une page ;
- les url() des feuilles de style de assets/css pointent vers des fichiers existants.

Code de sortie : 0 si tout est correct, 1 sinon. Bibliotheque standard uniquement.
"""
import pathlib
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

RACINE = pathlib.Path(__file__).resolve().parent.parent
SCHEMAS_EXTERNES = ("http", "https", "mailto", "tel", "data")


class Analyse(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.liens = []      # (attribut, valeur, ligne)
        self.cibles = []     # (attribut, id, ligne)

    def handle_starttag(self, tag, attrs):
        ligne = self.getpos()[0]
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        for nom in ("href", "src"):
            if a.get(nom) is not None:
                self.liens.append((nom, a[nom], ligne))
        if a.get("srcset"):
            for morceau in a["srcset"].split(","):
                self.liens.append(("srcset", morceau.strip().split()[0], ligne))
        cible = a.get("data-bs-target")
        if cible and cible.startswith("#"):
            self.cibles.append(("data-bs-target", cible[1:], ligne))
        if a.get("aria-controls"):
            self.cibles.append(("aria-controls", a["aria-controls"], ligne))
        if a.get("aria-labelledby"):
            for i in a["aria-labelledby"].split():
                self.cibles.append(("aria-labelledby", i, ligne))
        if a.get("data-filtre-groupe"):
            self.cibles.append(("data-filtre-groupe", a["data-filtre-groupe"], ligne))


def analyser(fichier):
    p = Analyse()
    p.feed(fichier.read_text(encoding="utf-8"))
    return p


def main():
    afficher_externes = "--externes" in sys.argv
    pages = sorted(RACINE.glob("*.html")) + sorted((RACINE / "pages").glob("*.html"))
    cle = lambda f: f.resolve().relative_to(RACINE).as_posix()
    analyses = {cle(f): analyser(f) for f in pages}
    dossiers = {cle(f): f.parent for f in pages}
    erreurs, externes, compte = [], set(), 0

    for nom, a in analyses.items():
        doublons = {i for i in a.ids if a.ids.count(i) > 1}
        for i in sorted(doublons):
            erreurs.append(f"{nom} : identifiant en double '{i}'")
        for attr, ident, ligne in a.cibles:
            if ident not in a.ids:
                erreurs.append(f"{nom}:{ligne} : {attr} vise '{ident}', absent de la page")
        for attr, valeur, ligne in a.liens:
            compte += 1
            morceaux = urlsplit(valeur)
            if morceaux.scheme in SCHEMAS_EXTERNES:
                if morceaux.scheme in ("http", "https"):
                    externes.add(valeur)
                continue
            if morceaux.scheme or valeur.startswith("//"):
                erreurs.append(f"{nom}:{ligne} : schema inattendu '{valeur}'")
                continue
            chemin = unquote(morceaux.path)
            if chemin:
                cible = (dossiers[nom] / chemin).resolve()
                if not cible.exists():
                    erreurs.append(f"{nom}:{ligne} : {attr}='{valeur}' : fichier introuvable")
                    continue
                page_cible = cle(cible) if cle(cible) in analyses else None
            else:
                page_cible = nom
            if morceaux.fragment:
                if page_cible is None:
                    erreurs.append(f"{nom}:{ligne} : ancre sur un fichier non HTML '{valeur}'")
                elif morceaux.fragment not in analyses[page_cible].ids:
                    erreurs.append(f"{nom}:{ligne} : ancre '#{morceaux.fragment}' absente de {page_cible}")
            elif valeur == "#":
                erreurs.append(f"{nom}:{ligne} : lien vide '#'")

    for css in sorted((RACINE / "assets" / "css").glob("*.css")):
        for url in re.findall(r"url\(\s*[\"']?([^\"')]+)", css.read_text(encoding="utf-8")):
            if url.startswith("data:"):
                continue
            compte += 1
            if not (css.parent / url.split("?")[0]).resolve().exists():
                erreurs.append(f"{css.relative_to(RACINE)} : url({url}) introuvable")

    print(f"{len(pages)} pages, {compte} liens et ressources examines, {len(externes)} liens externes distincts.")
    if afficher_externes:
        for u in sorted(externes):
            print("  externe :", u)
    if erreurs:
        print(f"{len(erreurs)} probleme(s) :")
        for e in erreurs:
            print("  -", e)
        return 1
    print("Aucun lien casse, aucune ancre manquante.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
