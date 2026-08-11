# Referência de Eventos

*[Início](Home_pt) | [Guia de Predefinições](Preset-Guide_pt) | [Referência completa de ações](Full-Action-Reference_pt)*

Esta página documenta todos os eventos disponíveis no PyGameMaker. Eventos são gatilhos que executam ações quando condições específicas ocorrem no seu jogo.

## Categorias de Eventos

- [Eventos de Objeto](Event-Reference-Object_pt) - Create, Step, Destroy
- [Eventos de Entrada](Event-Reference-Input_pt) - Teclado, Mouse
- [Eventos de Colisão](Event-Reference-Collision_pt) - Colisões de objetos
- [Eventos de Tempo](Event-Reference-Timing_pt) - Alarmes, Variantes de Step
- [Eventos de Desenho](Event-Reference-Drawing_pt) - Renderização personalizada
- [Eventos de Sala](Event-Reference-Room_pt) - Transições de sala
- [Eventos de Jogo](Event-Reference-Game_pt) - Início/Fim do jogo
- [Outros Eventos](Event-Reference-Other_pt) - Limites, Vidas, Saúde

---

## Ordem de Execução de Eventos

Entender quando os eventos disparam ajuda a criar um comportamento de
jogo previsível (verificado contra o loop principal em
`runtime/game_runner.py`):

1. **Begin Step** — Início do quadro
2. **Alarm** — Todos os alarmes disparados fazem a contagem regressiva e disparam
3. **Step** (e **Keyboard (mantida)**) — Lógica principal do jogo,
   depois verificações contínuas de teclas mantidas para a mesma
   instância
4. **Keyboard Press/Release, Mouse** — Os eventos de entrada
   acumulados para este quadro são processados (isso acontece *depois*
   de Step, não antes — o código em Step reage às teclas que já
   estavam pressionadas no *início* do quadro, não às pressionadas
   durante o quadro)
5. **Movimento, depois Colisão** — A física (gravidade/atrito/hspeed/
   vspeed) é aplicada, depois as colisões são detectadas e seus
   eventos disparam
6. **End Step** (e **Destroy**) — Após as colisões
7. **Draw** — Fase de renderização

---

## Eventos por Preset

Verificado contra `events.event_types.get_available_events()`
alimentado com cada preset real de `config/blockly_config.py` — veja o
[Guia de Predefinições](Preset-Guide_pt) para o que uma "predefinição"
realmente restringe (tanto o seletor do Blockly quanto o painel
estruturado Events/Actions) e como a predefinição de um projeto é
definida.

| Preset | Eventos Incluídos |
|--------|-------------------|
| **Iniciante** (19 eventos) | Create, Step, Keyboard (mantida), Keyboard \<Sem Tecla\>, Collision, Begin Step, End Step, Alarm, Draw, Draw GUI, Room Start, Room End, Game Start, Game End, Outside Room, Intersect Boundary, No More Lives, No More Health, Animation End |
| **Intermediário** (21 eventos) | + Destroy, Keyboard Press |
| **Completo** (apenas Edição Desenvolvimento, 23 eventos) | + Keyboard Release, Mouse |

---

## Veja Também

- [Referência Completa de Ações](Full-Action-Reference_pt) - Lista completa de ações
- [Preset Iniciante](Beginner-Preset_pt) - Eventos essenciais para iniciantes
- [Preset Intermediário](Intermediate-Preset_pt) - Eventos adicionais
- [Eventos e Ações](Eventos_e_Acoes_pt) - Visão geral dos conceitos básicos
