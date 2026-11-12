"""Testes adicionais: noites de quarto (diferença real de datas, virada de mês/ano, bissexto)."""

from datetime import date

import pytest
from helpers import run_cli

from onfly_report.services.stay_calculator import calculate_room_nights


@pytest.mark.parametrize(
    ("checkin", "checkout", "rooms", "expected"),
    [
        (date(2025, 1, 10), date(2025, 1, 13), 1, 3),  # exemplo do README: 10/01 -> 13/01 = 3 noites
        (date(2025, 1, 10), date(2025, 1, 11), 1, 1),  # uma noite
        (date(2025, 1, 30), date(2025, 2, 2), 2, 6),  # virada de mês, 2 quartos
        (date(2024, 12, 31), date(2025, 1, 2), 3, 6),  # virada de ano, 3 quartos
        (date(2024, 2, 28), date(2024, 3, 1), 1, 2),  # ano bissexto: existe 29/02
        (date(2025, 2, 28), date(2025, 3, 1), 1, 1),  # ano comum: não existe 29/02
    ],
)
def test_room_nights_is_non_inclusive_date_difference_times_rooms(checkin, checkout, rooms, expected):
    assert calculate_room_nights(checkin, checkout, rooms) == expected


def test_nights_across_year_boundary(tmp_path):
    report = run_cli(
        tmp_path,
        [{"checkin_date": "2024-12-31", "checkout_date": "2025-01-02", "rooms": "2"}],
    )
    assert report["summary"]["total_room_nights"] == 4
    assert report["by_month"] == [{"month": "2024-12", "reservations": 1, "room_nights": 4, "total_brl": "100.00"}]


def test_by_month_uses_checkin_month_and_is_sorted_ascending(tmp_path):
    report = run_cli(
        tmp_path,
        [
            # Estadia que termina em março, mas conta em fevereiro (mês do check-in).
            {"reservation_id": "R-1", "checkin_date": "2025-02-27", "checkout_date": "2025-03-02", "amount": "300.00"},
            # Fora de ordem de propósito: dezembro/2024 deve vir antes de fevereiro/2025.
            {"reservation_id": "R-2", "checkin_date": "2024-12-30", "checkout_date": "2025-01-03", "amount": "400.00"},
            {"reservation_id": "R-3", "checkin_date": "2025-02-10", "checkout_date": "2025-02-12", "amount": "50.00"},
        ],
    )
    assert report["by_month"] == [
        {"month": "2024-12", "reservations": 1, "room_nights": 4, "total_brl": "400.00"},
        {"month": "2025-02", "reservations": 2, "room_nights": 5, "total_brl": "350.00"},
    ]
