"""Utilidades: validação/normalização de CNPJ, telefone, texto e segmentação."""
from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime

from config import CNAE_SEGMENTOS


def so_digitos(valor: str | None) -> str:
    return re.sub(r"\D", "", valor or "")


def normalizar_texto(valor: str | None) -> str:
    """minúsculas, sem acento, espaços colapsados — para comparação/dedup."""
    if not valor:
        return ""
    txt = unicodedata.normalize("NFKD", valor)
    txt = txt.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", txt).strip().lower()


def cnpj_valido(cnpj: str | None) -> bool:
    """Valida os dígitos verificadores do CNPJ."""
    n = so_digitos(cnpj)
    if len(n) != 14 or len(set(n)) == 1:
        return False

    def dv(base: str, pesos: list[int]) -> str:
        soma = sum(int(d) * p for d, p in zip(base, pesos))
        resto = soma % 11
        return "0" if resto < 2 else str(11 - resto)

    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    p2 = [6] + p1
    return n[12] == dv(n[:12], p1) and n[13] == dv(n[:13], p2)


def formatar_cnpj(cnpj: str | None) -> str:
    n = so_digitos(cnpj)
    if len(n) != 14:
        return n
    return f"{n[:2]}.{n[2:5]}.{n[5:8]}/{n[8:12]}-{n[12:]}"


def limpar_telefone(valor: str | None) -> str:
    """Normaliza para formato brasileiro legível. Descarta lixo evidente."""
    n = so_digitos(valor)
    if len(n) == 13 and n.startswith("55"):        # +55 DDD numero
        n = n[2:]
    if len(n) == 11:                                # celular com DDD
        return f"({n[:2]}) {n[2:7]}-{n[7:]}"
    if len(n) == 10:                                # fixo com DDD
        return f"({n[:2]}) {n[2:6]}-{n[6:]}"
    return valor.strip() if valor else ""


def normalizar_cnae(cnae) -> str:
    """Normaliza um CNAE para 7 dígitos.

    A BrasilAPI devolve cnae_fiscal como NÚMERO, perdendo o zero à esquerda dos
    segmentos‑núcleo do ICP: mineração (05/07/08/09), petróleo (06) e agro
    (01/02/03). Ex.: 0710301 chega como 710301 — sem padding, o segmento some.
    """
    n = so_digitos(str(cnae) if cnae is not None else "")
    if 6 <= len(n) <= 7:
        return n.zfill(7)
    return n


def segmento_por_cnae(cnae: str | None) -> str:
    """Mapeia um CNAE para o segmento do ICP pelos 2 primeiros dígitos."""
    n = normalizar_cnae(cnae)
    if len(n) < 2:
        return ""
    return CNAE_SEGMENTOS.get(n[:2], "")


def parse_dinheiro(valor) -> float:
    """Converte capital/valor (número ou texto BR/US) para float.

    Aceita 120000000000 (número), "10.000,00" (BR) e "10000.00" (US) → todos
    corretos. Evita o bug de tratar "10000.00" como 1.000.000 ao remover pontos.
    """
    if isinstance(valor, (int, float)):
        return float(valor)
    s = re.sub(r"[^\d.,]", "", str(valor or ""))
    if not s:
        return 0.0
    if "," in s:                       # BR: ponto = milhar, vírgula = decimal
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def uf_valida(uf: str | None) -> str:
    uf = (uf or "").strip().upper()
    return uf if re.fullmatch(r"[A-Z]{2}", uf) else ""


def dias_ate_data(valor: str | None) -> int | None:
    """Dias entre hoje e uma data (PNCP/Sympla). Negativo = já passou; None se
    não der para interpretar. Aceita ISO (2026-07-16T10:00) e BR (dd/mm/aaaa)."""
    if not valor:
        return None
    s = str(valor).strip()
    parsers = (
        lambda x: datetime.fromisoformat(x),
        lambda x: datetime.strptime(x, "%d/%m/%Y %H:%M:%S"),
        lambda x: datetime.strptime(x, "%d/%m/%Y"),
        lambda x: datetime.strptime(x[:10], "%Y-%m-%d"),
    )
    for parse in parsers:
        try:
            return (parse(s).date() - date.today()).days
        except (ValueError, TypeError):
            continue
    return None


def chave_dedup(cnpj: str, nome: str, municipio: str, uf: str, url: str = "") -> str:
    """Identidade do lead para deduplicação.

    CNPJ é a melhor chave. Sem CNPJ, só use nome quando houver município/UF
    (evita fundir empresas homônimas em cidades diferentes). Sem local confiável,
    a URL é mais única que o nome isolado.
    """
    n = so_digitos(cnpj)
    if len(n) == 14:
        return f"cnpj:{n}"
    nome_n = normalizar_texto(nome)
    local = normalizar_texto(f"{municipio}|{uf}").strip("|")
    if nome_n and local:
        return f"nome:{nome_n}|{local}"
    if url:
        return f"url:{normalizar_texto(url)}"
    if nome_n:
        return f"nome:{nome_n}"
    return "vazio:"
