# README-ENTREGA — Consolidador de reservas de hotel (Onfly)

O CLI entregava números errados por **5 defeitos independentes**, todos no código (os dados e os
testes fornecidos estão corretos). Os 5 foram corrigidos com mudanças mínimas em `src/`, os testes
fornecidos passam **sem alteração** e foram adicionados 38 testes novos.

> Este trabalho foi feito com apoio de IA (caminho "com IA"). Detalhes, incluindo o que a IA fez e o
> que o candidato fez, em [`uso-de-ia/declaracao.md`](uso-de-ia/declaracao.md).

## Defeitos corrigidos

| # | Arquivo | Causa raiz (uma frase) | Correção |
|---|---------|------------------------|----------|
| 1 | `repositories/csv_reservation_repository.py` | O laço de leitura tinha um `break` ao chegar em 200 linhas, então reservas além da 200ª nunca entravam no relatório. | Removido o limite: o arquivo é lido por inteiro. |
| 2 | `services/status_policy.py` | `is_billable` usava `status != "CANCELLED"`, deixando `NO_SHOW` entrar em noites, valores, `by_month` e `top_hotels`. | `is_billable` passou a aceitar somente `CONFIRMED`. |
| 3 | `services/stay_calculator.py` | As noites eram calculadas com `checkout.day - checkin.day` (dia do mês), o que dá valores errados ou negativos quando a estadia vira o mês ou o ano. | Passou a usar a diferença entre datas completas: `(checkout - checkin).days * rooms`. |
| 4 | `services/currency_converter.py` | A conversão **dividia** pela taxa em vez de multiplicar e passava por `float`, contrariando a regra de usar `Decimal`. | `amount * rate_to_brl` usando só `Decimal`, sem arredondar (o arredondamento fica na serialização). |
| 5 | `services/report_builder.py` | O ranking ordenava por valor **crescente**, mostrando os hotéis de menor valor primeiro. | Chave de ordenação `(-valor, hotel_id)`: valor decrescente e, em empate, `hotel_id` ascendente. |

**Endurecimento extra (não é um dos defeitos do enunciado):** em `currency_converter.py`, uma moeda
sem taxa na tabela agora gera `InputFileError` (saída `2`, "entrada inválida") com mensagem clara,
em vez de um `KeyError` inesperado (saída `1`). Isso segue o contrato de códigos de saída do README.

### Efeito das correções (antes × depois)

| Execução | Antes | Depois |
|----------|-------|--------|
| Amostra do README (`exemplo-validacao.csv`) | `total_room_nights` = **-33**, `total_amount_brl` = 5962.41, média = 0.00 | 28 noites, **7566.00**, média **270.21** (igual à tabela do README) |
| Dataset completo (`reservas_hoteis.csv`) | 200 reservas lidas, 153 confirmadas, **-1393** noites, 193218.53 | **300** reservas, 235 confirmadas, **1347** noites, **396170.00**, média 294.11 |

## Como o problema foi investigado

1. **Leitura do README** para separar o que é regra (status, noites, câmbio, `Decimal`, ordenação,
   contrato do CLI) do que é incidental.
2. **Leitura do código seguindo o pipeline** do README — ler → converter tipos → contar status →
   filtrar `CONFIRMED` → agregar → serializar — comparando cada etapa com a regra correspondente.
   Cada defeito apareceu como um desvio entre uma etapa e a sua regra.
3. **Execução do CLI na amostra de validação**: o resultado (noites negativas, total muito abaixo do
   esperado, ranking de baixo para cima) confirmou os sintomas e ajudou a localizar os defeitos 2, 3, 4 e 5.
4. **Análise do dataset** (300 reservas; 93 estadias cruzam o mês e 16 cruzam o ano; 3 moedas): mostrou
   que o relatório original só enxergava 200 delas, o que revelou o defeito 1 — que os testes
   fornecidos (no máximo 4 reservas) não conseguem detectar.
5. **Correção mínima**, um defeito por vez, sem mudar CLI, schema ou semântica do relatório.
6. **Validação em camadas**: testes fornecidos; amostra do README (valores idênticos); comparação do
   CLI com um cálculo independente feito com `fractions.Fraction` nos dois CSVs e com `--top` 1, 3, 5,
   12 e 50; testes novos.
7. **Teste de mutação manual**: cada defeito foi reintroduzido, um por vez, para checar se os testes
   avisam. Resultado: os testes **fornecidos** não detectam o defeito 1, o uso de `float` no câmbio
   (defeito 4) nem o desempate por `hotel_id` (defeito 5) — os testes novos detectam todos.

## Como validar

Requisitos: Python 3.11+.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# testes (fornecidos + adicionais)
pytest -q

# relatório do dataset completo
PYTHONPATH=src python -m onfly_report \
  --input data/reservas_hoteis.csv \
  --rates data/taxas_cambio.csv \
  --output output/report.json

# amostra de validação do README
PYTHONPATH=src python -m onfly_report \
  --input data/exemplo-validacao.csv \
  --rates data/taxas_cambio.csv \
  --output output/exemplo.json
```

Resultado esperado no dataset completo: `Reservas: 300 | Confirmadas: 235 | Noites: 1347 | Total BRL: 396170.00`.

## Testes adicionados (`tests/test_extra_*.py` e `tests/cli_runner.py`)

Os arquivos fornecidos (`helpers.py` e `test_*.py` originais) **não foram alterados**.

| Arquivo | O que cobre |
|---------|-------------|
| `test_extra_nights.py` | noites (virada de mês, de ano, ano bissexto), `by_month` pelo mês do check-in e em ordem crescente |
| `test_extra_status.py` | só `CONFIRMED` é faturável; cancelados e no-show fora de `by_month` e `top_hotels`; relatório sem confirmadas |
| `test_extra_currency.py` | multiplicação pela taxa, `Decimal` exato, half-up só na serialização, arredondamento sobre a soma exata, formato do dinheiro, moeda sem taxa |
| `test_extra_ranking.py` | soma por hotel, desempate por `hotel_id`, limite `--top` |
| `test_extra_dataset.py` | amostra de validação do README e dataset completo (300 reservas) |
| `test_extra_cli_contract.py` | schema do JSON, saída no stdout, `--top` e `--output` padrão, códigos de saída `2` para entradas inválidas |
| `cli_runner.py` | utilitário (não altera o `helpers.py` fornecido) |

## Resultado do `pytest`

Esperado: **43 testes** (5 fornecidos + 38 adicionais), todos passando.

Saída real da execução local (colar antes do envio):

```text
43 passed in 1.41s
```
