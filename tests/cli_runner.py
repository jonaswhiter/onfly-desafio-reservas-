"""Utilitários dos testes adicionais: executam o CLI sem exigir código de saída 0.

O ``helpers.run_cli`` (fornecido) só serve para o caminho feliz. Aqui ficam as funções para
testar erros, argumentos e arquivos reais de ``data/``. O ``helpers.py`` não é alterado.
"""

from __future__ import annotations

import csv
import os
import subprocess
import sys
from pathlib import Path

from helpers import BASE, COLUMNS, PROJECT_ROOT, SRC_DIR

RATES_TEXT = "currency,rate_to_brl\nBRL,1.000000\nUSD,5.420000\nEUR,5.880000\n"


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    """Grava um CSV de reservas válido; cada linha parte de ``BASE`` e aplica as diferenças."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows({**BASE, **row} for row in rows)


def invoke(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Executa ``python -m onfly_report`` com os argumentos dados e devolve o resultado cru."""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + environment.get("PYTHONPATH", "")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "onfly_report", *args],
        cwd=str(cwd or PROJECT_ROOT),
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )


def run_rows(
    tmp_path: Path,
    rows: list[dict[str, str]],
    top: int | str | None = None,
) -> tuple[subprocess.CompletedProcess[str], Path]:
    """Roda o CLI sobre ``rows`` (sem exigir sucesso) e devolve o processo e o caminho do relatório.

    Quando ``top`` é ``None`` o argumento ``--top`` não é enviado (vale o padrão do CLI).
    """
    input_path = tmp_path / "reservas.csv"
    rates_path = tmp_path / "rates.csv"
    output_path = tmp_path / "report.json"

    write_rows(input_path, rows)
    rates_path.write_text(RATES_TEXT, encoding="utf-8")

    args = ["--input", str(input_path), "--rates", str(rates_path), "--output", str(output_path)]
    if top is not None:
        args += ["--top", str(top)]
    return invoke(args), output_path
