# Prompts Incrémentaux pour Refactorisation Avis Critiques

# Prompts Incrémentaux pour Refactorisation Avis Critiques

## BOUCLE 1 : Foundation et Tests (T001-T012)

### Prompt 1 : Création des Fixtures et Tests (T001-T003)

```
Tu vas créer les fondations pour la classe AvisCritique ET les utilitaires de dates en respectant les patterns existants du projet LMELP.

CONTEXTE : Le projet utilise pytest avec fixtures dans tests/fixtures/data/ et un pattern de test robuste avec mocking.

TÂCHES T001-T003 :

1. **T001** - Crée `tests/fixtures/data/avis_critique_data.json` contenant :
   - Exemples d'avis critiques valides (résumés complets)
   - Exemples d'avis critiques tronqués (pour tests de validation)
   - Structure compatible avec la collection MongoDB existante :
     ```json
     {
       "valid_avis_critiques": [
         {
           "episode_oid": "507f1f77bcf86cd799439011",
           "episode_title": "Le Masque et la Plume du 15 janvier 2023",
           "episode_date": "15 jan 2023", 
           "summary": "## 1. Livres présentés\n\n| Auteur | Titre | Genre |\n|--------|-------|-------|\n| Victor Hugo | Les Misérables | Roman |\n\n## 2. Avis critiques\n\nExcellent roman...",
           "created_at": "2023-01-15T20:00:00Z",
           "updated_at": "2023-01-15T20:00:00Z"
         }
       ],
       "truncated_avis_critiques": [...]
     }
     ```

2. **T002** - Crée `tests/unit/test_mongo_avis_critique.py` avec pattern existant :
   - Mock toutes les dépendances externes (MongoDB, config)
   - Utilise les fixtures créées en T001
   - Structure suivant `tests/unit/test_mongo_livre.py` comme référence
   - Tests pour méthodes de validation (is_summary_truncated, etc.)
   - Tests constructeurs (init, from_oid, from_episode_oid)
   - Tests CRUD (save_if_valid, update_summary, delete)

3. **T003** - Crée `tests/unit/test_date_utils.py` AVANT l'implémentation :
   - Tests pour fonction format_episode_date()
   - Tests pour constante DATE_FORMAT
   - Tests cas limites (dates invalides, formats différents)
   - Tests de compatibilité avec les formats existants dans le projet

RÉSULTAT ATTENDU : Fixtures et tests créés, tests peuvent échouer (modules pas encore implémentés).
```

### Prompt 2 : Implémentation Date Utils avec TDD (T004-T008)

```
Tu vas implémenter les utilitaires de dates en suivant une approche TDD stricte et refactoriser l'existant.

CONTEXTE : Il faut d'abord identifier toutes les utilisations de formatage de dates dans le projet pour centraliser

TÂCHES T004-T008 :

1. **T004** - Crée `nbs/date_utils.py` pour passer les tests T003 :
   ```python
   """Utilitaires de gestion des dates pour LMELP"""
   
   DATE_FORMAT = "%d %b %Y"
   
   def format_episode_date(date_str: str) -> str:
       """Formate une date d'épisode selon le format standard du projet"""
       # Implémentation pour passer TOUS les tests de test_date_utils.py
   ```

2. **T005** - Backup et première migration dans 4_avis_critiques.py :
   ```python
   # AVANT 
   DATE_FORMAT = "%d %b %Y"  # ligne ~42
   
   # APRÈS
   from date_utils import DATE_FORMAT, format_episode_date
   ```

3. **T006** - Recherche exhaustive des autres usages :
   ```bash
   grep -r "DATE_FORMAT\|%d %b %Y\|strftime.*%d.*%b.*%Y" --include="*.py" .
   grep -r "jan\|fév\|mar\|avr\|mai\|juin\|juil\|août\|sep\|oct\|nov\|déc" --include="*.py" .
   ```

4. **T007** - Refactorisation complète des autres fichiers identifiés :
   - Remplacer les formats hardcodés par date_utils
   - Maintenir la compatibilité existante
   - Tester chaque modification

5. **T008** - Validation complète :
   ```bash
   pytest tests/unit/test_date_utils.py -v
   # Tous les tests doivent passer
   ```

VALIDATION : Centralisation réussie sans régression
```

### Prompt 3 : Notebook et Classe AvisCritique (T009-T012)

### Prompt 3 : Notebook et Classe AvisCritique (T009-T012)

