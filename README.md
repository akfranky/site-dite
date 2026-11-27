# Site du DITE, ENS de Yaoundé : guide de mise à jour

Ce guide s'adresse à la personne chargée de tenir le site à jour. Il suppose seulement de savoir ouvrir et modifier un fichier HTML. Aucun logiciel spécial n'est nécessaire : un éditeur de texte (Notepad++, Visual Studio Code) et un navigateur suffisent.

Le site est fait de pages HTML statiques, avec Bootstrap 5.3.3 et Bootstrap Icons 1.11.3 servis depuis le dossier `lib/`. Il n'y a ni base de données, ni programme côté serveur, ni compilation.

## 1. Voir le site sur votre ordinateur

Double-cliquez sur `index.html` : le site s'ouvre dans votre navigateur. Toutes les pages fonctionnent ainsi, sans connexion à Internet.

Après chaque modification, enregistrez le fichier puis actualisez la page dans le navigateur (touche F5).

## 2. Organisation des fichiers

```
site-dite/
├── index.html            Accueil
├── 404.html              Page affichée quand une adresse n'existe pas (reste à la racine)
├── pages/
│   ├── departement.html              Présentation, mot du chef, missions, organisation
│   ├── parcours.html                 Concours, auditeurs libres, comparatif, questions fréquentes
│   ├── cursus.html                   Schéma du cursus, cycles, unités d'enseignement, stages
│   ├── enseignants.html              Cartes des enseignants (construites à partir des données)
│   ├── profil.html                   Page de profil unique : profil.html?id=tekouabou
│   ├── recherche.html                Domaines, mémoires, publications, séminaires
│   ├── etudiants.html                Emplois du temps, calendrier, ressources, documents
│   ├── actualites.html               Liste des actualités
│   ├── actualite.html                Article : suspension du recrutement des auditeurs libres
│   ├── actualite-concours-2026.html  Article : concours 2025-2026, avec captures des arrêtés
│   └── contact.html                  Coordonnées, formulaire, plan d'accès
├── lib/                  Bootstrap et Bootstrap Icons : NE JAMAIS MODIFIER
├── assets/
│   ├── css/style.css     Couleurs et mise en forme du site
│   ├── js/main.js        Filtres, tableaux sur mobile, formulaire
│   ├── js/enseignants.js Construction des cartes et de la page de profil
│   ├── data/enseignants.js  Données de tous les enseignants (format JSON)
│   ├── fonts/            Polices Montserrat et Source Sans 3
│   ├── img/              Images : logo/, enseignants/, actualites/, pages/, icons/
│   └── docs/             Documents PDF à télécharger
├── outils/               Scripts facultatifs (vérifications, captures, images, menu)
└── docs/captures/        Captures d'écran du site
```

**Chemins relatifs.** Les pages du dossier `pages/` remontent d'un niveau pour atteindre les images, les styles et l'accueil : elles écrivent `../assets/…`, `../lib/…` et `../index.html`. Entre elles, elles se citent directement (`contact.html`). L'accueil et la page 404, à la racine, écrivent `assets/…` et `pages/contact.html`. La page 404 reste à la racine, car GitHub Pages et Netlify ne la cherchent qu'à cet endroit.

Chaque page contient, dans l'ordre : l'en-tête (entre `<!-- ENTETE -->` et `<!-- /ENTETE -->`), le contenu (dans `<main>`), puis le pied de page (entre `<!-- PIED -->` et `<!-- /PIED -->`).

Repères utiles dans le code :

- `class="a-completer"` : texte en italique gris qui signale une information manquante. Remplacez le texte et retirez cette classe.
- `class="badge-exemple"` : étiquette « Exemple » ou « Profil d'exemple ». Retirez-la quand le contenu devient réel.

## 3. Règles à respecter

- Ne modifiez jamais les fichiers du dossier `lib/`. Toute personnalisation va dans `assets/css/style.css`.
- Images : format WebP, moins de 150 Ko (moins de 100 Ko pour un portrait), toujours avec `width`, `height` et un texte `alt` qui décrit l'image. Ajoutez `loading="lazy"` aux images qui ne sont pas en haut de la page.
- Pas d'emoji : les icônes viennent de Bootstrap Icons (`<i class="bi bi-…" aria-hidden="true"></i>`). La liste des icônes est sur icons.getbootstrap.com.
- Aucun fichier chargé depuis un autre site (pas de lien vers un CDN, pas de carte intégrée).
- Rédaction : vouvoiement, phrases courtes, dates en toutes lettres (« 27 novembre 2026 »).
- N'inventez rien : une information non confirmée reste marquée « à compléter ».

