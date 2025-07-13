"""
Tests unitaires pour le module date_utils

Ce module contient tous les tests pour les utilitaires de gestion des dates.
Suit l'approche TDD en définissant le comportement attendu avant l'implémentation.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, date
import locale


@pytest.fixture
def mock_locale():
    """Fixture pour mocker la configuration locale"""
    with patch("locale.setlocale") as mock_setlocale:
        yield mock_setlocale


class TestDateUtilsConstants:
    """Tests pour les constantes du module date_utils"""

    def test_date_format_constant(self):
        """Test que DATE_FORMAT est correctement défini"""
        from nbs.date_utils import DATE_FORMAT

        # Assert
        assert DATE_FORMAT == "%d %b %Y"
        assert isinstance(DATE_FORMAT, str)

    def test_locale_constant(self):
        """Test que LOCALE_FR est correctement défini"""
        from nbs.date_utils import LOCALE_FR

        # Assert
        assert LOCALE_FR == "fr_FR.UTF-8"
        assert isinstance(LOCALE_FR, str)

    def test_module_exports(self):
        """Test des exports __all__ du module"""
        from nbs import date_utils

        expected_exports = [
            "DATE_FORMAT",
            "LOCALE_FR",
            "format_date",
            "parse_date",
            "is_valid_date",
            "setup_french_locale",
        ]

        # Assert
        assert date_utils.__all__ == expected_exports

        # Verify all exports exist
        for export in expected_exports:
            assert hasattr(date_utils, export), f"Missing export: {export}"


class TestFormatDate:
    """Tests pour la fonction format_date"""

    def test_format_date_datetime_object(self, mock_locale):
        """Test format_date avec un objet datetime"""
        from nbs.date_utils import format_date

        test_date = datetime(2023, 1, 15, 10, 30, 0)

        result = format_date(test_date)

        # Assert
        assert result == "15 jan 2023"

    def test_format_date_date_object(self, mock_locale):
        """Test format_date avec un objet date"""
        from nbs.date_utils import format_date

        test_date = date(2023, 3, 8)

        result = format_date(test_date)

        # Assert
        assert result == "8 mar 2023"

    def test_format_date_string_iso(self, mock_locale):
        """Test format_date avec une chaîne ISO"""
        from nbs.date_utils import format_date

        test_date_str = "2023-06-22T20:00:00Z"

        result = format_date(test_date_str)

        # Assert
        assert result == "22 juin 2023"

    def test_format_date_string_simple(self, mock_locale):
        """Test format_date avec une chaîne simple YYYY-MM-DD"""
        from nbs.date_utils import format_date

        test_date_str = "2023-12-25"

        result = format_date(test_date_str)

        # Assert
        assert result == "25 déc 2023"

    def test_format_date_none_input(self):
        """Test format_date avec None"""
        from nbs.date_utils import format_date

        result = format_date(None)

        # Assert
        assert result is None

    def test_format_date_invalid_string(self):
        """Test format_date avec une chaîne invalide"""
        from nbs.date_utils import format_date

        with pytest.raises(ValueError, match="Invalid date format"):
            format_date("invalid-date")

    def test_format_date_custom_format(self, mock_locale):
        """Test format_date avec un format personnalisé"""
        from nbs.date_utils import format_date

        test_date = datetime(2023, 1, 15)
        custom_format = "%Y-%m-%d"

        result = format_date(test_date, date_format=custom_format)

        # Assert
        assert result == "2023-01-15"


class TestParseDate:
    """Tests pour la fonction parse_date"""

    def test_parse_date_french_format(self, mock_locale):
        """Test parse_date avec format français"""
        from nbs.date_utils import parse_date

        date_str = "15 jan 2023"

        result = parse_date(date_str)

        # Assert
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 15

    def test_parse_date_different_months(self, mock_locale):
        """Test parse_date avec différents mois français"""
        from nbs.date_utils import parse_date

        test_cases = [
            ("8 mar 2023", 3),
            ("22 juin 2023", 6),
            ("1 mai 2023", 5),
            ("25 déc 2023", 12),
        ]

        for date_str, expected_month in test_cases:
            result = parse_date(date_str)
            assert result.month == expected_month

    def test_parse_date_iso_format(self):
        """Test parse_date avec format ISO"""
        from nbs.date_utils import parse_date

        date_str = "2023-01-15T20:00:00Z"

        result = parse_date(date_str)

        # Assert
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 15

    def test_parse_date_simple_format(self):
        """Test parse_date avec format YYYY-MM-DD"""
        from nbs.date_utils import parse_date

        date_str = "2023-01-15"

        result = parse_date(date_str)

        # Assert
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 15

    def test_parse_date_none_input(self):
        """Test parse_date avec None"""
        from nbs.date_utils import parse_date

        result = parse_date(None)

        # Assert
        assert result is None

    def test_parse_date_empty_string(self):
        """Test parse_date avec chaîne vide"""
        from nbs.date_utils import parse_date

        result = parse_date("")

        # Assert
        assert result is None

    def test_parse_date_invalid_format(self):
        """Test parse_date avec format invalide"""
        from nbs.date_utils import parse_date

        with pytest.raises(ValueError, match="Unable to parse date"):
            parse_date("invalid-date-format")


class TestIsValidDate:
    """Tests pour la fonction is_valid_date"""

    def test_is_valid_date_datetime_object(self):
        """Test is_valid_date avec objet datetime"""
        from nbs.date_utils import is_valid_date

        test_date = datetime(2023, 1, 15)

        result = is_valid_date(test_date)

        # Assert
        assert result is True

    def test_is_valid_date_date_object(self):
        """Test is_valid_date avec objet date"""
        from nbs.date_utils import is_valid_date

        test_date = date(2023, 1, 15)

        result = is_valid_date(test_date)

        # Assert
        assert result is True

    def test_is_valid_date_valid_string(self):
        """Test is_valid_date avec chaîne valide"""
        from nbs.date_utils import is_valid_date

        test_cases = ["15 jan 2023", "2023-01-15", "2023-01-15T20:00:00Z"]

        for date_str in test_cases:
            result = is_valid_date(date_str)
            assert result is True, f"Failed for: {date_str}"

    def test_is_valid_date_invalid_string(self):
        """Test is_valid_date avec chaîne invalide"""
        from nbs.date_utils import is_valid_date

        test_cases = [
            "invalid-date",
            "32 jan 2023",  # Jour invalide
            "15 xyz 2023",  # Mois invalide
            "",
            "not-a-date-at-all",
        ]

        for date_str in test_cases:
            result = is_valid_date(date_str)
            assert result is False, f"Should be invalid: {date_str}"

    def test_is_valid_date_none_input(self):
        """Test is_valid_date avec None"""
        from nbs.date_utils import is_valid_date

        result = is_valid_date(None)

        # Assert
        assert result is False

    def test_is_valid_date_other_types(self):
        """Test is_valid_date avec autres types"""
        from nbs.date_utils import is_valid_date

        test_cases = [123, [], {}, True]

        for test_input in test_cases:
            result = is_valid_date(test_input)
            assert result is False


class TestSetupFrenchLocale:
    """Tests pour la fonction setup_french_locale"""

    def test_setup_french_locale_success(self):
        """Test setup_french_locale avec succès"""
        from nbs.date_utils import setup_french_locale

        with patch("locale.setlocale") as mock_setlocale:
            mock_setlocale.return_value = "fr_FR.UTF-8"

            result = setup_french_locale()

            # Assert
            assert result is True
            mock_setlocale.assert_called_once_with(locale.LC_TIME, "fr_FR.UTF-8")

    def test_setup_french_locale_fallback(self):
        """Test setup_french_locale avec fallback"""
        from nbs.date_utils import setup_french_locale

        with patch("locale.setlocale") as mock_setlocale:
            # Premier appel échoue, deuxième réussit
            mock_setlocale.side_effect = [locale.Error("Not available"), "fr_FR"]

            result = setup_french_locale()

            # Assert
            assert result is True
            assert mock_setlocale.call_count == 2

    def test_setup_french_locale_failure(self):
        """Test setup_french_locale avec échec total"""
        from nbs.date_utils import setup_french_locale

        with patch("locale.setlocale") as mock_setlocale:
            # Tous les appels échouent
            mock_setlocale.side_effect = locale.Error("No French locale available")

            result = setup_french_locale()

            # Assert
            assert result is False


class TestDateUtilsIntegration:
    """Tests d'intégration pour date_utils"""

    def test_round_trip_format_parse(self, mock_locale):
        """Test round-trip : format -> parse -> format"""
        from nbs.date_utils import format_date, parse_date

        original_date = datetime(2023, 6, 22, 15, 30, 0)

        # Format -> Parse -> Format
        formatted = format_date(original_date)
        parsed = parse_date(formatted)
        reformatted = format_date(parsed)

        # Assert
        assert formatted == reformatted
        assert parsed.year == original_date.year
        assert parsed.month == original_date.month
        assert parsed.day == original_date.day

    def test_validation_consistency(self):
        """Test cohérence entre is_valid_date et parse_date"""
        from nbs.date_utils import is_valid_date, parse_date

        test_cases = ["15 jan 2023", "2023-01-15", "invalid-date", None, ""]

        for test_case in test_cases:
            is_valid = is_valid_date(test_case)

            if is_valid:
                # Si is_valid_date dit que c'est valide, parse_date ne doit pas lever d'exception
                try:
                    result = parse_date(test_case)
                    assert result is not None
                except ValueError:
                    pytest.fail(f"parse_date failed for valid date: {test_case}")
            else:
                # Si is_valid_date dit que ce n'est pas valide
                if test_case is None or test_case == "":
                    assert parse_date(test_case) is None
                else:
                    with pytest.raises(ValueError):
                        parse_date(test_case)


