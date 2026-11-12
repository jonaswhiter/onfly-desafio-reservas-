"""Testes adicionais com os arquivos reais de ``data/``.

Os testes fornecidos usam no máximo 4 reservas. Estes rodam o CLI nos CSVs completos para
pegar defeitos que só aparecem com volume (por exemplo, leitura truncada) e para conferir a
amostra de validação publicada no README.
"""

import json
from pathlib import Path

from cli_runner import invoke
from helpers import PROJECT_ROOT

DATA_DIR = PROJECT_ROOT / "data"
RATES_FILE = DATA_DIR / "taxas_cambio.csv"


def _run_on_data_file(tmp_path: Path, reservations_file: str, top: int = 5) -> dict:
    output_path = tmp_path / "report.json"
    process = invoke(
        [
            "--input",
            str(DATA_DIR / reservations_file),
            "--rates",
            str(RATES_FILE),
            "--output",
            str(output_path),
            "--top",
            str(top),
        ]
    )
    assert process.returncode == 0, process.stderr
    return json.loads(output_path.read_text(encoding="utf-8"))


def _by_month(report: dict) -> list[tuple]:
    return [(m["month"], m["reservations"], m["room_nights"], m["total_brl"]) for m in report["by_month"]]


def _top_hotels(report: dict) -> list[tuple]:
    return [(h["hotel_id"], h["hotel_name"], h["room_nights"], h["total_brl"]) for h in report["top_hotels"]]


def test_validation_sample_matches_the_readme(tmp_path):
    report = _run_on_data_file(tmp_path, "exemplo-validacao.csv")
    assert report["summary"] == {
        "total_reservations": 12,
        "confirmed_reservations": 9,
        "cancelled_reservations": 2,
        "no_show_reservations": 1,
        "total_room_nights": 28,
        "total_amount_brl": "7566.00",
        "average_nightly_rate_brl": "270.21",
    }
    assert _by_month(report) == [
        ("2025-01", 8, 25, "6684.00"),
        ("2025-02", 1, 3, "882.00"),
    ]
    assert _top_hotels(report) == [
        ("H01", "Hotel Aurora Paulista", 3, "1200.00"),
        ("H02", "Hotel Mirante", 2, "1084.00"),
        ("H12", "Hotel Miami Beach", 1, "1000.00"),
        ("H10", "Hotel Madrid, Gran Vía", 4, "900.00"),
        ("H09", "Hotel Lisboa, Centro", 3, "882.00"),
    ]


def test_full_dataset_is_read_completely(tmp_path):
    """O CSV tem 300 reservas: nenhuma pode ficar de fora da leitura."""
    report = _run_on_data_file(tmp_path, "reservas_hoteis.csv")
    summary = report["summary"]
    assert summary["total_reservations"] == 300
    assert summary["confirmed_reservations"] == 235
    assert summary["cancelled_reservations"] == 31
    assert summary["no_show_reservations"] == 34
    assert (
        summary["confirmed_reservations"] + summary["cancelled_reservations"] + summary["no_show_reservations"]
        == summary["total_reservations"]
    )


def test_full_dataset_report(tmp_path):
    """Valores esperados calculados à parte, com frações exatas, a partir das regras do README."""
    report = _run_on_data_file(tmp_path, "reservas_hoteis.csv")
    assert report["summary"] == {
        "total_reservations": 300,
        "confirmed_reservations": 235,
        "cancelled_reservations": 31,
        "no_show_reservations": 34,
        "total_room_nights": 1347,
        "total_amount_brl": "396170.00",
        "average_nightly_rate_brl": "294.11",
    }
    assert _by_month(report) == [
        ("2024-12", 35, 174, "61335.80"),
        ("2025-01", 37, 235, "64662.89"),
        ("2025-02", 26, 138, "45991.09"),
        ("2025-03", 39, 215, "65984.99"),
        ("2025-04", 21, 146, "31335.97"),
        ("2025-05", 39, 196, "63507.98"),
        ("2025-06", 38, 243, "63351.29"),
    ]
    assert [(hotel_id, nights, total) for hotel_id, _name, nights, total in _top_hotels(report)] == [
        ("H06", 160, "45165.46"),
        ("H10", 120, "45041.69"),
        ("H12", 106, "41647.69"),
        ("H07", 148, "39920.52"),
        ("H11", 102, "37455.69"),
    ]
