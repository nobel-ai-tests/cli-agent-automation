# Snake Game Implementation

A classic Snake game implemented with HTML5 Canvas and Vanilla JavaScript.

## Completed Features
- [x] Basic HTML structure with Canvas and UI overlays.
- [x] CSS for layout and styling (centered, dark theme).
- [x] Game logic (snake movement, growth, food spawning).
- [x] Input handling for arrow keys and WASD.
- [x] Collision detection (walls and self).
- [x] Score tracking and Game Over screen.
- [x] Start and Restart functionality.
- [x] High score persistence using `localStorage`.

## Final Polish & Improvements
- [x] **Robust Input Handling:** Prevented rapid key presses from causing self-collision by limiting one turn per tick.
- [x] **Visual Polish:** Added gradients, shadows, and better snake head styling (eyes).
- [x] **Speed Scaling:** Game gradually increases in speed as you eat more food.

## Technical Details
- **Canvas:** 400x400 grid (20x20 tiles).
- **Game Loop:** `requestAnimationFrame` with a controlled frame rate for consistent speed.
- **No Dependencies:** Pure Vanilla JS and CSS.

## How to Play
1. Open `index.html` in any modern web browser.
2. Click "Start Game".
3. Use Arrow Keys or WASD to control the snake.
4. Eat the red food to grow and increase your score.
5. Don't hit the walls or yourself!