```
Tu vas créer le notebook et la classe AvisCritique maintenant que les utilitaires de dates sont stabilisés.

CONTEXTE : Le projet génère les modules .py depuis des notebooks Jupyter avec nbdev. Référence : nbs/py mongo helper livres.ipynb

TÂCHES T009-T012 :

1. **T009** - Crée `nbs/py mongo helper avis_critiques.ipynb` :
   - Structure identique à `nbs/py mongo helper livres.ipynb`
   - Cellule `# |default_exp mongo_avis_critique` 
   - Classe AvisCritique héritant de BaseEntity
   - Toutes les méthodes spécifiées dans modification-spec.md
   - Utilise `date_utils` pour le formatage des dates
   - Exemples d'utilisation dans le notebook
   - Compatible avec génération nbdev

2. **T010** - Génère `nbs/mongo_avis_critique.py` :
   ```bash
   cd nbs/
   jupyter nbconvert --to python "py mongo helper avis_critiques.ipynb" --output mongo_avis_critique
   ```

3. **T011** - Validation tests complets :
   ```bash
   pytest tests/unit/test_mongo_avis_critique.py -v
   ```

4. **T012** - Backup sécurisé avant refactorisation UI :
   ```bash
   cp ui/pages/4_avis_critiques.py ui/pages/4_avis_critiques.py.backup.$(date +%Y%m%d_%H%M%S)
   ```

PATTERN À RESPECTER : Même structure que mongo_livre.py avec BaseEntity
VALIDATION : Module importable sans erreur, tous tests passent
```

## BOUCLE 2 : Refactorisation Interface Utilisateur (T013-T020)

### Prompt 4 : Première Refactorisation UI (T013-T015)

```
Tu vas refactoriser progressivement l'UI en préservant l'interface utilisateur exacte.

CONTEXTE : ui/pages/4_avis_critiques.py contient 1106 lignes avec logique directe MongoDB

TÂCHES T013-T015 :

1. **T013** - Refactor get_summary_from_cache() :
   ```python
   # AVANT (lignes ~44-50)
   def get_summary_from_cache(episode_oid):
       try:
           collection = get_collection(collection_name="avis_critiques")
           cached_summary = collection.find_one({"episode_oid": episode_oid})
           return cached_summary
       except Exception as e:
           st.error(f"Erreur lors de la récupération du cache: {str(e)}")
           return None
   
   # APRÈS
   def get_summary_from_cache(episode_oid):
       try:
           avis_critique = AvisCritique.from_episode_oid(episode_oid)
           return avis_critique.to_dict() if avis_critique else None
       except Exception as e:
           st.error(f"Erreur lors de la récupération du cache: {str(e)}")
           return None
   ```

2. **T014** - Refactor save_summary_to_cache() :
   - Remplacer la logique de validation par avis_critique.is_valid_for_saving()
   - Utiliser avis_critique.get_truncation_debug_info() pour le debug
   - Préserver EXACTEMENT les mêmes messages UI

3. **T015** - Refactor check_existing_summaries() :
   - Utiliser des méthodes de classe au lieu d'accès direct MongoDB

VALIDATION APRÈS CHAQUE ÉTAPE :
```bash
streamlit run ui/lmelp.py
# Tester manuellement la page avis critiques
```
```

### Prompt 5 : Finalisation Refactorisation UI (T016-T020)

```
Tu vas refactoriser progressivement l'UI en préservant l'interface utilisateur exacte.

CONTEXTE : ui/pages/4_avis_critiques.py contient 1106 lignes avec logique directe MongoDB

TÂCHES T007-T009 :

1. **T007** - Backup sécurisé :
   ```bash
   cp ui/pages/4_avis_critiques.py ui/pages/4_avis_critiques.py.backup.$(date +%Y%m%d_%H%M%S)
   ```

2. **T008** - Refactor get_summary_from_cache() :
   ```python
   # AVANT (lignes ~44-50)
   def get_summary_from_cache(episode_oid):
       try:
           collection = get_collection(collection_name="avis_critiques")
           cached_summary = collection.find_one({"episode_oid": episode_oid})
           return cached_summary
       except Exception as e:
           st.error(f"Erreur lors de la récupération du cache: {str(e)}")
           return None
   
   # APRÈS
   def get_summary_from_cache(episode_oid):
       try:
           avis_critique = AvisCritique.from_episode_oid(episode_oid)
           return avis_critique.to_dict() if avis_critique else None
       except Exception as e:
           st.error(f"Erreur lors de la récupération du cache: {str(e)}")
           return None
   ```

