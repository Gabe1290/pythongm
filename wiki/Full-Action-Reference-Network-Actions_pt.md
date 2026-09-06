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
| `name` | Texto | — | A label of your choosing (e.g. "jump", "fire") |
| `key` | Texto | — | A key name: "space", "left", "a", "5", "lshift"... |

### Criar objeto em rede

| Propriedade | Valor |
|----------|-------|
| **Nome** | `network_spawn` |
| **Ícone** | ✨ |
| **Categoria** | Rede |

Só no anfitrião: cria uma instância que aparece automaticamente em todos os clientes, como um «fantasma» suavizado. Num cliente não faz nada. O anfitrião comanda a instância que cria: protege a sua lógica de jogo com global.is_host == 1

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `object` | Objeto | — | The type of object to create |
| `x` | Texto | `0` |  |
| `y` | Texto | `0` |  |
| `owner` | Texto | `0` | The player who drives this instance (0 = host). Often global.network_sender inside "Player joined".; opcional |
| `relative` | Sim/Não | Não | Position relative to the object running the action; opcional |

### Alojar um jogo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `host_game` |
| **Ícone** | 🌐 |
| **Categoria** | Rede |

Torna esta máquina o anfitrião de um jogo multijogador em LAN: os outros jogadores ligam-se a ela. Chama-a apenas uma vez (por exemplo no evento Criar do controlador da sala). Define global.player_id = 0 e global.network_role = "host"

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `game_name` | Texto | `PyGameMaker` | Name shown in the server list (network discovery); opcional |
| `max_players` | Número | `8` | Largest number of players, host included (2 to 16); opcional |
| `port` | Número | `45782` | TCP port -- must be the same on the host and every client; opcional |
| `player_name` | Texto | — | This player's name (empty = global.player_name, or "Player"); opcional |
| `show_lobby` | Sim/Não | Não | Show a "Waiting for players..." screen with a Start button before the game begins; opcional |

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
| `player` | Texto | `0` | Player number (0 = host) |
| `name` | Texto | — | The named input to test (e.g. "jump") |

### Entrar num jogo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `join_game` |
| **Ícone** | 🔌 |
| **Categoria** | Rede |

Liga-se a um jogo multijogador em LAN alojado noutra máquina. O anfitrião define global.player_id (1, 2, ...). Se não for possível contactar o anfitrião, o jogo continua a solo

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `host` | Texto | `127.0.0.1` | The host's LAN IP address ("auto" opens the built-in connection screen); opcional |
| `port` | Número | `45782` | TCP port -- must match the host's; opcional |
| `player_name` | Texto | — | This player's name (empty = global.player_name, or "Player"); opcional |

### Sair do jogo

| Propriedade | Valor |
|----------|-------|
| **Nome** | `leave_game` |
| **Ícone** | 🚪 |
| **Categoria** | Rede |

Desliga-se (ou deixa de alojar) e limpa as variáveis globais de rede

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
| `name` | Texto | — | Name of the shared variable to read |
| `into` | Texto | — | Name of the global variable to write the value into |

### Enviar mensagem de rede

| Propriedade | Valor |
|----------|-------|
| **Nome** | `send_network_message` |
| **Ícone** | ✉️ |
| **Categoria** | Rede |

Difunde uma mensagem à tua escolha. Dispara o evento «Mensagem de rede» nas máquinas em causa, com global.network_event / global.network_data / global.network_sender

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `event` | Texto | — | A label of your choosing that the handler tests (e.g. "buzz", "answer") |
| `data` | Texto | — | A number, text, true/false, or a short list; opcional |
| `target` | Escolha | `all` | all = everyone; host = the host only; Opções: `all`, `host` |

### Definir o modo de rede (v1)

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_network_mode` |
| **Ícone** | 🌐 |
| **Categoria** | Rede |

Uma ação antiga de baixo nível: arranca a sala em modo anfitrião ou cliente (só espetador — os comandos do cliente não têm efeito). É preferível «Alojar um jogo» / «Entrar num jogo». Mantida para os projetos existentes e para as opções --net-host / --net-client

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `mode` | Escolha | `host` | Host = others connect to you; Client = you connect to a host; Opções: `host`, `client` |
| `host` | Texto | `127.0.0.1` | The host's LAN IP address (Client mode only); opcional |
| `port` | Número | `45782` | TCP port -- must be the same on the host and the client; opcional |

### Definir variável partilhada

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_shared_var` |
| **Ícone** | 📤 |
| **Categoria** | Rede |

Escreve uma variável partilhada por todas as máquinas. No anfitrião é aplicada de imediato; num cliente é um pedido enviado ao anfitrião. Pode ler-se em qualquer lado como global.<nome>

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `name` | Texto | — | A plain identifier (letters, digits, _) -- no spaces or operators |
| `value` | Texto | `0` | A number, text or true/false (complex objects are refused) |

### Definir o dono da instância

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_instance_owner` |
| **Ícone** | 🎮 |
| **Categoria** | Rede |

Escolhe qual o jogador que comanda esta instância sincronizada (0 = anfitrião; 1, 2, ... = clientes). Na máquina desse jogador a instância corre localmente e responde bem, e o seu estado é comunicado ao anfitrião; em todas as outras é um fantasma suavizado. Chama-a no anfitrião, protegida por global.is_host == 1

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `player` | Texto | `0` | Player number (0 = host). Often global.network_sender inside "Player joined". |

### Ajustar a frequência de sincronização

| Propriedade | Valor |
|----------|-------|
| **Nome** | `set_sync_rate` |
| **Ícone** | ⏱️ |
| **Categoria** | Rede |

Ajusta com que frequência o anfitrião envia instantâneos e com que atraso os clientes os desenham. Chama-a uma vez no anfitrião, e nos clientes para o atraso

| Parâmetro | Tipo | Padrão | Notas |
|-----------|------|---------|-------|
| `hz` | Número | `20` | 10-30 works well on a local network (default 20); opcional |
| `interp_ms` | Número | `100` | How far behind ghosts are drawn, in milliseconds (default 100); opcional |

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
| `vars` | Texto | — | Instance variable names to copy as well, separated by commas (e.g. "hp, colour"); opcional |

---

## Outras Categorias

- [Movimento](Full-Action-Reference-Movement_pt) (20)
- [Instância](Full-Action-Reference-Instance_pt) (12)
- [Pontuação](Full-Action-Reference-Score_pt) (11)
- [Sala](Full-Action-Reference-Room_pt) (13)
- [Tempo](Full-Action-Reference-Timing_pt) (8)
- [Áudio](Full-Action-Reference-Audio_pt) (6)
- [Jogo](Full-Action-Reference-Game_pt) (25)
- [Controle](Full-Action-Reference-Control_pt) (19)
- [Grade](Full-Action-Reference-Grid_pt) (4)
- [Vistas](Full-Action-Reference-Views_pt) (2)
- [Vista 3D](Full-Action-Reference-3D-View-Actions_pt) (16)
- [Partículas](Full-Action-Reference-Particles_pt) (8)

[← Voltar à Referência Completa de Ações](Full-Action-Reference_pt)
