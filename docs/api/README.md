# Documentation API

Les fichiers de ce répertoire documentent les modules Python du projet via [mkdocstrings](https://mkdocstrings.github.io/).

## Structure

Chaque fichier `.md` correspond à un module de `nbs/` et utilise la directive mkdocstrings pour générer automatiquement la doc depuis les docstrings :

```markdown
# Module rss

::: nbs.rss
    rendering:
      show_root_full_path: false
```

## Génération

Ces fichiers sont **maintenus manuellement**. Le projet utilise nbdev pour générer les modules Python (`nbdev_export`), mais pas pour la documentation (`nbdev_docs` a été abandonné car il repose sur Quarto, incompatible avec mkdocs).

Quand tu ajoutes un nouveau module :
1. Créer le notebook `nbs/py mon_module.ipynb` avec `# |default_exp mon_module`
2. Exporter : `nbdev_export`
3. Créer `docs/api/mon_module.md` :

```markdown
# Module mon_module

::: nbs.mon_module
    rendering:
      show_root_full_path: false
```
