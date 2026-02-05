# Catch the Falling Objects Game

A high-performance, vanilla HTML5 and JavaScript game where the player catches falling items.

## Game Features
- **Responsive Controls**: Smooth movement using Left and Right Arrow keys.
- **Dynamic Difficulty**: Falling speed and object spawn rates increase as the score grows.
- **Score Tracking**: Points for every catch, with persistent high scores stored locally.
- **Game States**: Complete flow from Start Screen to Gameplay and Game Over.
- **Visual Effects**: Emoji-based objects, CSS animations, and screen shake on miss.
- **Audio Feedback**: Synthesized sound effects for catches and misses (No external assets required).

## Technical Implementation
- **Rendering**: Optimized 60FPS loop using `requestAnimationFrame`.
- **Physics**: Simple AABB collision detection.
- **Audio**: Web Audio API for procedural sound generation.
- **No Dependencies**: Pure HTML, CSS, and JavaScript.

## Development Plan
- [x] Core gameplay loop (Falling objects and player movement).
- [x] Scoring and collision detection.
- [x] Dynamic difficulty scaling.
- [x] Game Over and Restart functionality.
- [x] Keyboard shortcuts (Space/Enter) for menu navigation.
- [x] Pause functionality (P key).
- [x] Visual polish for the player and falling objects.
- [x] Add synthesized sound effects using Web Audio API.
- [x] Implement screen shake effect when an object is missed.

## Controls
- **Arrow Left / Right**: Move the basket.
- **Space / Enter**: Start or Restart the game.
- **P**: Pause / Resume.