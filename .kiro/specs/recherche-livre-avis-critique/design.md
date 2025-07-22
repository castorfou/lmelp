# Design Document

## Overview

Cette fonctionnalité ajoute une capacité de recherche par livre à l'application Streamlit "Le Masque et la Plume". Le design s'appuie sur l'architecture MongoDB existante et introduit de nouveaux composants pour l'extraction, l'indexation et la recherche des livres mentionnés dans les avis critiques.

L'approche consiste à :
1. Extraire automatiquement les livres des avis critiques existants et futurs
2. Créer une nouvelle collection MongoDB pour indexer les relations livre-épisode
3. Modifier l'interface utilisateur pour offrir deux modes de navigation
4. Implémenter un système de recherche et filtrage similaire à la page auteurs

## Architecture

### Architecture Actuelle
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   episodes      │    │ avis_critiques  │    │     livres      │
│                 │    │                 │    │                 │
│ - _id           │    │ - episode_oid   │    │ - nom           │
│ - titre         │◄───┤ - summary       │    │ - auteur        │
│ - date          │    │ - created_at    │    │ - editeur       │
│ - transcription │    └─────────────────┘    └─────────────────┘
└─────────────────┘                           
                                              ┌─────────────────┐
                                              │    auteurs      │
                                              │                 │
                                              │ - nom           │
                                              └─────────────────┘
```

### Architecture Proposée
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   episodes      │    │ avis_critiques  │    │     livres      │
│                 │    │                 │    │                 │
│ - _id           │◄───┤ - episode_oid   │    │ - nom           │
│ - titre         │    │ - summary       │    │ - auteur        │
│ - date          │    │ - created_at    │    │ - editeur       │
│ - transcription │    └─────────────────┘    └─────────────────┘
└─────────────────┘             │                       ▲
        ▲                       │                       │
        │                       ▼                       │
        │            ┌─────────────────┐                │
        │            │ episode_livres  │                │
        └────────────┤                 │────────────────┘
                     │ - episode_oid   │
                     │ - livre_titre   │
                     │ - livre_auteur  │
                     │ - note          │
                     │ - section       │
                     │ - created_at    │
                     └─────────────────┘
```

## Components and Interfaces

### 1. Parser d'Avis Critiques (`AvisCritiquesParser`)

**Responsabilité :** Extraire les livres et métadonnées des avis critiques au format markdown.

```python
class AvisCritiquesParser:
    def extract_books_from_summary(self, summary_text: str) -> List[BookMention]:
        """Extrait les livres d'un résumé d'avis critique"""
        
    def parse_markdown_table(self, table_section: str) -> List[Dict]:
        """Parse une section de tableau markdown"""
        
    def extract_rating(self, rating_html: str) -> Optional[float]:
        """Extrait la note numérique du HTML coloré"""
```

**Interface BookMention :**
```python
@dataclass
class BookMention:
    titre: str
    auteur: str
    note: Optional[float]
    section: str  # "programme" ou "coups_de_coeur"
    commentaire: Optional[str]
```

### 2. Gestionnaire Episode-Livre (`EpisodeLivre`)

**Responsabilité :** Gérer la collection `episode_livres` qui fait le lien entre épisodes et livres.

```python
class EpisodeLivre(BaseEntity):
    collection: str = "episode_livres"
    
    def __init__(self, episode_oid: ObjectId, livre_titre: str, livre_auteur: str):
        self.episode_oid = episode_oid
        self.livre_titre = livre_titre
        self.livre_auteur = livre_auteur
        self.note = None
        self.section = None
        
    @classmethod
    def find_by_book(cls, livre_titre: str = None, livre_auteur: str = None) -> List['EpisodeLivre']:
        """Trouve tous les épisodes mentionnant un livre ou auteur"""
        
    @classmethod
    def get_all_books(cls) -> List[Dict[str, str]]:
        """Retourne tous les livres uniques avec leurs auteurs"""
```

### 3. Moteur de Recherche (`AvisSearchEngine`)

**Responsabilité :** Fournir les fonctionnalités de recherche et filtrage pour l'interface utilisateur.

```python
class AvisSearchEngine:
    def __init__(self):
        self.episode_livre = EpisodeLivre
        
    def search_books(self, query: str) -> List[Dict]:
        """Recherche floue dans les titres et auteurs"""
        
    def get_book_episodes(self, livre_titre: str, livre_auteur: str) -> List[Dict]:
        """Récupère tous les épisodes mentionnant un livre"""
        
    def get_all_books_formatted(self) -> List[str]:
        """Retourne tous les livres formatés pour l'affichage"""
```

### 4. Interface Utilisateur Modifiée

**Structure de la page `4_avis_critiques.py` :**

```python
def main():
    st.title("📝 Avis Critiques")
    
    # Options de navigation (radio buttons)
    mode = st.radio(
        "Mode de navigation :",
        ["Par Épisode", "Par Livre"],
        horizontal=True
    )
    
    if mode == "Par Épisode":
        afficher_selection_episode()  # Code existant inchangé
    else:
        afficher_recherche_livre()   # Nouvelle fonctionnalité

def afficher_recherche_livre():
    """Nouvelle interface de recherche par livre"""
    search_engine = AvisSearchEngine()
    
    # Champ de filtre (similaire à la page auteurs)
    filtre = st.text_input("Filtrer les livres:", "")
    
    # Liste filtrée des livres
    livres_filtres = search_engine.filter_books(filtre)
    
    # Sélection et affichage
    if livre_selectionne := st.selectbox("Sélectionnez un livre:", livres_filtres):
        episodes = search_engine.get_book_episodes(livre_selectionne)
        afficher_avis_pour_livre(episodes)
```

