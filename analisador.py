from pathlib import Path

import pandas as pd

ARQ_VOTOS_CSV = Path("./vt-candidato-munzona-BR.csv")
ARQ_QE_CSV = Path("./qe-brasil-dep-federal.csv")
DIR_PARQUET = Path("./parquet")

COLS_QE = ["aa_eleicao", "UF", "cd_cargo", "ds_cargo", "vr_quociente_eleitoral"]
COLS_VOTOS = [
    # Ano, tipo de eleição, UF e cargo
    "ANO_ELEICAO",
    "CD_TIPO_ELEICAO",
    "NM_TIPO_ELEICAO",
    "SG_UF",
    "CD_CARGO",
    "DS_CARGO",
    # Candidato
    "NR_CANDIDATO",
    "NM_CANDIDATO",
    "NM_URNA_CANDIDATO",
    "NM_SOCIAL_CANDIDATO",
    # Diz respeito ao partido isolado/federação/coligação
    "TP_AGREMIACAO",  # Diz qual é
    "NR_PARTIDO",
    "SG_PARTIDO",
    "NM_PARTIDO",  # Partido
    "NR_FEDERACAO",
    "SG_FEDERACAO",
    "NM_FEDERACAO",  # Federação
    "SQ_COLIGACAO",
    "NM_COLIGACAO",  # Coligação
    # Votos do candidato
    "QT_VOTOS_NOMINAIS",
    "NM_TIPO_DESTINACAO_VOTOS",
    "QT_VOTOS_NOMINAIS_VALIDOS",
    "CD_SIT_TOT_TURNO",
    "DS_SIT_TOT_TURNO",
]


def salvar_por_uf(arquivo_csv: Path, colunas: list[str], col_uf: str, prefixo: str):
    df = pd.read_csv(arquivo_csv, sep=";", encoding="latin1", usecols=colunas)

    for uf, df_uf in df.groupby(col_uf):
        df_uf.to_parquet(DIR_PARQUET / f"{prefixo}-{uf}.parquet", index=False)
        print(f"{prefixo}-{uf}: {len(df_uf)} linhas")


def carregar_votos(uf: str) -> pd.DataFrame:
    return pd.read_parquet(DIR_PARQUET / f"votos-{uf.upper()}.parquet")


def carregar_qe(uf: str) -> pd.DataFrame:
    return pd.read_parquet(DIR_PARQUET / f"qe-{uf.upper()}.parquet")


def main():
    DIR_PARQUET.mkdir(exist_ok=True)
    salvar_por_uf(ARQ_VOTOS_CSV, COLS_VOTOS, "SG_UF", "votos")
    salvar_por_uf(ARQ_QE_CSV, COLS_QE, "UF", "qe")

    print(carregar_votos("RJ").head())
    print(carregar_qe("RJ").head())


if __name__ == "__main__":
    main()
