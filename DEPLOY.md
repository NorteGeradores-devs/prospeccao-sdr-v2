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

## 3. Secrets (obrigatório — senão o painel fica bloqueado)
Em **Settings → Secrets**, cole (formato TOML, veja `.streamlit/secrets.toml.example`):

```toml
APP_PASSWORD = "uma-senha-forte"
# opcionais:
GOOGLE_PLACES_API_KEY = ""
CNPJ_SEARCH_TOKEN = ""
SYMPLA_TOKEN = ""
AGENDOR_TOKEN = ""
```

O app lê tudo via `os.getenv`/`st.secrets` (config.py) — não precisa de código extra.

## 4. Pós-deploy (segurança) — NÃO PULAR
- **Restringir viewers por e-mail**: Settings → Sharing → adicionar só os e-mails da equipe. A URL é pública; a senha é a 2ª barreira, não a única.
- Usar **senha forte** em `APP_PASSWORD` (não reaproveite senhas de outros apps internos).
- Se algum token vazar no git, ele é permanente no histórico — a defesa é nunca commitar (`.gitignore`) + repo privado.

## 5. Automação (opcional)
O `cli.py` roda headless para alimentar o Agendor. Agende no **Agendador de Tarefas do Windows**:
```
python C:\Users\pedro.porpino\prospeccao-sdr\cli.py --fontes pncp sigmine --uf AM PA --enviar-agendor --temperatura quente
```
(As chaves vêm do `.env` local; o Streamlit Cloud não roda o cli.)
