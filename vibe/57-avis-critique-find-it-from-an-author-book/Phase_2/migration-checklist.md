# Migration Checklist - Accès aux avis critiques par livre/auteur

## Phase préparatoire

- [ ] **Backup du code actuel**
  - [ ] Commit des changements en cours
  - [ ] Tag de la version actuelle : `git tag v-before-search-feature`
  - [ ] Backup de la base MongoDB : `mongodump --db lmelp --out backup/`
  - [ ] Sauvegarde des fichiers audio importants

- [ ] **Environnement de développement**
  - [ ] Branch de feature créée : `57-avis-critique-find-it-from-an-author-book`
  - [ ] Environnement de test MongoDB séparé configuré
  - [ ] Dépendances Python à jour (`pip install -r requirements.txt`)
  - [ ] Tests existants passent : `python -m pytest` (si applicable)

## Phase 1 : Infrastructure des données

- [ ] **Création du parser d'avis critiques**
  - [ ] Module `nbs/avis_critiques_parser.py` créé
  - [ ] Classe `AvisCritiquesParser` implémentée
  - [ ] Tests unitaires `tests/test_avis_parser.py` créés et passent
  - [ ] Validation sur échantillon de 10 avis critiques
  - [ ] Gestion des cas d'erreur testée

- [ ] **Classe EpisodeLivre**
  - [ ] Module `nbs/mongo_episode_livre.py` créé
  - [ ] Classe hérite correctement de `BaseEntity`
  - [ ] Collection `episode_livres` testée en environnement dev
  - [ ] Tests unitaires `tests/test_episode_livre.py` passent
  - [ ] Intégration avec collections existantes validée

- [ ] **Moteur de recherche**
  - [ ] Module `nbs/avis_search.py` créé
  - [ ] Recherche fuzzy fonctionnelle avec `thefuzz`
  - [ ] Performance < 1 seconde sur jeu de test
  - [ ] Cache Streamlit configuré
  - [ ] Tests unitaires `tests/test_avis_search.py` passent

- [ ] **Script de migration**
  - [ ] Script `scripts/migrate_avis_to_episode_livres.py` créé
  - [ ] Test sur 50 épisodes en environnement de développement
  - [ ] Validation manuelle sur 10 entrées générées
  - [ ] Mode dry-run fonctionnel
  - [ ] Logs et reporting opérationnels

## Phase 2 : Interface utilisateur

- [ ] **Refactorisation page avis critiques**
  - [ ] Backup du fichier original `ui/pages/4_avis_critiques.py`
  - [ ] Code existant encapsulé dans `display_episode_view()` SANS modification
  - [ ] Onglets Streamlit ajoutés
  - [ ] Tests de non-régression sur onglet "Par Épisode" passent :
    - [ ] Navigation avec sélecteur fonctionne
    - [ ] Raccourcis clavier ← → préservés
    - [ ] Génération de résumés identique
    - [ ] Indicateurs 🟢⚪ corrects
    - [ ] Performance identique

- [ ] **Composant d'autocomplétion**
  - [ ] Module `ui/components/book_autocomplete.py` créé
  - [ ] Autocomplétion réactive < 1 seconde
  - [ ] Format "Auteur - Titre" correct
  - [ ] Gestion des cas sans résultat
  - [ ] Intégration Streamlit fonctionnelle

- [ ] **Interface de recherche**
  - [ ] Onglet "Par Livre/Auteur" fonctionnel
  - [ ] Recherche par auteur : "tolkien" → suggestions
  - [ ] Recherche par titre : "seigneur" → "Le Seigneur des Anneaux"
  - [ ] Affichage chronologique des résultats correct
  - [ ] Navigation vers épisode complet fonctionne

## Phase 3 : Déploiement et optimisation

- [ ] **Index MongoDB**
  - [ ] Script `scripts/create_mongodb_indexes.py` créé et testé
  - [ ] Index textuels créés sur production
  - [ ] Index chronologiques créés
  - [ ] Performance de recherche validée < 1 seconde
  - [ ] Impact sur autres requêtes évalué

