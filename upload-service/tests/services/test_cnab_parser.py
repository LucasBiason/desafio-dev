"""Tests for CnabParser."""

import pytest

from app.services.cnab_parser import CnabParser

# 21 valid CNAB lines — mirrors the reference CNAB.txt from the project assets.
CNAB_LINES = [
    "3201903010000014200096206760174753****3153153453JOAO MACEDO   BAR DO JOAO       ",
    "5201903010000013200556418150633123****7687145607MARIA JOSEFINALOJA DO O - MATRIZ",
    "3201903010000012200845152540736777****1313172712MARCOS PEREIRAMERCADO DA AVENIDA",
    "2201903010000011200096206760173648****0099234234JOAO MACEDO   BAR DO JOAO       ",
    "1201903010000015200096206760171234****7890233000JOAO MACEDO   BAR DO JOAO       ",
    "2201903010000010700845152540738723****9987123333MARCOS PEREIRAMERCADO DA AVENIDA",
    "2201903010000050200845152540738473****1231231233MARCOS PEREIRAMERCADO DA AVENIDA",
    "3201903010000060200232702980566777****1313172712JOSE COSTA    MERCEARIA 3 IRMAOS",
    "1201903010000020000556418150631234****3324090002MARIA JOSEFINALOJA DO O - MATRIZ",
    "5201903010000080200845152540733123****7687145607MARCOS PEREIRAMERCADO DA AVENIDA",
    "2201903010000010200232702980568473****1231231233JOSE COSTA    MERCEARIA 3 IRMAOS",
    "3201903010000610200232702980566777****1313172712JOSE COSTA    MERCEARIA 3 IRMAOS",
    "4201903010000015232556418150631234****6678100000MARIA JOSEFINALOJA DO O - FILIAL",
    "8201903010000010203845152540732344****1222123222MARCOS PEREIRAMERCADO DA AVENIDA",
    "3201903010000010300232702980566777****1313172712JOSE COSTA    MERCEARIA 3 IRMAOS",
    "9201903010000010200556418150636228****9090000000MARIA JOSEFINALOJA DO O - MATRIZ",
    "4201906010000050617845152540731234****2231100000MARCOS PEREIRAMERCADO DA AVENIDA",
    "2201903010000010900232702980568723****9987123333JOSE COSTA    MERCEARIA 3 IRMAOS",
    "8201903010000000200845152540732344****1222123222MARCOS PEREIRAMERCADO DA AVENIDA",
    "2201903010000000500232702980567677****8778141808JOSE COSTA    MERCEARIA 3 IRMAOS",
    "3201903010000019200845152540736777****1313172712MARCOS PEREIRAMERCADO DA AVENIDA",
]
CNAB_CONTENT = "\n".join(CNAB_LINES).encode("utf-8")

VALID_LINE = "3201903010000014200096206760174753****3153153453JOAO MACEDO   BAR DO JOAO       "


class TestCnabParser:
    """Tests for CnabParser.parse and CnabParser.parse_line."""

    def test_parse_valid_file(self):
        """Parse full CNAB content returns 21 transactions."""
        parser = CnabParser()
        transactions = parser.parse(CNAB_CONTENT)
        assert len(transactions) == 21

    def test_parse_line_valid(self):
        """Valid line returns a dict with all expected fields."""
        parser = CnabParser()
        result = parser.parse_line(VALID_LINE)
        assert result is not None
        assert "type_code" in result
        assert "date" in result
        assert "amount" in result
        assert "cpf" in result
        assert "card" in result
        assert "time" in result
        assert "store_owner" in result
        assert "store_name" in result

    def test_parse_line_empty(self):
        """Empty line returns None."""
        parser = CnabParser()
        assert parser.parse_line("") is None

    def test_parse_line_short(self):
        """Line shorter than 80 chars returns None."""
        parser = CnabParser()
        assert parser.parse_line("320190301000001") is None

    def test_parse_line_invalid_type(self):
        """Non-integer type code returns None."""
        parser = CnabParser()
        line = "X" + VALID_LINE[1:]
        assert parser.parse_line(line) is None

    def test_parse_line_invalid_amount(self):
        """Non-integer amount field returns None."""
        parser = CnabParser()
        line = VALID_LINE[0:1] + VALID_LINE[1:9] + "XXXXXXXXXX" + VALID_LINE[19:]
        assert parser.parse_line(line) is None

    def test_amount_normalization(self):
        """Amount 14200 is formatted as '142.00'."""
        parser = CnabParser()
        result = parser.parse_line(VALID_LINE)
        assert result is not None
        assert result["amount"] == "142.00"

    def test_date_formatting(self):
        """Date 20190301 is formatted as '2019-03-01'."""
        parser = CnabParser()
        result = parser.parse_line(VALID_LINE)
        assert result is not None
        assert result["date"] == "2019-03-01"

    def test_time_formatting(self):
        """Time 153453 is formatted as '15:34:53'."""
        parser = CnabParser()
        result = parser.parse_line(VALID_LINE)
        assert result is not None
        assert result["time"] == "15:34:53"

    def test_strip_names(self):
        """Trailing spaces in store_owner and store_name are removed."""
        parser = CnabParser()
        result = parser.parse_line(VALID_LINE)
        assert result is not None
        assert result["store_owner"] == result["store_owner"].strip()
        assert result["store_name"] == result["store_name"].strip()
