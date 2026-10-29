# Rede (multijogador em LAN)

*[Início](Home_pt) | [Referência completa de ações](Full-Action-Reference-Network-Actions_pt) | [Extensões](Extensions_pt)*

---

O PyGameMaker pode transformar um projeto em um **jogo multijogador em LAN**:
uma máquina hospeda, as outras entram pela rede local, e os jogadores
compartilham estado — um placar, mensagens personalizadas e até os avatares
uns dos outros na tela — sem servidor, sem conta e sem internet. Isso é
fornecido pela [extensão](Extensions_pt) **LAN Multiplayer** integrada, que já
vem ativada.

Os exemplos incluídos **`reseau_1`–`reseau_3`** são exemplos completos e
jogáveis: uma sala compartilhada onde dois jogadores se movem juntos, um quiz
de turma com placar ao vivo e uma caça ao tesouro cooperativa para dois.

Compatível hoje: a exportação para **desktop** (pygame), como anfitrião e como
cliente, e a exportação **HTML5** como cliente (uma página do navegador entra
em um anfitrião desktop; ela não consegue hospedar). Uma exportação
**Kivy/Android** executa o jogo como um jogador só — as ações de rede lá não
fazem nada, sem risco.

---

## Dois níveis

**Nível A — quadro compartilhado.** Sem avatares, só estado compartilhado:
variáveis que todos os jogadores podem ler e escrever, mensagens
personalizadas e quem está conectado. É a forma mais simples de acrescentar
multijogador a um projeto — um quiz, um placar compartilhado, uma campainha de
«quem responde primeiro».

**Nível B — instâncias em rede.** Instâncias criadas pelo anfitrião
(jogadores, inimigos, itens a coletar) que aparecem e se movem
automaticamente em todas as máquinas, mais avatares pertencentes a um jogador,
que cada um controla localmente enquanto os outros veem uma cópia interpolada
com suavidade.

---

## Como funciona

- Um jogador chama **Alojar um jogo**, geralmente a partir do evento Create de um
  objeto controlador da sala. Essa máquina se torna o **anfitrião** — as
  máquinas de todos os outros jogadores se conectam a ela. `global.player_id`
  passa a ser `0`.
- Os outros jogadores chamam **Entrar num jogo** com o endereço IP do anfitrião na
  LAN (ou `"auto"` para mostrar uma tela de conexão integrada que encontra
  anfitriões na rede automaticamente). O anfitrião atribui `global.player_id`
  (`1`, `2`, ...).
- Se o anfitrião não puder ser alcançado, **o jogo continua com um jogador só**
  — entrar nunca bloqueia nem derruba um jogo.
- A identidade do jogador e o estado da conexão são sempre legíveis como
  globais: `global.is_host`, `global.player_id`, `global.player_count`,
  `global.network_role`, `global.network_connected`.
- **Escreva a lógica do seu jogo com uma ação «Se» comum**, por exemplo
  `global.is_host == 1`, para reservar ao anfitrião a preparação (como criar
  inimigos) — não são necessárias ações especiais de «condição de rede».
- Uma variável compartilhada definida com **Definir variável partilhada** pode ser lida
  *em qualquer lugar* como `global.<nome>` — inclusive na máquina que a
  definiu.
- As **mensagens personalizadas** (**Enviar mensagem de rede**) permitem
  sinalizar um evento pelo nome com um pequeno dado anexado — um toque de
  campainha, uma resposta escolhida, um sinal de «pronto».

---

## As ações (categoria **Rede**)

| Ação | O que faz |
|------|-----------|
| **Alojar um jogo** | Tornar-se o anfitrião. Opcionalmente mostra uma sala de espera com um botão Iniciar. |
| **Entrar num jogo** | Conectar-se a um anfitrião por endereço (ou `"auto"` para a tela de conexão integrada). |
| **Sair do jogo** | Desconectar-se (ou parar de hospedar) e limpar as globais de rede. |
| **Começar o jogo em rede** | Somente anfitrião: encerrar a sala de espera e avisar todos para começar. |
| **Definir variável partilhada** | Escrever uma variável que todas as máquinas podem ler como `global.<nome>`. |
| **Ler variável partilhada** | Copiar uma variável compartilhada para uma global (para usar em um cálculo). |
| **Enviar mensagem de rede** | Transmitir a todos uma mensagem personalizada com nome e dados. |
| **Criar objeto em rede** | Somente anfitrião: criar uma instância que aparece em todos os clientes. |
| **Sincronizar esta instância** | Marcar a instância atuante como replicada entre as máquinas. |
| **Definir o dono da instância** | Dar a um jogador específico o controle local de uma instância sincronizada. |
| **Se eu controlo esta instância** | Condição: reserva a lógica de controle para rodar só na máquina proprietária. |
| **Associar uma tecla de rede** | Associar uma tecla local a uma entrada nomeada que o anfitrião pode ler. |
| **Se o jogador carregar** | Condição (anfitrião): um determinado jogador está mantendo uma entrada nomeada? |
| **Ajustar a frequência de sincronização** | Ajustar a taxa de instantâneos do anfitrião e o atraso de interpolação dos clientes. |

