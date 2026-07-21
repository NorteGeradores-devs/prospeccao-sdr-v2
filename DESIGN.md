---
name: Prospecção SDR — Norte Geradores
description: Console de prospecção "O Farol · Papel & Tinta" — papel claro emoldurado por tinta preta, amarelo travado como sinal de "quente".
colors:
  amarelo-farol: "#fff100"
  tinta-marinha: "#000917"
  tinta-hover: "#0b1524"
  corpo: "#1b2430"
  nevoa: "#5b6675"
  bruma: "#8a94a3"
  papel-frio: "#f5f6f8"
  superficie: "#ffffff"
  papel-afundado: "#eef0f3"
  hairline: "#e2e5ea"
  borda-forte: "#d2d7de"
  on-tinta: "#e9ecf1"
  on-tinta-nevoa: "#9aa4b2"
  morno-bg: "#fff3e0"
  morno-fg: "#8a5200"
  frio-bg: "#eef1f5"
  frio-fg: "#4b5566"
  sucesso: "#1e874b"
  perigo: "#c6303b"
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
    backgroundColor: "{colors.tinta-marinha}"
    textColor: "#ffffff"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    height: "40px"
    padding: "0 16px"
  button-primary-hover:
    backgroundColor: "{colors.tinta-hover}"
    textColor: "#ffffff"
  button-secondary:
    backgroundColor: "{colors.superficie}"
    textColor: "{colors.tinta-marinha}"
    rounded: "{rounded.lg}"
    height: "40px"
    padding: "0 16px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.tinta-marinha}"
    rounded: "{rounded.lg}"
    height: "40px"
    padding: "0 16px"
  input:
    backgroundColor: "{colors.superficie}"
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
    backgroundColor: "{colors.tinta-marinha}"
    textColor: "#ffffff"
    rounded: "{rounded.md}"
    height: "30px"
    padding: "0 12px"
  source-card:
    backgroundColor: "{colors.superficie}"
    textColor: "{colors.tinta-marinha}"
    rounded: "{rounded.lg}"
    padding: "12px 16px"
  temp-badge-quente:
    backgroundColor: "{colors.amarelo-farol}"
    textColor: "{colors.tinta-marinha}"
    rounded: "{rounded.sm}"
    height: "20px"
    padding: "0 8px"
---

# Design System: Prospecção SDR — Norte Geradores

## 1. Overview

**Creative North Star: "O Farol · Papel & Tinta"**

Um console de operação, não uma vitrine. O sistema é uma mesa de trabalho de papel claro (`#f5f6f8`) emoldurada por uma barra de tinta preta-marinha (`#000917`) — o *bezel* que segura a operação. Sobre esse papel, o dado vira ação: tabelas densas mas legíveis, medidores que se comportam como instrumentos, e um único ponto de luz — o amarelo `#fff100` — que só acende no que está **quente**. É o farol: a luz que diz onde o olho pousa primeiro.

A voz é **afiada e instrumental**. Controles precisos de cantos suaves, retângulos sóbrios, resposta rápida — a sensação de ter uma ferramenta boa na mão. Nada aqui é decorativo por decorar: cada cor, peso e sombra carrega função. A tipografia mistura Archivo (títulos, com aperto óptico) e IBM Plex Sans (corpo), com IBM Plex Mono reservado a números — porque score, valor e contagem são leituras de instrumento, e leitura de instrumento é monoespaçada.

O sistema **rejeita** explicitamente: cara de planilha crua ou protótipo Streamlit; SaaS colorido e lúdico (gradientes, ilustrações fofas, cor por decoração); dashboard corporativo pesado (cinza, denso, cheio de widget que ninguém olha); e a estética de landing page marqueteira (hero gigante, eyebrows em toda seção). A sobriedade e a precisão são o que sustenta a tela numa projeção — sem precisar de um "modo demo".

