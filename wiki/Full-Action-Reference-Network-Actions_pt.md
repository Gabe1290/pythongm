# Rede

*[Início](Home_pt) | [Guia de predefinições](Preset-Guide_pt) | [Referência de eventos](Event-Reference_pt)*

> **Gerado automaticamente** a partir do registro de ações do IDE via `tools/gen_action_reference.py` — não edite manualmente; execute novamente o gerador após alterar as ações. As traduções vêm de `tools/action_ref_i18n.py`.

### Associar uma tecla de rede

| Propriedade | Valor |
|----------|-------|
| **Nome** | `bind_network_input` |
| **Ícone** | ⌨️ |
| **Categoria** | Rede |

Associa uma tecla local a uma «entrada com nome» comunicada ao anfitrião. O anfitrião testa-a depois com «Se o jogador carregar». As setas e a barra de espaços já estão associadas ("left", "right", "up", "down", "space")

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Uma etiqueta à tua escolha (por ex. "jump", "fire") |
| `key` | Texto | — | Um nome de tecla: "space", "left", "a", "5", "lshift"... |

### Criar objeto em rede

| Propriedade | Valor |
|----------|-------|
| **Nome** | `network_spawn` |
| **Ícone** | ✨ |
| **Categoria** | Rede |

Só no anfitrião: cria uma instância que aparece automaticamente em todos os clientes, como um «fantasma» suavizado. Num cliente não faz nada. O anfitrião comanda a instância que cria: protege a sua lógica de jogo com global.is_host == 1

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | O tipo de objeto a criar |
| `x` | Texto | `0` |  |
| `y` | Texto | `0` |  |
| `owner` | Texto | `0` | O jogador que comanda esta instância (0 = anfitrião). Muitas vezes global.network_sender dentro de «Jogador entrou».; opcional |
| `relative` | Sim/Não | Não | Posição relativa ao objeto que executa a ação; opcional |

### End Turn (File Exchange)

| Propriedade | Valor |
|----------|-------|
| **Nome** | `end_turn` |
| **Ícone** | ✅ |
| **Categoria** | Rede |

Submit your move for this round: whatever you staged with "Set a Shared Variable (File Exchange)" since your last turn, written as one file for the host to pick up. Call it once per round -- even with nothing staged -- if this game expects every player to respond every round; a player who never calls it is skipped once the round deadline passes

*Parâmetros:* nenhum

### Alojar um jogo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `host_game` |
| **Ícone** | 🌐 |
| **Categoria** | Rede |

Torna esta máquina o anfitrião de um jogo multijogador em LAN: os outros jogadores ligam-se a ela. Chama-a apenas uma vez (por exemplo no evento Criar do controlador da sala). Define global.player_id = 0 e global.network_role = "host"

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `game_name` | Texto | `PyGameMaker` | Nome mostrado na lista de servidores (deteção na rede); opcional |
| `max_players` | Número | `8` | Número máximo de jogadores, incluindo o anfitrião (de 2 a 16); opcional |
| `port` | Número | `45782` | Porta TCP: tem de ser a mesma no anfitrião e em cada cliente; opcional |
| `player_name` | Texto | — | Nome deste jogador (vazio = global.player_name, ou "Player"); opcional |
| `show_lobby` | Sim/Não | Não | Mostrar um ecrã «À espera de jogadores...» com um botão Começar antes de o jogo arrancar; opcional |

### Host a Game (File Exchange)

| Propriedade | Valor |
|----------|-------|
| **Nome** | `host_game_files` |
| **Ícone** | 🗂️ |
| **Categoria** | Rede |

