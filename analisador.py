import sys
from pathlib import Path

import pandas as pd

from candidato import Candidato

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

# Colunas que identificam 1 candidato (o CSV tem 1 linha por município/zona)
CHAVES_CANDIDATO = [
    "ANO_ELEICAO",
    "NM_TIPO_ELEICAO",
    "SG_UF",
    "CD_CARGO",
    "DS_CARGO",
    "NR_CANDIDATO",
    "NM_CANDIDATO",
    "NM_URNA_CANDIDATO",
    "NM_SOCIAL_CANDIDATO",
    "TP_AGREMIACAO",
    "NR_PARTIDO",
    "SG_PARTIDO",
    "NM_PARTIDO",
    "NR_FEDERACAO",
    "SG_FEDERACAO",
    "NM_FEDERACAO",
    "NM_COLIGACAO",
    "CD_SIT_TOT_TURNO",
    "DS_SIT_TOT_TURNO",
]

# Colunas do parquet -> campos do modelo Candidato
RENOMEAR = {
    "ANO_ELEICAO": "ano_eleicao",
    "NM_TIPO_ELEICAO": "tipo_eleicao",
    "SG_UF": "uf",
    "CD_CARGO": "cd_cargo",
    "DS_CARGO": "cargo",
    "NR_CANDIDATO": "numero",
    "NM_CANDIDATO": "nome",
    "NM_URNA_CANDIDATO": "nome_urna",
    "NM_SOCIAL_CANDIDATO": "nome_social",
    "TP_AGREMIACAO": "tp_agremiacao",
    "NR_PARTIDO": "numero_partido",
    "SG_PARTIDO": "partido",
    "NM_PARTIDO": "nome_partido",
    "NR_FEDERACAO": "numero_federacao",
    "SG_FEDERACAO": "federacao",
    "NM_FEDERACAO": "nome_federacao",
    "NM_COLIGACAO": "coligacao",
    "CD_SIT_TOT_TURNO": "cd_situacao",
    "DS_SIT_TOT_TURNO": "situacao",
    "vr_quociente_eleitoral": "quociente_eleitoral",
}


# ---------- CSV -> Parquet (roda uma vez) ----------


def parquets_existem(prefixo: str) -> bool:
    return DIR_PARQUET.exists() and any(DIR_PARQUET.glob(f"{prefixo}-*.parquet"))


def salvar_por_uf(arquivo_csv: Path, colunas: list[str], col_uf: str, prefixo: str):
    df = pd.read_csv(arquivo_csv, sep=";", encoding="latin1", usecols=colunas)

    for uf, df_uf in df.groupby(col_uf):
        df_uf.to_parquet(DIR_PARQUET / f"{prefixo}-{uf}.parquet", index=False)
        print(f"{prefixo}-{uf}: {len(df_uf)} linhas")


def garantir_parquets():
    """Gera os parquets uma única vez. Se já existem, não faz nada.
    Se faltar o CSV necessário, avisa e encerra."""
    tarefas = [
        (ARQ_VOTOS_CSV, COLS_VOTOS, "SG_UF", "votos"),
        (ARQ_QE_CSV, COLS_QE, "UF", "qe"),
    ]

    pendentes = [t for t in tarefas if not parquets_existem(t[3])]
    ausentes = [t[0] for t in pendentes if not t[0].exists()]

    if ausentes:
        print("Arquivo(s) CSV não encontrado(s):")
        for arq in ausentes:
            print(f"  - {arq}")
        print("Leia o LEIAME.md para saber de onde baixar e como renomear.")
        sys.exit(1)

    DIR_PARQUET.mkdir(exist_ok=True)
    for arquivo_csv, colunas, col_uf, prefixo in pendentes:
        salvar_por_uf(arquivo_csv, colunas, col_uf, prefixo)


# ---------- Leitura dos parquets ----------


def carregar_votos(uf: str) -> pd.DataFrame:
    return pd.read_parquet(DIR_PARQUET / f"votos-{uf.upper()}.parquet")


