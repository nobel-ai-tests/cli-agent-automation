# Tic-Tac-Toe Project

A polished, two-player Tic-Tac-Toe game built with HTML, CSS, and Vanilla JavaScript.

## Features

- **Responsive Design**: Centered layout that works on both desktop and mobile devices.
- **Score Tracking**: Persistent scores for Player X and Player O during the session.
- **Visual Feedback**: Winning combinations are highlighted with an animation.
- **Accessibility**: Includes ARIA roles and labels for better screen reader support.
- **Game Controls**: 
  - **Reset Game**: Starts a new round while keeping the current scores.
  - **Clear Scores**: Resets the win counts for both players.

## How to Play

1. Open `index.html` in any modern web browser.
2. Player X starts first.
3. Click on any empty cell to place your symbol.
4. Alternate turns until a player gets three in a row (horizontally, vertically, or diagonally) or the board is full (Draw).
5. Use the "Reset Game" button to play again.

## Implementation Details

- **HTML5**: Structured with semantic elements and ARIA attributes.
- **CSS3**: Uses Flexbox for centering and Grid for the 3x3 game board.
- **JavaScript**: Managed board state, turn alternation, and win/draw detection logic.