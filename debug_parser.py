#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'nbs'))

# Mock BeautifulSoup pour éviter l'erreur d'import
class MockBeautifulSoup:
    def __init__(self, html, parser):
        self.text = html
    
    def get_text(self):
        # Extraire le texte simple en supprimant les balises HTML basiques
        import re
        text = re.sub(r'<[^>]+>', '', self.text)
        return text.strip()

# Remplacer BeautifulSoup par le mock
sys.modules['bs4'] = type(sys)('bs4')
sys.modules['bs4'].BeautifulSoup = MockBeautifulSoup

# Maintenant importer le parser
from avis_critiques_parser import AvisCritiquesParser, BookMention

def test_parser():
    print("=== Test du Parser d'Avis Critiques ===")
    
    # Test avec un exemple simple
    sample_avis = """## 1. LIVRES DISCUTÉS AU PROGRAMME du 15 décembre 2024

| Auteur | Titre | Éditeur | Avis détaillés des critiques | Note moyenne | Nb critiques | Coup de cœur | Chef d'œuvre |
|--------|-------|---------|------------------------------|--------------|--------------|-------------|-------------|
| Marie Darrieussecq | Kakapo | Gallimard | **Elisabeth Philippe**: "Magnifique" (9) | 8.5 | 2 | Elisabeth Philippe | |
| Alice Zeniter | L'Art de perdre | Actes Sud | **Michel Crépu**: "Excellent" (9) | 8.0 | 2 | Michel Crépu | |

## 2. COUPS DE CŒUR DES CRITIQUES du 15 décembre 2024

| Auteur | Titre | Éditeur | Critique | Note | Commentaire |
|--------|-------|---------|----------|------|-------------|
| Kamel Daoud | Zabor ou les Psaumes | Actes Sud | Frédéric Beigbeder | 9.5 | Un livre bouleversant |
"""

    try:
        parser = AvisCritiquesParser()
        books = parser.extract_books_from_summary(sample_avis)
        
        print(f"✅ Parser créé avec succès")
        print(f"✅ Livres extraits: {len(books)}")
        
        for i, book in enumerate(books, 1):
            print(f"{i}. {book.auteur}: '{book.titre}' ({book.section})")
            print(f"   Éditeur: {book.editeur}")
            print(f"   Note: {book.note}")
            if book.commentaire:
                print(f"   Commentaire: {book.commentaire[:50]}...")
            print()
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_parser()
    if success:
        print("✅ Test réussi!")
    else:
        print("❌ Test échoué!")