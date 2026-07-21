---
name: Prospecção SDR — Norte Geradores
description: Console de prospecção "O Farol Aceso" — superfície preto-marinho (a noite) com amarelo Norte como a luz da marca; o "quente" acende com glow.
colors:
  amarelo-farol: "#fff100"
  amarelo-press: "#e6da00"
  noite: "#0a1120"
  tinta: "#131f33"
  poco: "#070d18"
  elevado: "#1b2947"
  casco: "#060b16"
  hairline: "#2a3a56"
  borda-forte: "#465d80"
  luz: "#f5f7fb"
  corpo: "#cdd6e4"
  nevoa: "#93a1b8"
  bruma: "#61708a"
  on-farol: "#0a1120"
  morno-fg: "#f6b65a"
  morno-dot: "#f5a300"
  frio-fg: "#9fb0c6"
  frio-dot: "#6b7a90"
  sucesso: "#35c880"
  perigo: "#ff6b76"
  meter-frio: "#47566e"
  meter-morno: "#b8791f"
typography:
  display:
    fontFamily: "Archivo, Segoe UI, system-ui, sans-serif"
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1.14
    letterSpacing: "-0.01em"
  headline:
    fontFamily: "Archivo, Segoe UI, system-ui, sans-serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "normal"
  title:
    fontFamily: "Archivo, Segoe UI, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "normal"
  body:
    fontFamily: "IBM Plex Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: "20px"
    letterSpacing: "normal"
  label:
    fontFamily: "Archivo, Segoe UI, system-ui, sans-serif"
    fontSize: "11px"
    fontWeight: 600
    lineHeight: "14px"
    letterSpacing: "0.08em"
  mono:
    fontFamily: "IBM Plex Mono, ui-monospace, Cascadia Mono, Menlo, monospace"
    fontSize: "13px"
    fontWeight: 500
    lineHeight: 1.5
    letterSpacing: "normal"
    fontFeature: "'tnum' 1"
rounded:
  sm: "4px"
  md: "6px"
  lg: "8px"
  meter: "3px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  "2xl": "48px"
components:
  button-primary:
    backgroundColor: "{colors.amarelo-farol}"
    textColor: "{colors.on-farol}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    height: "40px"
    padding: "0 16px"
  button-primary-hover:
    backgroundColor: "{colors.amarelo-press}"
    textColor: "{colors.on-farol}"
  button-secondary:
    backgroundColor: "{colors.tinta}"
    textColor: "{colors.luz}"
    rounded: "{rounded.lg}"
    height: "40px"
    padding: "0 16px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.luz}"
    rounded: "{rounded.lg}"
    height: "40px"
    padding: "0 16px"
  input:
    backgroundColor: "{colors.tinta}"
    textColor: "{colors.corpo}"
    rounded: "{rounded.lg}"
    height: "40px"
    padding: "0 12px"
  chip:
    backgroundColor: "transparent"
    textColor: "{colors.nevoa}"
    rounded: "{rounded.md}"
    height: "30px"
    padding: "0 12px"
  chip-selected:
    backgroundColor: "{colors.amarelo-farol}"
    textColor: "{colors.on-farol}"
    rounded: "{rounded.md}"
    height: "30px"
    padding: "0 12px"
  source-card:
    backgroundColor: "{colors.tinta}"
    textColor: "{colors.luz}"
    rounded: "{rounded.lg}"
    padding: "12px 16px"
  temp-badge-quente:
    backgroundColor: "{colors.amarelo-farol}"
    textColor: "{colors.on-farol}"
    rounded: "{rounded.sm}"
    height: "20px"
    padding: "0 8px"
---

# Design System: Prospecção SDR — Norte Geradores

## 1. Overview

**Creative North Star: "O Farol Aceso"**

Um console de operação, não uma vitrine — e à noite. A superfície é a tinta da marca levada ao extremo: um preto-marinho profundo (`#0a1120`) que ocupa quase tudo. Sobre esse escuro, o amarelo `#fff100` da Norte é a **luz** — o farol aceso. Ele acende na ação (botão primário), na seleção (chip ligado, fonte escolhida), no foco e, glowing, no que está **quente**. É a marca preto-e-amarelo da Norte assumida por inteiro: industrial, de energia, inconfundível numa reunião.

