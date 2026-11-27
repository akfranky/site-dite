"""Recopie l'en-tete et le pied de page communs dans toutes les pages du site.

Usage (depuis le dossier du site) :
    python outils/synchroniser_gabarit.py

Outil FACULTATIF : le site fonctionne sans lui. Il evite seulement de recopier
a la main une modification du menu ou du pied de page dans les onze pages.

- Modeles : outils/gabarit/entete.html et outils/gabarit/pied.html
- Dans chaque page, le contenu situe entre les commentaires
  <!-- ENTETE --> ... <!-- /ENTETE --> et <!-- PIED --> ... <!-- /PIED -->
  est remplace par le modele.
- La page active du menu est lue dans l'attribut data-page de <body>.
  Dans le modele, {{actif a b}} devient " active" et {{courant a b}} devient
  ' aria-current="page"' quand data-page vaut a ou b.
"""
import pathlib
import re
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
GABARIT = RACINE / "outils" / "gabarit"


def remplir(modele: str, page: str) -> str:
    def actif(m):
        return " active" if page in m.group(1).split() else ""

    def courant(m):
        return ' aria-current="page"' if page in m.group(1).split() else ""

    modele = re.sub(r"\{\{actif ([^}]+)\}\}", actif, modele)
    return re.sub(r"\{\{courant ([^}]+)\}\}", courant, modele)


def main() -> int:
    entete = (GABARIT / "entete.html").read_text(encoding="utf-8").strip("\n")
    pied = (GABARIT / "pied.html").read_text(encoding="utf-8").strip("\n")
    modifiees = 0
    for fichier in sorted(RACINE.glob("*.html")):
        texte = fichier.read_text(encoding="utf-8")
        m = re.search(r'<body[^>]*\sdata-page="([^"]+)"', texte)
        if not m:
            print(f"ignore (pas de data-page sur <body>) : {fichier.name}")
            continue
        page = m.group(1)
        nouveau = texte
        for nom, modele in (("ENTETE", entete), ("PIED", pied)):
            motif = re.compile(rf"(<!-- {nom} -->\n).*?(\n<!-- /{nom} -->)", re.S)
            if not motif.search(nouveau):
                print(f"marqueurs {nom} absents : {fichier.name}")
                continue
            nouveau = motif.sub(lambda mm: mm.group(1) + remplir(modele, page) + mm.group(2), nouveau)
        if nouveau != texte:
            fichier.write_text(nouveau, encoding="utf-8", newline="\n")
            modifiees += 1
            print(f"mise a jour : {fichier.name}")
    print(f"{modifiees} page(s) modifiee(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