Veja a [Referência completa de ações](Full-Action-Reference-Network-Actions_pt) para todos os parâmetros.

---

## Os eventos (categoria **Rede**)

São disparados em cada instância cujo objeto os trata, em cada máquina
envolvida:

| Evento | Dispara quando |
|--------|----------------|
| **Network Ready** | Um cliente termina de se conectar ao anfitrião (o anfitrião não o dispara para si mesmo). |
| **Player Joined** | Um novo jogador se conecta. `global.network_sender` / `global.network_player_name` o identificam. |
| **Player Left** | Um jogador se desconecta. |
| **Network Message** | Chega um **Enviar mensagem de rede** — `global.network_event` / `global.network_data` / `global.network_sender`. |
| **Network Game Started** | O anfitrião chama **Começar o jogo em rede**. |
| **Connection Lost** | A conexão de um cliente com o anfitrião cai. O jogo continua — somente os fantasmas desse jogador somem. |

---

## Um exemplo mínimo de sala compartilhada (Nível A)

Em um objeto controlador de sala invisível:

- **Create:** `Alojar um jogo` se for a máquina do professor, senão `Entrar num jogo`
  com o IP dele (ou `"auto"`).
- **Create:** `Definir variável partilhada` `round = 1` (somente anfitrião, protegido por
  `global.is_host == 1`).
- Em qualquer lugar: `draw_text` mostrando `global.round` — todos os
  jogadores veem o mesmo valor.

## Um exemplo mínimo de avatares compartilhados (Nível B)

No evento Create do objeto jogador:

- `Sincronizar esta instância` — esta instância passa a ser replicada.
- No **anfitrião**: `Criar objeto em rede` cria uma instância de jogador para cada
  jogador que se conecta (em um tratador de **Player Joined**) e depois
  `Definir o dono da instância` com o número desse jogador.
- O código de movimento protegido por `Se eu controlo esta instância` roda somente na
  máquina do jogador proprietário; em todas as outras a instância é um
  fantasma interpolado com suavidade.

---

## Notas e limites

- **TCP, somente LAN.** Sem travessia de NAT, sem jogo pela internet — as duas
  máquinas precisam ser alcançáveis na mesma rede local (um Wi-Fi de sala de
  aula ou um laboratório cabeado). O Wi-Fi com isolamento de clientes (comum em
  redes escolares gerenciadas) bloqueia igualmente a descoberta e a conexão
  direta; um laboratório cabeado é a opção mais confiável.
- **Portas 45782 (TCP)** e **45783 (UDP, descoberta)** — consulte o setor de TI
  da escola antes de usar em uma rede gerenciada e espere um aviso do firewall
  na primeira vez que hospedar.
- Um cliente de navegador (exportação HTML5) se conecta à porta seguinte à do
  anfitrião, por exemplo `45783` se o anfitrião usar o padrão — isso acontece
  automaticamente.
- A perda do anfitrião é tratada com elegância: o jogo de um cliente continua;
  somente os fantasmas dos outros jogadores somem, e **Connection Lost** é
  disparado para você poder mostrar uma mensagem.
- Se a extensão LAN Multiplayer estiver **desativada**, essas ações e eventos
  simplesmente não fazem nada — veja [Extensões](Extensions_pt).

---

## Veja também

- [File Exchange Multiplayer](FileExchange) (em inglês) — o irmão por turnos,
  para uma sala de aula em que um firewall bloqueia as conexões diretas desta
  extensão
- [Extensões](Extensions_pt) — como o LAN Multiplayer é fornecido e como desligá-lo
- [Referência completa de ações](Full-Action-Reference-Network-Actions_pt) — cada ação e parâmetro
- [Referência de eventos](Event-Reference_pt)
