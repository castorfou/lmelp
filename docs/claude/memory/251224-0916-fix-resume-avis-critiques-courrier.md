# Fix génération résumé avis critiques - Issue #90

**Date:** 24 décembre 2024, 09:16
**Issue:** [#90 - La génération du résumé des avis critiques échoue sur certains épisodes](https://github.com/castorfou/lmelp/issues/90)
**Branche:** `90-bug-la-generation-du-resume-des-avis-critiques-echoue-sur-certains-episodes`
**Commit:** `f253226`

## Problème identifié

### Symptômes
- La génération du résumé des avis critiques échouait sur certains épisodes spécifiques
- Épisodes concernés :
  - 12 décembre 2021 : "Les livres de Stephen King, Ahmet Altan, Patricia Highsmith..."
  - 04 octobre 2020 : "Les nouveaux livres de Laurent Mauvignier, Irène Frain, Philippe Djian..."
- L'IA répondait : "Aucun livre discuté dans cet épisode. Cette émission semble porter sur d'autres sujets (cinéma, théâtre, musique)."
- Alors que ces épisodes discutaient clairement de livres (visible dans les titres et descriptions)

### Cause racine

**Découverte importante** : Le problème ne venait PAS du prompt lui-même (qui fonctionne bien sur 100+ autres épisodes).

**La vraie cause** : Ces épisodes commencent par une longue section "courrier de la semaine" où l'animateur lit des réactions d'auditeurs sur des livres d'**émissions PRÉCÉDENTES**.

Exemple de début de transcription :
```
Musique Le masque et la plume Musique Bonsoir à toutes et à tous...
dans le courrier de la semaine. Amaury Mesclon remercie Frédéric Becbedé
pour sa recommandation du voyant des temples d'Abel Quentin...
```

Le courrier mentionne des livres comme :
- Abel Quentin - "Le voyant des temples"
- Emmanuel Carrère - "Yoga"

Ces livres **ne font PAS partie du programme de l'émission**, mais l'IA les détectait en premier et se faisait piéger.

## Méthodologie de diagnostic

### 1. Analyse avec MongoDB MCP
- Utilisation du client MCP MongoDB pour récupérer les épisodes problématiques
- Découverte des longueurs de transcription (~53K et ~57K caractères, bien en dessous de la limite de 100K)

### 2. Tests progressifs
1. **Test simplifié** avec un prompt court → ✅ L'IA détecte les livres
2. **Test avec le prompt complet** → ❌ L'IA répond "Aucun livre discuté"
3. **Analyse des transcriptions** → 🎯 Découverte de la section "courrier de la semaine"
4. **Test avec prompt amélioré** → ✅ L'IA détecte correctement les livres

### 3. Scripts de test créés
- `test_episode_resume.py` : Test basique avec prompt simplifié
- `test_full_prompt.py` : Test avec le prompt exact du code
- `test_prompt_ameliore.py` : Test avec le prompt corrigé

## Solution implémentée

### Modifications du prompt

**Fichier modifié** : `ui/pages/4_avis_critiques.py` (lignes 877-982)

**Ajouts au prompt** :

1. **Section d'avertissement au début** (après l'introduction) :
```python
⚠️ ATTENTION IMPORTANTE:
L'émission commence souvent par une section "courrier de la semaine" où l'animateur
lit des réactions d'auditeurs sur des livres d'émissions PRÉCÉDENTES.
CES LIVRES DU COURRIER NE FONT PAS PARTIE DU PROGRAMME DE CETTE ÉMISSION.
Tu dois IGNORER complètement cette section du courrier.

Les livres du programme principal sont introduits APRÈS le courrier, généralement
après des phrases comme:
- "Et on commence avec..."
- "Pour commencer ce soir..."
- "Parlons maintenant de..."
- "Le premier livre de ce soir..."
```

2. **Modification de la consigne principale** :
```python
CONSIGNE PRINCIPALE:
Identifie TOUS les livres discutés AU PROGRAMME DE CETTE ÉMISSION (pas ceux du courrier)
```

3. **Rappel dans les instructions détaillées** :
```python
⚠️ RAPPEL: Ignore complètement les livres mentionnés dans le "courrier de la semaine"
au début de l'émission.
```

4. **Rappel final** :
```python
RAPPEL FINAL:
- IGNORE les livres du courrier de la semaine
- NE RETOURNE AUCUN TEXTE EXPLICATIF AVANT OU APRÈS LES TABLEAUX
- AUCUNE PHRASE COMME "voici l'analyse" ou "en résumé"
- COMMENCE IMMÉDIATEMENT PAR LE PREMIER TITRE DE TABLEAU
```

## Résultats

