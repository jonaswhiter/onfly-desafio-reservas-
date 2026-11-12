"""Conversão de valores para BRL."""

from __future__ import annotations

from decimal import Decimal

from ..exceptions import InputFileError


def convert_to_brl(amount: Decimal, currency: str, rates: dict[str, Decimal]) -> Decimal:
    """Converte um valor na moeda informada para BRL: ``amount * rate_to_brl``.

    Usa apenas ``Decimal`` (nunca ``float``) e não arredonda: o arredondamento acontece
    somente na serialização do relatório.
    """
    try:
        rate = rates[currency]
    except KeyError as err:
        raise InputFileError(f"sem taxa de câmbio para a moeda {currency!r}") from err
    return amount * rate
