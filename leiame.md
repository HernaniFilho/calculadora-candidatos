# LEIAME

Dados das eleições de 2026 para **deputado federal**, usados para calcular o
quociente eleitoral por UF e analisar a votação dos candidatos.

Os arquivos abaixo foram baixados manualmente do TSE em **07/11/2026** e
**renomeados**. O conteúdo não foi alterado.

## Arquivos

### `qe-brasil-dep-federal.csv`

Quociente eleitoral partidário, por UF, para deputado federal.

- **Fonte:** SIG Eleições – Resultados, TSE
- **Página:** https://sig.tse.jus.br/ords/dwapr/r/seai/sig-eleicao-resultados/quociente-eleitoral-partidário
- **Como obtive:** na página, usei a opção de gerar arquivo (download do CSV)
  com os filtros:
  - Ano: 2026
  - Região: Todas
  - UF: Todas
  - Turno: 1
  - Tipo de eleição: Eleição Ordinária
  - Eleição: Todas
  - Cargo: Deputado Federal
- **Nome original:** `quociente_eleitoral-brasil_deputado_federal_t1_2026.csv.zip`
  (basta descompactar)
- **Colunas usadas:** `aa_eleicao`, `UF`, `cd_cargo`, `ds_cargo`,
  `vr_quociente_eleitoral`
- **Observação:** o QE é único por (ano, UF, cargo), mas o arquivo repete a
  linha para cada partido, federação ou coligação.

### `vt-candidato-munzona-BR.csv`

Votação nominal de cada candidato, por município e zona eleitoral.

- **Fonte:** Portal de Dados Abertos do TSE, conjunto "Resultados 2026"
- **Página:** https://dadosabertos.tse.jus.br/dataset/resultados-2026
- **Recurso:** "Votação nominal por município e zona"
- **Nome original do zip:** `votacao_candidato_munzona_2026.zip`
- **Arquivo usado dentro do zip:** `votacao_candidato_munzona_2026_BRASIL.csv`
  (consolidado com todas as UFs)
- **Layout das colunas:** descrito no `leiame.pdf` que acompanha o conjunto de
  dados do TSE.

## Renomeação

| Nome original                                                                | Nome neste projeto            |
| ---------------------------------------------------------------------------- | ----------------------------- |
| `quociente_eleitoral-brasil_deputado_federal_t1_2026.csv` (dentro do `.zip`) | `qe-brasil-dep-federal.csv`   |
| `votacao_candidato_munzona_2026_BRASIL.csv` (dentro do `.zip`)               | `vt-candidato-munzona-BR.csv` |

## Convenções dos arquivos do TSE

Segundo o `leiame.pdf` do TSE:

- Codificação **Latin 1** (`encoding="latin1"`), separador `;`.
- `#NULO` = campo em branco no banco de dados (`-1` em campos numéricos).
- `#NE` = informação não registrada naquele ano (`-3` em campos numéricos).
- O campo de UF pode conter, além dos estados, `BR` (nacional), `VT` (voto em
  trânsito) e `ZZ` (exterior).

## Data do download

07/11/2026. Os arquivos do TSE são atualizados continuamente, então os números
podem mudar em downloads posteriores.
