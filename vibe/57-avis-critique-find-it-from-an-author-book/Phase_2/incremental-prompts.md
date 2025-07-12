# Prompts incrémentaux pour l'implémentation

## 1. Création du parser d'avis critiques

### Contexte
Le projet utilise des avis critiques stockés en format markdown dans MongoDB (collection `avis_critiques`). Il faut parser ces avis pour extraire les livres et auteurs mentionnés.

### Prompt pour nbs/avis_critiques_parser.py
```
Crée un module `nbs/avis_critiques_parser.py` qui parse les avis critiques au format markdown.

Contexte du projet :
- Architecture MongoDB avec collections episodes, livres, auteurs, avis_critiques
- Pattern BaseEntity utilisé dans mongo.py, mongo_livre.py, mongo_auteur.py
- Format des avis : tableaux markdown avec sections "## 1. LIVRES DISCUTÉS AU PROGRAMME" et "## 2. COUPS DE CŒUR DES CRITIQUES"

Exemple d'avis à parser :
```markdown
## 1. LIVRES DISCUTÉS AU PROGRAMME
| Auteur | Titre | Éditeur | Avis détaillés des critiques | Note moyenne | Nb critiques | Coup de cœur | Chef d'œuvre |
|--------|-------|---------|------------------------------|--------------|--------------|-------------|-------------|
| J.R.R. Tolkien | Le Seigneur des Anneaux | Gallimard | **Patricia Martin**: "Magistral" (9) | 8.5 | 4 | Patricia Martin | |
```

Implémente :
- AvisCritiquesParser class avec méthodes extract_books_from_summary(), parse_markdown_tables()
- Extraction robuste des données (auteur, titre, notes, critiques)
- Gestion des erreurs de parsing
- Logging détaillé pour debugging
- Tests unitaires intégrés

Respecte les patterns existants du projet (BaseEntity, logging, gestion erreurs).
```

## 2. Classe EpisodeLivre pour la nouvelle collection

### Prompt pour nbs/mongo_episode_livre.py
```
Crée une classe `EpisodeLivre` dans `nbs/mongo_episode_livre.py` suivant le pattern des autres classes mongo du projet.

Contexte :
- Hérite de BaseEntity (voir mongo.py)
- Collection "episode_livres" pour faire le lien épisode ↔ livre
- Schéma : episode_oid, livre_oid, auteur_oid, episode_date, livre_titre, auteur_nom, note_moyenne, etc.

Exemple d'usage des autres classes :
```python
# Depuis mongo_livre.py
class Livre(BaseEntity):
    collection: str = "livres"
    def __init__(self, titre: str) -> None:
        super().__init__(titre, self.collection)
```

Implémente :
- Classe EpisodeLivre héritant de BaseEntity
- Méthodes : __init__, add_rating_info(), extract_from_avis_summary()
- Validation des ObjectId références
- Méthodes de recherche : find_by_livre(), find_by_auteur()
- Intégration avec les collections existantes
- Tests unitaires

Préserve la compatibilité avec l'architecture existante.
```

## 3. Moteur de recherche autocomplete

### Prompt pour nbs/avis_search.py
```
Crée un moteur de recherche `AvisSearchEngine` dans `nbs/avis_search.py` pour l'autocomplétion.

Contexte :
- Recherche combinée auteur + titre de livre
- Format résultat : "Auteur - Titre"
- Recherche fuzzy pour trouver "seigneur" → "Le Seigneur des Anneaux"
- Performance < 1 seconde requis

Fonctionnalités :
- search_combined(query) : recherche dans auteurs ET titres
- fuzzy_search(query) : recherche approximative
- get_book_episodes(livre_oid) : épisodes chronologiques pour un livre
- Format suggestions : "J.R.R. Tolkien - Le Seigneur des Anneaux"

Utilise :
- Collection episode_livres créée précédemment
- Index MongoDB textuel pour performance
- Cache @st.cache_data pour Streamlit
- Thefuzz pour recherche fuzzy (déjà utilisé dans mongo_auteur.py)

Respecte les patterns de performance du projet.
```

## 4. Script de migration des données

### Prompt pour scripts/migrate_avis_to_episode_livres.py
```
Crée un script de migration `scripts/migrate_avis_to_episode_livres.py` pour alimenter la nouvelle collection.

Contexte :
- ~300 épisodes avec avis critiques existants
- Parser créé précédemment (avis_critiques_parser.py)
- Pattern scripts existants dans le projet

Fonctionnalités :
- Lecture de tous les avis de la collection avis_critiques
- Parse avec AvisCritiquesParser
- Création entrées episode_livres via EpisodeLivre
- Validation et reporting des erreurs
- Mode dry-run pour tester
- Progress bar pour suivi
- Logs détaillés

Structure :
```python
def migrate_existing_avis():
    # 1. Get all avis critiques
    # 2. Parse each avis
    # 3. Create episode_livres entries
    # 4. Validate and report

if __name__ == "__main__":
    # CLI interface with args
```

Suit les patterns des autres scripts du projet.
```

## 5. Refactorisation de la page avis critiques

### Prompt pour ui/pages/4_avis_critiques.py
```
Refactorise `ui/pages/4_avis_critiques.py` pour ajouter des onglets sans modifier le comportement existant.

CRITIQUE : Préservation totale de l'interface existante dans l'onglet "Par Épisode".

État actuel :
- Page unique avec navigation épisodes
- Raccourcis clavier ← → pour navigation
- Génération/affichage résumés d'avis
- Sélecteur d'épisodes avec indicateurs 🟢⚪

État cible :
```python
def main():
    st.title("📝 Avis Critiques")
    tab1, tab2 = st.tabs(["📺 Par Épisode", "📚 Par Livre/Auteur"])
    
    with tab1:
        display_episode_view()  # CODE EXISTANT EXACT
        
    with tab2:
        display_book_search_view()  # NOUVEAU
