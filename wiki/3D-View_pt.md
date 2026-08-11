# Vista 3D (renderização em primeira pessoa com raycast)

*[Início](Home_pt) | [Referência completa de ações](Full-Action-Reference_pt) | [Extensões](Extensions_pt)*

---

O PyGameMaker pode renderizar uma sala como uma **vista 3D em primeira pessoa no
estilo Doom/Wolfenstein** em vez da habitual vista de cima — muros como faixas
verticais, um chão e um teto coloridos ou com textura, um céu panorâmico opcional e
sprites "billboard" para objetos e monstros. A *lógica* do jogo (movimento,
colisões, eventos) não muda; muda apenas **como** a sala é desenhada.

Isso é fornecido pela **extensão 2.5D Raycast** integrada (a função
[Vista 3D](Extensions_pt)), ativada por padrão. Ela exporta para os três destinos —
computador, HTML5 e Kivy/Android — então um jogo em primeira pessoa funciona igual em
todos os lugares.

Os exemplos incluídos **`raycast_1`–`raycast_4`** são jogos completos e jogáveis (um
labirinto simples, um jogo de dois níveis com objetos e um monstro, uma variante com
saúde e kits médicos e uma demonstração de barra de status no estilo DOOM).

---

## Como funciona

- Uma sala se torna em primeira pessoa quando um objeto executa a ação **Ativar vista
  Raycast** (geralmente no seu evento Criar). Esse objeto é a **câmera** por padrão —
  sua posição é o ponto de vista e seu `facing_angle` (ângulo de visão) é a direção
  do olhar.
- **Os muros são suas instâncias sólidas.** O renderizador deriva finas *arestas* de
  muro de cada objeto sólido na sala, em uma grade cujo tamanho é o parâmetro
  `cell_size` da ação (32 por padrão — o tamanho que todos os exemplos
  `maze_*`/`raycast_*` usam). Um objeto sólido com sprite de muro texturiza o muro;
  caso contrário, usa-se uma cor `wall_color` uniforme.
- **A câmera gira** ao mudar `facing_angle` (ver **Definir ângulo de visão**) e se
  move com as ações de movimento habituais (ex. `set_direction_speed` com
  `direction = "facing_angle"` para andar para frente).
- **As instâncias não sólidas com sprite** (objetivos, objetos, monstros) são
  desenhadas como **billboards** voltados para a câmera, corretamente ocultados pelos
  muros.

---

## As ações (categoria **Vista 3D**)

| Ação | O que faz |
|------|-----------|
| **Ativar vista Raycast** (`enable_raycast_view`) | Muda a sala atual para a vista em primeira pessoa (ou volta) e configura a câmera: `camera_object`, `fov`, `render_distance`, `cell_size`, cores e texturas de muro/chão/teto, uma `sky_texture` opcional e `viewport_height` (uma barra no estilo DOOM). |
| **Definir ângulo de visão** (`set_facing_angle`) | Gira a câmera. Ângulo em graus GameMaker (0 = direita, 90 = cima); `relative` soma ao ângulo atual. |
| **Desenhar minimapa** (`draw_minimap`) | Desenha um minimapa orientado ao norte dos muros da sala com um marcador "você está aqui". Uma ação de HUD — coloque-a em um evento Desenhar. |
| **Desenhar HUD DOOM** (`draw_doom_hud`) | Desenha uma barra de status inferior no estilo DOOM: barra de saúde + número, um rosto que reage à saúde, pontuação, vidas e um contador de objetivo. Combina-se com `viewport_height` de `enable_raycast_view`. |

Veja a [Referência completa de ações](Full-Action-Reference-3D-View-Actions_pt) para todos os
parâmetros.

---

## Um controlador mínimo em primeira pessoa

No objeto jogador:

- **Criar:** `Ativar vista Raycast` (deixe `camera_object` vazio para que o jogador
  *seja* a câmera).
- **Teclado Esquerda / Direita:** `Definir ângulo de visão` com `relative` ativo
  (ex. ±3°).
- **Teclado Cima:** `Definir direção e velocidade` com `direction = facing_angle` e
  uma pequena velocidade para andar para frente.

Construa a sala com objetos-muro sólidos em uma grade de 32 pixels, exatamente como
os exemplos `maze_*` — o raycaster transforma esses muros em corredores 3D.

---

## Notas e limites

- As ações de HUD (`draw_minimap`, `draw_doom_hud` e as habituais `draw_score` /
  `draw_lives` / `draw_text`) sobrepõem-se **por cima** da imagem em primeira pessoa,
  em coordenadas de tela.
- Os muros são estáticos para a passagem em primeira pessoa — os muros
  criados/destruídos após o carregamento da sala não remodelam a geometria 3D.
- Se a extensão 2.5D Raycast estiver **desativada**, uma sala que ativa a vista
  simplesmente renderiza de cima e o IDE avisa você ao carregar — veja
  [Extensões](Extensions_pt).

---

## Veja também

- [Extensões](Extensions_pt) — como a Vista 3D é entregue e como desativá-la
- [Referência completa de ações](Full-Action-Reference-3D-View-Actions_pt) — as quatro ações em detalhe
- [Editor de salas](Editor_Salas_pt) — posicionar os objetos-muro a partir dos quais a vista é construída
