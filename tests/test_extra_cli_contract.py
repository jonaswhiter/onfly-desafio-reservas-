"""Testes adicionais: contrato do CLI (formato do JSON, códigos de saída e argumentos)."""

import json
import re

from cli_runner import RATES_TEXT, invoke, run_rows, write_rows
from helpers import run_cli

SUMMARY_KEYS = [
    "total_reservations",
    "confirmed_reservations",
    "cancelled_reservations",
    "no_show_reservations",
    "total_room_nights",
    "total_amount_brl",
    "average_nightly_rate_brl",
]
MONEY_FORMAT = re.compile(r"\d+\.\d{2}")


def test_report_follows_the_documented_schema(tmp_path):
    report = run_cli(tmp_path, [{"reservation_id": "R-1"}, {"reservation_id": "R-2", "status": "CANCELLED"}])

    assert list(report) == ["report_version", "generated_at", "summary", "by_month", "top_hotels"]
    assert report["report_version"] == "1.0"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-03:00", report["generated_at"])

    assert list(report["summary"]) == SUMMARY_KEYS
    for key in SUMMARY_KEYS:
        value = report["summary"][key]
        if key.endswith("_brl"):
            assert isinstance(value, str) and MONEY_FORMAT.fullmatch(value)
        else:
            assert isinstance(value, int)

    assert list(report["by_month"][0]) == ["month", "reservations", "room_nights", "total_brl"]
    assert list(report["top_hotels"][0]) == ["hotel_id", "hotel_name", "room_nights", "total_brl"]


def test_header_only_file_produces_an_empty_report(tmp_path):
    report = run_cli(tmp_path, [])
    assert report["summary"]["total_reservations"] == 0
    assert report["summary"]["total_amount_brl"] == "0.00"
    assert report["summary"]["average_nightly_rate_brl"] == "0.00"
    assert report["by_month"] == []
    assert report["top_hotels"] == []


def test_summary_is_printed_to_stdout(tmp_path):
    process, _ = run_rows(tmp_path, [{"reservation_id": "R-1"}, {"reservation_id": "R-2", "status": "CANCELLED"}])
    assert process.returncode == 0, process.stderr
    assert process.stdout.strip() == "Reservas: 2 | Confirmadas: 1 | Noites: 1 | Total BRL: 100.00"


def test_default_top_is_five(tmp_path):
    rows = [{"reservation_id": f"R-{i}", "hotel_id": f"H0{i}", "hotel_name": f"Hotel {i}"} for i in range(1, 8)]
    process, output_path = run_rows(tmp_path, rows)  # sem --top
    assert process.returncode == 0, process.stderr
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(report["top_hotels"]) == 5


def test_default_output_is_created_under_output_directory(tmp_path):
    input_path = tmp_path / "reservas.csv"
    rates_path = tmp_path / "rates.csv"
    write_rows(input_path, [{}])
    rates_path.write_text(RATES_TEXT, encoding="utf-8")

    process = invoke(["--input", str(input_path), "--rates", str(rates_path)], cwd=tmp_path)

    assert process.returncode == 0, process.stderr
    assert (tmp_path / "output" / "report.json").is_file()


def test_top_must_be_at_least_one(tmp_path):
    process, output_path = run_rows(tmp_path, [{}], top=0)
    assert process.returncode == 2
    assert not output_path.exists()


def test_top_must_be_an_integer(tmp_path):
    process, output_path = run_rows(tmp_path, [{}], top="abc")
    assert process.returncode == 2
    assert not output_path.exists()


def test_missing_required_argument_exits_with_2(tmp_path):
    rates_path = tmp_path / "rates.csv"
    rates_path.write_text(RATES_TEXT, encoding="utf-8")
    process = invoke(["--rates", str(rates_path)])  # falta --input
    assert process.returncode == 2


def test_missing_input_file_exits_with_2(tmp_path):
    rates_path = tmp_path / "rates.csv"
    rates_path.write_text(RATES_TEXT, encoding="utf-8")
    output_path = tmp_path / "report.json"
    process = invoke(
        ["--input", str(tmp_path / "nao-existe.csv"), "--rates", str(rates_path), "--output", str(output_path)]
    )
    assert process.returncode == 2
    assert not output_path.exists()


def test_missing_required_column_exits_with_2(tmp_path):
    input_path = tmp_path / "reservas.csv"
    rates_path = tmp_path / "rates.csv"
    input_path.write_text("reservation_id,status\nR-1,CONFIRMED\n", encoding="utf-8")
    rates_path.write_text(RATES_TEXT, encoding="utf-8")
    process = invoke(["--input", str(input_path), "--rates", str(rates_path), "--output", str(tmp_path / "r.json")])
    assert process.returncode == 2
    assert "colunas obrigatórias ausentes" in process.stderr


def test_invalid_date_exits_with_2_and_points_to_the_line(tmp_path):
    process, output_path = run_rows(tmp_path, [{"checkin_date": "10/01/2025"}])
    assert process.returncode == 2
    assert "linha 2" in process.stderr
    assert not output_path.exists()


def test_currency_without_rate_exits_with_2(tmp_path):
    process, output_path = run_rows(tmp_path, [{"currency": "GBP"}])
    assert process.returncode == 2
    assert "GBP" in process.stderr
    assert not output_path.exists()
