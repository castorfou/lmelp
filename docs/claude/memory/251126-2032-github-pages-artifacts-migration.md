# Migration GitHub Pages vers méthode artifacts

**Date:** 2025-11-26 20:32
**Issue:** #67
**Branche:** `67-moderniser-le-déploiement-github-pages-méthode-artifacts`

## 🎯 Objectif

Moderniser le déploiement GitHub Pages en remplaçant la méthode classique `mkdocs gh-deploy` (qui crée une branche `gh-pages`) par la méthode moderne GitHub Actions artifacts.

## 🔧 Modifications apportées

### 1. Workflow GitHub Actions modernisé

**Fichier:** `.github/workflows/ci.yml` → `.github/workflows/docs.yml` (renommé)

**Changements principaux:**

- **Architecture:** Passage d'un job unique à 2 jobs séparés (`build` + `deploy`)
- **Permissions:**
  - Ancien: `contents: write` (moins sécurisé)
  - Nouveau: `pages: write` + `id-token: write` (plus sécurisé)
- **Méthode de déploiement:**
  - Ancien: `mkdocs gh-deploy --force` (crée branche gh-pages)
  - Nouveau: Upload artifact + deploy via `actions/deploy-pages@v4`
- **Caching:** Ajout du caching des dépendances MkDocs
- **Build:** Retrait du mode `--strict` pour compatibilité (warnings de liens cassés)

### 2. Structure du nouveau workflow

```yaml
jobs:
  build:
    - Checkout code
    - Setup Python 3.11
    - Cache MkDocs dependencies
    - Install dependencies
    - Build MkDocs
    - Setup Pages
    - Upload artifact (site/)

  deploy:
    - Condition: github.ref == 'refs/heads/main'
    - Deploy artifact to GitHub Pages
```

### 3. Renommage pour cohérence

- `ci.yml` → `docs.yml` pour suivre le pattern des autres workflows:
  - `tests.yml` → Tests Unitaires
  - `docker-publish.yml` → Build and Publish Docker Image
  - `docs.yml` → Deploy MkDocs to GitHub Pages

## ✅ Tests effectués

### Test du workflow sur la branche feature

1. **Ajout temporaire du trigger** sur la branche `67-moderniser-le-déploiement-github-pages-méthode-artifacts`
2. **Résultat:**
   - ✅ Job `build`: Succès (21s)
   - ✅ Artifact `github-pages` créé
   - ✅ Job `deploy`: Correctement ignoré (pas sur main)

### Corrections apportées pendant les tests

1. **Problème:** Build échouait avec `--strict` (warnings traités comme erreurs)
   - **Cause:** Liens cassés dans la documentation
   - **Solution:** Retrait de `--strict` pour compatibilité avec l'ancien workflow
   - **Note:** Les warnings pourront être corrigés dans une issue dédiée

## 📋 Actions requises post-merge

### Configuration GitHub Pages (IMPORTANT)

**Avant de merger la PR, l'utilisateur doit:**

1. Aller dans **Settings > Pages** du repo
2. Dans **Source**, sélectionner **"GitHub Actions"** au lieu de **"Deploy from a branch"**
3. Sauvegarder

⚠️ **Sans cette configuration, le déploiement échouera même si le workflow s'exécute correctement.**

### Nettoyage post-validation

Une fois le nouveau système validé et fonctionnel:

```bash
# Supprimer la branche locale gh-pages
git branch -D gh-pages

# Supprimer la branche remote gh-pages
git push origin --delete gh-pages
```

## 🔍 Points techniques importants

### Workflow système `pages-build-deployment`

- Ce workflow automatique GitHub apparaît dans l'interface
- Il est créé par GitHub quand on utilise la branche `gh-pages`
- **Il disparaîtra** une fois la configuration changée vers "GitHub Actions"

### Doublons dans l'interface GitHub Actions

Après le renommage `ci.yml` → `docs.yml`, deux entrées "Deploy MkDocs to GitHub Pages" apparaissent temporairement:
- L'une correspond aux exécutions de l'ancien `ci.yml`
- L'autre aux exécutions du nouveau `docs.yml`
- **Solution naturelle:** Les anciennes exécutions disparaîtront progressivement de la vue par défaut

### Trigger temporaire de test

Pour tester le workflow sur la branche feature:
```yaml
branches: [ main, '67-moderniser-le-déploiement-github-pages-méthode-artifacts' ]
paths: [ 'docs/**', 'mkdocs.yml', '.github/workflows/docs.yml' ]
```

⚠️ **À retirer avant le merge final** pour revenir à:
```yaml
branches: [ main ]
paths: [ 'docs/**', 'mkdocs.yml' ]
```

## 📊 Bénéfices de la migration

1. **Historique git propre:** Pas de commits automatiques
2. **Liste de branches claire:** Pas de branche `gh-pages`
3. **Sécurité améliorée:** Permissions plus restrictives
4. **Séparation des responsabilités:** Build et deploy séparés
5. **Méthode recommandée:** Standard GitHub depuis 2022
6. **Meilleure traçabilité:** Artifacts GitHub Actions

## 🔗 Références

- [Documentation GitHub Pages avec GitHub Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow)
- [Action deploy-pages@v4](https://github.com/actions/deploy-pages)
- [Exemple dans back-office-lmelp](https://github.com/castorfou/back-office-lmelp/blob/main/.github/workflows/docs.yml)

## 📝 Notes pour futures migrations similaires

1. **Toujours tester sur une branche feature** avec trigger temporaire
2. **Vérifier la compatibilité** avec les warnings existants (`--strict` peut poser problème)
3. **Documenter la configuration manuelle** requise (Settings > Pages)
4. **Nettoyer les branches obsolètes** après validation
5. **Renommer les fichiers** pour cohérence avec le projet
