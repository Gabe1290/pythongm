# PyGameMaker — Tutorial 3: Classic Pong — Worksheet

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Worksheet-03-pong.pdf) · [ODT](downloads/Worksheet-03-pong.odt)

---

Name: ______________________________   Date: ______________

Do this worksheet after you have played your finished Pong game with a partner.

## Part A: Words

Match each word with what it means. Write the letter next to the number.

1. Solid ____
2. Bounce ____
3. Global variable ____
4. Goal ____

- **A.** A value that every object can read and change
- **B.** An object that detects that the ball has gone past a paddle
- **C.** Reverse the direction of movement after a hit
- **D.** An object that other objects cannot pass through

## Part B: Which object?

Write which object each rule belongs to.

1. Moves up when the W key is held: ______________________
2. Bounces when it touches a wall: ______________________
3. Adds 1 to a score when the ball reaches it: ______________________
4. Draws the scores on the screen: ______________________
5. Stops a paddle from leaving the room: ______________________

## Part C: Think about it

1. The ball has the events **Collision with obj_wall** and **Collision with obj_paddle_left**, both with *Bounce*. Why do we need a separate event for each object?

<br>

<br>

<br>


2. A goal adds 1 to `global.p2score` when the ball touches the **left** goal. Why does Player 2 get the point and not Player 1?

<br>

<br>

<br>


3. Why is the score kept in a **global** variable and not in the ball?

<br>

<br>

<br>


## Part D: Try it

- [ ] Both paddles move with their own keys and stop at the walls
- [ ] The ball bounces off the top, the bottom and both paddles
- [ ] When the ball is missed, it goes back to the centre
- [ ] The correct player's score goes up
- [ ] Both scores are shown on the screen

## Part E: Look back

1. What I am proudest of: ______________________________________
2. A bug I found and fixed: ______________________________________
3. What I would add next: ______________________________________