3. **T009** - Refactor save_summary_to_cache() :
   - Remplacer la logique de validation par avis_critique.is_valid_for_saving()
   - Utiliser avis_critique.get_truncation_debug_info() pour le debug
   - Préserver EXACTEMENT les mêmes messages UI

VALIDATION APRÈS CHAQUE ÉTAPE :
```bash
streamlit run ui/lmelp.py
# Tester manuellement la page avis critiques
```
```

### Prompt 5 : Finalisation Refactorisation UI (T010-T015)

### Prompt 5 : Finalisation Refactorisation UI (T016-T020)

```
Tu vas terminer la refactorisation en supprimant le code dupliqué et en ajustant les imports.

TÂCHES T016-T020 :

1. **T016** - Supprimer fonctions obsolètes :
   - is_summary_truncated() (~45 lignes)
   - debug_truncation_detection() (~55 lignes)
   - Ces fonctions sont maintenant des méthodes de AvisCritique

2. **T017** - Supprimer fonctions obsolètes suite

3. **T018-T019** - Mise à jour imports et constantes :
   ```python
   # Ajouter en haut du fichier
   from mongo_avis_critique import AvisCritique
   from date_utils import DATE_FORMAT, format_episode_date
   
   # Supprimer la constante hardcodée
   # DATE_FORMAT = "%d %b %Y"  # À supprimer
   ```

4. **T020** - Tests de régression :
   ```bash
   pytest tests/ui/test_4_avis_critiques.py -v
   ```

CRITÈRE SUCCÈS : Interface utilisateur identique à 100%
```

## BOUCLE 3 : Intégration et Validation (T021-T024)

### Prompt 6 : Tests d'Intégration (T021-T022)

```
Tu vas créer les tests d'intégration pour valider le comportement avec MongoDB réel.

TÂCHES T021-T022 :

1. **T021** - Crée `tests/integration/test_avis_critique_integration.py` :
   - Tests avec vraie base de données MongoDB
   - Utilise les patterns existants dans tests/integration/
   - Tests de persistence, récupération, mise à jour

2. **T022** - Validation intégration :
   ```bash
   pytest tests/integration/test_avis_critique_integration.py -v
   ```

OBJECTIF : Aucune régression de comportement avec MongoDB
```

### Prompt 7 : Validation Finale (T023-T024)

```
Tu vas finaliser l'intégration et valider le comportement global.

TÂCHES T023-T024 :

1. **T023** - Update imports globaux :
   ```python
   # nbs/__init__.py
   from .mongo_avis_critique import AvisCritique
   ```

2. **T024** - Tests manuels complets :
   ```bash
   streamlit run ui/lmelp.py
   ```
   
   CHECKLIST VALIDATION :
   - [ ] Page avis critiques charge sans erreur
   - [ ] Génération d'avis critique fonctionne
   - [ ] Cache/récupération fonctionne
   - [ ] Messages d'erreur identiques
   - [ ] Performance subjective maintenue
   - [ ] Aucune régression visuelle

CRITÈRE ÉCHEC : Si moindre différence comportementale → ROLLBACK
```

## BOUCLE 4 : Documentation et Finalisation (T025-T026)

### Prompt 8 : Documentation et Nettoyage (T025-T026)

```
Tu vas finaliser le projet avec documentation et nettoyage.

TÂCHES T025-T026 :

1. **T025** - Crée `docs/mongo_avis_critique.md` :
   - Documentation d'utilisation du nouveau module
   - Exemples de code
   - Migration depuis l'ancienne approche

2. **T026** - Finalise le notebook :
   - Nettoie les cellules de développement
   - Ajoute documentation complète
   - Assure compatibilité nbdev

VALIDATION FINALE :
```bash
pytest tests/ -v --cov=nbs/mongo_avis_critique.py
# Couverture ≥ 90%
```

LIVRABLE : Refactorisation complète, testée, documentée et déployable
```

## Notes d'Utilisation des Prompts

### Ordre d'Exécution
1. **BOUCLE 1** : Foundation solide avec tests
2. **BOUCLE 2** : Refactorisation progressive UI
3. **BOUCLE 3** : Validation intégration
4. **BOUCLE 4** : Finalisation

### Critères de Passage à la Boucle Suivante
- **BOUCLE 1 → 2** : Tous tests unitaires passent
- **BOUCLE 2 → 3** : Interface UI identique fonctionnelle  
- **BOUCLE 3 → 4** : Aucune régression détectée
- **BOUCLE 4** : Documentation complète

### Stratégie de Rollback
Chaque prompt inclut sa stratégie de rollback spécifique, permettant un retour en arrière granulaire si nécessaire.
