/*
 * Site du DITE, ENS de Yaounde : scripts du site (JavaScript sans bibliotheque).
 *
 * 1. Filtres par categorie (enseignants, actualites)
 * 2. Libelles des tableaux sur mobile
 * 3. Formulaires : validation Bootstrap et blocage de l'envoi des formulaires de demonstration
 */
(function () {
  'use strict';

  /* 1. Filtres ------------------------------------------------------------
   * Groupe de boutons : <div data-filtre-groupe="id-de-la-liste">
   *   <button data-filtre="tous">Tous</button> <button data-filtre="ia">...</button>
   * Elements filtres : enfants de #id-de-la-liste portant data-domaines="ia donnees"
   * Compteur facultatif : <p data-filtre-compteur="id-de-la-liste"
   *   data-singulier="enseignant" data-pluriel="enseignants"></p>
   */
  document.querySelectorAll('[data-filtre-groupe]').forEach(function (groupe) {
    var liste = document.getElementById(groupe.getAttribute('data-filtre-groupe'));
    if (!liste) { return; }
    var elements = liste.querySelectorAll('[data-domaines]');
    var boutons = groupe.querySelectorAll('[data-filtre]');
    var compteur = document.querySelector('[data-filtre-compteur="' + liste.id + '"]');
    var aucun = document.querySelector('[data-filtre-aucun="' + liste.id + '"]');

    function appliquer(valeur) {
      var visibles = 0;
      elements.forEach(function (el) {
        var domaines = (el.getAttribute('data-domaines') || '').split(/\s+/);
        var visible = valeur === 'tous' || domaines.indexOf(valeur) !== -1;
        el.hidden = !visible;
        if (visible) { visibles += 1; }
      });
      boutons.forEach(function (b) {
        var actif = b.getAttribute('data-filtre') === valeur;
        b.classList.toggle('active', actif);
        b.setAttribute('aria-pressed', actif ? 'true' : 'false');
      });
      if (compteur) {
        var mot = visibles > 1 ? compteur.getAttribute('data-pluriel') : compteur.getAttribute('data-singulier');
        compteur.textContent = visibles + ' ' + mot;
      }
      if (aucun) { aucun.hidden = visibles !== 0; }
    }

    boutons.forEach(function (b) {
      b.addEventListener('click', function () { appliquer(b.getAttribute('data-filtre')); });
    });
    appliquer('tous');
  });

  /* 2. Libelles des tableaux sur mobile -----------------------------------
   * Pour chaque tableau .table-cartes, recopie l'en-tete de colonne dans
   * l'attribut data-label de chaque cellule ; la feuille de style l'affiche
   * au-dessus de la valeur sur les petits ecrans.
   */
  document.querySelectorAll('table.table-cartes').forEach(function (table) {
    var entetes = [];
    table.querySelectorAll('thead th').forEach(function (th) { entetes.push(th.textContent.trim()); });
    table.querySelectorAll('tbody tr').forEach(function (tr) {
      Array.prototype.forEach.call(tr.children, function (cellule, i) {
        if (cellule.tagName === 'TD' && entetes[i] && !cellule.hasAttribute('data-label')) {
          cellule.setAttribute('data-label', entetes[i]);
        }
      });
    });
  });

  /* 3. Formulaires --------------------------------------------------------
   * .needs-validation : validation Bootstrap avant envoi.
   * data-formulaire-demo : l'envoi est bloque et un message s'affiche
   * (a retirer une fois le service de formulaires configure, voir README).
   */
  document.querySelectorAll('form.needs-validation, form[data-formulaire-demo]').forEach(function (form) {
    form.addEventListener('submit', function (event) {
      var demo = form.hasAttribute('data-formulaire-demo');
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
        form.classList.add('was-validated');
        var premier = form.querySelector(':invalid');
        if (premier) { premier.focus(); }
        return;
      }
      form.classList.add('was-validated');
      if (demo) {
        event.preventDefault();
        var message = form.querySelector('[data-message-demo]');
        if (message) {
          message.hidden = false;
          message.focus();
        }
      }
    });
  });
})();
