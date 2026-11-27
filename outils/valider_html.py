"""Valide toutes les pages avec le validateur du W3C (service en ligne Nu HTML Checker).

Usage (depuis le dossier du site) : python outils/valider_html.py [page.html ...]
Equivaut, pour chaque page, a :
  curl -H "Content-Type: text/html; charset=utf-8" --data-binary @page.html "https://validator.w3.org/nu/?out=json"
Affiche les erreurs et les avertissements ; code de sortie 1 s'il reste des erreurs.
"""
import json
import pathlib
import sys
import time
import urllib.request

RACINE = pathlib.Path(__file__).resolve().parent.parent
URL = "https://validator.w3.org/nu/?out=json"


def valider(fichier):
    req = urllib.request.Request(URL, data=fichier.read_bytes(), headers={
        "Content-Type": "text/html; charset=utf-8",
        "User-Agent": "verification-site-statique/1.0",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["messages"]


def main():
    pages = [RACINE / p for p in sys.argv[1:]] or sorted(RACINE.glob("*.html"))
    total_erreurs = 0
    for page in pages:
        messages = valider(page)
        erreurs = [m for m in messages if m["type"] == "error" or m.get("subType") == "fatal"]
        avert = [m for m in messages if m["type"] == "info" and m.get("subType") == "warning"]
        total_erreurs += len(erreurs)
        print(f"{page.name:18} {len(erreurs)} erreur(s), {len(avert)} avertissement(s)")
        for m in erreurs + avert:
            genre = "ERREUR" if m in erreurs else "avert."
            print(f"    {genre} ligne {m.get('lastLine', '?')} : {m['message']}")
        time.sleep(1)  # menager le service public
    print(f"Total : {total_erreurs} erreur(s) sur {len(pages)} page(s).")
    return 1 if total_erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