Become the host of a turn-based game played over a shared folder instead of a live connection -- works through a school firewall that blocks direct connections between machines. Call it once (for example in the room controller's Create event). Sets global.player_id = 0 and global.is_host = 1

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `folder` | Texto | — | Path to a folder both machines can reach (a mapped network drive, a synced Dropbox/OneDrive folder, ...) |
| `max_players` | Número | `8` | Número máximo de jogadores, incluindo o anfitrião (de 2 a 16); opcional |
| `player_name` | Texto | — | Nome deste jogador (vazio = global.player_name, ou "Player"); opcional |
| `round_deadline` | Número | `30` | How long to wait for every joined player's move before advancing the round anyway (a missing player is skipped that round, not left blocking the game forever); opcional |
| `show_lobby` | Sim/Não | Não | Show a "Waiting for players..." screen with a Start button before handing control back to the game; opcional |

### Se eu controlo esta instância

| Propriedade | Valor |
|----------|-------|
| **Nome** | `is_instance_owner` |
| **Ícone** | ❓ |
| **Categoria** | Rede |

Uma condição: verdadeira quando ESTA máquina é dona da instância sincronizada. Coloca-a antes de um bloco para que a lógica de controlo só corra na máquina do jogador certo

*Parâmetros:* nenhum

### Se o jogador carregar

| Propriedade | Valor |
|----------|-------|
| **Nome** | `remote_input` |
| **Ícone** | ❓ |
| **Categoria** | Rede |

Uma condição, no anfitrião: verdadeira enquanto o jogador indicado mantiver a entrada indicada. Permite ao anfitrião reagir às teclas de um cliente sem ser dono da personagem desse cliente

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `player` | Texto | `0` | Número do jogador (0 = anfitrião) |
| `name` | Texto | — | A entrada com nome a testar (por ex. "jump") |

### Entrar num jogo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `join_game` |
| **Ícone** | 🔌 |
| **Categoria** | Rede |

Liga-se a um jogo multijogador em LAN alojado noutra máquina. O anfitrião define global.player_id (1, 2, ...). Se não for possível contactar o anfitrião, o jogo continua a solo

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `host` | Texto | `127.0.0.1` | Endereço IP do anfitrião na rede local ("auto" abre o ecrã de ligação incorporado); opcional |
| `port` | Número | `45782` | Porta TCP: tem de coincidir com a do anfitrião; opcional |
| `player_name` | Texto | — | Nome deste jogador (vazio = global.player_name, ou "Player"); opcional |

### Join a Game (File Exchange)

| Propriedade | Valor |
|----------|-------|
| **Nome** | `join_game_files` |
| **Ícone** | 🔌 |
| **Categoria** | Rede |

Join a turn-based game hosted by another machine through a shared folder. The host assigns global.player_id (1, 2, ...)

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `folder` | Texto | — | Path to the SAME shared folder the host used ("auto" opens the built-in screen to type it in) |
| `player_name` | Texto | — | Nome deste jogador (vazio = global.player_name, ou "Player"); opcional |

### Sair do jogo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `leave_game` |
| **Ícone** | 🚪 |
| **Categoria** | Rede |

Desliga-se (ou deixa de alojar) e limpa as variáveis globais de rede

*Parâmetros:* nenhum

### Leave the Game (File Exchange)

| Propriedade | Valor |
|----------|-------|
| **Nome** | `leave_game_files` |
| **Ícone** | 🚪 |
| **Categoria** | Rede |

Stop hosting or leave the game, and clear the global status variables

*Parâmetros:* nenhum

### Ler variável partilhada

| Propriedade | Valor |
|----------|-------|
| **Nome** | `get_shared_var` |
| **Ícone** | 📥 |
| **Categoria** | Rede |

Copia uma variável partilhada para uma variável global, para a usar num cálculo. É o mesmo que ler global.<nome> diretamente

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Nome da variável partilhada a ler |
| `into` | Texto | — | Nome da variável global onde escrever o valor |

### Read a Shared Variable (File Exchange)

| Propriedade | Valor |
|----------|-------|
| **Nome** | `get_shared_var_files` |
| **Ícone** | 📥 |
| **Categoria** | Rede |

Copy a shared variable into a global variable, to use it in a calculation. The same as reading global.<name> directly -- the value as of the last round the host published, not live

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Nome da variável partilhada a ler |
| `into` | Texto | — | Nome da variável global onde escrever o valor |

### Enviar mensagem de rede

| Propriedade | Valor |
|----------|-------|
| **Nome** | `send_network_message` |
| **Ícone** | ✉️ |
| **Categoria** | Rede |

Difunde uma mensagem à tua escolha. Dispara o evento «Mensagem de rede» nas máquinas em causa, com global.network_event / global.network_data / global.network_sender

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `event` | Texto | — | Uma etiqueta à tua escolha que o tratamento testa (por ex. "buzz", "answer") |
| `data` | Texto | — | Um número, texto, true/false ou uma lista curta; opcional |
| `target` | Escolha | `all` | all = toda a gente; host = só o anfitrião; Opções: `all`, `host` |

### Send a Network Message (File Exchange)

| Propriedade | Valor |
|----------|-------|
| **Nome** | `send_network_message_files` |
| **Ícone** | ✉️ |
| **Categoria** | Rede |

Stage a message of your own, delivered the same way "Set a Shared Variable (File Exchange)" is -- at the next round boundary, not instantly. Fires the "Network Message (File Exchange)" event, with global.network_event / global.network_data / global.network_sender

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `event` | Texto | — | Uma etiqueta à tua escolha que o tratamento testa (por ex. "buzz", "answer") |
| `data` | Texto | — | Um número, texto, true/false ou uma lista curta; opcional |
| `target` | Escolha | `all` | all = everyone, once they pick up the next round; host = the host only, processed immediately when the round resolves; Opções: `all`, `host` |

### Definir o modo de rede (v1)

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_network_mode` |
| **Ícone** | 🌐 |
| **Categoria** | Rede |

Uma ação antiga de baixo nível: arranca a sala em modo anfitrião ou cliente (só espetador — os comandos do cliente não têm efeito). É preferível «Alojar um jogo» / «Entrar num jogo». Mantida para os projetos existentes e para as opções --net-host / --net-client

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `mode` | Escolha | `host` | Anfitrião = os outros ligam-se a ti; Cliente = tu ligas-te a um anfitrião; Opções: `host`, `client` |
| `host` | Texto | `127.0.0.1` | Endereço IP do anfitrião na rede local (só no modo Cliente); opcional |
| `port` | Número | `45782` | Porta TCP: tem de ser a mesma no anfitrião e no cliente; opcional |

### Definir variável partilhada

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_shared_var` |
| **Ícone** | 📤 |
| **Categoria** | Rede |

Escreve uma variável partilhada por todas as máquinas. No anfitrião é aplicada de imediato; num cliente é um pedido enviado ao anfitrião. Pode ler-se em qualquer lado como global.<nome>

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Um identificador simples (letras, algarismos, _): sem espaços nem operadores |
| `value` | Texto | `0` | Um número, texto ou true/false (objetos complexos são recusados) |

### Set a Shared Variable (File Exchange)

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_shared_var_files` |
| **Ícone** | 📤 |
| **Categoria** | Rede |

Stage a variable to publish to everyone. It takes effect once you call "End Turn" and the host folds your move into the next round -- not immediately, since there is no live connection to write over. Readable anywhere as global.<name> once published

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | Um identificador simples (letras, algarismos, _): sem espaços nem operadores |
| `value` | Texto | `0` | Um número, texto ou true/false (objetos complexos são recusados) |

### Definir o dono da instância

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_instance_owner` |
| **Ícone** | 🎮 |
| **Categoria** | Rede |

Escolhe qual o jogador que comanda esta instância sincronizada (0 = anfitrião; 1, 2, ... = clientes). Na máquina desse jogador a instância corre localmente e responde bem, e o seu estado é comunicado ao anfitrião; em todas as outras é um fantasma suavizado. Chama-a no anfitrião, protegida por global.is_host == 1

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `player` | Texto | `0` | Número do jogador (0 = anfitrião). Muitas vezes global.network_sender dentro de «Jogador entrou». |

### Ajustar a frequência de sincronização

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_sync_rate` |
| **Ícone** | ⏱️ |
| **Categoria** | Rede |

Ajusta com que frequência o anfitrião envia instantâneos e com que atraso os clientes os desenham. Chama-a uma vez no anfitrião, e nos clientes para o atraso

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `hz` | Número | `20` | De 10 a 30 funciona bem numa rede local (por omissão 20); opcional |
| `interp_ms` | Número | `100` | Com que atraso os fantasmas são desenhados, em milissegundos (por omissão 100); opcional |

### Começar o jogo em rede

| Propriedade | Valor |
|----------|-------|
| **Nome** | `start_networked_game` |
| **Ícone** | 🚦 |
| **Categoria** | Rede |

Só no anfitrião: tira toda a gente da sala de espera e começa o jogo. Dispara o evento «Jogo em rede iniciado» em todas as máquinas

*Parâmetros:* nenhum

### Sincronizar esta instância

| Propriedade | Valor |
|----------|-------|
| **Nome** | `sync_instance` |
| **Ícone** | 🔗 |
| **Categoria** | Rede |

Marca como sincronizada a instância que executa esta ação: a sua posição, rotação, imagem e visibilidade são copiadas para todas as máquinas. Chama-a no evento Criar. Por omissão pertence ao anfitrião; usa «Definir o dono da instância» para que seja um cliente a comandá-la

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `vars` | Texto | — | Nomes de variáveis de instância a copiar também, separados por vírgulas (por ex. "hp, colour"); opcional |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (21)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (6)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (8)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (14)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (3)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (18)
- [Desenho](Full-Action-Reference-Drawing_pt) (11)
- [Partículas](Full-Action-Reference-Particles_pt) (8)
- [Score/Lives/Health](Full-Action-Reference-Score-Lives-Health_pt) (5)
- [micro:bit](Full-Action-Reference-Microbit-Actions_pt) (16)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