## Data Models

### Collection `episode_livres`

```javascript
{
  "_id": ObjectId,
  "episode_oid": ObjectId,        // Référence vers episodes._id
  "livre_titre": String,          // Titre du livre
  "livre_auteur": String,         // Auteur du livre
  "note": Number,                 // Note attribuée (optionnel)
  "section": String,              // "programme" ou "coups_de_coeur"
  "commentaire": String,          // Commentaire de la critique (optionnel)
  "created_at": Date,             // Date de création
  "updated_at": Date              // Date de mise à jour
}
```

### Index MongoDB Recommandés

```javascript
// Index composé pour la recherche par livre
db.episode_livres.createIndex({ "livre_titre": 1, "livre_auteur": 1 })

// Index pour la recherche par auteur seul
db.episode_livres.createIndex({ "livre_auteur": 1 })

// Index pour la recherche textuelle
db.episode_livres.createIndex({ 
  "livre_titre": "text", 
  "livre_auteur": "text" 
})

// Index pour les requêtes par épisode
db.episode_livres.createIndex({ "episode_oid": 1 })
```

## Error Handling

### 1. Parsing des Avis Critiques

**Erreurs Possibles :**
- Format markdown invalide ou inattendu
- Tableaux malformés
- Notes non parsables

**Stratégie :**
```python
try:
    books = parser.extract_books_from_summary(summary)
except ParsingError as e:
    logger.warning(f"Erreur parsing épisode {episode_id}: {e}")
    # Continuer le traitement, logger l'erreur
    books = []
```

### 2. Recherche et Affichage

**Erreurs Possibles :**
- Aucun résultat trouvé
- Erreurs de connexion MongoDB
- Données corrompues

**Stratégie :**
```python
def afficher_recherche_livre():
    try:
        search_engine = AvisSearchEngine()
        # ... logique de recherche
    except DatabaseError:
        st.error("Erreur de connexion à la base de données")
    except Exception as e:
        st.error(f"Erreur inattendue: {e}")
        logger.exception("Erreur dans recherche livre")
```

### 3. Migration des Données

**Erreurs Possibles :**
- Avis critiques corrompus
- Échec d'insertion en base
- Interruption du processus

**Stratégie :**
```python
def migrate_existing_avis():
    failed_episodes = []
    for avis in all_avis:
        try:
            process_avis(avis)
        except Exception as e:
            failed_episodes.append((avis['episode_oid'], str(e)))
            continue
    
    # Rapport final
    print(f"Migration terminée. {len(failed_episodes)} échecs.")
```

## Testing Strategy

### 1. Tests Unitaires

**Parser (`test_avis_critiques_parser.py`) :**
```python
def test_extract_books_from_valid_summary():
    """Test extraction avec un résumé valide"""
    
def test_extract_books_with_malformed_table():
    """Test robustesse avec tableau malformé"""
    
def test_extract_rating_from_html():
    """Test extraction des notes colorées"""
```

**EpisodeLivre (`test_episode_livre.py`) :**
```python
def test_create_episode_livre():
    """Test création d'une relation épisode-livre"""
    
def test_find_by_book():
    """Test recherche par livre"""
    
def test_get_all_books():
    """Test récupération de tous les livres"""
```

**Moteur de Recherche (`test_avis_search.py`) :**
```python
def test_search_books_fuzzy():
    """Test recherche floue"""
    
def test_filter_books():
    """Test filtrage des livres"""
    
def test_get_book_episodes():
    """Test récupération des épisodes d'un livre"""
```

### 2. Tests d'Intégration

**Migration (`test_migration.py`) :**
```python
def test_full_migration_process():
    """Test du processus complet de migration"""
    
def test_migration_with_corrupted_data():
    """Test migration avec données corrompues"""
```

**Interface Utilisateur (`test_ui_integration.py`) :**
```python
def test_episode_mode_unchanged():
    """Vérifier que le mode épisode fonctionne comme avant"""
    
def test_book_search_mode():
    """Test du nouveau mode de recherche par livre"""
```

### 3. Tests de Performance

**Recherche (`test_performance.py`) :**
```python
def test_search_performance_1000_books():
    """Test performance avec 1000+ livres"""
    
def test_filter_response_time():
    """Test temps de réponse du filtrage"""
```

### 4. Tests de Régression

**Compatibilité (`test_regression.py`) :**
```python
def test_existing_functionality_unchanged():
    """Vérifier que les fonctionnalités existantes ne sont pas impactées"""
    
def test_avis_generation_still_works():
    """Vérifier que la génération d'avis fonctionne toujours"""
```

## Migration Strategy

### Phase 1 : Infrastructure
1. Créer les nouveaux modules (`AvisCritiquesParser`, `EpisodeLivre`, `AvisSearchEngine`)
2. Créer la collection `episode_livres` avec les index appropriés
3. Tests unitaires complets

### Phase 2 : Migration des Données
1. Script de migration pour traiter tous les avis existants
2. Validation des données migrées
3. Tests d'intégration

### Phase 3 : Interface Utilisateur
1. Modification de la page `4_avis_critiques.py`
2. Ajout du mode de recherche par livre
3. Tests de régression pour s'assurer que le mode épisode fonctionne toujours

### Phase 4 : Intégration Continue
1. Modification du processus de génération d'avis pour extraire automatiquement les livres
2. Tests end-to-end
3. Documentation utilisateur