## 4. Ajouter ou modifier un enseignant

Toutes les informations des enseignants sont dans **un seul fichier** : `assets/data/enseignants.js`. Il n'y a rien à écrire en HTML :

- la page `pages/enseignants.html` construit une carte par enseignant (photo, nom, grade, trois mots-clés) ;
- la page unique `pages/profil.html` affiche le profil complet de l'enseignant indiqué dans l'adresse : `profil.html?id=tekouabou`.

### Pourquoi un fichier .js et pas .json

Le site doit fonctionner en ouvrant les fichiers directement (double-clic). Dans ce cas, les navigateurs interdisent de lire un fichier `.json` séparé. Le fichier `enseignants.js` contient donc du JSON strict, précédé d'une seule ligne : `window.DITE_ENSEIGNANTS =`. Ne modifiez pas cette ligne ni le `;` final ; tout ce qui est entre les crochets `[` et `]` suit les règles du JSON :

- textes entre guillemets droits `"…"` ; une apostrophe s'écrit normalement (`l'école`) ;
- une virgule entre deux éléments, **jamais** après le dernier ;
- `true` / `false` sans guillemets.

### Ajouter un enseignant

1. Préparez la photo (portrait, fond neutre) :
   ```
   python outils/convertir_image.py photo.jpg assets/img/enseignants/dupont.webp
   ```
2. Dans `assets/data/enseignants.js`, copiez le bloc `{ … }` de l'enseignant `"id": "tekouabou"`, collez-le après lui (séparé par une virgule) et modifiez les valeurs :

| Champ | Contenu |
| --- | --- |
| `id` | Identifiant unique, sans espace ni accent (`dupont`). Il forme l'adresse `profil.html?id=dupont` |
| `exemple` | `false` pour un vrai profil |
| `titre`, `nom` | `"Dr"`, `"Jean Dupont"` |
| `grade`, `grade_detail` | Grade court (carte) et grade complet (profil) |
| `fonction`, `depuis` | Responsabilité éventuelle ; date d'arrivée (`"septembre 2015"`) ou `""` |
| `photo`, `photo_alt` | Nom du fichier dans `assets/img/enseignants/` et description ; `""` si pas de photo |
| `domaines` | Codes du filtre : `tice`, `logiciel`, `reseaux`, `ia`, `donnees` |
| `mots_cles_carte` | Trois mots-clés au plus, affichés sur la carte |
| `presentation` | Liste de paragraphes |
| `enseignements`, `recherche` | Listes de textes |
| `publications` | Liste d'objets `auteurs`, `titre`, `source`, `annee`, `lien` |
| `contacts` | `courriel`, `telephone`, `adresse`, `bureau` (`""` si inconnu : « À compléter » s'affiche) |
| `liens` | `site`, `linkedin`, `scholar`, `orcid`, `researchgate`, `github`, `dblp` : une icône n'apparaît que si le lien est rempli |
| `source` | Adresse d'où viennent les informations, ou `""` |

3. Supprimez un bloc d'exemple (`"exemple": true`) chaque fois qu'un vrai profil le remplace.
4. Dans `pages/recherche.html`, ajoutez le nom de l'enseignant dans ses domaines, avec le lien `profil.html?id=dupont`.
5. Vérifiez : `python outils/verifier_liens.py` signale un JSON mal écrit (virgule en trop, guillemet oublié), un identifiant en double, une photo introuvable ou un lien vers un profil inexistant. Ouvrez ensuite `pages/enseignants.html` et la nouvelle fiche dans le navigateur.

La publication d'une photo ou d'un numéro de téléphone demande l'accord écrit de l'enseignant.

## 5. Ajouter une actualité

1. Dans le dossier `pages/`, copiez `actualite.html` (article simple) ou `actualite-concours-2026.html` (article avec tableau et captures) sous un nouveau nom, sans espace ni accent (par exemple `pages/actualite-soutenances-2027.html`).
2. Dans la copie, modifiez le `<title>`, la `meta description`, le fil d'Ariane, le titre `<h1>`, la catégorie, la date (`<time datetime="2027-06-15">15 juin 2027</time>`), le texte et les pièces jointes.
3. Pour l'image de l'article : convertissez-la avec
   `python outils/convertir_image.py photo.jpg assets/img/actualites/nom.webp --format 16:9 --largeur 960 --max-ko 150`,
   puis remplacez le bloc `<div class="emplacement-image …">…</div>` par
   `<img class="img-fluid rounded-3 mb-4" src="../assets/img/actualites/nom.webp" width="960" height="540" alt="Description de l'image">`.
   Pour la capture d'un document officiel (arrêté, communiqué), enregistrez une image de la première page, convertissez-la de la même façon avec `--format 3:4 --largeur 760`, et faites-en un lien vers le PDF officiel.
4. Dans `pages/actualites.html`, copiez une carte (le bloc `<div class="col-md-6 col-lg-4" data-domaines="…">`), placez-la en premier, et modifiez le titre, la date, le résumé et le lien. La valeur de `data-domaines` est la catégorie : `annonce`, `concours`, `auditeurs`, `evenement`, `soutenance` ou `vie`.
5. Sur l'accueil (`index.html`), la section « Dernières actualités » montre les trois articles les plus récents : remplacez la carte la plus ancienne par la nouvelle. Depuis l'accueil, liens et images s'écrivent `pages/actualite-….html` et `assets/img/…` (sans `../`).
6. Le badge « Nouveau » (`<span class="badge-nouveau">Nouveau</span>`) se place sur l'article le plus récent ; retirez-le des anciens.
7. Supprimez les cartes marquées « Exemple » dès que de vrais articles sont publiés.

Au-delà de neuf articles, créez `pages/actualites-2.html` (copie de `actualites.html` avec les articles plus anciens) et activez les liens « Suivant » et « Précédent » de la pagination.

## 6. Ajouter un document à télécharger

1. Placez le fichier PDF dans `assets/docs/`, avec un nom sans espace ni accent (par exemple `calendrier-2026-2027.pdf`).
2. Dans `pages/etudiants.html`, section « Documents à télécharger », remplacez la ligne concernée par :
   ```html
   <li class="list-group-item">
     <i class="bi bi-file-earmark-pdf" aria-hidden="true"></i>
     <div><a href="../assets/docs/calendrier-2026-2027.pdf">Calendrier académique 2026-2027</a><div class="meta">PDF, 240 Ko</div></div>
   </li>
   ```
   Indiquez toujours le format et la taille réelle du fichier (clic droit, Propriétés).

## 7. Mettre à jour un emploi du temps

1. Enregistrez le PDF dans `assets/docs/`, par exemple `edt-niveau-1.pdf`. Gardez le même nom d'une version à l'autre : les liens restent valables.
2. Dans `pages/etudiants.html`, repérez l'onglet du niveau (`id="edt-n1"` pour le niveau 1, jusqu'à `edt-n5`) et remplacez ses deux paragraphes par :
   ```html
   <p class="mb-2"><a class="btn btn-primary" href="../assets/docs/edt-niveau-1.pdf"><i class="bi bi-file-earmark-pdf" aria-hidden="true"></i> Emploi du temps du niveau 1 (PDF, 180 Ko)</a></p>
   <p class="text-secondary small mb-0">Mis à jour le 5 janvier 2027</p>
   ```
3. Pour annoncer la mise à jour, modifiez le message jaune en haut de la page et retirez l'étiquette « Exemple d'annonce ».

## 8. Modifier le menu ou le pied de page

Le menu et le pied de page sont recopiés dans toutes les pages. Deux méthodes :

- **Avec Python (recommandé)** : modifiez `outils/gabarit/entete.html` ou `outils/gabarit/pied.html`, puis lancez depuis le dossier du site :
  ```
  python outils/synchroniser_gabarit.py
  ```
  Le script recopie le modèle dans toutes les pages (racine et `pages/`), remplace `{{racine}}` et `{{pages}}` par les bons chemins, et marque la rubrique active grâce à l'attribut `data-page` de la balise `<body>`.
- **À la main** : faites la même modification dans tous les fichiers HTML, en adaptant les chemins (`../` dans `pages/`), entre les commentaires `<!-- ENTETE -->` et `<!-- /ENTETE -->` (ou `<!-- PIED -->` et `<!-- /PIED -->`).

Pour retirer le bandeau « Version de travail » une fois les contenus validés, supprimez le bloc `<div class="bandeau-travail">…</div>` du modèle d'en-tête, puis synchronisez.

## 9. Activer le formulaire de contact

Le formulaire de `pages/contact.html` n'envoie rien pour l'instant : il affiche un message et l'adresse électronique. Pour l'activer avec Formspree (offre gratuite limitée) :

1. Créez un compte sur formspree.io avec l'adresse du secrétariat, puis un formulaire. Formspree donne une adresse du type `https://formspree.io/f/abcdwxyz`.
2. Dans `pages/contact.html`, sur la balise `<form>` :
   - ajoutez `action="https://formspree.io/f/abcdwxyz"` ;
   - supprimez l'attribut `data-formulaire-demo`.
