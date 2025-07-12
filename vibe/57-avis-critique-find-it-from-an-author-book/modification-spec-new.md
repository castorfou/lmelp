# Spécification des modifications - Accès aux avis critiques par livre/auteur

## Vue d'ensemble

Cette fonctionnalité ajoute un accès alternatif aux avis critiques en permettant la recherche par livre ou auteur, complétant l'accès existant par épisode. Elle sera intégrée sous forme de sous-onglet dans la page avis critiques existante.

## Objectifs

- Permettre la recherche d'avis critiques en tapant le nom d'un auteur ou d'un livre
- Afficher les résultats sous forme "Auteur - Titre" dans l'autocomplétion
- Montrer une liste chronologique des épisodes où le livre a été discuté
- Préserver totalement l'interface existante (rétrocompatibilité stricte)

## Fonctionnalités détaillées

### 1. Interface utilisateur avec sous-onglets

**Structure nouvelle de la page 4_avis_critiques.py :**
```
📝 Avis Critiques
├── 📺 Par Épisode (interface actuelle refactorisée)
│   ├── Navigation avec flèches clavier (conservée)
│   ├── Sélecteur d'épisodes (identique)
│   └── Génération/affichage résumés (identique)
└── 📚 Par Livre/Auteur (nouveau)
    ├── Champ de recherche autocomplete
    ├── Suggestions "Auteur - Titre"
    └── Résultats chronologiques par épisode
```

### 2. Recherche autocomplete unifiée

**Comportement :**
- Recherche active à partir de 3 caractères
- Recherche simultanée dans auteurs ET titres de livres
- Affichage unifié : `"J.R.R. Tolkien - Le Seigneur des Anneaux"`
- Recherche fuzzy : "annea" trouve "Le Seigneur des Anneaux"
- Performance cible : < 1 seconde

**Exemples :**
- Tape "tolkien" → `"J.R.R. Tolkien - Le Seigneur des Anneaux"`
- Tape "seigneur" → `"J.R.R. Tolkien - Le Seigneur des Anneaux"`
- Tape "vargas" → `"Mario Vargas Llosa - Je vous dédie mon silence"`

### 3. Affichage des résultats

Après sélection d'un livre, affichage chronologique :

```
📖 Le Seigneur des Anneaux - J.R.R. Tolkien

🗓️ 26 janvier 2025 - Episode: "Les nouvelles pages..."
   📊 Note: 8.5/10 | 🎯 Coup de cœur: Patricia Martin
   💬 "Roman épique magistral, univers riche et complexe"

🗓️ 15 mars 2024 - Episode: "Retour sur les classiques..."
   📊 Note: 9.2/10 | 🏆 Chef d'œuvre: Bernard Poiret  
   💬 "L'œuvre de référence de la fantasy moderne"
```

## Spécifications techniques

### 1. Modèle de données

**Collection `episode_livres` (nouvelle) :**
```javascript
{
  _id: ObjectId,
  episode_oid: ObjectId,
  livre_oid: ObjectId,
  auteur_oid: ObjectId,
  episode_date: Date,
  episode_titre: String,
  livre_titre: String,
  auteur_nom: String,
  note_moyenne: Number,
  coups_de_coeur: [String], // Noms des critiques
  chef_oeuvre: String, // Nom du critique si applicable
  extrait_avis: String, // Premier commentaire ou synthèse
  type_discussion: String // "programme" ou "coup_de_coeur"
}
```

**Index MongoDB recommandés :**
```javascript
// Index de recherche textuelle
db.episode_livres.createIndex({
  "livre_titre": "text",
  "auteur_nom": "text"
})

// Index de performance
db.episode_livres.createIndex({
  "livre_oid": 1,
  "episode_date": -1
})

db.episode_livres.createIndex({
  "auteur_oid": 1,
  "episode_date": -1
})
```

### 2. Nouveaux modules Python

**`nbs/avis_critiques_parser.py` :**
```python
class AvisCritiquesParser:
    def extract_books_from_summary(self, summary_text: str) -> List[BookMention]
    def parse_markdown_tables(self, content: str) -> Dict[str, List[Dict]]
    def extract_ratings(self, avis_text: str) -> Dict[str, float]
    def build_episode_livres_index(self) -> None
```

**`nbs/avis_search.py` :**
```python
class AvisSearchEngine:
    def search_combined(self, query: str) -> List[AutocompleteResult]
    def get_book_episodes(self, livre_oid: ObjectId) -> List[EpisodeAvis]
    def fuzzy_search(self, query: str) -> List[Tuple[str, str]]  # (auteur, titre)
```

**`nbs/mongo_episode_livre.py` :**
```python
class EpisodeLivre(BaseEntity):
    collection: str = "episode_livres"
    def __init__(self, episode_oid: ObjectId, livre_oid: ObjectId)
    def add_rating_info(self, note: float, critiques: List[str])
    @classmethod
    def extract_from_avis_summary(cls, avis_critique_doc: Dict)
```

### 3. Interface Streamlit refactorisée

