# Começar

> [English](Getting-Started) | [Français](Demarrage_fr) | [Deutsch](Erste_Schritte_de) | [Italiano](Iniziare_it) | [Español](Empezar_es) | [Português](Comecar_pt) | [Slovenščina](Zacetek_sl) | [Українська](Pochatok_uk) | [Русский](Nachalo_ru)

---

[Voltar ao Início](Home_pt)

Este guia vai ajudá-lo a pôr o PyGameMaker a funcionar no seu sistema.

---

## Requisitos do Sistema

- **Python** 3.10 ou superior
- **Sistema Operativo:** Windows, Linux ou macOS
- **Espaço em Disco:** ~500 MB para a instalação
- **RAM:** mínimo 4 GB, 8 GB recomendados

---

## Instalação

### Passo 1: Instalar o Python

Descarregue o Python 3.10+ de [python.org](https://www.python.org/downloads/) e instale-o. Certifique-se de marcar "Add Python to PATH" durante a instalação no Windows.

### Passo 2: Clonar o Repositório

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
```

Ou descarregue o ficheiro ZIP da [página de Releases](https://github.com/Gabe1290/pythongm/releases).

### Passo 3: Criar um Ambiente Virtual

Criar um ambiente virtual mantém as dependências do PyGameMaker isoladas:

```bash
python -m venv venv
```

Ative o ambiente virtual:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Passo 4: Instalar as Dependências

```bash
pip install -r requirements.txt
```

### Passo 5: Executar o PyGameMaker

```bash
python main.py
```

---

## Primeiro Arranque

Ao iniciar o PyGameMaker pela primeira vez, verá:

1. **Barra de Menu** — os menus File, Edit, Assets, Build, Tools e Help
2. **Árvore de Recursos** — painel esquerdo com os recursos do projeto (Sprites, Sons, Fundos, Objetos, Salas)
3. **Área de Trabalho** — área central para editar recursos
4. **Painel de Propriedades** — painel direito para as propriedades dos recursos

---

## Criar o Seu Primeiro Projeto

1. Vá a **File > New Project**
2. Escolha uma localização e um nome para o seu projeto
3. Será criada uma nova pasta de projeto com a estrutura padrão

---

## Estrutura do Projeto

Cada projeto do PyGameMaker contém:

```
meu_projeto/
├── project.json      # Configurações do projeto
├── sprites/          # Imagens dos sprites
├── sounds/           # Ficheiros de áudio
├── backgrounds/      # Imagens de fundo
├── objects/          # Definições dos objetos do jogo
├── rooms/            # Layouts dos níveis
├── fonts/            # Ficheiros de fontes
├── scripts/          # Scripts personalizados
└── data/             # Ficheiros de dados personalizados
```

---

## Mudar de Idioma

O PyGameMaker suporta vários idiomas:

1. Vá a **Tools > Language**
2. Selecione o seu idioma preferido no menu
3. Reinicie o PyGameMaker para aplicar a alteração

Idiomas disponíveis: Inglês, Francês, Alemão, Italiano, Espanhol, Português, Esloveno, Ucraniano, Russo

---

## Próximos Passos

- [[Primeiro_Jogo_pt]] - Construa um jogo simples passo a passo
- [[Editor_Objetos_pt]] - Aprenda a criar objetos do jogo
- [[Editor_Salas_pt]] - Desenhe os seus níveis de jogo
- [[Eventos_e_Acoes_pt]] - Compreenda a lógica do jogo

---

## Resolução de Problemas

### Python não encontrado
Certifique-se de que o Python está instalado e adicionado ao PATH. Experimente executar `python --version` para verificar.

### Dependências em falta
Se receber erros de importação, tente reinstalar as dependências:
```bash
pip install -r requirements.txt --force-reinstall
```

### Problemas de visualização
No Linux, o Qt (a framework de GUI em que o PyGameMaker é construído)
precisa de algumas bibliotecas de sistema que o `pip` não instala:
```bash
sudo apt-get install -y libegl1 libxkbcommon0 libxcb-cursor0 \
    libxcb-icccm4 libxcb-keysyms1 libxcb-shape0 libasound2-dev libgl1-mesa-dev
```

---

## Obter Ajuda

- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) - Reporte bugs ou solicite funcionalidades
- [[FAQ_pt]] - Perguntas e respostas comuns
