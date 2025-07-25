#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== Test du Parser d'Avis Critiques ===")

# Test avec un exemple simple
sample_avis = """## 1. LIVRES DISCUTÉS AU PROGRAMME du 15 décembre 2024

| Auteur | Titre | Éditeur | Avis détaillés des critiques | Note moyenne | Nb critiques | Coup de cœur | Chef d'œuvre |
|--------|-------|---------|------------------------------|--------------|--------------|-------------|-------------|
| Marie Darrieussecq | Kakapo | Gallimard | **Elisabeth Philippe**: "Magnifique" (9) | 8.5 | 2 | Elisabeth Philippe | |

## 2. COUPS DE CŒUR DES CRITIQUES du 15 décembre 2024

| Auteur | Titre | Éditeur | Critique | Note | Commentaire |
|--------|-------|---------|----------|------|-------------|
| Kamel Daoud | Zabor ou les Psaumes | Actes Sud | Frédéric Beigbeder | 9.5 | Un livre bouleversant |
"""

print(f"Texte d'entrée (longueur: {len(sample_avis)} caractères)")

# Test de détection des sections
import re

# Test section 1
section1_pattern = r"## 1\. LIVRES DISCUTÉS AU PROGRAMME.*?\n(.*?)(?=## 2\.|$)"
match1 = re.search(section1_pattern, sample_avis, re.DOTALL | re.IGNORECASE)

if match1:
    print("✅ Section 'LIVRES DISCUTÉS AU PROGRAMME' trouvée")
    table1_content = match1.group(1)
    print("Contenu section 1:")
    print(repr(table1_content[:200]))
else:
    print("❌ Section 'LIVRES DISCUTÉS AU PROGRAMME' NON trouvée")

# Test section 2 avec caractère œ
section2_pattern = r"## 2\. COUPS DE C[ŒO]EUR DES CRITIQUES.*?\n(.*?)$"
match2 = re.search(section2_pattern, sample_avis, re.DOTALL | re.IGNORECASE)

if match2:
    print("✅ Section 'COUPS DE CŒUR DES CRITIQUES' trouvée")
else:
    print("❌ Section 'COUPS DE CŒUR DES CRITIQUES' NON trouvée")
    # Test avec pattern alternatif
    section2_alt = r"## 2\. COUPS DE C.*?EUR DES CRITIQUES.*?\n(.*?)$"
    match2_alt = re.search(section2_alt, sample_avis, re.DOTALL | re.IGNORECASE)
    if match2_alt:
        print("✅ Section trouvée avec pattern alternatif")
    else:
        print("❌ Aucun pattern ne fonctionne pour section 2")

print("Test terminé")