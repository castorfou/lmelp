#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'nbs'))

# Mock BeautifulSoup
class MockBeautifulSoup:
    def __init__(self, html, parser):
        self.text = html
    
    def get_text(self):
        import re
        text = re.sub(r'<[^>]+>', '', self.text)
        return text.strip()

sys.modules['bs4'] = type(sys)('bs4')
sys.modules['bs4'].BeautifulSoup = MockBeautifulSoup

from avis_critiques_parser import AvisCritiquesParser

def test_rating_extraction():
    parser = AvisCritiquesParser()
    
    # Test 1: HTML avec note décimale
    rating_html = '<span style="background-color: #4CAF50; color: white;">8.5</span>'
    result = parser._extract_rating(rating_html)
    print(f"Test 1 - HTML avec 8.5: {result} (attendu: 8.5)")
    
    # Test 2: Nombre simple
    rating_simple = "8.5"
    result = parser._extract_rating(rating_simple)
    print(f"Test 2 - Nombre simple 8.5: {result} (attendu: 8.5)")
    
    # Test 3: Nombre entier
    rating_int = "9"
    result = parser._extract_rating(rating_int)
    print(f"Test 3 - Nombre entier 9: {result} (attendu: 9.0)")

def test_section_detection():
    parser = AvisCritiquesParser()
    
    sample_avis = """## 2. COUPS DE CŒUR DES CRITIQUES

| Auteur | Titre | Éditeur | Critique | Note | Commentaire |
|--------|-------|---------|----------|------|-------------|
| Test Auteur | Test Titre | Test Éditeur | Test Critique | 8.0 | Test |
"""
    
    import re
    patterns = [
        r"##\s*2\.\s*COUPS DE C[ŒO]EUR DES CRITIQUES.*?\n(.*?)$",
        r"##\s*2\.\s*COUPS DE COEUR DES CRITIQUES.*?\n(.*?)$",
        r"##\s*2\.\s*COUPS DE C.*?EUR DES CRITIQUES.*?\n(.*?)$",
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, sample_avis, re.DOTALL | re.IGNORECASE)
        print(f"Pattern {i+1}: {'✅' if match else '❌'} - {pattern}")
        if match:
            print(f"  Contenu: {match.group(1)[:50]}...")

if __name__ == "__main__":
    print("=== Test d'extraction des notes ===")
    test_rating_extraction()
    
    print("\n=== Test de détection des sections ===")
    test_section_detection()