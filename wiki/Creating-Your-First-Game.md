# Creating Your First Game

> [English](Creating-Your-First-Game) | [Français](Premier_Jeu_fr) | [Deutsch](Erstes_Spiel_de) | [Italiano](Primo_Gioco_it) | [Español](Primer_Juego_es) | [Português](Primeiro_Jogo_pt) | [Slovenščina](Prva_Igra_sl) | [Українська](Persha_Gra_uk) | [Русский](Pervaya_Igra_ru)

---

> [Back to Home](Home)

In this tutorial, we'll create a simple "Catch the Stars" game where a player moves to collect falling stars.

---

## What You'll Learn

- Creating sprites
- Creating objects with events and actions
- Using the room editor
- Running and testing your game

---

## Step 1: Create a New Project

1. Launch PyGameMaker
2. Go to **File > New Project**
3. Name your project "CatchTheStars"
4. Click **Create**

---

## Step 2: Create the Player Sprite

1. Right-click on **Sprites** in the resource tree
2. Select **Create Sprite**
3. Name it `spr_player`
4. Click **Edit Sprite** to open the sprite editor
5. Draw a simple character (or use a 32x32 colored rectangle)
6. Click **Save**

---

## Step 3: Create the Star Sprite

1. Right-click on **Sprites** > **Create Sprite**
2. Name it `spr_star`
3. Draw a star shape (or use a yellow circle)
4. Click **Save**

---

## Step 4: Create the Player Object

1. Right-click on **Objects** in the resource tree
2. Select **Create Object**
3. Name it `obj_player`
4. Set the **Sprite** to `spr_player`

### Add Keyboard Events

**Left Arrow Key:**
1. Click **Add Event** > **Keyboard** > **Left**
2. Add action: **Set Horizontal Speed** with value `-4`

**Right Arrow Key:**
1. Click **Add Event** > **Keyboard** > **Right**
2. Add action: **Set Horizontal Speed** with value `4`

**No Key Pressed:**
1. Click **Add Event** > **Keyboard** > **No Key**
2. Add action: **Set Horizontal Speed** with value `0`

---

## Step 5: Create the Star Object

1. Right-click on **Objects** > **Create Object**
2. Name it `obj_star`
3. Set the **Sprite** to `spr_star`

### Add Create Event
1. Click **Add Event** > **Create**
2. Add action: **Set Vertical Speed** with value `3`
3. Add action: **Jump to Random Position** (horizontal only)

### Add Outside Room Event
1. Click **Add Event** > **Other** > **Outside Room**
2. Add action: **Jump to Start Position**
3. Add action: **Set Score** with value `1` and **Relative** checked

### Add Collision with Player
1. Click **Add Event** > **Collision** > select `obj_player`
2. Add action: **Set Score** with value `10` and **Relative** checked
3. Add action: **Play Sound** (optional, if you have a sound)
4. Add action: **Jump to Random Position**

---

## Step 6: Create the Room

1. Right-click on **Rooms** in the resource tree
2. Select **Create Room**
3. Name it `room_game`
4. Set room size to **640 x 480**

### Place Objects
1. Select the **Objects** tab in the room editor
2. Click on `obj_player` and place it at the bottom center of the room
3. Click on `obj_star` and place 5-10 stars scattered at the top

---

## Step 7: Display the Score

1. Open `obj_player`
2. Click **Add Event** > **Draw**
3. Add action: **Draw Score** at position (10, 10)

---

## Step 8: Run Your Game!

1. Press **F5** or go to **Run > Run Game**
2. Use the left and right arrow keys to move
3. Catch the falling stars to increase your score!

---

## Enhancements to Try

### Add Lives
1. Create a "game over" object that appears when lives reach 0
2. Add a collision event with a "bad" object that reduces lives

### Add Levels
1. Create multiple rooms
2. Use the **Next Room** action when score reaches a threshold

### Add Sound
1. Import sound files in the Sounds resource
2. Add **Play Sound** actions to events

### Use Visual Programming
1. Open an object
2. Click the **Blockly** tab to use drag-and-drop programming
3. Build the same logic visually with blocks

---

## Complete Project Structure

After completing this tutorial, your project should have:

- **Sprites:** spr_player, spr_star
- **Objects:** obj_player, obj_star
- **Rooms:** room_game

---

## Next Steps

- [[Object-Editor]] - Learn more about object properties
- [[Events-and-Actions]] - Explore all available events and actions
- [[Visual-Programming]] - Try building with Blockly blocks
- [[Exporting-Games]] - Share your game with others
