# Réseau — Quiz de classe (reseau_2)

A shared-blackboard (Tier A) LAN multiplayer game: **the host is the
quizmaster, up to 3 connected players answer multiple-choice questions,
and everyone sees a live scoreboard.** No player avatars, no movement —
this is the gentlest way to teach `host_game`/`join_game`, shared
variables, and custom messages.

## Run it

You need **two or more machines on the same wired LAN** (or two windows
on one machine for a quick test). Launch the game normally (double-click
the export, or **Test Game** in the IDE), then:

- **Host** (the quizmaster): press **H**. A lobby appears — wait for
  players to join, then press the on-screen "Démarrer" button.
- **Each other player**: press **J**, which opens the built-in server
  browser (or type the host's LAN address directly). Once connected,
  wait for the host to start the round.

Once the round starts, press **A**, **B**, **C** or **D** to answer.
Each question lasts 8 seconds; scores update live for everyone.

## How it works

| Object | Role |
|---|---|
| `obj_quiz` | The only object. Everyone runs the same code, branching on `global.is_host` / `global.is_client`. |

- **The host owns the quiz.** On **Partie réseau démarrée**
  (`network_game_started`, guarded by `global.is_host == 1`), it
  publishes the first question's full text into shared variables
  (`question`, `option_a`..`option_d`) and starts an 8-second alarm.
  When the alarm fires, it advances to the next question — or, once the
  three questions are used, publishes `etat = "fin"`.
- **A client answers by sending a message**, not by writing a shared
  variable directly: pressing A/B/C/D calls `send_network_message(event=
  "reponse", data="A", target="host")`. Only the host's own **Message
  réseau** (`network_message`) handler awards the point, checking
  `global.network_data` against the instance variable `self.correct`
  (a per-machine secret — never published as a shared variable, so it
  can't be read off another machine).
- **Every score is its own shared variable** (`score_0`..`score_3`, one
  per player slot). Action parameter *names* (like `set_shared_var`'s
  `name` field) are read literally, never evaluated as an expression —
  so awarding a point branches explicitly on `global.network_sender`
  (0/1/2/3) rather than trying to build a variable name dynamically.
- **The scoreboard is always visible** (bottom of the screen), even
  while the current question is showing — no separate "results" phase.

## Things to try

- Change `QUESTIONS` (well, its native-language authoring equivalent: the
  round-setup actions in **Partie réseau démarrée** and **alarm_0**) to
  your own quiz — the pattern is entirely explicit branches, easy to
  extend to more rounds or more players.
- Add a `network_message` handler for a **new** event name (e.g.
  `"buzz"`) so a player can ring in before answering, like a real quiz
  show.
- Shorten or lengthen the per-question timer by changing `set_alarm`'s
  `steps` (240 = 8 seconds at this room's 30 fps `room_speed`).

## Notes for teachers

- Ports used: **45782/TCP** (game) and **45783/UDP** (discovery). Ask IT
  before using on a managed network.
- **Wired labs work best.** Many school Wi-Fi access points block
  device-to-device traffic, which stops LAN multiplayer entirely — no
  software can work around that.
- Unlike `reseau_1`, nobody needs to move or react quickly — a dropped
  frame or a moment of lag doesn't cost anyone the round, making this a
  good first LAN multiplayer session to run with a class.
