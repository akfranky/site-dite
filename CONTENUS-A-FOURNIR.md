# Contenus à fournir par le département

État au 27 novembre 2026. Sur le site, chaque élément manquant est signalé par la mention « à compléter » (classe `a-completer`) ou par l'étiquette « Exemple ». Cochez les lignes au fur et à mesure.

## 1. Validations et autorisations

- [ ] Accord de la direction de l'ENS pour réutiliser le logo, l'emblème, la photo de la fresque et le bandeau du département, repris du site www.ens-yde.cm.
- [ ] Logo de l'ENS en haute définition ou en vectoriel (SVG ou PDF), si possible avec une version monochrome blanche officielle (celle du pied de page est générée à partir de l'emblème).
- [ ] Relecture et validation de l'ensemble des textes par le département.
- [ ] Légende exacte des trois photos de bâtiment fournies (s'agit-il du bâtiment du DITE ? nom du bâtiment ?). Elles sont légendées pour l'instant « Un bâtiment de cours du campus de l'ENS de Yaoundé ». Deux personnes y apparaissent de loin : vérifier qu'elles ne s'opposent pas à la publication.

## 2. Le département (pages/departement.html)

- [ ] Confirmation du chef de département : le site de l'ENS affiche Pr Marcel Fouda Ndjodo, sur une page non datée.
- [ ] Photo du chef de département (portrait 4:3, fond neutre).
- [ ] Mot du chef de département, de 150 à 250 mots, rédigé ou validé par l'intéressé.
- [ ] Organisation : nom, fonction et contact institutionnel des responsables des niveaux 1 à 5 et du secrétariat.

## 3. Parcours et admission (pages/parcours.html)

- [ ] Texte officiel de la suspension du recrutement des auditeurs libres : lettre du ministre au directeur de l'ENS, citée par le Journal du Cameroun le 22 janvier 2026. Recherchée le 27 novembre 2026 : son texte intégral n'est publié ni sur le site du MINESUP ni sur celui de l'ENS.
- [ ] Texte officiel de la décision du Conseil d'administration du 4 septembre 2024 sur les frais des auditeurs libres (source actuelle : Cameroon Desks, source secondaire). Préciser si ces frais s'appliquent aux auditeurs recrutés avant cette décision (point non affiché faute de source).
- [ ] Auditeurs libres : public concerné, évaluations et stages, document délivré en fin de formation.
- [x] Arrêtés du concours 2025-2026 (n° 26/00038 et 26/00037/MINESUP du 13 janvier 2026) : trouvés sur le site du MINESUP, résumés et capturés dans `pages/actualite-concours-2026.html`.
- [ ] Confirmation que la filière « Mathématiques-Informatique » de ces arrêtés est bien celle qui alimente le DITE (les arrêtés ne nomment pas les départements).
- [ ] Arrêtés des concours suivants, dès leur parution.
- [ ] Frais universitaires des étudiants réguliers.
- [x] Liste des pièces du dossier : reprise de l'arrêté de 2026 (question fréquente n° 2).

## 4. Cursus et niveaux (pages/cursus.html)

- [ ] Programme officiel par niveau, du niveau 1 au niveau 5 : code, intitulé, crédits, semestre et ouverture aux auditeurs libres de chaque unité d'enseignement. Les quatre unités du niveau 1 sont des exemples de la maquette.
- [ ] Confirmation de la numérotation des niveaux (1 à 5) utilisée par la scolarité.
- [ ] Stages pratiques : niveaux concernés, périodes, durées, établissements d'accueil, modalités d'évaluation.

## 5. Enseignants (pages/enseignants.html)

- [ ] Liste complète des enseignants du département. Pour chacun : photo 4:3, grade, fonction, unités enseignées (avec le niveau), deux à quatre mots-clés de recherche, présentation de trois à cinq phrases, trois à cinq publications avec lien, mémoires encadrés, courriel institutionnel, téléphone (avec accord), bureau et horaires de réception, liens (site, LinkedIn, Google Scholar, ORCID, ResearchGate, GitHub).
- [ ] Accord écrit de chaque enseignant pour la publication de sa photo et de son téléphone.
- [ ] Dr Ing. Cédric Stéphane Koumetio Tekouabou : validation de son profil (repris de sa page personnelle), accord pour la photo et le numéro de téléphone, courriel institutionnel éventuel (le site affiche son adresse personnelle publiée sur sa page), bureau et horaires de réception.
- [ ] Personnel administratif et technique : noms, fonctions, contacts.
- [ ] Liste définitive des domaines du filtre (actuellement : Technologies éducatives, Génie logiciel, Réseaux et systèmes, Intelligence artificielle, Données).

Toutes ces informations se saisissent dans `assets/data/enseignants.js` (voir README, section 4). Les trois profils marqués `"exemple": true` sont à supprimer au fur et à mesure.

## 6. Recherche (pages/recherche.html)

- [ ] Description de chaque domaine de recherche (deux à trois phrases) et enseignants associés. Seuls les domaines du Dr Tekouabou sont renseignés.
- [ ] Mémoires soutenus : année, titre, auteur, encadreur, domaine.
- [ ] Publications des autres enseignants.
- [ ] Programme des séminaires.

## 7. Espace étudiants (pages/etudiants.html)

- [ ] Emplois du temps des niveaux 1 à 5 (PDF), avec leur date de mise à jour.
- [ ] Dates du calendrier académique : rentrée, examens des deux semestres, stages, soutenances.
- [ ] Ressources pédagogiques et plateformes utilisées.
- [ ] Documents PDF à télécharger (calendrier, programme, autres).

## 8. Actualités (pages/actualites.html, pages/actualite*.html, index.html)

- [ ] Premières actualités réelles du département, avec date et, si possible, photo. Les trois cartes « Exemple » sont à remplacer.
- [ ] Photos du département pour les articles : salles, cérémonies, soutenances (prises de vue sur place, pas de banque d'images).

## 9. Contact (pages/contact.html)

- [ ] Téléphone et courriel institutionnel du secrétariat du département.
- [ ] Horaires d'ouverture, bâtiment et bureau.
- [ ] Plan d'accès ou itinéraire sur le campus.
- [ ] Compte Formspree (ou service équivalent) au nom du secrétariat, pour activer le formulaire (voir README, section 9).

## 10. Mise en ligne

- [ ] Choix de l'hébergement : serveur de l'université, GitHub Pages ou Netlify.
- [ ] Adresse définitive du site (nom de domaine).
- [ ] Personne responsable des mises à jour.

## Ressources écartées

- `background.png` (fond du diaporama du site de l'ENS) : téléchargé mais non utilisé, car ses aplats bleu et violet sortent de la charte graphique.
- `dsc_3832-300x253-1.jpg` (photo de la page du département) : non reprise, 300 px de large seulement.
- Portrait du Dr Tekouabou : récupéré sur sa page personnelle, recadré en 4:3 sur fond sable (fond d'origine transparent).
