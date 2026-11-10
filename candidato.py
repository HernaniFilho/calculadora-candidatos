import unicodedata

from pydantic import BaseModel, computed_field, field_validator


def _normalizar(txt: str) -> str:
    """Sem acento e em maiúsculo, para comparar textos do TSE."""
    return unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode().upper()


class Candidato(BaseModel):
    # Eleição
    ano_eleicao: int
    tipo_eleicao: str
    uf: str
    cd_cargo: int
    cargo: str

    # Candidato
    numero: int
    nome: str
    nome_urna: str
    nome_social: str | None = None

    # Partido / federação / coligação
    tp_agremiacao: str
    numero_partido: int
    partido: str
    nome_partido: str
    numero_federacao: int | None = None
    federacao: str | None = None
    nome_federacao: str | None = None
    coligacao: str | None = None

    # Votos
    votos_nominais: int
    votos_validos: int
    destinacoes_votos: list[str] = []
    quociente_eleitoral: float  # QE da UF/cargo do candidato

    # Situação oficial de totalização no turno
    cd_situacao: int | None = None
    situacao: str

    @field_validator("*", mode="before")
    @classmethod
    def _nulo_texto(cls, v):
        # LEIAME do TSE: #NULO = em branco, #NE = não registrado
        if isinstance(v, str) and v.strip() in {"#NULO", "#NE"}:
            return None
        return v

    @field_validator("numero_federacao", mode="before")
    @classmethod
    def _nulo_numero(cls, v):
        # LEIAME do TSE: -1 = #NULO, -3 = #NE nos campos numéricos
        return None if v in (-1, -3) else v

    @computed_field
    @property
    def pct_do_qe(self) -> float:
        return round(self.votos_validos / self.quociente_eleitoral * 100, 2)

    @computed_field
    @property
    def atingiu_qe(self) -> bool:
        """Votos próprios >= QE (eleito 'com o próprio voto')."""
        return self.votos_validos >= self.quociente_eleitoral

    @computed_field
    @property
    def atingiu_10pct_qe(self) -> bool:
        return self.votos_validos >= 0.10 * self.quociente_eleitoral

    @computed_field
    @property
    def eleito(self) -> bool:
        return _normalizar(self.situacao).startswith("ELEITO")

    @computed_field
    @property
    def eleito_por(self) -> str | None:
        if not self.eleito:
            return None
        sit = _normalizar(self.situacao)
        if "QP" in sit:
            return "QP"
        if "MEDIA" in sit:
            return "MEDIA"
        return "OUTRO"
