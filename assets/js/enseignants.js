/*
 * Site du DITE : affichage des enseignants a partir de assets/data/enseignants.js.
 *
 * - pages/enseignants.html : construit une carte par enseignant dans #liste-enseignants.
 * - pages/profil.html?id=xxx : remplit la page de profil de l'enseignant dont l'id vaut xxx.
 *
 * Les donnees ne sont jamais inserees comme du HTML (textContent uniquement).
 * A charger apres assets/data/enseignants.js ; main.js applique ensuite les filtres.
 */
(function () {
  'use strict';

  var DONNEES = window.DITE_ENSEIGNANTS || [];
  var IMG = '../assets/img/';

  var LIENS = [
    { cle: 'courriel', libelle: 'Courriel', icone: 'bi-envelope', prefixe: 'mailto:' },
    { cle: 'telephone', libelle: 'Téléphone', icone: 'bi-telephone', prefixe: 'tel:' },
    { cle: 'site', libelle: 'Site web personnel', icone: 'bi-globe2' },
    { cle: 'linkedin', libelle: 'Profil LinkedIn', icone: 'bi-linkedin' },
    { cle: 'scholar', libelle: 'Profil Google Scholar', image: 'icons/googlescholar.svg' },
    { cle: 'orcid', libelle: 'Profil ORCID', image: 'icons/orcid.svg' },
    { cle: 'researchgate', libelle: 'Profil ResearchGate', image: 'icons/researchgate.svg' },
    { cle: 'github', libelle: 'Profil GitHub', icone: 'bi-github' }
  ];

  /* Cree un element : el('p', {className: 'x'}, ['texte', autreElement]) */
  function el(tag, props, enfants) {
    var n = document.createElement(tag);
    Object.keys(props || {}).forEach(function (k) {
      if (k === 'className' || k === 'textContent' || k === 'href' || k === 'src' || k === 'alt' || k === 'id') {
        n[k] = props[k];
      } else {
        n.setAttribute(k, props[k]);
      }
    });
    (enfants || []).forEach(function (e) {
      if (e === null || e === undefined) { return; }
      n.appendChild(typeof e === 'string' ? document.createTextNode(e) : e);
    });
    return n;
  }

  function icone(nom) { return el('i', { className: 'bi ' + nom, 'aria-hidden': 'true' }); }
  function nomComplet(p) { return (p.titre ? p.titre + ' ' : '') + p.nom; }
  function aCompleter(texte) { return el('p', { className: 'a-completer' }, [texte || 'À compléter']); }

  function photo(p, classe) {
    if (p.photo) {
      return el('img', { className: classe || 'photo', src: IMG + 'enseignants/' + p.photo, width: '480', height: '360', alt: p.photo_alt || 'Portrait de ' + p.nom });
    }
    return el('div', { className: 'photo-vide' }, [icone('bi-person-fill'), el('span', {}, ['Photo, format 4:3'])]);
  }

  function badgeExemple() {
    return el('p', { className: 'mb-2' }, [el('span', { className: 'badge-exemple' }, ["Profil d'exemple"])]);
  }

  /* ---------- Cartes de la page Enseignants ---------- */
  function cartes(conteneur) {
    conteneur.textContent = '';
    DONNEES.forEach(function (p) {
      var tags = el('ul', { className: 'tags mb-3' }, (p.mots_cles_carte || []).slice(0, 3).map(function (m) {
        return el('li', { className: 'tag tag-recherche' }, [m]);
      }));
      var corps = el('div', { className: 'card-body p-3 d-flex flex-column' }, [
        p.exemple ? badgeExemple() : null,
        el('h3', { className: 'h5 mb-1' }, [el('a', { className: 'stretched-link', href: 'profil.html?id=' + encodeURIComponent(p.id) }, [nomComplet(p)])]),
        el('p', { className: 'grade small mb-2' }, [p.grade]),
        tags,
        el('span', { className: 'lien-fleche mt-auto' }, ['Voir le profil ', icone('bi-arrow-right')])
      ]);
      var carte = el('article', { className: 'card carte-enseignant carte-compacte card-lien h-100', id: p.id }, [photo(p), corps]);
      conteneur.appendChild(el('div', { className: 'col-sm-6 col-lg-4 col-xl-3', 'data-domaines': (p.domaines || []).join(' ') }, [carte]));
    });
    var compteur = document.querySelector('[data-filtre-compteur="' + conteneur.id + '"]');
    if (compteur) { compteur.textContent = DONNEES.length + ' profils affichés'; }
  }

  /* ---------- Page de profil ---------- */
  function section(titre, contenu, premier) {
    return [el('h2', { className: 'titre-section' + (premier ? '' : ' mt-5') }, [titre])].concat(contenu);
  }

  function listeTags(valeurs, classe) {
    if (!valeurs || !valeurs.length) { return aCompleter(); }
    return el('ul', { className: 'tags mb-3' }, valeurs.map(function (v) { return el('li', { className: 'tag ' + classe }, [v]); }));
  }

  function profil(racine, p) {
    var liens = p.liens || {};
    var contacts = p.contacts || {};
    var valeurs = { courriel: contacts.courriel, telephone: contacts.telephone };
    Object.keys(liens).forEach(function (k) { valeurs[k] = liens[k]; });

    document.title = nomComplet(p) + ' | Enseignants du DITE, ENS Yaoundé';
    var meta = document.querySelector('meta[name="description"]');
    if (meta) { meta.setAttribute('content', 'Profil de ' + p.nom + ', ' + p.grade.toLowerCase() + ' au DITE de l\'ENS de Yaoundé : parcours, enseignements, recherche, publications et contacts.'); }
    document.getElementById('profil-fil').textContent = p.nom;
    document.getElementById('profil-titre').textContent = nomComplet(p);
    document.getElementById('profil-sous-titre').textContent = p.grade_detail + (p.depuis ? ' · au DITE depuis ' + p.depuis : '');

    /* Colonne de gauche : photo, liens, contacts */
    var icones = el('ul', { className: 'icones-contact' }, LIENS.filter(function (l) { return valeurs[l.cle]; }).map(function (l) {
      var cible = l.prefixe ? l.prefixe + valeurs[l.cle].replace(/\s/g, '') : valeurs[l.cle];
      var contenu = l.image ? el('img', { src: IMG + l.image, width: '17', height: '17', alt: '' }) : icone(l.icone);
      return el('li', {}, [el('a', { className: 'btn-icone', href: cible, 'aria-label': l.libelle }, [contenu])]);
    }));
    var dl = el('dl', { className: 'profil-contacts mb-0' });
    function ligne(terme, valeur, lien) {
      dl.appendChild(el('dt', {}, [terme]));
      dl.appendChild(valeur ? el('dd', {}, [lien ? el('a', { href: lien }, [valeur]) : valeur]) : el('dd', { className: 'a-completer' }, ['À compléter']));
    }
    ligne('Courriel', contacts.courriel, contacts.courriel ? 'mailto:' + contacts.courriel : '');
    ligne('Téléphone', contacts.telephone, contacts.telephone ? 'tel:' + contacts.telephone.replace(/\s/g, '') : '');
    ligne('Adresse', contacts.adresse);
    ligne('Bureau et réception', contacts.bureau);
    if (liens.orcid) { ligne('ORCID', liens.orcid.replace('https://orcid.org/', ''), liens.orcid); }
    if (liens.dblp) { ligne('DBLP', liens.dblp.replace('https://', '').replace('.html', ''), liens.dblp); }

    var aside = el('aside', { className: 'col-lg-4', 'aria-labelledby': 'titre-contacts' }, [
      el('div', { className: 'card carte-enseignant profil-aside' }, [
        photo(p),
        el('div', { className: 'card-body p-4' }, [
          p.fonction ? el('p', { className: 'fonction' }, [p.fonction]) : null,
          icones.childNodes.length ? icones : null,
          el('h2', { className: 'h5', id: 'titre-contacts' }, ['Contacts']),
          dl
        ])
      ])
    ]);

    /* Colonne principale */
    var pubs = (p.publications || []).length ? el('ol', { className: 'publications ps-3' }, p.publications.map(function (pub) {
      return el('li', {}, [
        pub.auteurs + ', « ' + pub.titre + ' », ',
        el('em', {}, [pub.source]),
        ', ' + pub.annee + '. ',
        pub.lien ? el('a', { href: pub.lien }, [pub.lien.replace('https://doi.org/', 'doi:')]) : null
      ]);
    })) : aCompleter('Trois à cinq publications ou projets, avec lien.');

    var principal = el('div', { className: 'col-lg-8' }, [].concat(
      section('Présentation', (p.presentation || []).length ? p.presentation.map(function (t) { return el('p', {}, [t]); }) : [aCompleter('Trois à cinq phrases sur le parcours et les travaux en cours, validées par l\'enseignant.')], true),
      section('Enseignements à l\'ENS', [listeTags(p.enseignements, 'tag-enseigne')]),
      section('Domaines de recherche', [listeTags(p.recherche, 'tag-recherche'),
        el('p', {}, [el('a', { className: 'lien-fleche', href: 'recherche.html#domaines' }, ['Les domaines de recherche du département ', icone('bi-arrow-right')])])]),
      section('Publications récentes', [pubs,
        p.note_publications ? el('p', { className: 'small text-secondary' }, [p.note_publications]) : null]),
      p.source ? [el('p', { className: 'sources' }, ['Source : ', el('a', { href: p.source }, ['page personnelle de l\'enseignant']), '. Profil à faire valider par l\'intéressé.'])] : [],
      [el('p', { className: 'mt-4 mb-0' }, [el('a', { className: 'btn btn-outline-primary', href: 'enseignants.html' }, [icone('bi-arrow-left'), ' Tous les enseignants'])])]
    ));

    racine.textContent = '';
    if (p.exemple) {
      racine.appendChild(el('div', { className: 'alert alert-warning', role: 'note' }, [
        el('span', { className: 'badge-exemple me-1' }, ["Profil d'exemple"]),
        ' Ce profil montre la mise en page ; il sera remplacé par les informations fournies par l\'enseignant.'
      ]));
    }
    racine.appendChild(el('div', { className: 'row g-4 g-lg-5' }, [aside, principal]));
  }

  function introuvable(racine) {
    document.title = 'Profil introuvable | Enseignants du DITE, ENS Yaoundé';
    document.getElementById('profil-titre').textContent = 'Profil introuvable';
    document.getElementById('profil-fil').textContent = 'Profil introuvable';
    document.getElementById('profil-sous-titre').textContent = "Aucun enseignant ne correspond à cette adresse.";
    racine.textContent = '';
    racine.appendChild(el('p', {}, ['Ce profil n\'existe pas ou a été retiré. ',
      el('a', { href: 'enseignants.html' }, ['Voir la liste des enseignants']), '.']));
  }

  var liste = document.getElementById('liste-enseignants');
  if (liste) { cartes(liste); }

  var racine = document.getElementById('profil');
  if (racine) {
    var id = new URLSearchParams(window.location.search).get('id');
    var trouve = DONNEES.filter(function (p) { return p.id === id; })[0];
    if (trouve) { profil(racine, trouve); } else { introuvable(racine); }
  }
})();
