# PyGameMaker IDE

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Home) | [Français](Home_fr) | [Deutsch](Home_de) | [Italiano](Home_it) | [Español](Home_es) | [Português](Home_pt) | [Slovenščina](Home_sl) | [Українська](Home_uk) | [Русский](Home_ru)

---

**Um ambiente de desenvolvimento de jogos visual inspirado no GameMaker 7.0**

PyGameMaker é uma IDE de código aberto que torna a criação de jogos 2D acessível através de programação visual baseada em blocos (Google Blockly) e um sistema de eventos-ações. Crie jogos sem conhecimentos profundos de programação e depois exporte-os para Windows, Linux, HTML5 ou plataformas móveis.

---

## Escolha Seu Nível

PyGameMaker usa **predefinições** para controlar quais eventos e ações estão disponíveis. Isso ajuda iniciantes a focar nas funcionalidades essenciais enquanto permite que usuários experientes acessem o conjunto completo de ferramentas.

| Predefinição | Ideal Para | Funcionalidades |
|--------------|------------|-----------------|
| [**Iniciante**](Beginner-Preset_pt) | Novos em desenvolvimento de jogos | 4 eventos, 17 ações - Movimento, colisões, pontuação, salas |
| [**Intermediário**](Intermediate-Preset_pt) | Alguma experiência | +4 eventos, +12 ações - Vidas, saúde, som, alarmes, desenho |
| **Avançado** | Usuários experientes | Todos os 40+ eventos e ações disponíveis |

**Novos usuários:** Comece com a [Predefinição Iniciante](Beginner-Preset_pt) para aprender os fundamentos sem se sentir sobrecarregado.

Veja o [Guia de Predefinições](Preset-Guide_pt) para uma visão completa do sistema de predefinições.

---

## Funcionalidades em Destaque

| Funcionalidade | Descrição |
|----------------|-----------|
| **Programação Visual** | Codificação arrastar e soltar com Google Blockly 12.x |
| **Sistema Eventos-Ações** | Lógica baseada em eventos compatível com GameMaker 7.0 |
| **Predefinições por Nível** | Conjuntos de funcionalidades Iniciante, Intermediário e Avançado |
| **Exportação Multi-Plataforma** | Windows EXE, HTML5, Linux, Kivy (móvel/desktop) |
| **Gestão de Recursos** | Sprites, sons, fundos, fontes e salas |
| **Interface Multilingue** | Inglês, Francês, Alemão, Italiano, Espanhol, Português, Esloveno, Ucraniano, Russo |
| **Extensível** | Sistema de plugins para eventos e ações personalizados |

---

## Primeiros Passos

### Requisitos do Sistema