**Key Characteristics:**
- **Papel & Tinta:** superfícies de papel claro, moldura de tinta preta-marinha. Sem dark mode; sem cinza corporativo.
- **Amarelo é sinal, nunca enfeite:** `#fff100` é travado no significado "quente". Se aparece, quer dizer algo.
- **Números são instrumento:** todo dígito (score, valor, contagem) vem em mono com tabular-nums.
- **Plano por padrão:** hairlines de 1px organizam o espaço; sombra só aparece no que flutua (drawer, barra de seleção, toast).
- **Denso, mas com hierarquia:** tabela de trabalho com respiro no grid de 4px; o score conduz o olho.

## 2. Colors

A paleta é quase monocromática de propósito — papel e tinta — para que o amarelo signifique alguma coisa quando surge. Cor aqui é sinal e estado, não temperamento.

### Primary
- **Amarelo Farol** (`#fff100`): o único acento saturado, e o amarelo **cheio** é travado em "quente" — preenchimento do medidor de score, badge de temperatura quente, segmento "Quente" do filtro, o pulso do farol no toprail e nos estados vazios. Nunca é fundo de página, nunca é texto sobre papel (1,18:1 — ilegível). Sobre tinta marinha rende 16,96:1. Sua versão **translúcida** (14%, `--yellow-tint`) estende o sinal a estados correlatos ao calor — linha selecionada, motivo positivo de score. A única marca decorativa cheia que escapa disso é o ponto que assinala a pill "CCEE" no toprail.

### Neutral — Tinta (frente)
- **Tinta Marinha** (`#000917`): a tinta. Azul-marinho quase preto, cor oficial da marca. É a moldura (toprail, painel de login), o texto de maior peso (títulos), o fundo do botão primário, o estado selecionado de chips e a borda interna da linha **em foco** (teclado). 19,97:1 sobre branco.
- **Tinta Hover** (`#0b1524`): a tinta um passo mais clara, só para hover do botão primário.
- **Corpo** (`#1b2430`): o texto de leitura corrente. 14,48:1 sobre o papel — este é o texto, não um cinza claro "por elegância".
- **Névoa** (`#5b6675`): cinza médio para texto secundário — labels, chaves de resumo, descrições de apoio, placeholder de campo. Piso de legibilidade respeitado (5,39:1 sobre papel, 5,83:1 sobre branco).
- **Bruma** (`#8a94a3`): o cinza mais claro. **Reservado a marcas decorativas e ícones** (setas de ordenação, ícones de contato apagados, o traço "—" de vazio). Rende ~3:1 — abaixo do piso de texto, então **nunca** carrega texto que precise ser lido.

### Neutral — Papel (superfícies)
- **Papel Frio** (`#f5f6f8`): o canvas da aplicação. Cinza-papel levíssimo, frio, não creme.
- **Superfície** (`#ffffff`): branco puro dos cartões, tabela, campos e overlays — o que "sobe" do papel.
- **Papel Afundado** (`#eef0f3`): o tom rebaixado — trilho do medidor, fundo de textarea, tag de fonte, hover de botão fantasma.
- **Hairline** (`#e2e5ea`) e **Borda Forte** (`#d2d7de`): as duas espessuras de traço de 1px. Hairline separa (divisórias, bordas de cartão); borda forte contém (campos, botão secundário, segmented).

### Neutral — sobre a Tinta
- **Sobre-Tinta** (`#e9ecf1`): texto claro sobre a moldura marinha — a cor de texto padrão do toprail e a contagem da barra de seleção (o wordmark em si vai a branco puro). 16,87:1.
- **Sobre-Tinta Névoa** (`#9aa4b2`): texto secundário sobre a moldura (subtítulo central, pills). 7,92:1.

### Secondary — Temperatura (estado, não marca)
- **Brasa Morna** (fundo `#fff3e0`, texto `#8a5200`, ponto `#f5a300`): o "morno". Âmbar quente e discreto — 5,82:1. É o único lugar onde um laranja aparece, e é estado, não acento de marca.
- **Frio** (fundo `#eef1f5`, texto `#4b5566`): o "frio". Cinza-azulado neutro — 6,64:1. Ausência de calor, literalmente.

