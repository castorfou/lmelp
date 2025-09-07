"""
Utilitaires de gestion des dates pour le projet LMELP

Ce module centralise toutes les fonctions de manipulation des dates,
avec support du format français standard et gestion des locales.
"""

import locale
from datetime import datetime, date
from typing import Union, Optional
import re

# Constantes
DATE_FORMAT = "%d %b %Y"
LOCALE_FR = "fr_FR.UTF-8"

# Exports du module
__all__ = [
    "DATE_FORMAT",
    "LOCALE_FR",
    "format_date",
    "parse_date",
    "is_valid_date",
    "setup_french_locale",
]


def setup_french_locale() -> bool:
    """
    Configure la locale française pour l'affichage des dates.

    Essaie différentes variantes de locale française avec fallback.

    Returns:
        bool: True si la locale a été configurée avec succès, False sinon
    """
    locales_to_try = [LOCALE_FR, "fr_FR", "French_France", "fr"]

    for loc in locales_to_try:
        try:
            locale.setlocale(locale.LC_TIME, loc)
            return True
        except locale.Error:
            continue

    return False


def format_date(
    date_input: Union[datetime, date, str, None], date_format: str = DATE_FORMAT
) -> Optional[str]:
    """
    Formate une date selon le format français standard.

    Args:
        date_input: Date à formater (datetime, date, string ISO, ou None)
        date_format: Format de sortie (défaut: DATE_FORMAT)

    Returns:
        str: Date formatée selon le format spécifié, ou None si input None

    Raises:
        ValueError: Si la date d'entrée est invalide
    """
    if date_input is None:
        return None

    # Conversion en datetime si nécessaire
    if isinstance(date_input, str):
        try:
            dt = parse_date(date_input)
            if dt is None:
                raise ValueError(f"Invalid date format: {date_input}")
        except ValueError:
            raise ValueError(f"Invalid date format: {date_input}")
    elif isinstance(date_input, date) and not isinstance(date_input, datetime):
        dt = datetime.combine(date_input, datetime.min.time())
    elif isinstance(date_input, datetime):
        dt = date_input
    else:
        raise ValueError(f"Unsupported date type: {type(date_input)}")

    # Essayer d'abord avec la locale française
    if setup_french_locale():
        formatted = dt.strftime(date_format)
        # Vérifier si on obtient des mois français (pas de majuscules en début)
        if not any(
            month in formatted
            for month in [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ]
        ):
            return formatted

    # Fallback : traduction manuelle des mois
    formatted = dt.strftime(date_format)
    month_translations = {
        "Jan": "jan",
        "Feb": "fév",
        "Mar": "mar",
        "Apr": "avr",
        "May": "mai",
        "Jun": "juin",
        "Jul": "juil",
        "Aug": "aoû",
        "Sep": "sep",
        "Oct": "oct",
        "Nov": "nov",
        "Dec": "déc",
        "January": "janvier",
        "February": "février",
        "March": "mars",
        "April": "avril",
        "June": "juin",
        "July": "juillet",
        "August": "août",
        "September": "septembre",
        "October": "octobre",
        "November": "novembre",
        "December": "décembre",
    }

    for en_month, fr_month in month_translations.items():
        formatted = formatted.replace(en_month, fr_month)

    # Supprimer le 0 devant les jours si présent (08 -> 8)
    formatted = re.sub(r"\b0(\d)", r"\1", formatted)

    return formatted


def parse_date(date_string: Union[str, None]) -> Optional[datetime]:
    """
    Parse une chaîne de date en objet datetime.

    Supporte plusieurs formats:
    - Format français: "15 jan 2023"
    - Format ISO: "2023-01-15T20:00:00Z"
    - Format simple: "2023-01-15"

    Args:
        date_string: Chaîne à parser ou None

    Returns:
        datetime: Objet datetime parsé, ou None si input None/vide

    Raises:
        ValueError: Si le format de date n'est pas reconnu
    """
    if not date_string:
        return None

    date_string = date_string.strip()
    if not date_string:
        return None

    # Traduction des mois français vers anglais pour le parsing
    # On privilégie les abréviations car le format par défaut est "%d %b %Y"
    month_translations = {
        "jan": "Jan",
        "fév": "Feb",
        "mar": "Mar",
        "avr": "Apr",
        "mai": "May",
        "juin": "Jun",
        "juil": "Jul",
        "aoû": "Aug",
        "sep": "Sep",
        "oct": "Oct",
        "nov": "Nov",
        "déc": "Dec",
        # Versions longues vers abréviations aussi
        "janvier": "Jan",
        "février": "Feb",
        "mars": "Mar",
        "avril": "Apr",
        "juillet": "Jul",
        "août": "Aug",
        "septembre": "Sep",
        "octobre": "Oct",
        "novembre": "Nov",
        "décembre": "Dec",
    }

    # Créer une version traduite pour le parsing
    translated_string = date_string
    for fr_month, en_month in month_translations.items():
        translated_string = translated_string.replace(fr_month, en_month)

    # Formats à essayer dans l'ordre
    formats_to_try = [
        DATE_FORMAT,  # "15 jan 2023" -> "15 Jan 2023"
        "%Y-%m-%dT%H:%M:%SZ",  # "2023-01-15T20:00:00Z"
        "%Y-%m-%dT%H:%M:%S",  # "2023-01-15T20:00:00"
        "%Y-%m-%d",  # "2023-01-15"
        "%d/%m/%Y",  # "15/01/2023"
        "%d-%m-%Y",  # "15-01-2023"
    ]

    # Essayer d'abord avec la chaîne traduite
    for fmt in formats_to_try:
        try:
            return datetime.strptime(translated_string, fmt)
        except ValueError:
            continue

    # Si ça échoue, essayer avec la chaîne originale
    for fmt in formats_to_try:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date: {date_string}")


def is_valid_date(date_input: Union[datetime, date, str, None, any]) -> bool:
    """
    Vérifie si une entrée représente une date valide.

    Args:
        date_input: Valeur à vérifier

    Returns:
        bool: True si l'entrée est une date valide, False sinon
    """
    if date_input is None:
        return False

    # Objets datetime/date sont toujours valides
    if isinstance(date_input, (datetime, date)):
        return True

    # Pour les chaînes, essayer de les parser
    if isinstance(date_input, str):
        # Chaînes vides ou whitespace uniquement sont invalides
        if not date_input.strip():
            return False
        try:
            result = parse_date(date_input)
            return result is not None
        except (ValueError, TypeError):
            return False

    # Tous les autres types sont invalides
    return False