def carregar_qe(uf: str) -> pd.DataFrame:
    return pd.read_parquet(DIR_PARQUET / f"qe-{uf.upper()}.parquet")


# ---------- Candidatos ----------


def carregar_candidatos(uf: str) -> list[Candidato]:
    """Todos os candidatos da UF para os cargos que têm QE, com votos somados."""
    qe = (
        carregar_qe(uf)
        .dropna(subset=["vr_quociente_eleitoral"])
        # QE é único por (ano, UF, cargo); o CSV repete a linha por partido/federação
        .drop_duplicates(subset=["aa_eleicao", "UF", "cd_cargo"])
        .rename(
            columns={"aa_eleicao": "ANO_ELEICAO", "UF": "SG_UF", "cd_cargo": "CD_CARGO"}
        )[["ANO_ELEICAO", "SG_UF", "CD_CARGO", "vr_quociente_eleitoral"]]
    )

    # O arquivo de votos traz todos os cargos; fica só com os que têm QE (dep. federal)
    votos = carregar_votos(uf)
    votos = votos[votos["CD_CARGO"].isin(qe["CD_CARGO"])]

    # Soma os votos de todas as zonas: 1 linha por candidato
    cand = votos.groupby(CHAVES_CANDIDATO, as_index=False, dropna=False).agg(
        votos_nominais=("QT_VOTOS_NOMINAIS", "sum"),
        votos_validos=("QT_VOTOS_NOMINAIS_VALIDOS", "sum"),
        destinacoes_votos=("NM_TIPO_DESTINACAO_VOTOS", "unique"),
    )
    cand["destinacoes_votos"] = cand["destinacoes_votos"].apply(
        lambda arr: sorted(str(x) for x in arr if pd.notna(x))
    )

    cand = cand.merge(qe, on=["ANO_ELEICAO", "SG_UF", "CD_CARGO"], how="left")

    sem_qe = cand[cand["vr_quociente_eleitoral"].isna()]
    if not sem_qe.empty:
        chaves = sem_qe[["ANO_ELEICAO", "SG_UF", "CD_CARGO"]].drop_duplicates()
        raise ValueError(
            f"{len(sem_qe)} candidato(s) sem quociente eleitoral. "
            f"Chaves sem correspondência no QE:\n{chaves}"
        )

    cand = cand.sort_values("votos_validos", ascending=False)

    # NaN -> None e nomes das colunas -> campos do modelo
    cand = cand.astype(object).where(cand.notna(), None).rename(columns=RENOMEAR)
    return [Candidato(**linha) for linha in cand.to_dict("records")]


def carregar_eleitos(uf: str) -> list[Candidato]:
    return [c for c in carregar_candidatos(uf) if c.eleito]


def listar_ufs() -> list[str]:
    """UFs que têm quociente eleitoral (as 27 do deputado federal)."""
    return sorted(p.stem.removeprefix("qe-") for p in DIR_PARQUET.glob("qe-*.parquet"))


def carregar_eleitos_todas_ufs() -> list[Candidato]:
    eleitos: list[Candidato] = []
    for uf in listar_ufs():
        eleitos.extend(carregar_eleitos(uf))
    return eleitos


def main():
    garantir_parquets()

    # A partir daqui só usa parquet
    eleitos = carregar_eleitos("RJ")
    print(f"{len(eleitos)} eleitos")

    for c in eleitos:
        print(
            f"{c.nome_urna:<30} {c.partido:<10} {c.votos_validos:>8} votos "
            f"| QE {c.quociente_eleitoral:.0f} | {c.pct_do_qe:>6}% do QE | {c.eleito_por}"
        )

    # Exemplo de refinamento: eleitos que não atingiram o QE sozinhos
    puxados = [c for c in eleitos if not c.atingiu_qe]
    print(f"\n{len(puxados)} eleitos abaixo de 100% do QE")


if __name__ == "__main__":
    main()