class TestDateUtilsEdgeCases:
    """Tests pour les cas limites de date_utils"""

    def test_leap_year_handling(self, mock_locale):
        """Test gestion des années bissextiles"""
        from nbs.date_utils import format_date, parse_date

        # 29 février 2024 (année bissextile)
        leap_date = datetime(2024, 2, 29)

        formatted = format_date(leap_date)
        parsed = parse_date(formatted)

        # Assert
        assert parsed.year == 2024
        assert parsed.month == 2
        assert parsed.day == 29

    def test_year_boundaries(self, mock_locale):
        """Test limites d'années"""
        from nbs.date_utils import format_date, parse_date

        test_dates = [
            datetime(1900, 1, 1),
            datetime(2000, 12, 31),
            datetime(2099, 6, 15),
        ]

        for test_date in test_dates:
            formatted = format_date(test_date)
            parsed = parse_date(formatted)

            assert parsed.year == test_date.year
            assert parsed.month == test_date.month
            assert parsed.day == test_date.day

    def test_all_months_french(self, mock_locale):
        """Test tous les mois en français"""
        from nbs.date_utils import format_date

        expected_months = [
            "jan",
            "fév",
            "mar",
            "avr",
            "mai",
            "juin",
            "juil",
            "aoû",
            "sep",
            "oct",
            "nov",
            "déc",
        ]

        for month_num, expected_month in enumerate(expected_months, 1):
            test_date = datetime(2023, month_num, 15)
            formatted = format_date(test_date)

            assert expected_month in formatted.lower()
