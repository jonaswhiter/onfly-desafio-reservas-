# Declaração de uso de IA

- **Candidato:** Jonas Whiter Leão Xavier
- **Desafio:** Onfly — Consolidador de reservas de hotel (correção de defeitos do CLI)
- **Data:** 11/11/2026

## Ferramenta e modelo usados

- **Ferramenta:** Claude (Anthropic), em interface de chat (claude.ai / app Claude), com acesso a um
  ambiente de execução de código.
- **Modelo:** Claude Sonnet 5.5.

## O que a IA fez

- Abriu o `.zip` do desafio, leu o README, todo o código-fonte, os testes fornecidos e os CSVs.
- Localizou os 5 defeitos descritos em [`../README-ENTREGA.md`](../README-ENTREGA.md) e escreveu as
  correções em `src/onfly_report/` (5 arquivos).
- Escreveu os 38 testes adicionais (`tests/test_extra_*.py` e `tests/cli_runner.py`), sem alterar os
  testes fornecidos.
- Validou o resultado: testes fornecidos e adicionais, amostra de validação do README, comparação
  com um cálculo independente (`fractions.Fraction`) e teste de mutação manual (reintroduzir cada
  defeito para ver se os testes avisam).
- Escreveu o `README-ENTREGA.md`, esta declaração e o log consolidado da sessão (`sessao.md`).
- Explicou ao candidato, em linguagem simples, o que foi feito.

**Limitações da verificação feita pela IA:** o ambiente dela não tinha acesso à internet, então
`pytest` e `ruff` não puderam ser instalados, e o Python disponível era o 3.12 (o desafio pede 3.11+).
Os testes foram executados com um executor mínimo escrito pela própria IA, que imita o `pytest`
(coleta `test_*`, fixture `tmp_path`, `pytest.raises` e `parametrize`). Por isso, a execução real do
`pytest -q` (e a confirmação em Python 3.11) precisa ser feita pelo candidato e colada no
`README-ENTREGA.md`.

## O que o candidato fez

- Forneceu o projeto do desafio (`.zip`) e pediu à IA que o resolvesse e explicasse o resultado
  (pedido literal registrado em [`sessao.md`](sessao.md)).
- **[PREENCHER ANTES DE ENVIAR — escreva apenas o que você realmente fez. Por exemplo: leu o código e
  a explicação; rodou `pytest -q` na sua máquina; conferiu o relatório gerado; publicou o repositório
  no GitHub.]**