### Tests de validation
✅ **Épisode du 12 déc. 2021** : L'IA détecte correctement :
- Ahmet Altan - "Madame Hayat" (note 9.8/10)
- Stephen King - "Après"
- François-Henri Désérable - "Mon maître et mon vainqueur"
- Patricia Highsmith - "Écrits intimes"
- Catherine Sauvat - "Depuis que je vous ai lu, je vous admire"

✅ **Épisode du 04 oct. 2020** : Détection correcte de tous les livres du programme

✅ **CI/CD** : Tests passés avec succès

### Validation utilisateur
L'utilisateur a confirmé que le fix fonctionne correctement dans l'interface Streamlit.

## Apprentissages clés

### 1. Ne pas modifier un prompt qui fonctionne
- Le prompt original fonctionnait sur 100+ épisodes
- Le problème venait d'un cas edge spécifique, pas du prompt global
- **Leçon** : Ajouter des instructions ciblées plutôt que tout refactoriser

### 2. Importance de l'analyse des données réelles
- L'analyse des transcriptions brutes a été cruciale
- Le problème n'était visible que dans les premiers caractères
- **Leçon** : Toujours examiner les données d'entrée en cas de comportement inattendu

### 3. Structure des émissions "Le Masque et la Plume"
- Les émissions commencent souvent par un "courrier de la semaine"
- Cette section peut mentionner de nombreux livres qui ne sont pas au programme
- Les livres du programme sont introduits après le courrier
- **Impact** : Ce pattern peut piéger les LLMs qui analysent de longues transcriptions

### 4. Méthodologie de debug pour LLM
1. Tester avec un prompt simplifié
2. Tester avec le prompt complet
3. Analyser les différences de résultats
4. Examiner les données d'entrée (transcriptions)
5. Ajouter des instructions ciblées
6. Valider avec les cas problématiques

### 5. Utilisation efficace du MCP MongoDB
- Le client MCP MongoDB facilite l'exploration rapide des données
- Commandes utiles :
  - `mcp__MongoDB__find` : Récupérer des documents
  - `mcp__MongoDB__aggregate` : Analyses complexes
  - `mcp__MongoDB__collection-schema` : Comprendre la structure

## Points techniques

### Configuration MongoDB
- Base de données : `masque_et_la_plume`
- Collection : `episodes`
- Port : 27018 (non standard, hardcodé dans `nbs/mongo.py:37`)

### Structure des épisodes
```python
{
    "_id": ObjectId,
    "titre": str,
    "date": Date,
    "type": "livres",  # ou films/théâtre/spéciale
    "transcription": str,
    "description": str,
    ...
}
```

### Prompt LLM
- Modèle : Azure OpenAI (GPT-4o)
- Fonction : `generate_critique_summary()` dans `ui/pages/4_avis_critiques.py`
- Timeout : 300 secondes (5 minutes)
- Max tokens : 4000
- Temperature : 0.1 (pour cohérence)

## Documentation et communication

### Commentaire GitHub
Ajout d'un commentaire détaillé sur l'issue #90 expliquant :
- La cause du problème
- La solution implémentée
- Les tests effectués
- Le fichier modifié

### Commit message
```
fix: améliore le prompt pour ignorer le courrier de la semaine (#90)

Le prompt de génération des résumés d'avis critiques a été amélioré pour
gérer correctement les épisodes qui commencent par une section "courrier de
la semaine". Cette section contient des réactions d'auditeurs sur des livres
d'émissions précédentes, et ne doit pas être analysée comme faisant partie
du programme de l'émission en cours.

Changements:
- Ajout d'instructions explicites pour ignorer le courrier de la semaine
- Ajout d'exemples de phrases d'introduction du programme principal
- Ajout de rappels à plusieurs endroits dans le prompt

Résout: #90
```

## Recommandations futures

### 1. Prétraitement des transcriptions
Envisager d'ajouter une étape de détection automatique du "courrier de la semaine" pour le supprimer avant l'analyse.

### 2. Tests de régression
Ajouter des tests unitaires/d'intégration avec ces 2 épisodes pour éviter les régressions futures.

### 3. Monitoring
Surveiller les cas où l'IA répond "Aucun livre discuté" pour détecter d'autres patterns problématiques.

### 4. Documentation du format d'émission
Documenter la structure typique des émissions pour faciliter les futurs debugs.

## Fichiers impliqués

- **Modifié** : `ui/pages/4_avis_critiques.py`
- **Créés (tests temporaires)** :
  - `test_episode_resume.py` (supprimé après tests)
  - `test_full_prompt.py` (supprimé après tests)
  - `test_prompt_ameliore.py` (conservé pour référence)

## Liens utiles

- Issue GitHub : https://github.com/castorfou/lmelp/issues/90
- Commentaire d'analyse : https://github.com/castorfou/lmelp/issues/90#issuecomment-3689044236
- Commit : https://github.com/castorfou/lmelp/commit/f253226
