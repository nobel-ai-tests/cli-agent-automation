# Simple Pong Game

A classic Pong game implementation using HTML5, CSS, and vanilla JavaScript.

## Features
- **Player vs Computer:** Control the left paddle against a basic AI on the right.
- **Score Tracking:** Real-time score display for both players via HTML overlay.
- **Responsive Controls:** Use keyboard (**W/S** keys or **Arrow Up/Down**) to move the paddle.
- **Dynamic Ball Physics:** The ball increases speed with each paddle hit and bounces at different angles depending on where it strikes the paddle.
- **Restart Functionality:** A button to reset the scores and positions at any time.
- **Clean UI:** A centered, dark-themed game area with a dashed net.

## Project Structure
- `index.html`: Contains the game layout, scoreboard, and canvas element.
- `style.css`: Provides the visual styling, centering, and responsive design.
- `script.js`: Implements the game loop, physics engine, AI logic, and input handling.

## How to Play
1. Open `index.html` in any modern web browser.
2. Use **W/S** keys or **Up/Down Arrows** to control the left paddle.
3. The AI controls the right paddle.
4. The game continues indefinitely until you hit the **Restart Game** button.

## Implementation Details
- **Game Loop**: Driven by `requestAnimationFrame` for smooth 60fps performance.
- **Collision Detection**: Axis-Aligned Bounding Box (AABB) collision detection between the ball and paddles.
- **Paddle Physics**: Ball deflection angle is calculated based on the distance from the center of the paddle, allowing for strategic "angled" shots.
- **AI Logic**: A simple tracking algorithm with a slight delay and speed cap to keep the game challenging but fair.
