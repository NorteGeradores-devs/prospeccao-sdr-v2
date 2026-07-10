"""Cliente HTTP compartilhado: uma Session com retry/backoff e timeout padrão.

Mesma estratégia usada no BI (Session única + urllib3 Retry) para ser resiliente
a instabilidades das APIs públicas (PNCP, BrasilAPI, ANM) sem dependências extras.
"""
from __future__ import annotations

import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import HTTP_RETRIES, HTTP_TIMEOUT, USER_AGENT

log = logging.getLogger("prospeccao")


class HttpClient:
    """Wrapper fino sobre requests.Session com timeout e retry padronizados."""

    def __init__(self, timeout: int = HTTP_TIMEOUT, retries: int = HTTP_RETRIES,
                 backoff: float = 0.6, headers: dict | None = None):
        self.timeout = timeout
        self.session = requests.Session()
        retry = Retry(
            total=retries,
            backoff_factor=backoff,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST"]),
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update({"User-Agent": USER_AGENT})
        if headers:
            self.session.headers.update(headers)

    def get(self, url: str, **kw) -> requests.Response:
        kw.setdefault("timeout", self.timeout)
        return self.session.get(url, **kw)

    def post(self, url: str, **kw) -> requests.Response:
        kw.setdefault("timeout", self.timeout)
        return self.session.post(url, **kw)

    def get_json(self, url: str, **kw):
        resp = self.get(url, **kw)
        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
