# Workflow

## Phase 0 - Context

### Generate your codebase

from project repo

gco [BRANCH-NAME]

```bash
repomix --output vibe/[BRANCH-NAME]/output.txt --ignore "node_modules,dist,build"
```

### Generate project summary and current state

using gemini-cli

```
Voici le code source de mon projet existant @vibe/[BRANCH-NAME]/output.txt. 

Analyse-le et génère :

1. vibe/[BRANCH-NAME]/Phase_0/project-summary.md : Vue d'ensemble du projet
   - Architecture actuelle
   - Technologies utilisées
   - Structure des fichiers
   - Patterns identifiés
   
2. vibe/[BRANCH-NAME]/Phase_0/current-state.md : État actuel
   - Fonctionnalités existantes
   - Points forts du code
   - Problèmes identifiés
   - Dette technique
```

## Phase 1 - specifications for our new feature

the overall new feature is in github/issues

copy/paste this issue to `vibe/[BRANCH-NAME]/issue_description.txt`

using github-copilot

```
Je veux commencer le développement de cette nouvelle feature

`vibe/[BRANCH-NAME]/issue_description.txt`

Voici le contexte du projet

`vibe/[BRANCH-NAME]/Phase_0/project-summary.md`

et son état actuel

`vibe/[BRANCH-NAME]/Phase_0/current-state.md`

Nous entrons dans la phase 1 du projet, à cette étape il n'y a aucun developpement, modifications de fichiers techniques.

Pose-moi des questions pour comprendre :
- Comment cette modification s'intègre dans l'existant
- Quels fichiers seront impactés
- Les contraintes de rétrocompatibilité
- Les risques de régression
- La stratégie de migration si nécessaire

Compile ensuite dans le repertoire `vibe/[BRANCH-NAME]/Phase_1`:
1. `modification-spec.md` : Spécification des changements
2. `impact-analysis.md` : Analyse d'impact sur le code existant
3. `integration-strategy.md` : Stratégie d'intégration
```

### discussion

copilot va poser de nombreuses questions.
conserve les dans vibe/[BRANCH-NAME]/Phase_1/discussion.txt

réponds à ce que tu peux dans ce meme fichier en préfixant tes réponses par >

```
voici mes réponses (partielles)
j'ai repris toutes tes questions et j'ai commencé mes réponses par un chevron (>)
```

## Phase 2 - adapted Increment planification

Prends cette spécification de modification et le contexte du projet :

<MODIFICATION_SPEC>
[Coller modification-spec.md]
</MODIFICATION_SPEC>

<PROJECT_CONTEXT>
[Coller les parties pertinentes de output.txt ou project-summary.md]
</PROJECT_CONTEXT>

Crée un plan qui :
1. Minimise les modifications du code existant
2. Respecte les patterns et conventions actuels
3. Permet un rollback facile si nécessaire

Génère dans vibe/[BRANCH-NAME]/Phase_2:

### modification-plan.csv
ID,Status,Action,File,Type,Priority,Complexity,Current State,Target State,Tests to Update,Rollback Strategy
T001,TODO,CREATE/MODIFY/REFACTOR,[fichier],[New/Update/Refactor],BOUCLE1,[Low/Medium/High],[état actuel],[état cible],[tests à modifier],[stratégie rollback]

Chaque tâche a un identifiant unique (T001, T002, etc.) pour faciliter le référencement.
Les priorités sont organisées par BOUCLE1, BOUCLE2, etc. pour une approche itérative rapide.

### incremental-prompts.md
Des prompts pour chaque modification qui :
- Référencent les tâches par leur ID (ex: "Implémenter T001-T006")
- Incluent le contexte nécessaire du code existant
- Définissent précisément les changements
- Préservent la compatibilité
- Incluent les tests de régression

### migration-checklist.md
- [ ] Backup du code actuel
- [ ] BOUCLE1 : Boucle complète avec test simple (T001-T011)
- [ ] BOUCLE2 : Tests config.py (T012-T015)
- [ ] BOUCLE3+ : Tests modules critiques par boucle
- [ ] Tests de régression passent
- [ ] Documentation mise à jour
- [ ] Code review effectuée

## Phase 3 - Exécution avec Préservation (Adaptée)

```
Tu vas modifier le projet existant. Nous entrons dans la phase 3.
Nous allons boucler pour traiter toutes les taches de @ vibe/[BRANCH-NAME]/Phase_2/modification-plan.csv

Tu connais le contexte qui est 
CONTEXTE ACTUEL : @ vibe/[BRANCH-NAME]/Phase_0/project-summary.md

MODIFICATION À FAIRE : [Référencer la ligne du modification-plan.csv]

Pour chaque modification :

    Montre d'abord les changements exacts (diff style)
    Explique pourquoi ces changements sont nécessaires
    Génère le code modifié complet
    Adapte/crée les tests
    Vérifie qu'aucune régression n'est introduite

Après chaque modification, mets à jour :

    Phase_2/modification-plan.csv : Status → DONE, ajoute Result Notes
    Phase_3/changelog.md : Ajoute un git-friendly changelog entry
    Note tout effet de bord découvert
```

## Phase 4 : Documentation et Analyse Post-Modification

Maintiens ces fichiers spécifiques aux modifications :

dans vibe/[BRANCH-NAME]/Phase_4:

### modification-log.md
[Date] - [Feature/Fix]
- Fichiers modifiés : [liste avec lignes changées]
- Raison : [justification]
- Impact : [effets sur le système]
- Tests : [nouveaux/modifiés]
- Rollback : [comment revenir en arrière]

### regression-tests.md
Liste des tests à exécuter pour vérifier qu'aucune régression :
- [ ] [Test 1] - [Fichier] - [Résultat attendu]
- [ ] [Test 2] - [Fichier] - [Résultat attendu]

### technical-debt.md
Dette technique ajoutée/résolue :
- Résolue : [description]
- Ajoutée : [description + plan pour la résoudre]
- À surveiller : [points d'attention]

### code-review-notes.md
Points à vérifier en revue de code :
- Respect des conventions existantes
- Performance maintenue/améliorée
- Sécurité préservée
- Documentation à jour