### Tertiary — Funcional
- **Sucesso** (`#1e874b`): verde de confirmação — toasts de sucesso, ícone de contato presente, o *flash* de cópia. **O flash de "copiado" é verde, nunca amarelo** — amarelo é travado em "quente".
- **Perigo** (`#c6303b`): vermelho de erro — toasts de erro, motivos negativos de score, situação cadastral irregular.

### Named Rules
**A Regra do Sinal.** O amarelo **cheio** (`#fff100`) só significa "quente" — nunca fundo de página, nunca hover genérico. O sinal se estende, translúcido, a estados correlatos ao calor (seleção, motivo positivo); como cor decorativa cheia, só o ponto da pill CCEE. A raridade é o ponto.

**A Regra Papel & Tinta.** O fundo é papel claro; a estrutura é tinta preta-marinha. Sem dark mode "porque fica moderno", sem creme/bege, sem cinza corporativo. Calor vem do amarelo e da tipografia, nunca de um fundo tingido.

## 3. Typography

**Display Font:** Archivo (fallback Segoe UI, system-ui, sans-serif)
**Body Font:** IBM Plex Sans (fallback system-ui, -apple-system, Segoe UI, sans-serif)
**Label/Mono Font:** IBM Plex Mono (fallback ui-monospace, Cascadia Mono, Menlo, monospace)

**Character:** um par de contraste, não de similaridade. Archivo é uma grotesca condensada de peso 600–700 com aperto óptico (`letter-spacing: -0.01em`) para títulos que "seguram" a tela; IBM Plex Sans é humanista, calma e altamente legível a 14px para o corpo. O mono não é opção — é identidade: todo número é leitura de instrumento.

### Hierarchy
- **Display** (Archivo 700, 28px, line 32px, `-0.01em`): título da tela de login. O maior texto do app; teto propositalmente baixo — o console não grita.
- **Headline** (Archivo 700, 20px): nome do lead no drawer, cabeçalho "Leads" da tabela. Sem aperto de tracking — o `-0.01em` fica só no Display.
- **Title** (Archivo 600, 16px): título de cartão-resumo e blocos de seção.
- **Body** (IBM Plex Sans 400, 14px / line 20px): a base de tudo. Comprimento de linha de leitura corrente mantido curto (drawer ~34–40ch); nunca prosa larga.
- **Label** (Archivo 600, 11px, `letter-spacing: 0.08em`, UPPERCASE): a *eyebrow* — rótulos de seção e de célula de métrica. **Uso deliberado e nomeado**, não scaffolding em toda seção.
- **Mono** (IBM Plex Mono, pesos 400–600, 11–28px, `font-feature-settings: "tnum" 1`): números — do valor-instrumento de 28px nos tiles de métrica ao score de 15px na linha, mais contagem CCEE, tags de fonte e pesos de motivo.

### Named Rules
**A Regra do Instrumento.** Todo número que o operador lê como medida — score, R$, contagem, prazo — vem em IBM Plex Mono com tabular-nums. Números nunca ficam na fonte de corpo; a monoespessura é o que faz a tabela ler como painel de instrumento.

**A Regra da Eyebrow Nomeada.** O rótulo em caixa-alta tracked (`.eyebrow`) é um elemento de sistema, usado em métricas e cabeçalhos de seção da busca — não um kicker reflexo acima de cada bloco. Se aparece, nomeia uma região real.

## 4. Elevation

O sistema é **plano por padrão**. Profundidade se organiza com traços de 1px (hairline e borda forte) e com o rebaixamento tonal do Papel Afundado — não com sombra. Sombra é cara e só aparece no que **genuinamente flutua sobre o papel**: o drawer de detalhe, a barra de seleção fixa, os toasts e overlays. Nunca em cartões ou linhas em repouso.

