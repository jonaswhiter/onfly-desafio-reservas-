"""Testes adicionais: câmbio e exatidão do dinheiro (Decimal, half-up só na serialização)."""

from decimal import Decimal

import pytest
from helpers import run_cli

from onfly_report.exceptions import InputFileError
from onfly_report.services.currency_converter import convert_to_brl

RATES = {"BRL": Decimal("1.000000"), "USD": Decimal("5.420000"), "EUR": Decimal("5.880000")}


def test_convert_multiplies_amount_by_rate():
    assert convert_to_brl(Decimal("100.00"), "BRL", RATES) == Decimal("100")
    assert convert_to_brl(Decimal("100.00"), "USD", RATES) == Decimal("542")
    assert convert_to_brl(Decimal("100.00"), "EUR", RATES) == Decimal("588")


def test_convert_is_exact_decimal_arithmetic():
    result = convert_to_brl(Decimal("0.10"), "EUR", RATES)
    assert isinstance(result, Decimal)
    assert result == Decimal("0.588")  # com float seria 0.5880000000000001


def test_convert_without_rate_is_an_input_error():
    with pytest.raises(InputFileError, match="GBP"):
        convert_to_brl(Decimal("10.00"), "GBP", RATES)


def test_half_up_rounding_at_serialization(tmp_path):
    # 100.75 USD * 5.42 = 546.065 -> half-up dá 546.07 (arredondar para o par daria 546.06).
    report = run_cli(tmp_path, [{"currency": "USD", "amount": "100.75"}])
    assert report["summary"]["total_amount_brl"] == "546.07"
    assert report["by_month"][0]["total_brl"] == "546.07"
    assert report["top_hotels"][0]["total_brl"] == "546.07"


def test_rounding_happens_once_on_the_exact_sum(tmp_path):
    # Cada linha vale 0.01 USD * 5.42 = 0.0542. A soma exata é 0.1626 -> "0.16".
    # Arredondar linha a linha (0.05 + 0.05 + 0.05) daria "0.15".
    rows = [{"reservation_id": f"R-{i}", "currency": "USD", "amount": "0.01"} for i in range(3)]
    report = run_cli(tmp_path, rows)
    assert report["summary"]["total_amount_brl"] == "0.16"
    assert report["by_month"][0]["total_brl"] == "0.16"


def test_money_is_a_string_with_two_decimals_and_no_thousands_separator(tmp_path):
    report = run_cli(tmp_path, [{"amount": "1234567.5"}])
    assert report["summary"]["total_amount_brl"] == "1234567.50"
    assert report["summary"]["average_nightly_rate_brl"] == "1234567.50"
