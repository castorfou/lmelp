# Spécification des Changements : Refactorisation Avis Critiques

## Vue d'ensemble

### Objectif
Refactoriser la page `ui/pages/4_avis_critiques.py` pour utiliser les fonctions back-office via un nouveau module `mongo_avis_critique.py`, suivant le même pattern que les modules existants (`mongo_livre.py`, `mongo_auteur.py`).

### Principe directeur
- **Rétrocompatibilité totale** : L'interface utilisateur doit rester 100% identique
- **Pattern existant** : Suivre l'architecture établie avec nbdev et BaseEntity
- **Tests en premier** : Approche TDD pour garantir la qualité

## Spécifications Techniques

### 1. Nouveau Module MongoDB : `mongo_avis_critique.py`

#### 1.1 Classe AvisCritique
```python
class AvisCritique(BaseEntity):
    collection: str = "avis_critiques"
    
    def __init__(self, episode_oid: ObjectId, episode_title: str, episode_date: str, summary: str) -> None:
        """Initialise une instance d'avis critique."""
        super().__init__(summary, self.collection)
        self.episode_oid = episode_oid
        self.episode_title = episode_title  
        self.episode_date = episode_date
        self.summary = summary
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
```

#### 1.2 Méthodes de validation intégrées
Les fonctions actuelles de validation seront intégrées comme méthodes de classe :

```python
def is_summary_truncated(self) -> bool:
    """Vérifie si le résumé semble tronqué"""
    # Logic actuelle de is_summary_truncated()

def get_truncation_debug_info(self) -> List[str]:
    """Retourne les informations de débogage pour la détection de troncature"""
    # Logic actuelle de debug_truncation_detection()

def is_valid_for_saving(self) -> bool:
    """Détermine si l'avis critique peut être sauvegardé"""
    return not self.is_summary_truncated()
```

#### 1.3 Constructeurs alternatifs
```python
@classmethod
def from_oid(cls: Type[T], oid: ObjectId) -> T:
    """Crée une instance depuis un ObjectId MongoDB"""

@classmethod
def from_episode_oid(cls, episode_oid: ObjectId) -> Optional['AvisCritique']:
    """Récupère un avis critique existant pour un épisode donné"""
```

#### 1.4 Méthodes CRUD
```python
def save_if_valid(self) -> bool:
    """Sauvegarde seulement si le résumé n'est pas tronqué"""
    
def update_summary(self, new_summary: str) -> bool:
    """Met à jour le résumé avec validation"""
    
def delete(self) -> bool:
    """Supprime l'avis critique de la base"""
```

### 2. Notebook Jupyter : `nbs/py mongo helper avis_critiques.ipynb`

#### 2.1 Structure du notebook
```
# |default_exp mongo_avis_critique

## Avis Critique

# |export
[Code de la classe AvisCritique]

## Tests et exemples
[Cellules de démonstration et validation]

## Documentation
[Exemples d'utilisation et cas d'usage]
```

#### 2.2 Compatibilité nbdev
- Utilisation des commentaires `# |export` pour la génération automatique
- Documentation intégrée avec docstrings
- Exemples d'utilisation dans les cellules de test

### 3. Fonctions utilitaires centralisées

#### 3.1 Module utilitaire pour les dates
Créer `nbs/date_utils.py` :
```python
DATE_FORMAT = "%d %b %Y"

def format_episode_date(date_str: str) -> str:
    """Formate une date d'épisode selon le format standard"""
```

### 4. Refactorisation de `ui/pages/4_avis_critiques.py`

#### 4.1 Remplacement des fonctions existantes
```python
# AVANT
def get_summary_from_cache(episode_oid):
    collection = get_collection(collection_name="avis_critiques")
    cached_summary = collection.find_one({"episode_oid": episode_oid})
    return cached_summary

# APRÈS  
def get_summary_from_cache(episode_oid):
    return AvisCritique.from_episode_oid(episode_oid)
```

#### 4.2 Simplification de la logique
```python
# AVANT
def save_summary_to_cache(episode_oid, episode_title, episode_date, summary):
    if is_summary_truncated(summary):
        st.warning("⚠️ Résumé tronqué détecté")
        debug_info = debug_truncation_detection(summary)
        # ... logique complexe
        return False
    # ... sauvegarde

# APRÈS
def save_summary_to_cache(episode_oid, episode_title, episode_date, summary):
    avis_critique = AvisCritique(episode_oid, episode_title, episode_date, summary)
    if not avis_critique.is_valid_for_saving():
        st.warning("⚠️ Résumé tronqué détecté")
        debug_info = avis_critique.get_truncation_debug_info()
        # ... affichage des infos de debug
        return False
    return avis_critique.save_if_valid()
```

## Migration des Fonctionnalités

### 1. Préservation des fonctionnalités existantes
- **Cache Streamlit** : `@st.cache_data` sur `get_episodes_with_transcriptions()` maintenu
- **Interface utilisateur** : Tous les éléments UI restent identiques
- **Messages d'erreur** : Préservation des messages actuels
- **Logique de validation** : Migration sans modification de la logique métier

### 2. Amélioration de la maintenabilité
- **Séparation des responsabilités** : UI vs logique métier
- **Réutilisabilité** : Module utilisable dans notebooks et scripts
- **Testabilité** : Classe isolée pour tests unitaires
- **Cohérence** : Pattern uniforme avec les autres entités

## Contraintes Techniques

### 1. Rétrocompatibilité
- Aucun changement de l'interface utilisateur
- Préservation des signatures de fonctions publiques
- Maintien des performances (cache)

### 2. Qualité du code
- Tests unitaires complets
- Documentation des fonctions
- Gestion d'erreur robuste
- Respect des patterns existants

### 3. Déploiement
- Migration transparente
- Possibilité de rollback
- Pas de modification de schéma de base de données

## Tests Requis

### 1. Tests unitaires
- `test_mongo_avis_critique.py` : Tests de la classe AvisCritique
- Tests des méthodes de validation
- Tests des constructeurs alternatifs
- Tests CRUD

### 2. Tests d'intégration  
- Interface avec MongoDB
- Cohérence avec les autres modules

### 3. Tests de régression
- Interface utilisateur inchangée
- Performance maintenue
- Fonctionnalités existantes préservées

## Critères de Succès

1. **Fonctionnel** : L'interface utilisateur fonctionne à l'identique
2. **Technique** : Code plus maintenable et testable
3. **Qualité** : Couverture de tests ≥ 90%
4. **Performance** : Pas de dégradation observable
5. **Cohérence** : Pattern uniforme avec les autres modules du projet
