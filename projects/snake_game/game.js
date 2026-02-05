const canvas = document.getElementById('snakeCanvas');
const ctx = canvas.getContext('2d');
const scoreBoard = document.getElementById('score-board');
const startScreen = document.getElementById('start-screen');
const gameOverScreen = document.getElementById('game-over');
const finalScoreText = document.getElementById('final-score');
const startBtn = document.getElementById('start-btn');
const restartBtn = document.getElementById('restart-btn');

const gridSize = 20;
const tileCount = canvas.width / gridSize;

let score = 0;
let highScore = localStorage.getItem('snakeHighScore') || 0;
let dx = 0;
let dy = 0;
let snake = [];
let food = { x: 5, y: 5 };
let gameRunning = false;
let nextDx = 0;
let nextDy = 0;
let lastTime = 0;
const initialSpeed = 120; // ms per frame
let currentSpeed = initialSpeed;
let directionChangedInFrame = false;

function init() {
    score = 0;
    highScore = localStorage.getItem('snakeHighScore') || 0;
    dx = 0;
    dy = -1; // Start moving up
    nextDx = 0;
    nextDy = -1;
    directionChangedInFrame = false;
    // Initial snake position
    snake = [
        { x: 10, y: 10 },
        { x: 10, y: 11 },
        { x: 10, y: 12 }
    ];
    placeFood();
    updateScoreBoard();
    startScreen.style.display = 'none';
    gameOverScreen.style.display = 'none';
    gameRunning = true;
    currentSpeed = initialSpeed;
    lastTime = 0;
    requestAnimationFrame(gameLoop);
}

function updateScoreBoard() {
    scoreBoard.innerHTML = `Score: ${score} <span style="margin-left: 20px; font-size: 0.8em; opacity: 0.8;">High Score: ${highScore}</span>`;
}

function placeFood() {
    food.x = Math.floor(Math.random() * tileCount);
    food.y = Math.floor(Math.random() * tileCount);
    
    // Make sure food doesn't spawn on snake
    for (let part of snake) {
        if (part.x === food.x && part.y === food.y) {
            return placeFood();
        }
    }
}

function drawSnake() {
    snake.forEach((part, index) => {
        // Head is slightly different color
        ctx.fillStyle = (index === 0) ? '#27ae60' : '#2ecc71';
        ctx.strokeStyle = '#34495e';
        ctx.lineWidth = 2;
        
        const x = part.x * gridSize;
        const y = part.y * gridSize;
        
        // Add a bit of roundedness to the snake parts
        ctx.fillRect(x + 1, y + 1, gridSize - 2, gridSize - 2);
        
        if (index === 0) {
            // Draw eyes for the head
            ctx.fillStyle = 'white';
            const eyeSize = 3;
            if (dx === 1) { // Right
                ctx.fillRect(x + gridSize - 6, y + 4, eyeSize, eyeSize);
                ctx.fillRect(x + gridSize - 6, y + gridSize - 7, eyeSize, eyeSize);
            } else if (dx === -1) { // Left
                ctx.fillRect(x + 3, y + 4, eyeSize, eyeSize);
                ctx.fillRect(x + 3, y + gridSize - 7, eyeSize, eyeSize);
            } else if (dy === -1) { // Up
                ctx.fillRect(x + 4, y + 3, eyeSize, eyeSize);
                ctx.fillRect(x + gridSize - 7, y + 3, eyeSize, eyeSize);
            } else if (dy === 1) { // Down
                ctx.fillRect(x + 4, y + gridSize - 6, eyeSize, eyeSize);
                ctx.fillRect(x + gridSize - 7, y + gridSize - 6, eyeSize, eyeSize);
            }
        }
    });
}

function drawFood() {
    ctx.fillStyle = '#e74c3c';
    ctx.shadowBlur = 10;
    ctx.shadowColor = '#e74c3c';
    ctx.beginPath();
    const centerX = food.x * gridSize + gridSize / 2;
    const centerY = food.y * gridSize + gridSize / 2;
    const radius = gridSize / 2 - 2;
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0; // Reset shadow for other drawings
}

function moveSnake() {
    dx = nextDx;
    dy = nextDy;
    directionChangedInFrame = false;

    const head = { x: snake[0].x + dx, y: snake[0].y + dy };
    
    // Check wall collision
    if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
        return gameOver();
    }

    // Check self collision
    for (let part of snake) {
        if (part.x === head.x && part.y === head.y) {
            return gameOver();
        }
    }

    snake.unshift(head);

    // Check food collision
    if (head.x === food.x && head.y === food.y) {
        score += 10;
        if (score > highScore) {
            highScore = score;
            localStorage.setItem('snakeHighScore', highScore);
        }
        updateScoreBoard();
        placeFood();
        // Slightly increase speed
        if (currentSpeed > 60) currentSpeed -= 1.5;
    } else {
        snake.pop();
    }
}

function gameOver() {
    gameRunning = false;
    gameOverScreen.style.display = 'block';
    finalScoreText.textContent = `Final Score: ${score}`;
    if (score >= highScore && score > 0) {
        finalScoreText.innerHTML += '<br><span style="color: #f1c40f;">New High Score!</span>';
    }
}

function clearCanvas() {
    ctx.fillStyle = '#34495e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw subtle grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= tileCount; i++) {
        ctx.beginPath();
        ctx.moveTo(i * gridSize, 0);
        ctx.lineTo(i * gridSize, canvas.height);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(0, i * gridSize);
        ctx.lineTo(canvas.width, i * gridSize);
        ctx.stroke();
    }
}

function gameLoop(currentTime) {
    if (!gameRunning) return;

    if (!lastTime) lastTime = currentTime;
    const elapsed = currentTime - lastTime;

    if (elapsed > currentSpeed) {
        clearCanvas();
        drawFood();
        moveSnake();
        if (gameRunning) drawSnake();
        lastTime = currentTime;
    }
    
    requestAnimationFrame(gameLoop);
}

window.addEventListener('keydown', e => {
    if (!gameRunning || directionChangedInFrame) return;
    
    switch (e.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
            if (dy !== 1) { nextDx = 0; nextDy = -1; directionChangedInFrame = true; }
            break;
        case 'ArrowDown':
        case 's':
        case 'S':
            if (dy !== -1) { nextDx = 0; nextDy = 1; directionChangedInFrame = true; }
            break;
        case 'ArrowLeft':
        case 'a':
        case 'A':
            if (dx !== 1) { nextDx = -1; nextDy = 0; directionChangedInFrame = true; }
            break;
        case 'ArrowRight':
        case 'd':
        case 'D':
            if (dx !== -1) { nextDx = 1; nextDy = 0; directionChangedInFrame = true; }
            break;
    }
});

startBtn.addEventListener('click', init);
restartBtn.addEventListener('click', init);

// Show start screen initially
clearCanvas();