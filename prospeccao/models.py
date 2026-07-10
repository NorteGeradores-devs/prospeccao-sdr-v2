"""Modelo de dados do lead — estrutura única para todas as fontes."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from prospeccao.utils import chave_dedup, normalizar_texto

# Ordem das colunas na exportação (CSV/Excel) e na UI.
COLUNAS = [
    "score", "temperatura", "fonte", "nome", "nome_fantasia", "segmento",
    "cnpj", "cnae", "cnae_descricao", "municipio", "uf", "endereco",
    "telefone", "email", "site", "contato_nome", "contato_cargo",
    "capital_social", "situacao_cadastral", "valor_estimado",
    "titulo", "data_evento", "url", "motivos_score", "observacoes", "coletado_em",
]


@dataclass
class Lead:
    fonte: str                       # pncp | google_places | cnpj | sympla | sigmine
    nome: str
    cnpj: str = ""
    nome_fantasia: str = ""
    segmento: str = ""
    cnae: str = ""
    cnae_descricao: str = ""
    municipio: str = ""
    uf: str = ""
    telefone: str = ""
    email: str = ""
    site: str = ""
    endereco: str = ""
    contato_nome: str = ""           # sócio/administrador (enriquecimento RF)
    contato_cargo: str = ""
    capital_social: float = 0.0
    situacao_cadastral: str = ""
    valor_estimado: float = 0.0      # valor da licitação/oportunidade (PNCP)
    titulo: str = ""                 # objeto da licitação / nome do evento
    data_evento: str = ""            # abertura da proposta / data do evento
    url: str = ""
    observacoes: str = ""
    score: int = 0
    temperatura: str = "frio"        # quente | morno | frio
    motivos_score: list[str] = field(default_factory=list)
    coletado_em: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    def chave(self) -> str:
        # Um edital do PNCP é uma oportunidade única: sua identidade é a URL do
        # edital, NÃO o CNPJ do órgão (que se repete entre várias licitações).
        if self.fonte == "pncp" and self.url:
            return f"url:{normalizar_texto(self.url)}"
        return chave_dedup(self.cnpj, self.nome, self.municipio, self.uf, self.url)

    def to_row(self) -> dict:
        d = asdict(self)
        d["motivos_score"] = "; ".join(self.motivos_score)
        return {c: d.get(c, "") for c in COLUNAS}
