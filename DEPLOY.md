# Deploy — Prospecção SDR (Streamlit Community Cloud)

Mesmo caminho do BI de Faturamento: **repositório privado + `st.secrets`**.

## 0. Pré-requisitos
- Conta GitHub (a equipe usa **NorteGeradores-devs**).
- Conta no Streamlit Community Cloud vinculada a esse GitHub.
- `gh` autenticado: se precisar, rode no chat `! gh auth login`.

## 1. Repositório (local → GitHub privado)
O `git init` e o 1º commit já podem estar feitos. Para publicar:

```bash
gh repo create NorteGeradores-devs/prospeccao-sdr --private --source . --remote origin --push
```

> **Confirme antes de subir:** nenhum segredo versionado. Rode:
> ```bash
> git ls-files | grep -E "\.env$|secrets\.toml$" ; echo "(vazio acima = OK)"
> ```
> `.env`, `.streamlit/secrets.toml` e `.cache/` estão no `.gitignore`.

## 2. Criar o app no Streamlit Cloud
1. https://share.streamlit.io → **Create app** → **Deploy a public app from GitHub**.
2. Repo `NorteGeradores-devs/prospeccao-sdr`, branch `main`, arquivo **`app.py`**.
3. Advanced settings → Python **3.12/3.13**.
4. Repo privado exige 2ª autorização: **Settings → Linked accounts → Source control → Connect**.

## 3. Secrets (chaves das fontes — todas opcionais)
Em **Settings → Secrets**, cole (formato TOML, veja `.streamlit/secrets.toml.example`):

```toml
# todas opcionais — cada fonte degrada com elegância sem a sua chave:
GOOGLE_PLACES_API_KEY = ""
CNPJ_SEARCH_TOKEN = ""
SYMPLA_TOKEN = ""
AGENDOR_TOKEN = ""
```

O app lê tudo via `os.getenv`/`st.secrets` (config.py) — não precisa de código extra.
O painel **não tem mais senha** (`APP_PASSWORD` foi removido) — veja a seção 4.

## 4. Pós-deploy (segurança) — NÃO PULAR
- ⚠️ **O painel agora abre sem senha.** Qualquer um que alcançar a URL usa o console — inclusive **enviar leads ao Agendor** (escreve no CRM). A barreira de acesso passou a ser **exclusivamente** a lista de viewers.
- **Restringir viewers por e-mail** (Settings → Sharing → só os e-mails da equipe) é agora a **única** barreira — não é mais opcional. A URL é pública.
- Se algum token vazar no git, ele é permanente no histórico — a defesa é nunca commitar (`.gitignore`) + repo privado.

## 5. Automação (opcional)
O `cli.py` roda headless para alimentar o Agendor. Agende no **Agendador de Tarefas do Windows**:
```
python C:\Users\pedro.porpino\prospeccao-sdr\cli.py --fontes pncp sigmine --uf AM PA --enviar-agendor --temperatura quente
```
(As chaves vêm do `.env` local; o Streamlit Cloud não roda o cli.)
