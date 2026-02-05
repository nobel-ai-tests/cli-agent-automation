# Guess the Number Game

A simple, self-contained web-based game where the computer selects a random number between 1 and 100, and the player tries to guess it.

## Features
- **Random Number Selection:** The game generates a random integer between 1 and 100 at the start.
- **Player Input:** A text input field for players to enter their guesses.
- **Input Validation:** Ensures the input is a valid number within the 1-100 range.
- **Dynamic Feedback:** Provides immediate feedback ("Too high", "Too low", or "Correct").
- **Attempt Tracking:** Keeps track of how many guesses the player has made.
- **Success Message:** Displays a celebratory message and the total attempts when the player wins.
- **Guess History:** Shows a list of previous guesses to help the player refine their strategy.
- **Restart Functionality:** A button to reset the game and start over with a new number.
- **Responsive Design:** Styled with CSS for a modern, centered, and mobile-friendly UI.

## Implementation Plan
1. **HTML Structure:** Create a clean layout with a container, heading, input, buttons, and display areas for feedback/stats.
2. **CSS Styling:** Use Material Design principles for a polished look, centering the game on the page and using clear typography.
3. **JavaScript Logic:**
    - Initialize the game by picking a random number.
    - Handle the "Submit" button click and "Enter" key press.
    - Validate player input.
    - Compare the guess with the target number and update the UI.
    - Track attempts and store guess history.
    - Handle the "Restart" button to reset the state.

## Progress
- [x] Initial Plan created in README.md
- [x] Implement index.html with HTML, CSS, and JS
- [x] Add Guess History feature
- [x] Final polish and verification

## How to Play
1. Open `index.html` in any modern web browser.
2. Enter a number between 1 and 100 in the input field.
3. Click "Submit Guess" or press Enter.
4. Follow the feedback (Too high/Too low) until you find the correct number.
5. Click "Play Again" to start a new round.