A voz é **afiada e instrumental**. Controles precisos de cantos suaves, retângulos sóbrios, resposta rápida. No escuro, a profundidade vem da **luminância das superfícies**, não de sombra: a tinta base é a mais escura, cartões e a tabela sobem um degrau, painéis flutuantes sobem outro. A tipografia mistura Archivo (títulos) e IBM Plex Sans (corpo), com IBM Plex Mono reservado a números — porque score, valor e contagem são leituras de instrumento.

O sistema **rejeita** explicitamente: cara de planilha crua ou protótipo Streamlit; SaaS colorido e lúdico (gradientes, ilustrações fofas); dashboard corporativo pesado (cinza, denso, cheio de widget que ninguém olha); e a estética de landing page marqueteira (hero gigante, eyebrows em toda seção). O escuro aqui é decisão de marca, não moda: preto e amarelo são as cores da Norte.

**Key Characteristics:**
- **Preto & Amarelo:** superfície preto-marinho (a noite), amarelo Norte como a luz. Sem tema claro; as cores são as da marca.
- **Amarelo é a luz da marca:** acento de ação, seleção, foco e estado. Restrito e proposital — nunca inunda a tela.
- **O quente acende:** badge e medidor "quente" ganham glow amarelo; destacam mesmo com o amarelo sendo acento geral.
- **Profundidade por luz, não sombra:** superfícies mais claras = mais altas; hairlines de 1px organizam o resto.
- **Números são instrumento:** todo dígito (score, valor, contagem) vem em mono com tabular-nums.

## 2. Colors

Quase monocromática de propósito — a noite preto-marinho — para que o amarelo signifique alguma coisa quando acende. Cor aqui é a marca, o sinal e o estado; nunca decoração.

### Primary
- **Amarelo Farol** (`#fff100`): a luz. Acento principal da interface e cor da marca — botão primário (texto preto, `--on-farol`), estado selecionado de chips e cards de fonte, aresta da linha em foco, anel de foco de campos, o pulso do farol, a barra de progresso. Sobre a noite rende 16,01:1. **Nunca é texto sobre papel claro** (não há papel) e sempre carrega texto preto quando é fundo.
- **Amarelo Brasa** (`#e6da00`): o mesmo amarelo pressionado (`:active`/hover do primário).

### Neutral — Tinta (superfícies escuras)
- **Noite** (`#0a1120`): o canvas base da aplicação — preto-marinho profundo, a extensão da tinta da marca.
- **Tinta** (`#131f33`): a superfície de trabalho um degrau acima — cartões, tabela, campos, cabeçalho de tabela.
- **Poço** (`#070d18`): o degrau rebaixado — trilho do medidor, fundo de textarea, tags de fonte.
- **Elevado** (`#1b2947`): painéis que flutuam — barra de seleção (e o tom de referência da elevação máxima).
- **Casco** (`#060b16`): a moldura mais profunda — toprail e painel de login, o bezel que segura a operação.
- **Hairline** (`#2a3a56`) e **Borda Forte** (`#465d80`): as duas espessuras de traço de 1px. Hairline separa (divisórias, bordas de cartão); borda forte contém (campos, botão secundário, segmented).

### Neutral — Luz (texto claro)
- **Luz** (`#f5f7fb`): o texto de máxima ênfase — títulos, nomes, valores. 17,58:1 sobre a noite; este é o texto forte, não um cinza.
- **Corpo** (`#cdd6e4`): a leitura corrente. 12,87:1 — confortável o dia inteiro.
- **Névoa** (`#93a1b8`): texto secundário — labels, descrições, placeholder de campo, ícones apagados. 7,21:1 sobre a noite (bem acima do piso).
- **Bruma** (`#61708a`): o cinza mais claro, decorativo — setas de ordenação, o traço "—" de vazio. ~3,76:1: **nunca** carrega texto que precise ser lido.
- **Sobre-Casco** (`#e9ecf1`): texto claro sobre a moldura (rótulos do toprail, contagem da barra de seleção). 16,62:1.

