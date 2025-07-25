#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('nbs')

# Test simple du parser sans dépendances externes
def test_parser_simple():
    """Test basique du parser sans BeautifulSoup"""
    
    # Test avec un exemple simple
    sample_avis = """
## 1. LIVRES DISCUTÉS AU PROGRAMME du 15 décembre 2024

| Auteur | Titre | Éditeur | Avis détaillés des critiques | Note moyenne | Nb critiques | Coup de cœur | Chef d'œuvre |
|--------|-------|---------|------------------------------|--------------|--------------|-------------|-------------|
| Marie Darrieussecq | Kakapo | Gallimard | **Elisabeth Philippe**: "Magnifique" (9) | 8.5 | 2 | Elisabeth Philippe | |
| Alice Zeniter | L'Art de perdre | Actes Sud | **Michel Crépu**: "Excellent" (9) | 8.0 | 2 | Michel Crépu | |

## 2. COUPS DE CŒUR DES CRITIQUES du 15 décembre 2024

| Auteur | Titre | Éditeur | Critique | Note | Commentaire |
|--------|-------|---------|----------|------|-------------|
| Kamel Daoud | Zabor ou les Psaumes | Actes Sud | Frédéric Beigbeder | 9.5 | Un livre bouleversant |
"""

    print("=== Test du Parser d'Avis Critiques ===")
    print(f"Texte d'entrée (longueur: {len(sample_avis)} caractères)")
    
    # Test de détection des sections
    import re
    
    # Test section 1
    section1_pattern = r"## 1\. LIVRES DISCUTÉS AU PROGRAMME.*?\n(.*?)(?=## 2\.|$)"
    match1 = re.search(section1_pattern, sample_avis, re.DOTALL | re.IGNORECASE)
    
    if match1:
        print("✅ Section 'LIVRES DISCUTÉS AU PROGRAMME' trouvée")
        table1_content = match1.group(1)
        print(f"Contenu section 1 (longueur: {len(table1_content)}):")
        print(table1_content[:200] + "..." if len(table1_content) > 200 else table1_content)
    else:
        print("❌ Section 'LIVRES DISCUTÉS AU PROGRAMME' NON trouvée")
    
    # Test section 2 avec caractère œ
    section2_pattern = r"## 2\. COUPS DE C[ŒO]EUR DES CRITIQUES.*?\n(.*?)$"
    match2 = re.search(section2_pattern, sample_avis, re.DOTALL | re.IGNORECASE)
    
    if match2:
        print("✅ Section 'COUPS DE CŒUR DES CRITIQUES' trouvée")
        table2_content = match2.group(1)
        print(f"Contenu section 2 (longueur: {len(table2_content)}):")
        print(table2_content[:200] + "..." if len(table2_content) > 200 else table2_content)
    else:
        print("❌ Section 'COUPS DE CŒUR DES CRITIQUES' NON trouvée")
        
        # Test avec pattern alternatif
        section2_alt = r"## 2\. COUPS DE C.*?EUR DES CRITIQUES.*?\n(.*?)$"
        match2_alt = re.search(section2_alt, sample_avis, re.DOTALL | re.IGNORECASE)
        if match2_alt:
            print("✅ Section trouvée avec pattern alternatif")
        else:
            print("❌ Aucun pattern ne fonctionne")
    
    # Test parsing des lignes de tableau
    if match1:
        lines = table1_content.strip().split('\n')
        print(f"\n=== Analyse des lignes du tableau 1 ===")
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            print(f"Ligne {i}: {line[:100]}...")
            
            if '|' in line and ('Auteur' in line or 'Titre' in line):
                print("  -> En-tête détecté")
            elif line.startswith('|') and '-' in line:
                print("  -> Séparateur détecté")
            elif line.startswith('|'):
                columns = [col.strip() for col in line.split('|')[1:-1]]
                print(f"  -> Données: {len(columns)} colonnes")
                if len(columns) >= 2:
                    print(f"     Auteur: '{columns[0]}'")
                    print(f"     Titre: '{columns[1]}'")
                    if len(columns) > 4:
                        # Test extraction de note
                        note_text = columns[4]
                        import re
                        number_match = re.search(r'(\d+\.?\d*)', note_text)
                        if number_match:
                            print(f"     Note extraite: {number_match.group(1)}")

if __name__ == "__main__":
    test_parser_simple()