**Structure de `ui/pages/4_avis_critiques.py` (modifiée) :**
```python
def main():
    st.title("📝 Avis Critiques")
    
    # Onglets principaux  
    tab1, tab2 = st.tabs(["📺 Par Épisode", "📚 Par Livre/Auteur"])
    
    with tab1:
        display_episode_view()  # Code actuel refactorisé sans changement
        
    with tab2:
        display_book_search_view()  # Nouvelle fonctionnalité

def display_episode_view():
    # Déplacement du code existant ici, identique
    # Navigation, sélection épisode, génération résumés
    # Raccourcis clavier préservés
    
def display_book_search_view():
    search_query = st.text_input("Rechercher un livre ou auteur...", 
                                min_chars=3)
    if len(search_query) >= 3:
        # Autocomplétion et résultats
        suggestions = get_autocomplete_suggestions(search_query)
        # Affichage chronologique des épisodes
```

**Nouveau composant `ui/components/book_autocomplete.py` :**
```python
def render_autocomplete(query: str, min_chars: int = 3) -> List[str]
def format_suggestion(auteur: str, titre: str) -> str
def parse_selected_suggestion(suggestion: str) -> Tuple[str, str]
```

## Flux utilisateur

### Recherche et sélection
1. Utilisateur va sur "Avis Critiques" → onglet "📚 Par Livre/Auteur"
2. Tape dans le champ de recherche (ex: "tolkien")
3. Voit des suggestions formatées : "J.R.R. Tolkien - Le Seigneur des Anneaux"
4. Clique sur une suggestion

### Affichage des résultats
5. Page affiche le titre/auteur sélectionné
6. Liste chronologique des épisodes où le livre a été mentionné  
7. Pour chaque épisode : date, titre épisode, note, critiques, extrait
8. Possibilité de cliquer pour aller vers l'épisode complet dans l'onglet "Par Épisode"

## Contraintes et exigences

### Rétrocompatibilité stricte
- ✅ L'onglet "Par Épisode" garde exactement le même comportement
- ✅ Tous les raccourcis clavier existants sont préservés  
- ✅ Aucune régression fonctionnelle
- ✅ Interface actuelle utilisable sans changement

### Performance
- ✅ Recherche < 1 seconde (avec index MongoDB appropriés)
- ✅ Pas de pagination nécessaire pour l'instant
- ✅ Cache en mémoire pour les recherches fréquentes

### Données
- ✅ Migration one-shot des avis existants vers `episode_livres`
- ✅ Intégration future dans le processus de création d'avis
- ✅ Préservation de la qualité des données existantes

## Phases d'implémentation

### Phase 1 : Infrastructure et parsing (Semaine 1)
- Développement `avis_critiques_parser.py`
- Création collection `episode_livres` 
- Script de migration des avis existants
- Tests sur échantillon limité (50 épisodes)

### Phase 2 : Interface utilisateur (Semaine 2)
- Refactorisation page avec onglets (préservation code existant)
- Développement composant de recherche autocomplete
- Logique de recherche fuzzy combinée auteur/titre
- Interface d'affichage des résultats chronologiques

### Phase 3 : Intégration et performance (Semaine 3)
- Tests complets de non-régression sur onglet "Par Épisode"
- Optimisation des performances avec index MongoDB
- Migration complète des 300 épisodes
- Tests de charge et d'utilisation

### Phase 4 : Finalisation (Semaine 4)
- Tests utilisateur sur nouvelle fonctionnalité
- Documentation utilisateur et technique
- Intégration dans processus futur de création d'avis
- Déploiement final

## Critères d'acceptation

### Fonctionnels
- [ ] Recherche par auteur fonctionne ("tolkien" → suggestions avec livres)
- [ ] Recherche par titre fonctionne ("seigneur" → "Le Seigneur des Anneaux")
- [ ] Autocomplétion réactive < 1 seconde
- [ ] Format suggestions : "Auteur - Titre"
- [ ] Affichage chronologique correct des épisodes
- [ ] Données exactes (notes, critiques, dates) extraites des avis

### Rétrocompatibilité
- [ ] Onglet "Par Épisode" : comportement exactement identique
- [ ] Raccourcis clavier flèches gauche/droite préservés
- [ ] Génération/regénération de résumés inchangée
- [ ] Navigation épisodes identique à l'existant

### Performance
- [ ] Recherche autocomplete < 1 seconde
- [ ] Pas de régression de performance sur onglet "Par Épisode"
- [ ] Chargement initial de la page inchangé

### Techniques
- [ ] Collection `episode_livres` alimentée pour tous les avis existants
- [ ] Index MongoDB optimisés pour recherche textuelle et chronologique
- [ ] Tests unitaires pour nouveaux modules (parser, search)
- [ ] Documentation technique complète

## Métriques de succès

### Utilisation
- Temps de recherche moyen < 500ms
- Taux de réussite de recherche > 95% (trouve le livre recherché)
- Adoption de la nouvelle fonctionnalité mesurée (analytics optionnel)

### Qualité des données
- 100% des avis critiques existants parsés avec succès
- Zéro perte de données dans la migration
- Cohérence notes/critiques entre source et index

### Maintenance  
- Processus d'ajout futur d'avis critiques documenté
- Script de re-indexation disponible si nécessaire
- Code maintenable pour évolutions futures
