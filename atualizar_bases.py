"""Atualiza as bases externas que precisam de refresh periódico.

Hoje: base de consumidores livres da CCEE/ANEEL (fonte `ccee`). A base é
baixada ao vivo e cacheada em `.cache/` (nada é versionado).

Uso avulso:      python atualizar_bases.py
Agendado (cron): 1x por semana, fora do horário comercial. Ex. na VM:
  0 5 * * 1  cd ~/apps/prospeccao-sdr && .venv/bin/python atualizar_bases.py
"""
from __future__ import annotations

import sys

from prospeccao.fontes import ccee


def main() -> int:
    print("== Atualização de bases externas ==")
    try:
        qtd = ccee.atualizar_cache_aneel()
    except Exception as e:                              # noqa: BLE001
        print(f"[CCEE/ANEEL] ERRO: {e}")
        return 1
    print(f"[CCEE/ANEEL] {qtd} consumidores livres na base.")
    return 0 if qtd else 1


if __name__ == "__main__":
    sys.exit(main())
