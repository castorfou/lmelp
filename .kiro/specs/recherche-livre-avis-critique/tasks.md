# Implementation Plan

- [ ] 1. Créer le parser d'avis critiques
  - Implémenter la classe `AvisCritiquesParser` pour extraire les livres des résumés markdown
  - Créer les méthodes de parsing des tableaux avec gestion des notes colorées
  - Ajouter la validation et la gestion d'erreurs pour les formats inattendus
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 2. Implémenter les tests unitaires du parser
  - Créer `tests/test_avis_critiques_parser.py` avec cas de test complets
  - Tester l'extraction avec des résumés valides et malformés
  - Valider la robustesse du parsing des notes et commentaires
  - _Requirements: 4.4_

- [ ] 3. Créer la classe EpisodeLivre pour la gestion des relations
  - Implémenter `EpisodeLivre` héritant de `BaseEntity`
  - Ajouter les méthodes de recherche par livre et par auteur
  - Créer les méthodes d'agrégation pour récupérer tous les livres uniques
  - _Requirements: 5.1, 5.2_

- [ ] 4. Implémenter les tests unitaires d'EpisodeLivre
  - Créer `tests/test_episode_livre.py` avec tests CRUD complets
  - Tester les méthodes de recherche et d'agrégation
  - Valider l'intégration avec MongoDB et les relations ObjectId
  - _Requirements: 5.3_

- [ ] 5. Développer le moteur de recherche AvisSearchEngine
  - Implémenter la classe `AvisSearchEngine` avec recherche floue
  - Créer les méthodes de filtrage similaires à la page auteurs
  - Ajouter la mise en cache Streamlit pour optimiser les performances
  - _Requirements: 2.1, 2.2, 2.3, 7.1, 7.3_

- [ ] 6. Implémenter les tests du moteur de recherche
  - Créer `tests/test_avis_search.py` avec tests de recherche floue
  - Tester les performances avec un grand nombre de livres
  - Valider le filtrage en temps réel et la mise en évidence du texte
  - _Requirements: 7.2, 7.4_

- [ ] 7. Créer le script de migration des avis existants
  - Développer `scripts/migrate_avis_to_episode_livres.py`
  - Implémenter la logique de traitement batch avec gestion d'erreurs
  - Ajouter le logging détaillé et le rapport de migration
  - _Requirements: 5.1, 5.2, 5.4_

- [ ] 8. Tester et valider la migration des données
  - Exécuter la migration sur un échantillon de données de test
  - Valider l'intégrité des données migrées
  - Créer les tests d'intégration pour le processus de migration
  - _Requirements: 5.3, 5.4_

- [ ] 9. Créer les index MongoDB optimisés
  - Développer `scripts/create_mongodb_indexes.py`
  - Implémenter les index composés pour les recherches par livre/auteur
  - Ajouter l'index de recherche textuelle pour la recherche floue
  - _Requirements: 7.1, 7.3_

- [ ] 10. Refactoriser la page avis critiques avec options radio
  - Modifier `ui/pages/4_avis_critiques.py` pour ajouter les options de navigation
  - Encapsuler le code existant dans `afficher_selection_episode()` sans modification
  - Implémenter la structure avec options radio horizontales
  - _Requirements: 1.1, 1.2, 1.4, 6.1, 6.2_

- [ ] 11. Implémenter l'interface de recherche par livre
  - Créer la fonction `afficher_recherche_livre()` avec filtrage en temps réel
  - Implémenter le champ de filtre similaire à la page auteurs
  - Ajouter la mise en évidence du texte correspondant au filtre
  - _Requirements: 1.3, 2.1, 2.2, 2.3, 2.4_

- [ ] 12. Développer l'affichage des avis critiques pour un livre
  - Créer la fonction `afficher_avis_pour_livre()` avec métadonnées d'épisode
  - Implémenter l'affichage des avis multiples si plusieurs épisodes mentionnent le livre
  - Ajouter les liens vers les épisodes complets
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 13. Intégrer l'extraction automatique dans la génération d'avis
  - Modifier la fonction de sauvegarde d'avis pour déclencher l'extraction
  - Intégrer `AvisCritiquesParser` dans le workflow existant
  - Assurer la compatibilité avec le processus de génération/régénération
  - _Requirements: 4.1, 4.4_

- [ ] 14. Créer les tests de régression pour l'interface utilisateur
  - Développer `tests/test_ui_regression.py`
  - Valider que le mode "Par Épisode" fonctionne exactement comme avant
  - Tester la navigation, les boutons et les raccourcis clavier
  - _Requirements: 6.2, 6.3, 6.4_

- [ ] 15. Implémenter les tests d'intégration end-to-end
  - Créer `tests/test_integration_livre_search.py`
  - Tester le workflow complet : génération d'avis → extraction → recherche
  - Valider l'intégration entre tous les composants
  - _Requirements: 1.4, 2.4, 3.4_

- [ ] 16. Optimiser les performances et finaliser
  - Profiler les requêtes MongoDB et optimiser si nécessaire
  - Valider les temps de réponse selon les critères de performance
  - Ajouter la gestion des cas d'erreur dans l'interface utilisateur
  - _Requirements: 7.1, 7.2, 7.4_