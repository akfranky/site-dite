"""Captures d'ecran pleine page de chaque page a 390, 768 et 1280 px de large.

Usage (depuis le dossier du site) :
    python outils/captures.py                 toutes les pages (et chaque profil d'enseignant)
    python outils/captures.py index.html ...  certaines pages ("pages/profil.html?id=tekouabou" accepte)

Les images sont enregistrees dans docs/captures/<page>-<largeur>.png.

Chrome (ou Chromium) est lance sans interface et pilote par le protocole
DevTools : la largeur est emulee exactement (mode mobile a 390 px), ce que
l'option --window-size ne garantit pas sous Windows. Bibliotheque standard
uniquement (client WebSocket minimal ci-dessous).
"""
import base64
import json
import os
import pathlib
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request

RACINE = pathlib.Path(__file__).resolve().parent.parent
SORTIE = RACINE / "docs" / "captures"
LARGEURS = (390, 768, 1280)
CHROMES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "chromium", "chromium-browser", "chrome",
]


def trouver_chrome():
    for c in CHROMES:
        if pathlib.Path(c).exists():
            return c
        if shutil.which(c):
            return shutil.which(c)
    sys.exit("Chrome ou Chromium introuvable.")


class WebSocket:
    """Client WebSocket minimal (RFC 6455), suffisant pour le protocole DevTools local."""

    def __init__(self, url):
        hote_port, chemin = url[len("ws://"):].split("/", 1)
        hote, port = hote_port.split(":")
        self.s = socket.create_connection((hote, int(port)), timeout=60)
        cle = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((
            f"GET /{chemin} HTTP/1.1\r\nHost: {hote_port}\r\nUpgrade: websocket\r\n"
            f"Connection: Upgrade\r\nSec-WebSocket-Key: {cle}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        ).encode())
        reponse = b""
        while b"\r\n\r\n" not in reponse:
            reponse += self.s.recv(4096)
        if b" 101 " not in reponse.split(b"\r\n")[0]:
            raise RuntimeError("Connexion WebSocket refusee")
        self.tampon = reponse.split(b"\r\n\r\n", 1)[1]
        self.id = 0

    def _lire(self, n):
        while len(self.tampon) < n:
            morceau = self.s.recv(1 << 20)
            if not morceau:
                raise ConnectionError("Connexion fermee")
            self.tampon += morceau
        data, self.tampon = self.tampon[:n], self.tampon[n:]
        return data

    def envoyer(self, texte):
        charge = texte.encode()
        entete = bytearray([0x81])
        n = len(charge)
        if n < 126:
            entete.append(0x80 | n)
        elif n < 65536:
            entete.append(0x80 | 126)
            entete += struct.pack(">H", n)
        else:
            entete.append(0x80 | 127)
            entete += struct.pack(">Q", n)
        masque = os.urandom(4)
        self.s.sendall(bytes(entete) + masque + bytes(b ^ masque[i % 4] for i, b in enumerate(charge)))

    def recevoir(self):
        message = b""
        while True:
            b1, b2 = self._lire(2)
            n = b2 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._lire(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._lire(8))[0]
            message += self._lire(n)
            if b1 & 0x80:
                return message.decode()

    def commande(self, methode, **params):
        self.id += 1
        self.envoyer(json.dumps({"id": self.id, "method": methode, "params": params}))
        while True:
            reponse = json.loads(self.recevoir())
            if reponse.get("id") == self.id:
                if "error" in reponse:
                    raise RuntimeError(f"{methode} : {reponse['error']}")
                return reponse.get("result", {})


def capturer(ws, url, largeur, cible):
    mobile = largeur < 768
    ws.commande("Emulation.setDeviceMetricsOverride", width=largeur, height=900,
                deviceScaleFactor=1, mobile=mobile)
    ws.commande("Page.navigate", url=url)
    for _ in range(100):
        time.sleep(0.1)
        etat = ws.commande("Runtime.evaluate", expression="document.readyState + (document.fonts ? document.fonts.status : '')")
        if etat["result"].get("value") == "completeloaded":
            break
    # Charge les images differees (loading="lazy") avant la capture pleine page
    ws.commande("Runtime.evaluate", expression="document.querySelectorAll('img[loading=lazy]').forEach(function(i){i.loading='eager'})")
    time.sleep(0.6)
    hauteur = ws.commande("Runtime.evaluate", expression="document.documentElement.scrollHeight")["result"]["value"]
    resultat = ws.commande("Page.captureScreenshot", format="png", captureBeyondViewport=True,
                           clip={"x": 0, "y": 0, "width": largeur, "height": hauteur, "scale": 1})
    cible.write_bytes(base64.b64decode(resultat["data"]))


def main():
    chrome = trouver_chrome()
    pages = sys.argv[1:] or [p.relative_to(RACINE).as_posix() for p in
                             sorted(RACINE.glob("*.html")) + sorted((RACINE / "pages").glob("*.html"))
                             if p.name != "profil.html"]
    if not sys.argv[1:]:
        donnees = (RACINE / "assets/data/enseignants.js").read_text(encoding="utf-8")
        pages += [f"pages/profil.html?id={i}" for i in re.findall(r'"id": "([^"]+)"', donnees)[:2]]
    SORTIE.mkdir(parents=True, exist_ok=True)
    port = 9333
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as profil:
        proc = subprocess.Popen([
            chrome, "--headless", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
            "--no-default-browser-check", f"--user-data-dir={profil}",
            f"--remote-debugging-port={port}", "about:blank",
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(100):
                try:
                    cibles = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
                    onglet = next(c for c in cibles if c["type"] == "page")
                    break
                except (OSError, StopIteration):
                    time.sleep(0.1)
            else:
                sys.exit("Chrome ne repond pas sur le port de debogage.")
            ws = WebSocket(onglet["webSocketDebuggerUrl"])
            ws.commande("Page.enable")
            for page in pages:
                chemin, _, requete = page.partition("?")
                url = (RACINE / chemin).as_uri() + ("?" + requete if requete else "")
                suffixe = "-" + requete.split("=")[-1] if requete else ""
                for largeur in LARGEURS:
                    cible = SORTIE / f"{pathlib.Path(chemin).stem}{suffixe}-{largeur}.png"
                    capturer(ws, url, largeur, cible)
                    print(cible.relative_to(RACINE))
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    main()
