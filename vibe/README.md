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

1. vibe/<<<new branch>>>/project-summary.md : Vue d'ensemble du projet
   - Architecture actuelle
   - Technologies utilisées
   - Structure des fichiers
   - Patterns identifiés
   
2. vibe/<<<new branch>>>/current-state.md : État actuel
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

Compile ensuite dans le repertoire vibe/<<<new branch>>>:
1. modification-spec.md : Spécification des changements
2. impact-analysis.md : Analyse d'impact sur le code existant
3. integration-strategy.md : Stratégie d'intégration
```