### Secondary — Temperatura (estado)
- **Quente**: amarelo cheio (`#fff100`) com texto preto e **glow** (`0 0 10px rgba(255,241,0,0.30)`) — o badge e o medidor acendem. É o único elemento amarelo que brilha, e é isso que o separa do amarelo-acento (botões/chips) mesmo no escuro.
- **Morno** (fundo âmbar translúcido, texto `#f6b65a`, ponto `#f5a300`): âmbar quente — 6,96:1. O único laranja da tela, e é estado.
- **Frio** (fundo slate translúcido, texto `#9fb0c6`): cinza-azulado frio — 6,01:1. Ausência de calor.

### Tertiary — Funcional
- **Sucesso** (`#35c880`): verde de confirmação, calibrado para o escuro — toasts, ícone de contato presente, o *flash* de cópia. 7,65:1 sobre a tinta. **O flash de "copiado" é verde, nunca amarelo** — amarelo é ação/marca.
- **Perigo** (`#ff6b76`): coral de erro — toasts, motivos negativos, situação irregular. 5,99:1.

### Named Rules
**A Regra da Luz.** O amarelo cheio (`#fff100`) é a luz da marca e só aparece com propósito: ação (botão primário), seleção (chip/fonte ativos), foco, o farol e o "quente". Nunca é fundo de grandes áreas, nunca é texto, nunca é decoração. A superfície é a noite; a luz é rara — é isso que a faz significar.

**A Regra do Quente Aceso.** Como o amarelo agora é acento geral, o "quente" se distingue **acendendo**: badge e medidor quentes ganham glow. Morno é âmbar, frio é slate. O quente é o único amarelo que brilha.

## 3. Typography

**Display Font:** Archivo (fallback Segoe UI, system-ui, sans-serif)
**Body Font:** IBM Plex Sans (fallback system-ui, -apple-system, Segoe UI, sans-serif)
**Label/Mono Font:** IBM Plex Mono (fallback ui-monospace, Cascadia Mono, Menlo, monospace)

**Character:** um par de contraste, não de similaridade. Archivo é uma grotesca condensada de peso 600–700 com aperto óptico (`letter-spacing: -0.01em`) para títulos que "seguram" a tela; IBM Plex Sans é humanista, calma e legível a 14px em texto claro sobre o escuro. O mono não é opção — é identidade: todo número é leitura de instrumento.

### Hierarchy
- **Display** (Archivo 700, 28px, line 32px, `-0.01em`): título da tela de login. O maior texto do app; teto propositalmente baixo — o console não grita.
- **Headline** (Archivo 700, 20px): nome do lead no drawer, cabeçalho "Leads" da tabela. Sem aperto de tracking — o `-0.01em` fica só no Display.
- **Title** (Archivo 600, 16px): título de cartão-resumo e blocos de seção.
- **Body** (IBM Plex Sans 400, 14px / line 20px): a base de tudo. Comprimento de linha de leitura corrente mantido curto (drawer ~34–40ch); nunca prosa larga.
- **Label** (Archivo 600, 11px, `letter-spacing: 0.08em`, UPPERCASE): a *eyebrow* — rótulos de seção e de célula de métrica. Uso deliberado e nomeado, não scaffolding em toda seção.
- **Mono** (IBM Plex Mono, pesos 400–600, 11–28px, `font-feature-settings: "tnum" 1`): números — do valor-instrumento de 28px nos tiles de métrica ao score de 15px na linha, mais contagem CCEE, tags de fonte e pesos de motivo.

### Named Rules
**A Regra do Instrumento.** Todo número que o operador lê como medida — score, R$, contagem, prazo — vem em IBM Plex Mono com tabular-nums. A monoespessura faz a tabela ler como painel de instrumento.

**A Regra da Eyebrow Nomeada.** O rótulo em caixa-alta tracked é um elemento de sistema (métricas, cabeçalhos de seção da busca), não um kicker reflexo acima de cada bloco.

## 4. Elevation

Tema escuro: **profundidade vem da luminância das superfícies, não de sombra**. Há uma escala de quatro degraus — Casco (`#060b16`, moldura) < Noite (`#0a1120`, base) < Tinta (`#131f33`, cartões/tabela) < Elevado (`#1b2947`, painéis flutuantes) — e é a diferença de luz entre eles que cria a hierarquia. Sombra é secundária: existe para separar o que **genuinamente flutua** (drawer, barra de seleção, toast), reforçada por uma borda hairline, porque no escuro a sombra sozinha some.

