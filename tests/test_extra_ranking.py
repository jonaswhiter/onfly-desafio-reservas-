"""Testes adicionais: ranking de hotéis (soma por hotel, desempate e limite --top)."""

from helpers import run_cli


def _hotel_rows(count: int) -> list[dict[str, str]]:
    """Um hotel por reserva, com valores crescentes: H01=100, H02=200, ..."""
    return [
        {
            "reservation_id": f"R-{index}",
            "hotel_id": f"H{index:02d}",
            "hotel_name": f"Hotel {index}",
            "amount": f"{index * 100}.00",
        }
        for index in range(1, count + 1)
    ]


def test_ranking_sums_all_reservations_of_the_same_hotel(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "hotel_name": "Hotel A", "amount": "600.00"},
            {"reservation_id": "R-2", "hotel_id": "H01", "hotel_name": "Hotel A", "amount": "600.00"},
            {"reservation_id": "R-3", "hotel_id": "H02", "hotel_name": "Hotel B", "amount": "1000.00"},
        ],
    )
    assert [(h["hotel_id"], h["room_nights"], h["total_brl"]) for h in report["top_hotels"]] == [
        ("H01", 2, "1200.00"),
        ("H02", 1, "1000.00"),
    ]


def test_ranking_tie_breaks_by_hotel_id_ascending(tmp_path):
    report = run_cli(
        tmp_path,
        [
            # Fora de ordem de propósito: o desempate não pode depender da ordem do arquivo.
            {"reservation_id": "R-1", "hotel_id": "H03", "hotel_name": "Hotel C", "amount": "500.00"},
            {"reservation_id": "R-2", "hotel_id": "H01", "hotel_name": "Hotel A", "amount": "500.00"},
            {"reservation_id": "R-3", "hotel_id": "H02", "hotel_name": "Hotel B", "amount": "500.00"},
        ],
    )
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01", "H02", "H03"]


def test_top_limits_the_number_of_hotels(tmp_path):
    report = run_cli(tmp_path, _hotel_rows(4), top=2)
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H04", "H03"]


def test_top_larger_than_the_number_of_hotels_returns_all_of_them(tmp_path):
    report = run_cli(tmp_path, _hotel_rows(4), top=10)
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H04", "H03", "H02", "H01"]
