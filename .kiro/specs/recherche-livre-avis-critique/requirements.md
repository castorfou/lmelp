# Requirements Document

## Introduction

Cette fonctionnalité permettra aux utilisateurs de rechercher un livre spécifique et de trouver l'avis critique correspondant dans l'application Streamlit "Le Masque et la Plume". Actuellement, les utilisateurs peuvent seulement naviguer par épisode pour consulter les avis critiques. Cette nouvelle fonctionnalité ajoutera une approche de recherche centrée sur les livres, permettant une découverte plus intuitive du contenu.

## Requirements

### Requirement 1

**User Story:** En tant qu'utilisateur de l'application, je veux pouvoir choisir entre deux modes de navigation (par épisode ou par livre), afin d'accéder aux avis critiques selon ma préférence.

#### Acceptance Criteria

1. WHEN l'utilisateur accède à la page avis critiques THEN le système SHALL afficher des options radio avec "Par Épisode" et "Par Livre"
2. WHEN l'utilisateur sélectionne "Par Épisode" THEN le système SHALL afficher l'interface actuelle de navigation par épisodes
3. WHEN l'utilisateur sélectionne "Par Livre" THEN le système SHALL afficher une interface de recherche de livres
4. WHEN l'utilisateur change d'option THEN l'interface SHALL se mettre à jour dynamiquement

### Requirement 2

**User Story:** En tant qu'utilisateur, je veux pouvoir filtrer et rechercher des livres de manière intuitive, afin de trouver rapidement le livre qui m'intéresse parmi tous ceux discutés dans les émissions.

#### Acceptance Criteria

1. WHEN l'utilisateur sélectionne "Par Livre" THEN le système SHALL afficher un champ de filtre textuel similaire à celui de la page auteurs
2. WHEN l'utilisateur tape dans le champ de filtre THEN le système SHALL filtrer la liste des livres en temps réel (insensible à la casse)
3. WHEN l'utilisateur tape une partie du titre ou de l'auteur THEN le système SHALL mettre en évidence le texte correspondant dans les résultats
4. WHEN l'utilisateur clique sur un livre dans la liste filtrée THEN le système SHALL afficher l'avis critique correspondant

### Requirement 3

**User Story:** En tant qu'utilisateur, je veux voir l'avis critique complet avec le contexte de l'épisode, afin de comprendre les détails de la critique et pouvoir accéder à l'épisode complet si nécessaire.

#### Acceptance Criteria

1. WHEN l'utilisateur sélectionne un livre THEN le système SHALL afficher l'avis critique formaté (tableaux markdown avec notes et commentaires)
2. WHEN un avis critique est affiché THEN le système SHALL montrer les métadonnées de l'épisode (date, titre, durée)
3. WHEN un avis critique est affiché THEN le système SHALL fournir un lien ou bouton pour accéder à l'épisode complet
4. IF plusieurs épisodes mentionnent le même livre THEN le système SHALL afficher tous les avis avec leurs épisodes respectifs

### Requirement 4

**User Story:** En tant qu'administrateur système, je veux pouvoir extraire automatiquement les livres et auteurs des avis critiques existants, afin de créer une base de données structurée pour la recherche.

#### Acceptance Criteria

1. WHEN un avis critique est généré ou régénéré THEN le système SHALL automatiquement extraire les livres et auteurs mentionnés
2. WHEN le système parse un avis critique THEN il SHALL identifier les sections "LIVRES DISCUTÉS AU PROGRAMME" et "COUPS DE CŒUR DES CRITIQUES"
3. WHEN le système extrait un livre THEN il SHALL capturer le titre, l'auteur, et la note attribuée
4. WHEN l'extraction est terminée THEN le système SHALL sauvegarder les données dans une collection dédiée pour la recherche

### Requirement 5

**User Story:** En tant qu'administrateur système, je veux pouvoir traiter rétroactivement tous les avis critiques existants, afin de construire la base de données de livres pour la recherche.

#### Acceptance Criteria

1. WHEN le script de migration est exécuté THEN il SHALL traiter tous les avis critiques existants dans la collection
2. WHEN le script traite un avis critique THEN il SHALL extraire tous les livres mentionnés et les associer à l'épisode correspondant
3. WHEN une erreur de parsing survient THEN le système SHALL logger l'erreur et continuer le traitement
4. WHEN la migration est terminée THEN le système SHALL fournir un rapport du nombre de livres extraits

### Requirement 6

**User Story:** En tant qu'utilisateur, je veux que l'interface existante reste inchangée, afin de continuer à utiliser la navigation par épisode comme avant.

#### Acceptance Criteria

1. WHEN l'utilisateur accède à la page avis critiques THEN l'option "Par Épisode" SHALL être sélectionnée par défaut
2. WHEN l'utilisateur utilise l'option "Par Épisode" THEN toutes les fonctionnalités existantes SHALL fonctionner exactement comme avant
3. WHEN l'utilisateur navigue entre les épisodes THEN la sélection, les boutons de navigation et les raccourcis clavier SHALL fonctionner normalement
4. WHEN l'utilisateur génère ou régénère un résumé THEN le processus SHALL fonctionner comme avant

### Requirement 7

**User Story:** En tant qu'utilisateur, je veux que la recherche soit performante et réactive, afin d'avoir une expérience fluide lors de la saisie.

#### Acceptance Criteria

1. WHEN l'utilisateur tape dans le champ de recherche THEN les suggestions SHALL apparaître en moins de 500ms
2. WHEN l'utilisateur sélectionne un livre THEN l'avis critique SHALL s'afficher en moins de 2 secondes
3. WHEN la base de données contient plus de 1000 livres THEN la recherche SHALL rester fluide
4. IF aucun résultat n'est trouvé THEN le système SHALL afficher un message informatif approprié