# Workflow

## Phase 0 - Context

### Generate your codebase

from project repo

gco <<<new branch>>>

```bash
repomix --output vibe/<<<new branch>>>/output.txt --ignore "node_modules,dist,build"
```

### Generate project summary and current state

using gemini-cli

```
Voici le code source de mon projet existant @vibe/<<<new branch>>>/output.txt. 

Analyse-le et génère :

1. vibe/<<<new branch>>>/Phase_0/project-summary.md : Vue d'ensemble du projet
   - Architecture actuelle
   - Technologies utilisées
   - Structure des fichiers
   - Patterns identifiés
   
2. vibe/<<<new branch>>>/Phase_0/current-state.md : État actuel
   - Fonctionnalités existantes
   - Points forts du code
   - Problèmes identifiés
   - Dette technique
```

## Phase 1 - specifications for our new feature

the overall new feature is in github/issues

copy/paste this issue to vibe/<<<new branch>>>/issue_description.txt

using github-copilot

```
Je veux ajouter une nouvelle fonctionnalite a ce projet. Voici comment je l'ai decrite @vibe/<<<new branch>>>/issue_description.txt

Contexte du projet :
- [@ project-summary.md]
- [@ current-state.md]

Pose-moi des questions pour comprendre :
- Comment cette modification s'intègre dans l'existant
- Quels fichiers seront impactés=/;
- Les contraintes de rétrocompatibilité
- Les risques de régression
- La stratégie de migration si nécessaire

Compile ensuite dans le repertoire vibe/<<<new branch>>>/Phase_1:
1. modification-spec.md : Spécification des changements
2. impact-analysis.md : Analyse d'impact sur le code existant
3. integration-strategy.md : Stratégie d'intégration
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

Génère dans vibe/<<<new branch>>>/Phase_2:

### modification-plan.csv
Status,Action,File,Type,Priority,Complexity,Current State,Target State,Tests to Update,Rollback Strategy
TODO,CREATE/MODIFY/REFACTOR,[fichier],[New/Update/Refactor],HIGH,[Low/Medium/High],[état actuel],[état cible],[tests à modifier],[stratégie rollback]

### incremental-prompts.md
Des prompts pour chaque modification qui :
- Incluent le contexte nécessaire du code existant
- Définissent précisément les changements
- Préservent la compatibilité
- Incluent les tests de régression

### migration-checklist.md
- [ ] Backup du code actuel
- [ ] Tests de régression passent
- [ ] Nouvelles fonctionnalités implémentées
- [ ] Documentation mise à jour
- [ ] Code review effectuée