### Shadow Vocabulary
- **Overlay** (`box-shadow: 0 12px 32px rgba(0,0,0,0.5), 0 2px 8px rgba(0,0,0,0.4)`): elementos que pairam — drawer, barra de seleção, toast. Sombra preta e mais densa que no claro, para separar do fundo escuro; sempre acompanhada de superfície mais clara + borda.
- **Pin** (`box-shadow: 0 6px 16px rgba(0,0,0,0.35)`): token de elevação sutil **definido mas ainda sem uso** — reservado para um estado afixado/em foco.
- **Glow do Farol** (`0 0 10px rgba(255,241,0,0.30)`): não é elevação, é sinal — o brilho do "quente" (badge e medidor).
- **Focus ring** (`0 0 0 3px rgba(255,241,0,0.18)` + borda amarela): estado de foco de campos — o anel agora é amarelo (a luz da marca).

### Named Rules
**A Regra do Degrau de Luz.** Elevar = clarear. Um cartão sobe virando uma superfície mais clara (Tinta sobre Noite), não ganhando sombra parado. Se algo precisa "subir", troca o tom de superfície; sombra só entra quando o elemento realmente flutua sobre o conteúdo.

## 5. Components

O caráter geral: **afiado e instrumental**. Cantos suaves (4–8px, nunca pílula), traços de 1px, transições curtas (80–260ms) com curvas *ease-out*. Tudo responde rápido e sem drama.

### Buttons
- **Shape:** cantos suaves (8px, `--r-lg`). Altura 40px (32px na variante `sm`). Peso 600.
- **Primary:** fundo Amarelo Farol (`#fff100`), texto preto (`--on-farol`). Hover escurece para Amarelo Brasa (`#e6da00`). É a luz da marca na ação — "Enviar ao Agendor", confirmações.
- **Secondary:** fundo Tinta (`#131f33`), texto Luz, borda forte de 1px (`#465d80`). Hover para o tom de linha (`--row-hover`). Ações neutras (CSV, Excel, Refinar).
- **Ghost:** só texto Luz; hover ganha fundo Poço. Ações terciárias (limpar filtros).
- **On-dark / outline:** sobre a moldura (barra de seleção), o CTA principal também é amarelo (`btn-on-dark`); ações secundárias são contorno claro (`btn-outline-dark`).
- **Feedback:** `:active` aplica `transform: scale(0.99)` — um clique tátil, não um bounce.

### Chips
- **Style:** retângulo de 30px, borda hairline, texto Névoa, **fonte mono em caixa-alta** (rótulo técnico — UF, fonte).
- **State:** selecionado inverte para fundo Amarelo Farol + texto preto (`aria-pressed="true"`). Seleção = a luz da marca.

### Cards / Containers
- **Corner Style:** 8px (`--r-lg`).
- **Background:** Tinta (`#131f33`) sobre a Noite; trilhos e tags usam Poço.
- **Shadow Strategy:** **nenhuma em repouso** (ver Elevation). Definição vem da borda hairline de 1px + do degrau de luz.
- **Border:** hairline (`#2a3a56`) para separar; borda forte (`#465d80`) quando o container contém interação.
- **Internal Padding:** 16–24px, no grid de 4px.
- **Source card** (seleção de fonte): estado ativo troca a borda por um traço **amarelo** de 2px + um *check* amarelo que aparece — nunca um preenchimento colorido.

### Inputs / Fields
- **Style:** fundo Tinta, borda forte de 1px, cantos 8px, altura 40px. Textarea usa fundo Poço e fonte mono (entrada técnica — keywords, CNPJs).
- **Focus:** borda vira **amarela** + anel `0 0 0 3px rgba(255,241,0,0.18)`. Firme, cor da marca.
- **Placeholder:** cor Névoa (`#93a1b8`, 6,32:1 sobre a tinta) — legível. **Nunca Bruma:** placeholder é texto e precisa de ≥ 4,5:1.
- **Switch / Slider:** trilho escuro que vira **amarelo** quando ligado; o polegar do slider é amarelo. Ligado = ativo = a luz da marca. O switch é o único lugar com uma curva levemente elástica (`cubic-bezier(0.34,1.56,0.64,1)`).

