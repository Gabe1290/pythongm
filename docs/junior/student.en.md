# PyGameMaker Junior: Make Your Own Game

## How to Use This Handout

Keep this sheet next to your computer. Do each part on the screen, then
tick the box. Ask a neighbour first, then your teacher, if you get stuck.

## Part 1: Your Tools

Look at the top of the window. These are the buttons you will use:

- **New** (a blank page): start a new game
- **Open** (a folder): open a game you saved
- **Save** (a disk): save your game. Do this often!
- **Green triangle**: **play your game** (also the **F5** key)
- **Tick mark**: share your game as a web page

On the left you see your **Resources**: sprites, objects and rooms.

- A **sprite** is a picture.
- An **object** is something in your game that does things.
- A **room** is a level where the game happens.

## Part 2: Draw a Sprite

- [ ] Click **Assets > Create Sprite**.
- [ ] Type a name, for example `spr_hero`, then press OK.
- [ ] A drawing window opens. Pick a colour and draw with the pencil.
- [ ] Click **Save** when you are happy with it.

> TIP: Names start with `spr_` for sprites and `obj_` for objects. Use
> letters and numbers only, no spaces.

You can also click **Assets > Import Sprite** to use a picture from a file.
To change a sprite later, **double-click** it in the list on the left.

## Part 3: Make an Object Move

- [ ] Click **Assets > Create Object** and name it `obj_hero`.
- [ ] In **Sprite**, choose your sprite.
- [ ] In the **Blockly** area, drag blocks from the left to build what
      happens. For example: **Keyboard: Left** then **Set horizontal speed**.
- [ ] Add **Keyboard: No key** then **Stop moving**, so your hero stops.

> TIP: Right-click a block to **Duplicate** or **Delete** it.

## Part 4: Build a Room and Play

- [ ] Click **Assets > Create Room**.
- [ ] Click an object in the list, then click in the room to place it.
- [ ] Press the **green triangle** (or **F5**) to play.

> DONE: You should see your sprite in the game and be able to move it.

## Part 5: Share Your Game

- [ ] Click **File > Export as HTML5**.
- [ ] Choose a folder to save it in.
- [ ] Click **Yes** to open it in your browser.

You get one file ending in `.html`. Send it to a friend, and they can play
it in any browser!

## Stuck?

| What happens | Try this |
|---|---|
| My object does not move | Did you put a block under the **Keyboard** event? Is the object in the room? |
| My hero never stops | Add **Keyboard: No key** and **Stop moving** |
| I cannot see my sprite in the game | Did you choose the sprite in the object's **Sprite** box? |
| I deleted something by mistake | **Tools > Restore Deleted Assets** brings it back |
| The game shows a grey window | Wait a few seconds, then try again |

## Words to Know

- **Sprite**: a picture used in your game
- **Object**: something in your game that can do things
- **Room**: a level
- **Event**: "when something happens", like pressing a key
- **Action**: "do something", like moving
- **Block**: one piece of your program

## Challenges

- **Try this (5 min):** draw a second sprite and make a second object.
- **Push further:** make your hero move up and down as well.
- **Invent:** make a wall object that stops your hero.

## Think About It

1. What does a **Keyboard** event do?
2. What is the difference between a sprite and an object?
3. How would you show your game to someone at home?

## My Notes

[[notes:6]]
