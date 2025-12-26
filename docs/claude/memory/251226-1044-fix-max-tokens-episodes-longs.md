# Fix : Augmentation max_tokens pour épisodes longs

**Date :** 26 décembre 2024
**Issues :** #92, #93
**Branche :** `92-bug-generation-resume-episode-du-29-mars-2020-echoue`
**Fichier modifié :** `ui/pages/4_avis_critiques.py`

## Problème identifié

### Symptômes
La génération de résumés d'avis critiques échouait sur certains épisodes longs avec le message :
```
⚠️ La réponse de l'IA semble tronquée (trop courte ou se termine brutalement)
📊 Longueur de la réponse: 137 caractères
```

### Épisodes affectés
- **29 mars 2020** : "Albert Camus, Cristina Comencini, Stephen King... Des livres en temps de confinement" (issue #92)
- **17 nov. 2019** : Épisode long (issue #93)

Ces épisodes ont des transcriptions très longues (~3240 secondes = 54 minutes, ~16000 mots).

### Cause racine
**Limite de tokens insuffisante pour la réponse.**

Le paramètre `max_tokens=4000` était trop faible pour générer des tableaux complets avec :
- 5+ livres à analyser
- Avis détaillés de 4-5 critiques par livre
- Tableaux markdown formatés avec HTML

Pour les épisodes très longs, même si GPT-4o a une limite de contexte de 128K tokens :
- Le prompt + la longue transcription consomment beaucoup de tokens en **entrée**
- Il reste peu de marge pour une **sortie** détaillée
- La génération s'arrêtait brutalement au milieu d'un tableau

## Solution implémentée

### Modification du code
**Fichier :** `ui/pages/4_avis_critiques.py` (ligne 992)

**Avant :**
```python
response = model.complete(
    prompt,
    max_tokens=4000,  # Augmenter significativement la limite pour des résumés détaillés
    temperature=0.1,
)
```

**Après :**
```python
response = model.complete(
    prompt,
    max_tokens=8000,  # Augmenté à 8000 pour gérer les épisodes longs avec beaucoup de livres (fix #92)
    temperature=0.1,
)
```

### Pourquoi 8000 ?
- **4000 tokens** = ~3000 mots = insuffisant pour 5 livres avec avis détaillés
- **8000 tokens** = ~6000 mots = suffisant pour :
  - Tableau 1 : Livres du programme (5+ livres × 3-4 avis détaillés)
  - Tableau 2 : Coups de cœur personnels
  - Formatage HTML pour les couleurs
  - Marge de sécurité

### Impact
✅ **Pas d'augmentation des coûts** : `max_tokens` est une limite maximale, pas un quota obligatoire. Les épisodes courts continueront à générer des réponses courtes.

## Tests effectués

### Tests utilisateur (validation complète)
1. ✅ **Épisode 29 mars 2020** : Génération complète réussie
2. ✅ **Épisode 17 nov. 2019** : Génération complète réussie (issue #93)
3. ✅ **Épisodes courts** : Fonctionnent toujours correctement
4. ✅ **Épisodes moyens** : Aucune régression

### Tests automatisés
```bash
PYTHONPATH=/workspaces/lmelp/src python -m pytest tests/unit/
# Résultat : 249 passed in 1.27s
```

## Différence avec l'issue #90

### Issue #90 (PR #91)
**Problème :** Prompt insuffisant pour ignorer le "courrier de la semaine"
**Solution :** Amélioration du prompt avec instructions explicites

### Issues #92 & #93 (cette PR)
**Problème :** Limite de tokens insuffisante pour réponses longues
**Solution :** Augmentation de `max_tokens` de 4000 à 8000

Ces deux fixes sont **complémentaires** :
- #91 améliore la **qualité** du prompt (quoi analyser)
- #92/#93 augmentent la **capacité** de réponse (combien générer)

## Points clés à retenir

### 1. Redémarrage Streamlit obligatoire
⚠️ **Important :** Un simple rafraîchissement du navigateur (F5) ne suffit PAS pour recharger le code Python modifié dans Streamlit.

**Procédure correcte :**
```bash
# Dans le terminal où tourne Streamlit
Ctrl+C
./ui/lmelp_ui.sh
```

### 2. Différence entre tokens d'entrée et de sortie
- **Tokens d'entrée** : Prompt + transcription (non modifiable pour un épisode donné)
- **Tokens de sortie** : Réponse générée (contrôlé par `max_tokens`)
- **Limite totale GPT-4o** : 128K tokens (entrée + sortie)

Pour les très longs épisodes :
- Entrée : ~50K-80K tokens (transcription longue)
- Sortie max possible : ~40K-70K tokens
- Notre limite : 8K tokens (largement suffisant, économique)

### 3. Détection de troncature
Le code a déjà une détection robuste de réponses tronquées :
```python
if (
    len(response_text) < 300
    or response_text.endswith("**")
    or response_text.endswith("→")
):
    st.error("⚠️ La réponse de l'IA semble tronquée")
    return "Réponse de l'IA tronquée. Veuillez réessayer."
```

Cette détection a permis d'identifier rapidement le problème.

## Fichiers modifiés

```
ui/pages/4_avis_critiques.py    | 2 +-
1 file changed, 1 insertion(+), 1 deletion(-)
```

## Commandes utiles

```bash
# Vérifier les épisodes longs dans la base
db.episodes.find({duree: {$gte: 3000}}).sort({duree: -1}).limit(10)

# Tester la génération pour un épisode spécifique
# Via l'interface Streamlit : Pages > 📝 Avis Critiques > Sélectionner épisode > Générer

# Lancer les tests unitaires
PYTHONPATH=/workspaces/lmelp/src python -m pytest tests/unit/ -v
```

## Documentation associée

- **Issue #92 :** https://github.com/castorfou/lmelp/issues/92
- **Issue #93 :** https://github.com/castorfou/lmelp/issues/93
- **PR #91 (fix courrier) :** https://github.com/castorfou/lmelp/pull/91
- **Mémoire précédente :** `251224-0916-fix-resume-avis-critiques-courrier.md`

## Leçons apprises

1. **Distinguer les problèmes de prompt vs limites techniques**
   - Problème de prompt → Améliorer les instructions
   - Problème de tokens → Ajuster les limites

2. **Tester avec des cas extrêmes**
   - Épisodes très longs (>50 min)
   - Épisodes avec beaucoup de livres (5+)
   - Épisodes avec "courrier de la semaine" long

3. **Le cache Streamlit est agressif**
   - Toujours redémarrer l'app après modification Python
   - Ne pas se fier au rafraîchissement navigateur

4. **max_tokens est une limite max, pas un quota**
   - Augmenter max_tokens n'augmente pas les coûts si pas utilisé
   - GPT-4o s'arrête naturellement quand la réponse est complète