### Navigation
- **Toprail:** barra fixa de 56px em Casco (`#060b16`), `z-index: 40`. Wordmark "Norte · Prospecção" em Archivo 700 branco, precedido pelo farol pulsante. Centro em mono Sobre-Casco Névoa; direita com pill CCEE, "Nova busca" e "Sair".
- **Filters bar:** faixa *sticky* logo abaixo do toprail, fundo Noite, com o *segmented control* de temperatura. O segmento genérico selecionado usa um preenchimento slate (`--selected-fill`); o segmento **"Quente" ativo acende amarelo** (texto preto) — filtrar por quente literalmente acende a luz.

### Signature Components
- **O Farol (beacon):** ponto de 8px em Amarelo Farol com halo `0 0 0 3px rgba(255,241,0,0.18)`, pulsando suave (scale 1→1.15, opacity 0.7→1, 2200ms, `easeInOutSine`, alternate). É o **único loop de marca** e a assinatura visual — os outros loops contínuos são só estados de carregamento (barra de progresso amarela, shimmer do skeleton). Brilha no escuro — o farol aceso.
- **Score Meter:** número mono (tabular) + trilho Poço com preenchimento pela temperatura (frio slate `#47566e`, morno âmbar `#b8791f`, quente amarelo **com glow**). As barras "assentam" na entrada (`easeOutCubic`, 520ms, stagger 18ms). *(O preenchimento é `display: block` — sem isso o span inline colapsa a 0px.)*
- **Temp Badge:** cápsula de 20px com ponto + rótulo. Quente = amarelo + texto preto + glow; morno = âmbar; frio = slate. O acento de 3px na borda esquerda da linha/cartão (`temp-accent`) é um filete colorido **sancionado** — ao lado do filete de status do toast — porque codifica dado (temperatura), não decora.
- **Selection Bar:** barra flutuante fixa em Elevado (`#1b2947`, mais clara que a base) com borda hairline, contagem mono e ações. No escuro, um painel flutuante precisa **clarear** para subir — não escurecer.

## 6. Do's and Don'ts

### Do:
- **Do** tratar o amarelo (`#fff100`) como a **luz da marca**: ação, seleção, foco, farol e quente. Restrito e proposital, sempre com texto preto quando é fundo.
- **Do** compor sobre a noite preto-marinho (`#0a1120` / `#131f33`); elevar clareando a superfície, não com sombra.
- **Do** acender o "quente" com glow (badge e medidor) para que salte mesmo com o amarelo sendo acento geral.
- **Do** usar IBM Plex Mono com `tnum` para todo número que é medida (score, R$, contagem, prazo).
- **Do** usar texto Luz (`#f5f7fb`) e Corpo (`#cdd6e4`) para leitura, Névoa (`#93a1b8`) para secundário — todos ≥ 4,5:1 sobre o escuro.
- **Do** manter transições curtas (80–260ms) com curvas *ease-out*, e um alternativo para `prefers-reduced-motion` (o app zera durações e mata o loop do farol).

### Don't:
- **Don't** deixar o app com **cara de planilha crua ou protótipo Streamlit** — tabelão sem hierarquia, widgets soltos, sem identidade.
- **Don't** cair em **SaaS colorido e lúdico** — gradientes, ilustrações fofas, cor por decoração. Amarelo é marca e estado.
- **Don't** virar **dashboard corporativo pesado** — cinza morto, denso, cheio de painel que ninguém olha.
- **Don't** adotar estética de **landing page marqueteira** — hero gigante, *eyebrow* acima de cada seção, blocos de venda. Isto é console, não vitrine.
- **Don't** inundar de amarelo: ele é a luz, não a superfície. Grandes áreas amarelas, texto amarelo sobre claro (1,18:1) e amarelo decorativo são proibidos. E **nunca** o *flash* de "copiado" em amarelo: é verde (`#35c880`).
- **Don't** usar Bruma (`#61708a`) para texto que precise ser lido — é decorativa (~3,76:1). Placeholder e labels usam Névoa.
- **Don't** criar profundidade com sombra em repouso — no escuro, elevar é **clarear** a superfície. Sombra só no que flutua.
- **Don't** aplicar `background-clip: text` com gradiente ou glassmorphism decorativo; filete colorido de borda só quando **codifica estado** (temp-accent da linha, status do toast).
