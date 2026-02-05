# Click Counter Game

A simple, timed click counter game built with vanilla HTML, CSS, and JavaScript.

## Plan

1.  **HTML Structure**:
    -   Create a centered container for the game.
    -   Display the current score and a countdown timer.
    -   Provide a large, clickable button.
    -   Include a results section (hidden during play) for the final score and performance message.
    -   Add a "Restart" button.

2.  **CSS Styling**:
    -   Center all elements on the page using Flexbox.
    -   Style the main click button to be large and interactive.
    -   Ensure the layout is responsive and visually appealing.

3.  **JavaScript Logic**:
    -   Implement a 10-second countdown timer.
    -   Handle click events to increment the score.
    -   Automatically start the timer on the first click.
    -   Disable the button and display results when the timer reaches zero.
    -   Add performance-based feedback messages.
    -   Implement reset/restart functionality.

## Implementation Details

- **Time Limit**: 10 seconds.
- **Feedback Tiers**:
  - < 30 clicks: "Keep practicing! 🐢"
  - 30-49 clicks: "Not bad! 🐇"
  - 50-74 clicks: "Fast fingers! 🔥"
  - 75+ clicks: "Legendary clicking speed! ⚡"

## Features

- **Responsive Design**: Centered layout that works on both desktop and mobile devices.
- **High Score Tracking**: Automatically saves your best score to local storage.
- **Keyboard Support**: Use Space or Enter keys to click the button and restart the game.
- **Visual Feedback**: Dynamic animations for clicks, score updates, and timer warnings.
- **Performance Feedback**: Custom messages and emojis based on your clicking speed.
