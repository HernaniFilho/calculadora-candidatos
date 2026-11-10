import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analisador import carregar_eleitos_todas_ufs, garantir_parquets

# Faixas de % do QE: 0-10, 10-20, ..., 90-100 e 100%+ (100 exato entra em 100%+)
LIMITES = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, float("inf")]
FAIXAS = [
    "<10%",
    "10–20%",
    "20–30%",
    "30–40%",
    "40–50%",
    "50–60%",
    "60–70%",
    "70–80%",
    "80–90%",
    "90–100%",
    "100%+",
]
ARQ_PNG = "eleitos_por_faixa_qe.png"
ARQ_PNG_PIZZA = "eleitos_por_faixa_qe_pizza.png"


def montar_tabela() -> pd.DataFrame:
    eleitos = carregar_eleitos_todas_ufs()
    df = pd.DataFrame(
        {
            "uf": [c.uf for c in eleitos],
            "nome": [c.nome_urna for c in eleitos],
            "partido": [c.partido for c in eleitos],
            "votos": [c.votos_validos for c in eleitos],
            "qe": [c.quociente_eleitoral for c in eleitos],
            "eleito_por": [c.eleito_por for c in eleitos],
        }
    )
    # % sem arredondar, para não empurrar 99,996% para a faixa 100%+
    df["pct_qe"] = df["votos"] / df["qe"] * 100
    df["faixa"] = pd.cut(
        df["pct_qe"], bins=LIMITES, labels=FAIXAS, right=False, include_lowest=True
    )
    return df


def desenhar(df: pd.DataFrame):
    # contagem por faixa, separada por QP e média
    cont = (
        df.groupby(["faixa", "eleito_por"], observed=False)
        .size()
        .unstack(fill_value=0)
        .reindex(FAIXAS, fill_value=0)
    )
    for col in ["QP", "MEDIA"]:
        if col not in cont.columns:
            cont[col] = 0

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(cont.index, cont["QP"], label="Eleito por QP", color="#2a6fb0")
    ax.bar(
        cont.index,
        cont["MEDIA"],
        bottom=cont["QP"],
        label="Eleito por média",
        color="#e0a030",
    )

    totais = cont["QP"] + cont["MEDIA"]
    for i, total in enumerate(totais):
        if total > 0:
            ax.text(i, total + 0.5, str(total), ha="center", va="bottom", fontsize=10)

    ax.set_title(
        f"Deputados federais eleitos em 2026 por faixa de votos em relação ao QE da UF\n"
        f"({len(df)} eleitos, todas as UFs)"
    )
    ax.set_xlabel("Votos do candidato como % do quociente eleitoral da sua UF")
    ax.set_ylabel("Número de eleitos")
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(ARQ_PNG, dpi=150)
    print(f"Gráfico salvo em {ARQ_PNG}")


def desenhar_pizza(df: pd.DataFrame):
    """Pizza com o total de eleitos por faixa, sem separar QP e média."""
    cont = df["faixa"].value_counts().reindex(FAIXAS, fill_value=0)
    cont = cont[cont > 0]  # faixas vazias não entram na pizza
    total = int(cont.sum())

    cores = plt.get_cmap("viridis")(np.linspace(0.05, 0.95, len(cont)))

    fig, ax = plt.subplots(figsize=(10, 7))
    wedges, _, autotexts = ax.pie(
        cont,
        colors=cores,
        startangle=90,
        counterclock=False,
        # só escreve o % dentro das fatias grandes, para não amontoar
        autopct=lambda p: f"{p:.0f}%" if p >= 4 else "",
        pctdistance=0.75,
        wedgeprops={"edgecolor": "white"},
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontsize(10)

    ax.legend(
        wedges,
        [f"{faixa}: {n} ({n / total * 100:.1f}%)" for faixa, n in cont.items()],
        title="Faixa de votos / QE",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
    )
    ax.set_title(
        f"Deputados federais eleitos em 2026 por faixa de votos em relação ao QE\n"
        f"({total} eleitos, todas as UFs)"
    )
    fig.tight_layout()
    fig.savefig(ARQ_PNG_PIZZA, dpi=150, bbox_inches="tight")
    print(f"Gráfico salvo em {ARQ_PNG_PIZZA}")


def main():
    garantir_parquets()
    df = montar_tabela()

    print(f"{len(df)} eleitos em {df['uf'].nunique()} UFs")
    print(df["faixa"].value_counts().reindex(FAIXAS))

    desenhar(df)
    desenhar_pizza(df)
    plt.show()  # abre as duas figuras


if __name__ == "__main__":
    main()
