# Plan d'Implémentation - Avis Critiques par Livre/Auteur

## Vue d'ensemble
Ajouter une fonctionnalité de recherche par livre/auteur dans la page avis critiques existante, en utilisant des sous-onglets pour organiser les deux modes d'accès.

## Architecture de Données

### 1. Relation Livres-Épisodes
**Problème actuel** : Pas de lien direct entre livres et épisodes
**Solution proposée** : 
- Ajouter un champ `livres_discutes` dans la collection `episodes`
- Format : `livres_discutes: [ObjectId("livre1"), ObjectId("livre2"), ...]`

### 2. Index MongoDB
```javascript
// Index composé pour recherche efficace
db.episodes.createIndex({ "livres_discutes": 1, "date_publication": -1 })
db.livres.createIndex({ "nom": "text", "auteur": 1 })
db.auteurs.createIndex({ "nom": "text" })
```

### 3. Structure de données étendue
```python
# Episode avec livres
{
  "_id": ObjectId("..."),
  "titre": "Episode Title",
  "date_publication": "2025-01-15",
  "livres_discutes": [
    ObjectId("livre1_id"),
    ObjectId("livre2_id")
  ],
  # ... autres champs existants
}
```

## Interface Utilisateur

### 1. Structure en Onglets
```
📝 Avis Critiques
├── 📺 Par Épisode (existant, refactorisé)
└── 📚 Par Livre/Auteur (nouveau)
```

### 2. Sous-onglet "Par Livre/Auteur"
- **Recherche autocomplete** : combinant livres ET auteurs
- **Résultats en temps réel** à partir de 3 caractères
- **Affichage chronologique** des avis pour un livre donné
- **Navigation contextuelle** vers les épisodes

### 3. Workflow utilisateur
1. Utilisateur tape "Seigneur" → suggestions : "Le Seigneur des Anneaux", "Tolkien"
2. Clic sur résultat → liste chronologique des avis critiques
3. Chaque avis affiche : date épisode, extrait, lien vers épisode complet

## Implémentation Technique

### Phase 1 : Données et Relations (Semaine 1)
1. **Script de migration** pour analyser les transcriptions existantes et identifier les livres par épisode
2. **Nouveau module** `mongo_episode_livre.py` pour gérer les relations
3. **Index MongoDB** pour optimiser les performances

### Phase 2 : Interface (Semaine 2)  
1. **Refactorisation** de `4_avis_critiques.py` avec système d'onglets
2. **Nouveau composant** de recherche autocomplete unifiée
3. **Logique de recherche** combinant livres et auteurs

### Phase 3 : Optimisation (Semaine 3)
1. **Cache de recherche** pour améliorer les performances
2. **Pagination** pour les résultats nombreux
3. **Tests et affinements**

## Fichiers à Modifier/Créer

### Nouveaux Fichiers
- `nbs/mongo_episode_livre.py` : Gestion des relations livre-épisode
- `ui/components/search_livre_auteur.py` : Composant de recherche autocomplete

### Fichiers à Modifier
- `ui/pages/4_avis_critiques.py` : Ajout des onglets et nouvelle logique
- `nbs/mongo_episode.py` : Méthodes pour recherche par livre/auteur
- `nbs/mongo_livre.py` : Méthodes de recherche optimisées

## Estimation des Efforts
- **Données et relations** : 2 jours
- **Interface utilisateur** : 3 jours  
- **Tests et optimisations** : 2 jours
- **Total** : ~1 semaine de développement

## Risques et Mitigation
1. **Performance** : Index MongoDB et cache de recherche
2. **Qualité des données** : Validation manuelle des relations livre-épisode
3. **Compatibilité** : Tests de non-régression sur l'interface existante

## Prochaines Étapes
1. Validation du plan par le développeur
2. Analyse des transcriptions pour extraire les relations livre-épisode
3. Implémentation par phases avec tests à chaque étape