- **Python** 3.10 ou superior
- **Sistema Operacional:** Windows, Linux ou macOS

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/Gabe1290/pythongm.git
   cd pythongm
   ```

2. Crie um ambiente virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # ou
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute o PyGameMaker:
   ```bash
   python main.py
   ```

---

## Conceitos Fundamentais

### Objetos
Entidades do jogo com sprites, propriedades e comportamentos. Cada objeto pode ter múltiplos eventos com ações associadas.

### Eventos
Gatilhos que executam ações quando condições específicas ocorrem:
- **Create** - Quando uma instância é criada
- **Step** - Cada frame (tipicamente 60 FPS)
- **Draw** - Fase de renderização personalizada
- **Destroy** - Quando uma instância é destruída
- **Keyboard** - Tecla pressionada, solta ou mantida
- **Mouse** - Cliques, movimento, entrada/saída
- **Collision** - Quando instâncias se tocam
- **Alarm** - Temporizadores de contagem regressiva (12 disponíveis)

Veja a [Referência de Eventos](Event-Reference_pt) para documentação completa.

### Ações
Operações realizadas quando eventos são disparados. 40+ ações integradas para:
- Movimento e física
- Desenho e sprites
- Pontuação, vidas e saúde
- Som e música
- Gestão de instâncias e salas

Veja a [Referência Completa de Ações](Full-Action-Reference_pt) para documentação completa.

### Salas
Níveis do jogo onde você posiciona instâncias de objetos, define fundos e a área de jogo.

---

## Programação Visual com Blockly

PyGameMaker integra Google Blockly para programação visual. Os blocos são organizados em categorias:

- **Eventos** - Create, Step, Draw, Keyboard, Mouse
- **Movimento** - Velocidade, direção, posição, gravidade
- **Temporização** - Alarmes e atrasos
- **Desenho** - Formas, texto, sprites
- **Pontuação/Vidas/Saúde** - Rastreamento do estado do jogo
- **Instância** - Criar e destruir objetos
- **Sala** - Navegação e gestão
- **Valores** - Variáveis e expressões
- **Som** - Reprodução de áudio
- **Saída** - Debug e exibição

---

## Opções de Exportação

### Windows EXE
Executáveis Windows independentes usando PyInstaller. Nenhum Python necessário na máquina de destino.

### HTML5
Jogos web de arquivo único que funcionam em qualquer navegador moderno. Comprimidos com gzip para carregamento rápido.

### Linux
Executáveis Linux nativos para ambientes Python 3.10+.

### Kivy
Aplicações multiplataforma para móvel (iOS/Android) e desktop via Buildozer.

---

## Estrutura do Projeto

```
nome_projeto/
├── project.json      # Configuração do projeto
├── backgrounds/      # Imagens de fundo e metadados
├── data/             # Arquivos de dados personalizados
├── fonts/            # Definições de fontes
├── objects/          # Definições de objetos (JSON)
├── rooms/            # Layouts de salas (JSON)
├── scripts/          # Scripts personalizados
├── sounds/           # Arquivos de áudio e metadados
├── sprites/          # Imagens de sprites e metadados
└── thumbnails/       # Miniaturas de recursos geradas
```

---

## Conteúdo da Wiki

### Predefinições e Referência
- [Guia de Predefinições](Preset-Guide_pt) - Visão geral do sistema de predefinições
- [Predefinição Iniciante](Beginner-Preset_pt) - Funcionalidades essenciais para novos usuários
- [Predefinição Intermediário](Intermediate-Preset_pt) - Funcionalidades adicionais
- [Referência de Eventos](Event-Reference_pt) - Documentação completa de eventos
- [Referência de Ações](Full-Action-Reference_pt) - Documentação completa de ações

### Tutoriais e Guias
- [Primeiros Passos](Primeiros_Passos_pt) - Primeiros passos com PyGameMaker
- [Crie Seu Primeiro Jogo](Primeiro_Jogo_pt) - Tutorial passo a passo
- [Tutorial Breakout](Tutorial-Breakout_pt) - Crie um jogo Breakout clássico
- [Editor de Objetos](Editor_Objetos_pt) - Trabalhar com objetos do jogo
- [Editor de Salas](Editor_Salas_pt) - Projetar níveis
- [Eventos e Ações](Eventos_e_Acoes_pt) - Referência de lógica do jogo
- [Programação Visual](Programacao_Visual_pt) - Usar blocos Blockly
- [Exportar Jogos](Exportar_Jogos_pt) - Compilar para diferentes plataformas
- [FAQ](FAQ_pt) - Perguntas frequentes

---

## Contribuir

Contribuições são bem-vindas! Veja nossas diretrizes de contribuição para:
- Relatórios de bugs e solicitações de funcionalidades
- Contribuições de código
- Traduções
- Melhorias na documentação

---

## Licença

PyGameMaker é licenciado sob a **GNU General Public License v3 (GPLv3)**.

Copyright (c) 2024-2025 Gabriel Thullen

---

## Links

- [Repositório GitHub](https://github.com/Gabe1290/pythongm)
- [Rastreador de Issues](https://github.com/Gabe1290/pythongm/issues)
- [Lançamentos](https://github.com/Gabe1290/pythongm/releases)
