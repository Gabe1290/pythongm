# PyGameMaker IDE — Events & Actions by Edition

This reference lists every event and action available in each IDE edition.
A checkmark indicates the block is available in that edition.

| Edition | Preset | Blocks | Tutorials |
|---------|--------|--------|-----------|
| Beginner | beginner | 28 | Getting Started, First Game, Pong, Breakout |
| Advanced | intermediate | 50 | All 8 tutorials |
| Development | full | 117 | All tutorials + experimental |

## Events

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Create Event | When object is created | x | x | x |
| Step Event | Every frame | x | x | x |
| Draw Event | During drawing phase | x | x | x |
| Destroy Event | When object is destroyed |  | x | x |
| No Key | No key pressed | x | x | x |
| Any Key | Any key pressed |  |  | x |
| Keyboard (held) | Key held down | x | x | x |
| Key Press | Key pressed once |  | x | x |
| Key Release | Key released |  |  | x |
| Mouse Events | Mouse clicks and movement |  |  | x |
| Collision | Collision with object | x | x | x |
| Alarm Events | Alarm triggers (0-11) | x | x | x |
| Other Events | No more lives, health, room events |  |  | x |

## Movement

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Set Horizontal Speed | Set X velocity | x | x | x |
| Set Vertical Speed | Set Y velocity | x | x | x |
| Stop Movement | Stop all movement | x | x | x |
| Move Direction | Move in 4 directions | x | x | x |
| Move Towards | Move to point |  |  | x |
| Snap to Grid | Align to grid |  | x | x |
| Jump to Position | Instant teleport | x | x | x |
| Move Grid | Move one grid unit in a direction |  | x | x |
| Stop if No Keys | Grid movement helper |  |  | x |
| Check Keys and Move | Grid movement helper |  |  | x |
| If On Grid | Grid-aligned check |  | x | x |
| Set Gravity | Apply gravity force |  | x | x |
| Set Friction | Apply friction |  | x | x |
| Reverse Horizontal | Flip X direction | x | x | x |
| Reverse Vertical | Flip Y direction | x | x | x |
| Bounce | Bounce off solid objects | x | x | x |
| Wrap Around Room | Wrap to opposite side |  |  | x |
| Move to Contact | Move until touching |  |  | x |

## Timing

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Set Alarm | Set timer (0-11) | x | x | x |

## Drawing

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Draw Text | Display text | x | x | x |
| Draw Rectangle | Draw filled rectangle |  |  | x |
| Draw Circle | Draw filled circle |  |  | x |
| Set Sprite | Change sprite image |  | x | x |
| Set Transparency | Set alpha (0-1) |  |  | x |

## Score/Lives/Health

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Set Score | Set score value | x | x | x |
| Add to Score | Change score | x | x | x |
| Set Lives | Set lives value | x | x | x |
| Add to Lives | Change lives | x | x | x |
| Set Health | Set health value |  | x | x |
| Add to Health | Change health |  | x | x |
| Draw Score | Display score text | x | x | x |
| Draw Lives | Display lives icons | x | x | x |
| Draw Health Bar | Display health bar |  | x | x |

## Instance

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Destroy Instance | Destroy this object | x | x | x |
| Destroy Other | Destroy colliding object | x | x | x |
| Create Instance | Spawn new object | x | x | x |
| Change Instance | Transform into different object type |  | x | x |
| If Can Push | Sokoban-style push check |  | x | x |

## Room

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Next Room | Go to next room |  | x | x |
| Previous Room | Go to previous room |  | x | x |
| Restart Room | Restart current room | x | x | x |
| Go to Room | Go to specific room |  | x | x |
| If Next Room Exists | Check if next room exists |  | x | x |
| If Previous Room Exists | Check if previous room exists |  | x | x |

## Sound

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Play Sound | Play sound effect |  | x | x |
| Play Music | Play background music |  | x | x |
| Stop Music | Stop music |  | x | x |

## Output

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Show Message | Display message dialog | x | x | x |
| Execute Code | Execute custom Python code |  | x | x |

## Game

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| End Game | Close the game |  |  | x |
| Restart Game | Restart from first room |  |  | x |
| Show Highscore | Display highscore table |  |  | x |
| Clear Highscore | Reset highscore table |  |  | x |

## Values

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| X Position | Get X coordinate |  |  | x |
| Y Position | Get Y coordinate |  |  | x |
| Horizontal Speed | Get X velocity |  |  | x |
| Vertical Speed | Get Y velocity |  |  | x |
| Score | Get score value |  |  | x |
| Lives | Get lives value |  |  | x |
| Health | Get health value |  |  | x |
| Mouse X | Get mouse X |  |  | x |
| Mouse Y | Get mouse Y |  |  | x |

## Thymio Events

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Forward Button | Forward button pressed |  |  | x |
| Backward Button | Backward button pressed |  |  | x |
| Left Button | Left button pressed |  |  | x |
| Right Button | Right button pressed |  |  | x |
| Center Button | Center button pressed |  |  | x |
| Any Button | Any button state changed |  |  | x |
| Proximity Update | Proximity sensors updated (10 Hz) |  |  | x |
| Ground Update | Ground sensors updated (10 Hz) |  |  | x |
| Timer 0 | Timer 0 triggered |  |  | x |
| Timer 1 | Timer 1 triggered |  |  | x |
| Tap Detected | Robot tapped/shaken |  |  | x |
| Sound Detected | Microphone threshold exceeded |  |  | x |
| Sound Finished | Sound playback completed |  |  | x |
| Message Received | IR message received |  |  | x |

## Thymio Motors

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Set Motor Speeds | Set left and right motor speeds |  |  | x |
| Move Forward | Move forward at speed |  |  | x |
| Move Backward | Move backward at speed |  |  | x |
| Turn Left | Turn left at speed |  |  | x |
| Turn Right | Turn right at speed |  |  | x |
| Stop Motors | Stop both motors |  |  | x |

## Thymio LEDs

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Set Top LED | Set top RGB LED color |  |  | x |
| Set Bottom Left LED | Set bottom left RGB LED |  |  | x |
| Set Bottom Right LED | Set bottom right RGB LED |  |  | x |
| Set Circle LED | Set one circle LED |  |  | x |
| Set All Circle LEDs | Set all 8 circle LEDs |  |  | x |
| Turn Off LEDs | Turn off all LEDs |  |  | x |

## Thymio Sound

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Play Tone | Play frequency tone |  |  | x |
| Play System Sound | Play built-in sound |  |  | x |
| Stop Sound | Stop sound playback |  |  | x |

## Thymio Sensors

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Read Proximity | Read proximity sensor value |  |  | x |
| Read Ground | Read ground sensor value |  |  | x |
| Read Button | Read button state |  |  | x |

## Thymio Conditions

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| If Proximity | Check proximity sensor |  |  | x |
| If Ground Dark | Check if ground is dark |  |  | x |
| If Ground Light | Check if ground is light |  |  | x |
| If Button Pressed | Check if button pressed |  |  | x |
| If Button Released | Check if button released |  |  | x |
| If Variable | Check variable condition |  |  | x |

## Thymio Timers

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Set Timer Period | Set timer period (ms) |  |  | x |

## Thymio Variables

| Block | Description | Beginner | Advanced | Development |
|-------|-------------|:--------:|:--------:|:-----------:|
| Set Variable | Set variable value |  |  | x |
| Increase Variable | Increment variable |  |  | x |
| Decrease Variable | Decrement variable |  |  | x |

