# PyGameMaker — Tutorial 15: Fruit Fusion — Worksheet

*[Home](Home) | [Teacher resources](Teacher-Resources)*

**Download:** [PDF](downloads/Worksheet-15-fruit-fusion.pdf) · [ODT](downloads/Worksheet-15-fruit-fusion.odt)

**For teachers:** [Answer key](Answer-Key-15-fruit-fusion)

---

Name: ______________________________   Date: ______________

Do this worksheet after you have won and lost... actually, you cannot lose! Do it after you have won the game at least once.

## Part A: Words

Match each word with what it means. Write the letter next to the number.

1. Fusion ____
2. Held fruit ____
3. If / Else ____
4. Spawner ____

- **A.** A block that does one thing when something is true, and a different thing when it is not
- **B.** An invisible object whose only job is to create other objects on a timer
- **C.** Catching a matching fruit so it grows into the next, bigger fruit
- **D.** The one fruit the basket is currently carrying, remembered in `held_level`

## Part B: Which object and event?

Write the object and the event for each rule.

1. Turn into a strawberry when a matching cherry is caught: ______________________
2. Create a new cherry every 90 steps: ______________________
3. Remove a fruit that falls past the basket without being caught: ______________________
4. Show the YOU WIN! message: ______________________
5. Restart the game when SPACE is pressed on the win screen: ______________________

## Part C: Think about it

1. `held_level` starts at 1 (a cherry). Why does catching a cherry while `held_level` is already 3 (an orange) only give 1 point instead of fusing?

<br>

<br>

<br>


2. What would happen if the orange collision's *Go to room room_win* action were accidentally placed in the *Otherwise* branch instead of the *If* branch?

<br>

<br>

<br>


3. Why does each fruit type need its own spawner object, instead of one spawner picking a random fruit type?

<br>

<br>

<br>


## Part D: Try it

- [ ] The basket moves and stops
- [ ] Catching a matching cherry turns the basket into a strawberry and adds 10 points
- [ ] Catching a matching strawberry turns the basket into an orange and adds 20 points
- [ ] Catching a matching orange turns the basket into a watermelon, adds 50 points, and shows YOU WIN!
- [ ] A mismatched catch only adds 1 point and changes nothing else

## Part E: Look back

1. What I am proudest of: ______________________________________
2. A bug I found and fixed: ______________________________________
3. What I would add next: ______________________________________
