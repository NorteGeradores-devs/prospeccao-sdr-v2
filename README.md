# ⚡ Prospecção SDR — Norte Geradores

Ferramenta de **prospecção ativa de leads** para a equipe comercial da Norte
Geradores (locação/venda de grupos moto geradores). Busca oportunidades em
**5 fontes públicas**, enriquece os contatos com dados da **Receita Federal**,
pontua cada lead pelo perfil de cliente ideal (ICP) e exporta ou envia direto
para o CRM **Agendor**.

> Busca de leads em fontes públicas (PNCP, Google Places, CNPJ, Sympla, SIGMINE)
> com enriquecimento de contatos via Receita Federal.

---

## Por que estas fontes?

Quem compra/aluga gerador é quem precisa de energia própria ou de backup. Cada
fonte encontra um tipo de comprador:

| Fonte | O que traz | Por que é lead de gerador |
|-------|-----------|---------------------------|
| **PNCP** | Licitações públicas com objeto "gerador/geração" | Intenção de compra explícita — é só disputar o edital |
| **Google Places** | Empresas do segmento por cidade | Construtoras, hospitais, hotéis, supermercados, indústrias |
| **CNPJ** | Empresas ativas por CNAE / lista | Segmentação fina + base para enriquecer |
| **Sympla** | Eventos presenciais | Palco, som, arena e food trucks precisam de energia temporária |
| **SIGMINE (ANM)** | Titulares de processos minerários | Mineração remota, quase sempre fora da rede elétrica |
| **Receita Federal** | Razão social, contato, sócios, CNAE | Enriquecimento — vira contato acionável |

O scoring prioriza os **estados do Norte** (AM, PA, RR, RO, AC, AP, TO), onde a
demanda por geração é maior.

---

## Instalação

```bash
cd prospeccao-sdr
python -m venv .venv
.venv\Scripts\activate            # Windows (PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt
copy .env.example .env            # e preencha as chaves que tiver
```

Nenhuma chave é obrigatória para começar: **PNCP, SIGMINE e o enriquecimento via
Receita (BrasilAPI) funcionam de graça, sem cadastro.** As demais habilitam
recursos extras (veja `.env.example`).

---

## Uso

### Painel (equipe de SDR)

```bash
python -m streamlit run app.py     # abre http://localhost:8501
```

O painel abre direto, sem login. Na barra lateral: escolha as
fontes, os estados e clique em **Buscar leads**. A tabela vem ordenada por
score, com filtros por temperatura/fonte, download em Excel/CSV e botão para
**enviar ao Agendor**.

### Linha de comando (automação / agendado)

```bash
# Licitações de gerador nos estados do Norte, salvando em Excel
python cli.py --fontes pncp --uf AM PA RO --saida leads.xlsx

# Varredura ampla numa cidade
python cli.py --fontes pncp google_places sigmine --uf AM --municipios Manaus

# Enriquecer uma lista de CNPJs (associados, expositores de feira...)
python cli.py --fontes cnpj --cnpjs 00000000000191 11444777000161

# Buscar e já subir os quentes para o CRM
python cli.py --fontes pncp --uf AM --enviar-agendor --temperatura quente
```

Agende no **Agendador de Tarefas do Windows** para rodar toda manhã e alimentar
o funil automaticamente.

---

## Como o score é calculado

Cada lead recebe de 0 a 100 pontos (`prospeccao/scoring.py`):

- **Fonte** — PNCP (+30, intenção explícita) > SIGMINE > Sympla > CNPJ > Places
- **Segmento‑alvo** identificado: +15
- **UF prioritária** (Norte): +20 · **secundária**: +10
- **Contato** — telefone +8, e‑mail +6, sócio +6
- **Licitação** — ≥ R$500k: +15 · com valor: +8
- **Porte** — capital ≥ R$1M: +8
- **CNPJ ativo** na Receita: +5 · situação irregular: −15

`quente ≥ 65 · morno ≥ 40 · frio < 40` (ajustável em `config.py`).

---

## Arquitetura

```
prospeccao-sdr/
├── app.py                 # Painel Streamlit (SDR)
├── cli.py                 # Linha de comando (automação)
├── config.py              # Segredos + ICP (keywords, CNAEs, UFs)
├── smoke_test.py          # Verificação offline do pipeline
├── prospeccao/
│   ├── http.py            # Session HTTP com retry/backoff
│   ├── cache.py           # Cache em disco (CNPJ, shapefiles)
│   ├── utils.py           # CNPJ, telefone, normalização, dedup
│   ├── models.py          # Lead (dataclass) + colunas
│   ├── enriquecimento.py  # Receita Federal (BrasilAPI / ReceitaWS)
│   ├── scoring.py         # Pontuação por ICP
│   ├── pipeline.py        # Orquestração buscar→dedup→enriquecer→pontuar
│   ├── export.py          # CSV/Excel com sanitização anti-injeção
│   ├── agendor.py         # Envio de leads ao CRM Agendor
│   └── fontes/            # Um conector por fonte
│       ├── pncp.py  google_places.py  cnpj.py  sympla.py  sigmine.py
└── tests/test_utils.py    # pytest das funções puras
```

Fluxo: **buscar** (fontes em paralelo lógico) → **deduplicar** (mescla por CNPJ)
→ **enriquecer** (Receita, com cache) → **pontuar** → **ordenar** → **exportar**.

---

## Deploy (Streamlit Community Cloud)

Mesmo padrão do BI de Faturamento: repositório privado + `st.secrets`. Coloque
as chaves em **Settings → Secrets** (`AGENDOR_TOKEN`, etc.). O painel **não tem
mais senha** — como a URL é pública, **restringir os viewers por e‑mail passa a
ser a única barreira de acesso**.

---

## Limitações honestas

- **CNPJ por segmento**: não existe API pública gratuita que liste empresas por
  CNAE. O modo segmento usa a **CNPJá** (chave paga) e seu contrato **não foi
  verificado** — valide antes de confiar. Sem ela, use o modo **lista de CNPJs**
  (enriquecimento grátis via BrasilAPI), que funciona 100%.
- **PNCP**: o endpoint de busca **não retorna o valor** da contratação
  (`valor_estimado` fica 0). O SDR consulta o valor no portal pelo link do
  edital (`/app/editais/{cnpj}/{ano}/{seq}`), que o conector monta corretamente.
- **Sympla**: a API oficial (token) só lista eventos da **própria conta** — não
  há busca pública de eventos de terceiros. Sem `SYMPLA_TOKEN`, a fonte é
  ignorada (não finge resultados). Parceria com produtores é o caminho.
- **Google Places / BrasilAPI**: têm limites de requisição (rate limit); o cache
  de CNPJ (7 dias) reduz o consumo. Leads do Places vêm **sem CNPJ** → o
  enriquecimento por razão social é manual.
- **SIGMINE**: baixa o shapefile da UF (~2 MB) na 1ª busca e cacheia; lê apenas
  os atributos (`.dbf`). O titular vem sem CNPJ — enriquecer por razão social.

---

## Verificação

```bash
python smoke_test.py         # valida o pipeline sem rede
python -m pytest -q          # testes das funções puras
```
