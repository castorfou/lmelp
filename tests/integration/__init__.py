"""
Package pour les tests d'intégration du projet LMELP.

Ce package contient les tests qui vérifient l'interaction entre plusieurs modules
du projet, contrairement aux tests unitaires qui testent les modules en isolation.

Workflows testés :
- RSS parsing → MongoDB storage → LLM analysis
- Configuration → Base de données → Processing
- End-to-end scenarios complets

Les tests d'intégration utilisent des données réelles ou semi-réelles
pour valider que l'ensemble du système fonctionne correctement.
"""