```

Implémentation :
1. Encapsule le code existant dans display_episode_view() SANS MODIFICATION
2. Nouveau display_book_search_view() avec :
   - Champ recherche autocomplete
   - Suggestions format "Auteur - Titre"
   - Affichage chronologique résultats
3. Tests de non-régression obligatoires
4. Préservation raccourcis clavier dans onglet 1

Respecte l'architecture Streamlit existante.
```

## 6. Composant d'autocomplétion

### Prompt pour ui/components/book_autocomplete.py
```
Crée un composant Streamlit `ui/components/book_autocomplete.py` pour l'autocomplétion livre/auteur.

Contexte Streamlit du projet :
- Pages dans ui/pages/ utilisent Streamlit
- Pattern @st.cache_data pour performance
- Architecture modulaire

Fonctionnalités :
- render_autocomplete(query, min_chars=3) : rendu autocomplétion
- format_suggestion(auteur, titre) : format "Auteur - Titre"
- parse_selected_suggestion(suggestion) : extraction auteur/titre
- Intégration avec AvisSearchEngine

Interface :
```python
def render_book_autocomplete(query: str) -> Optional[Tuple[str, str]]:
    """Rendu autocomplétion retournant (auteur, titre) si sélection"""
    
def display_search_results(auteur: str, titre: str):
    """Affichage chronologique des épisodes pour un livre"""
```

Utilise les patterns Streamlit du projet (voir pages existantes).
```

## 7. Index MongoDB pour performance

### Prompt pour scripts/create_mongodb_indexes.py
```
Crée un script `scripts/create_mongodb_indexes.py` pour optimiser les performances de recherche.

Contexte :
- Collection episode_livres nouvellement créée
- Requêtes de recherche textuelle fréquentes
- Performance < 1 seconde requise

Index à créer :
```javascript
// Index recherche textuelle
db.episode_livres.createIndex({
  "livre_titre": "text",
  "auteur_nom": "text"
}, {
  "weights": { "livre_titre": 2, "auteur_nom": 1 }
})

// Index chronologique
db.episode_livres.createIndex({
  "livre_oid": 1,
  "episode_date": -1
})
```

Implémente :
- Création des index avec gestion d'erreurs
- Vérification si index existent déjà
- Mesure du temps de création
- Validation des performances post-création

Suit les patterns MongoDB du projet.
```

## 8. Tests unitaires complets

### Prompt pour tests/test_avis_parser.py
```
Crée des tests unitaires pour `tests/test_avis_parser.py` couvrant le parser d'avis critiques.

Structure des tests :
- TestAvisCritiquesParser class
- test_extract_books_from_valid_summary()
- test_parse_markdown_tables()
- test_extract_ratings()
- test_handle_malformed_markdown()
- test_empty_avis_handling()

Utilise :
- unittest framework
- Données de test réalistes (vraies structures markdown)
- Mocking pour MongoDB si nécessaire
- Assertions robustes

Suit les patterns de test du projet (s'il y en a).
```

## 9. Enrichissement pages auteurs/livres (optionnel)

### Prompt pour ui/pages/2_auteurs.py et 3_livres.py
```
Ajoute des liens vers avis critiques dans les pages auteurs et livres existantes.

IMPORTANT : Modifications minimales, préservation interface existante.

Pour chaque auteur/livre affiché :
- Vérifier si des avis critiques existent
- Ajouter bouton/lien discret "📝 Voir avis critiques"
- Redirection vers page avis critiques avec pré-sélection

Implémentation :
```python
# Ajout dans afficher_auteurs() et afficher_livres()
if has_avis_critiques_for_author(author_name):
    st.button("📝 Avis critiques", key=f"avis_{author_name}")
```

Respecte l'interface existante, ajouts non-intrusifs.
```

## 10. Documentation utilisateur

### Prompt pour docs/recherche_avis.md
```
Crée une documentation utilisateur `docs/recherche_avis.md` pour la nouvelle fonctionnalité.

Contenu :
- Guide d'utilisation de la recherche par livre/auteur
- Exemples concrets de recherche
- Explication du format "Auteur - Titre"
- Cas d'usage typiques
- FAQ

Format MkDocs compatible avec l'existant (voir autres docs/).

Structure :
# Recherche d'avis critiques
## Comment utiliser la recherche
## Exemples pratiques
## Questions fréquentes

Intègre dans mkdocs.yml si nécessaire.
```

## Notes d'implémentation

### Ordre recommandé
1. Parser et classes base (étapes 1-3)
2. Migration des données (étape 4)
3. Interface utilisateur (étapes 5-6)
4. Optimisation et tests (étapes 7-8)
5. Enrichissements optionnels (étapes 9-10)

### Points critiques
- **Rétrocompatibilité stricte** pour ui/pages/4_avis_critiques.py
- **Tests de non-régression** obligatoires avant chaque commit
- **Performance** : surveiller temps réponse < 1 seconde
- **Rollback** : chaque modification doit être facilement réversible

### Validation continue
- Tests unitaires après chaque module
- Tests d'intégration après l'interface
- Tests de performance après index MongoDB
- Tests utilisateur avant déploiement final