### Shadow Vocabulary
- **Overlay** (`box-shadow: 0 8px 24px rgba(0,9,23,0.12), 0 1px 2px rgba(0,9,23,0.08)`): elementos que pairam — drawer, barra de seleção, toast. A sombra é tingida com a tinta marinha, não preto puro.
- **Pin** (`box-shadow: 0 4px 12px rgba(0,9,23,0.06)`): token de elevação sutil **definido mas ainda sem uso** — reservado para um estado afixado/em foco. Registrado para não ser reinventado com outro valor.
- **Focus ring** (`0 0 0 3px rgba(0,9,23,0.1)` + borda tinta): não é elevação, é estado — o "glow" de foco de campos.

### Named Rules
**A Regra do Plano em Repouso.** Superfícies são planas em repouso. Sombra é uma resposta a estado (flutuar, focar), nunca decoração de cartão. Se um cartão tem sombra parado na tela, está errado — use hairline.

## 5. Components

O caráter geral: **afiado e instrumental**. Cantos suaves (4–8px, nunca pílula), traços de 1px, transições curtas (80–160ms) com curvas *ease-out*. Tudo responde rápido e sem drama.

### Buttons
- **Shape:** cantos suaves (8px, `--r-lg`). Altura 40px (32px na variante `sm`). Peso 600.
- **Primary:** fundo Tinta Marinha (`#000917`), texto branco. Hover clareia para Tinta Hover (`#0b1524`). O CTA "Enviar ao Agendor" e ações de confirmação.
- **Secondary:** fundo branco, texto tinta, borda forte de 1px (`#d2d7de`). Hover para `#f1f3f6`. Ações neutras (CSV, Excel, Refinar).
- **Ghost:** só texto tinta; hover ganha fundo Papel Afundado. Ações terciárias (limpar filtros).
- **On-dark:** sobre a moldura marinha, invertem — fundo branco/contorno claro, para "Nova busca" e "Sair".
- **Feedback:** `:active` aplica `transform: scale(0.99)` — um clique tátil, não um bounce.

### Chips
- **Style:** retângulo de 30px, borda hairline, texto Névoa, **fonte mono em caixa-alta** (é rótulo técnico — UF, fonte).
- **State:** selecionado inverte para fundo Tinta Marinha + texto branco (`aria-pressed="true"`). Sem meio-termo colorido.

### Cards / Containers
- **Corner Style:** 8px (`--r-lg`).
- **Background:** Superfície branca sobre o Papel Frio; cabeçalhos de tabela e trilhos usam Papel Afundado.
- **Shadow Strategy:** **nenhuma em repouso** (ver Elevation). Definição vem da borda hairline de 1px.
- **Border:** hairline (`#e2e5ea`) para separar; borda forte (`#d2d7de`) só quando o container precisa conter interação.
- **Internal Padding:** 16–24px (`--sp-4`/`--sp-6`), no grid de 4px.
- **Source card** (seleção de fonte): estado ativo troca a borda por um traço tinta de 2px (compensado no padding para não pular layout) + um *check* que aparece — nunca um preenchimento colorido.

### Inputs / Fields
- **Style:** fundo branco, borda forte de 1px, cantos 8px, altura 40px. Textarea usa fundo Papel Afundado e fonte mono (é entrada técnica — keywords, CNPJs).
- **Focus:** borda vira tinta + anel `0 0 0 3px rgba(0,9,23,0.1)`. Firme, não difuso.
- **Placeholder:** cor Névoa (`#5b6675`, 5,83:1) — legível. **Nunca Bruma:** placeholder é texto e precisa de ≥ 4,5:1.
- **Switch / Slider:** trilho cinza que vira tinta quando ligado; polegar branco de cantos suaves. O switch é o único lugar com uma curva levemente elástica (`cubic-bezier(0.34,1.56,0.64,1)`) — o "clique" do interruptor.

