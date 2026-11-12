"""Testes adicionais: regras de status (somente CONFIRMED é faturável)."""

import pytest
from helpers import run_cli

from onfly_report.services.status_policy import is_billable


@pytest.mark.parametrize(
    ("status", "expected"),
    [("CONFIRMED", True), ("CANCELLED", False), ("NO_SHOW", False)],
)
def test_only_confirmed_is_billable(status, expected):
    assert is_billable(status) is expected


def test_cancelled_and_no_show_never_reach_by_month_or_top_hotels(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {
                "reservation_id": "R-1",
                "status": "CONFIRMED",
                "hotel_id": "H01",
                "hotel_name": "Hotel A",
                "checkin_date": "2025-01-10",
                "checkout_date": "2025-01-12",
                "amount": "200.00",
            },
            {
                "reservation_id": "R-2",
                "status": "CANCELLED",
                "hotel_id": "H02",
                "hotel_name": "Hotel B",
                "checkin_date": "2025-03-10",
                "checkout_date": "2025-03-12",
                "amount": "900.00",
            },
            {
                "reservation_id": "R-3",
                "status": "NO_SHOW",
                "hotel_id": "H03",
                "hotel_name": "Hotel C",
                "checkin_date": "2025-04-10",
                "checkout_date": "2025-04-12",
                "amount": "800.00",
            },
        ],
    )
    # Todas as reservas contam nas contagens...
    assert report["summary"]["total_reservations"] == 3
    # ...mas só a CONFIRMED entra em noites, valores, mês e ranking.
    assert report["summary"]["total_room_nights"] == 2
    assert report["summary"]["total_amount_brl"] == "200.00"
    assert [month["month"] for month in report["by_month"]] == ["2025-01"]
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01"]


def test_report_without_confirmed_reservations_has_zeroed_totals(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "status": "CANCELLED"},
            {"reservation_id": "R-2", "status": "NO_SHOW"},
        ],
    )
    assert report["summary"] == {
        "total_reservations": 2,
        "confirmed_reservations": 0,
        "cancelled_reservations": 1,
        "no_show_reservations": 1,
        "total_room_nights": 0,
        "total_amount_brl": "0.00",
        "average_nightly_rate_brl": "0.00",
    }
    assert report["by_month"] == []
    assert report["top_hotels"] == []