3. Supprimez le bloc `<div class="alert alert-info" … data-message-demo hidden>…</div>`.
4. Faites un envoi d'essai et confirmez l'adresse dans le courriel reçu de Formspree.

## 10. Couleurs et styles

Les couleurs de la charte sont définies au début de `assets/css/style.css` (variables `--dite-…`). Ébène `#1E1A17`, latérite `#A63D24`, latérite foncée `#852F1A`, ocre `#E8B04B`, sable `#F6F1EA`, anthracite `#212529`, brun gris `#6B5E55`. L'ocre ne s'utilise jamais comme couleur de texte sur fond blanc.

## 11. Vérifier le site avant publication

Ces scripts demandent Python 3 (et Pillow pour les deux derniers). Lancez-les depuis le dossier du site.

| Commande | Rôle |
| --- | --- |
| `python outils/verifier_liens.py` | Liens internes, ancres, images et fichiers manquants, fichier des enseignants |
| `python outils/valider_html.py` | Validation de chaque page par le service du W3C (connexion Internet nécessaire) |
| `python outils/audit.py` | Poids des pages, images, `alt`, `lang`, titres, ressources externes, emojis, contrastes |
| `python outils/captures.py` | Captures d'écran à 390, 768 et 1280 px dans `docs/captures/` (Chrome nécessaire) |