- [ ] **Migration complète des données**
  - [ ] Backup complet avant migration
  - [ ] Migration des 300 épisodes sur production
  - [ ] Validation qualité sur échantillon 5%
  - [ ] Vérification cohérence données
  - [ ] Monitoring erreurs pendant 24h

- [ ] **Tests de charge**
  - [ ] 100 recherches simultanées testées
  - [ ] Performance interface existante inchangée
  - [ ] Pas de régression détectée
  - [ ] Monitoring ressources système OK

## Phase 4 : Finalisation

- [ ] **Tests utilisateur**
  - [ ] Interface intuitive validée par 3 utilisateurs test
  - [ ] Cas d'usage principaux testés
  - [ ] Feedback collecté et traité
  - [ ] Corrections mineures apportées si nécessaire

- [ ] **Documentation**
  - [ ] Documentation utilisateur `docs/recherche_avis.md` créée
  - [ ] README principal mis à jour
  - [ ] Docstrings complètes dans nouveaux modules
  - [ ] Guide de maintenance créé

- [ ] **Code review**
  - [ ] Review complète du code par pairs
  - [ ] Patterns et conventions respectés
  - [ ] Sécurité et performance validées
  - [ ] Commentaires de review traités

- [ ] **Intégration continue**
  - [ ] Tests automatisés passent
  - [ ] Linting et formatage OK
  - [ ] Documentation générée sans erreur
  - [ ] Build de l'application réussit

## Phase 5 : Déploiement final

- [ ] **Préparation production**
  - [ ] Backup final avant déploiement
  - [ ] Plan de rollback documenté et testé
  - [ ] Monitoring alertes configurées
  - [ ] Communication aux utilisateurs préparée

- [ ] **Déploiement**
  - [ ] Code déployé sur production
  - [ ] Migration données finalisée
  - [ ] Tests de fumée passent
  - [ ] Fonctionnalité accessible aux utilisateurs

- [ ] **Post-déploiement**
  - [ ] Monitoring 48h sans problème
  - [ ] Métriques d'utilisation collectées
  - [ ] Performance maintenue
  - [ ] Aucune régression détectée

## Phase 6 : Maintenance et amélioration

- [ ] **Intégration dans workflow**
  - [ ] Processus création futurs avis critiques adapté
  - [ ] Documentation maintenance à jour
  - [ ] Formation équipe sur nouvelle fonctionnalité
  - [ ] Procédures de support utilisateur

- [ ] **Améliorations futures planifiées**
  - [ ] Analytics d'utilisation configurées
  - [ ] Roadmap améliorations documentée
  - [ ] Optimisations basées sur usage réel
  - [ ] Feedback utilisateurs intégré

## Critères de succès

### Fonctionnels
- [ ] Recherche par auteur et titre fonctionne
- [ ] Autocomplétion < 1 seconde
- [ ] Affichage chronologique correct
- [ ] Aucune régression sur interface existante

### Non-fonctionnels
- [ ] Performance générale maintenue
- [ ] Qualité des données préservée
- [ ] Code maintenable et documenté
- [ ] Architecture extensible

### Utilisateur
- [ ] Interface intuitive et utilisable
- [ ] Valeur ajoutée mesurable
- [ ] Feedback utilisateur positif
- [ ] Adoption de la fonctionnalité

## Stratégies de rollback

### Rollback rapide (< 1 heure)
- [ ] **Interface** : `git revert` vers version précédente
- [ ] **Données** : Désactivation onglet recherche via feature flag
- [ ] **MongoDB** : Suppression collection `episode_livres`

### Rollback complet (< 4 heures)
- [ ] **Code** : Retour version taguée `v-before-search-feature`
- [ ] **Base** : Restauration backup MongoDB complet
- [ ] **Index** : Suppression index créés
- [ ] **Tests** : Validation fonctionnement interface originale

### Points de non-retour
- [ ] Migration données > 80% : continuer avec corrections
- [ ] Régression majeure détectée : rollback immédiat
- [ ] Performance < 50% : rollback puis investigation
