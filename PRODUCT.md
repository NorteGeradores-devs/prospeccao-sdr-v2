# Product

## Register

product

## Platform

web

## Users

O usuário é a equipe comercial da Norte Geradores — SDRs e vendedores que trabalham locação e venda de grupos moto geradores. O contexto de uso é a prospecção ativa: sentado no console (desktop, no escritório) garimpando quem precisa de energia própria ou de backup, antes de partir para a ligação ou visita. O trabalho a ser feito é sair de "não sei quem abordar" para "tenho uma lista priorizada de quem comprar/alugar gerador, com contato na mão".

A mesma tela é, ocasionalmente, apresentada ao vivo para a diretoria e para clientes numa reunião — não existe uma vitrine separada. Isso significa que a operação precisa se sustentar sozinha na projeção: profissional o bastante para impressionar rodando, sem precisar de um "modo demo".

## Product Purpose

Transformar dado público espalhado em oportunidade de venda pronta para trabalhar. A ferramenta busca leads em cinco fontes públicas (PNCP, Google Places, CNPJ, Sympla, SIGMINE), enriquece os contatos com a Receita Federal, pontua cada empresa pelo perfil de cliente ideal (ICP, com peso extra para os estados do Norte) e entrega uma lista ordenada — que o SDR exporta ou envia direto para o CRM Agendor.

Sucesso é quando a ferramenta encurta o caminho inteiro do funil de entrada: o lead quente vira oportunidade no Agendor sem retrabalho, o SDR gasta minutos e não horas garimpando, empresas novas que ninguém tinha mapeado aparecem, e o score dá confiança para atacar na ordem certa. Os quatro juntos — não um só.

## Positioning

O único lugar onde dados públicos dispersos viram uma lista pontuada e acionável de quem compra ou aluga gerador no Norte — sem garimpo manual, sem planilha morta.

## Brand Personality

Ágil e afiado, enxuto e moderno. A voz é a de um instrumento de precisão: direta, sem enfeite, vai ao ponto e responde rápido. Não é fofa nem "corporativa formal" — é a sensação de ter uma ferramenta boa na mão, que dá segurança para bater meta. O tom emocional é confiança + velocidade: o SDR sente que está no controle e que a próxima ligação está a um clique.

Como a tela é mostrada ao vivo, essa afiação também é o que a torna apresentável: a sobriedade e a precisão são o que impressiona, não o brilho.

## Anti-references

- **Planilha / Streamlit genérico**: cara de protótipo, tabelão cru sem identidade, widgets soltos. É exatamente o que esta v2 saiu para superar.
- **SaaS colorido e lúdico**: gradientes, ilustrações fofas, excesso de cor. Cor aqui é sinal (amarelo = quente), nunca decoração.
- **Dashboard corporativo pesado**: denso, cinza, cheio de painéis que ninguém olha. Densidade sem hierarquia é ruído.
- **Landing page marqueteira**: hero gigante, eyebrows em toda seção, blocos de venda. O lado de apresentação vem da operação bem-feita, não de uma vitrine.

## Design Principles

Instrumento, não planilha — cada tela é ferramenta de trabalho: o dado existe para virar ação (ligar, exportar, enviar ao Agendor), não para ser admirado.

Priorização conduz o olho — o score é o eixo da interface; o quente salta primeiro, e a ordem em que as coisas aparecem carrega informação, não é acaso.

Do lead à ação em poucos cliques — nada se interpõe entre o SDR e a próxima ligação; o caminho para o Agendor é curto e óbvio.

Apresentável sem modo demo — a operação real é digna de uma reunião com a diretoria como está; a sobriedade é a qualidade que impressiona.

Cor é a luz da marca, não enfeite — sobre a superfície preto-marinho (a noite), o amarelo Norte é o acento de ação, seleção e foco, e o "quente" acende com glow. Restrito e proposital: a luz é rara para significar algo.

## Accessibility & Inclusion

Bom padrão de acessibilidade, sem formalidade de certificação. O compromisso é prático: texto de corpo legível (o design system já mira contraste ~4.5:1), foco de teclado sempre visível (`:focus-visible` em todo controle, com contorno branco sobre superfícies escuras), e respeito a `prefers-reduced-motion` (animações viram transição instantânea). Não se persegue um selo WCAG AA formal como entregável — mira-se o comportamento correto porque a ferramenta é usada o dia inteiro e a leitura precisa ser confortável.