### Navigation
- **Toprail:** barra fixa de 56px em Tinta Marinha, `z-index: 40`. Wordmark "Norte · Prospecção" em Archivo 700 branco, precedido pelo farol pulsante. Centro em mono Sobre-Tinta Névoa com o resumo da busca; direita com pill CCEE, "Nova busca" e "Sair". Foco visível inverte para contorno branco sobre a moldura escura.
- **Filters bar:** faixa *sticky* logo abaixo do toprail (`top: 56px`), fundo papel, com o *segmented control* de temperatura (Todos / Quente / Morno / Frio). O segmento "Quente" ativo é o raro caso de fundo amarelo — porque é temperatura.

### Signature Components
- **O Farol (beacon):** ponto de 8px em Amarelo Farol com halo `0 0 0 3px rgba(255,241,0,0.18)`, pulsando suave (scale 1→1.15, opacity 0.7→1, 2200ms, `easeInOutSine`, alternate). É o **único loop de marca** e a assinatura visual — os outros loops contínuos são apenas estados de carregamento (barra de progresso, shimmer do skeleton). Aparece no toprail e nos estados vazios ("acender o farol").
- **Score Meter:** número mono (tabular) + trilho de 64px com preenchimento colorido pela temperatura (frio cinza-claro, morno cinza-médio, quente amarelo com keyline). As barras "assentam" na entrada (`easeOutCubic`, 520ms, stagger 18ms) — comportamento de instrumento, não enfeite.
- **Temp Badge:** cápsula de 20px com ponto + rótulo. Quente = amarelo sobre tinta (keyline interna); morno = brasa; frio = cinza-azulado. O acento de 3px na borda esquerda da linha/cartão (`temp-accent`) é um filete colorido **sancionado** — ao lado do filete de status do toast — porque codifica dado (temperatura), não decora.
- **Selection Bar:** barra flutuante fixa em Tinta Marinha, centralizada na base, com contagem mono e ações. Entra por baixo (`easeOutCubic`, 260ms).

## 6. Do's and Don'ts

### Do:
- **Do** manter o Amarelo Farol (`#fff100`) travado em "quente" — medidor, badge, segmento, farol. Se acender, significa temperatura.
- **Do** compor sobre Papel & Tinta: papel claro (`#f5f6f8` / `#ffffff`) emoldurado por tinta marinha (`#000917`).
- **Do** usar IBM Plex Mono com `tnum` para todo número que é medida (score, R$, contagem, prazo).
- **Do** organizar profundidade com hairlines de 1px e rebaixo tonal; reservar sombra para o que flutua (drawer, barra de seleção, toast).
- **Do** usar texto Corpo (`#1b2430`) para leitura e Névoa (`#5b6675`) para secundário — ambos ≥ 4,5:1.
- **Do** manter transições curtas (80–260ms) com curvas *ease-out*, e um alternativo para `prefers-reduced-motion` (o app zera durações e mata o loop do farol).

### Don't:
- **Don't** deixar o app com **cara de planilha crua ou protótipo Streamlit** — tabelão sem hierarquia, widgets soltos, sem identidade.
- **Don't** cair em **SaaS colorido e lúdico** — gradientes, ilustrações fofas, cor por decoração. Cor aqui é sinal e estado.
- **Don't** virar **dashboard corporativo pesado** — cinza, denso, cheio de painel que ninguém olha.
- **Don't** adotar estética de **landing page marqueteira** — hero gigante, *eyebrow* acima de cada seção, blocos de venda. Isto é console, não vitrine.
- **Don't** usar Amarelo Farol como fundo, hover genérico ou texto sobre papel (1,18:1 — ilegível). E **nunca** o *flash* de "copiado" em amarelo: ele é verde (`#1e874b`).
- **Don't** usar Bruma (`#8a94a3`) para texto que precise ser lido — é decorativa (~3:1). Placeholder e labels usam Névoa.
- **Don't** aplicar `background-clip: text` com gradiente, ou glassmorphism decorativo. Filete colorido de borda-esquerda só é sancionado quando **codifica estado** — o `temp-accent` de 3px da linha (temperatura) e o filete de status do toast (sucesso/erro); como enfeite, nunca.
- **Don't** pôr sombra em cartão ou linha em repouso — se está parado na tela, é plano.
