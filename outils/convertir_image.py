"""Prepare une photo pour le site : recadrage, redimensionnement, WebP sous le poids maximal.

Usage (depuis le dossier du site) :
    python outils/convertir_image.py PHOTO.jpg DESTINATION.webp [--format 4:3|16:9] [--largeur 480] [--max-ko 100]

Exemples :
    portrait d'enseignant (4:3, 480 px, moins de 100 Ko) :
        python outils/convertir_image.py dupont.jpg assets/img/enseignants/dupont.webp
    image d'actualite (16:9, 960 px, moins de 150 Ko) :
        python outils/convertir_image.py ceremonie.jpg assets/img/actualites/ceremonie.webp --format 16:9 --largeur 960 --max-ko 150

Le recadrage garde le centre de l'image (un peu vers le haut pour les portraits).
A la fin, le script affiche les attributs width et height a recopier dans la balise <img>.
Necessite Pillow (pip install Pillow).
"""
import argparse
import os
import sys

from PIL import Image, ImageOps


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source")
    p.add_argument("destination")
    p.add_argument("--format", default="4:3")
    p.add_argument("--largeur", type=int, default=480)
    p.add_argument("--max-ko", type=int, default=100)
    a = p.parse_args()

    rw, rh = (int(x) for x in a.format.split(":"))
    im = ImageOps.exif_transpose(Image.open(a.source)).convert("RGB")
    w, h = im.size
    if w / h > rw / rh:
        nw = int(h * rw / rh)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w * rh / rw)
        haut = int((h - nh) * (0.25 if rw <= rh * 4 / 3 else 0.5))
        im = im.crop((0, haut, w, haut + nh))
    hauteur = round(a.largeur * rh / rw)
    im = im.resize((a.largeur, hauteur), Image.LANCZOS)

    qualite = 82
    while True:
        im.save(a.destination, "WEBP", quality=qualite, method=6)
        ko = os.path.getsize(a.destination) / 1024
        if ko <= a.max_ko or qualite <= 40:
            break
        qualite -= 6
    print(f"{a.destination} : {a.largeur} x {hauteur} px, {ko:.0f} Ko (qualite {qualite})")
    print(f'A recopier dans la balise : width="{a.largeur}" height="{hauteur}"')
    if ko > a.max_ko:
        print("Attention : poids encore superieur au maximum, reduisez --largeur.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