Pour les scores Lighthouse : ouvrez la page dans Chrome, touche F12, onglet Lighthouse, mode « Mobile », catégories Performance, Accessibilité, Bonnes pratiques et SEO. Objectifs : Performance 90 ou plus, les trois autres 95 ou plus. Pour un résultat fiable, auditez le site publié (ou servi par `python -m http.server 8000` puis `http://localhost:8000`), pas le fichier ouvert directement.

## 12. Publier

### GitHub Pages

1. Créez un dépôt sur GitHub (par exemple `site-dite`) et envoyez-y ce dossier :
   ```
   git remote add origin https://github.com/COMPTE/site-dite.git
   git push -u origin main
   ```
2. Sur GitHub : Settings, Pages, « Deploy from a branch », branche `main`, dossier `/ (root)`, Save.
3. Le site est en ligne après une ou deux minutes à l'adresse `https://COMPTE.github.io/site-dite/`.
4. Ensuite, chaque modification se publie par `git add -A`, `git commit -m "Description"` et `git push`.

Le fichier `.nojekyll` empêche GitHub de transformer les fichiers. La page `404.html` est utilisée automatiquement pour les adresses inexistantes.

### Netlify (autre possibilité)

Sur app.netlify.com, « Add new site », puis « Deploy manually » : glissez-déposez le dossier `site-dite`. Aucun réglage de compilation n'est nécessaire.

### Serveur de l'université

Copiez tout le contenu du dossier (sauf `.git/`, `outils/` et `docs/captures/`, facultatifs) à la racine du site sur le serveur.

## 13. Crédits

- Bootstrap 5.3.3 et Bootstrap Icons 1.11.3 : licence MIT (fichiers `LICENSE` dans `lib/`).
- Polices Montserrat et Source Sans 3 : licence SIL Open Font License 1.1 (`assets/fonts/LICENCES.txt`).
- Icônes ORCID, ResearchGate et Google Scholar : Simple Icons, licence CC0 (`assets/img/icons/LICENCE.txt`).
- Logo, emblème, fresque et bandeau : ENS de Yaoundé, réutilisation soumise à l'accord de la direction.
