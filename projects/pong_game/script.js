const canvas = document.getElementById("pong");
const ctx = canvas.getContext("2d");

// Game elements
const user = {
    x: 0,
    y: canvas.height / 2 - 100 / 2, // centered vertically
    width: 10,
    height: 100,
    color: "WHITE",
    score: 0
};

const com = {
    x: canvas.width - 10,
    y: canvas.height / 2 - 100 / 2,
    width: 10,
    height: 100,
    color: "WHITE",
    score: 0
};

const ball = {
    x: canvas.width / 2,
    y: canvas.height / 2,
    radius: 10,
    speed: 7,
    velocityX: 5,
    velocityY: 5,
    color: "WHITE"
};

const net = {
    x: (canvas.width - 2) / 2,
    y: 0,
    height: 10,
    width: 2,
    color: "WHITE"
};

// Input state
const keys = {
    w: false,
    s: false,
    ArrowUp: false,
    ArrowDown: false
};

// Helper functions for drawing
function drawRect(x, y, w, h, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, w, h);
}

function drawArc(x, y, r, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2, true);
    ctx.closePath();
    ctx.fill();
}

function drawNet() {
    for (let i = 0; i <= canvas.height; i += 15) {
        drawRect(net.x, net.y + i, net.width, net.height, net.color);
    }
}

const playerScoreEl = document.getElementById("player-score");
const comScoreEl = document.getElementById("computer-score");

function updateScore() {
    playerScoreEl.innerText = user.score;
    comScoreEl.innerText = com.score;
}

// Reset Ball
function resetBall() {
    ball.x = canvas.width / 2;
    ball.y = canvas.height / 2;
    ball.speed = 7;
    
    // Random direction
    ball.velocityX = (Math.random() > 0.5 ? 1 : -1) * 5;
    ball.velocityY = (Math.random() > 0.5 ? 1 : -1) * 5;
}

// Collision detection
function collision(b, p) {
    p.top = p.y;
    p.bottom = p.y + p.height;
    p.left = p.x;
    p.right = p.x + p.width;

    b.top = b.y - b.radius;
    b.bottom = b.y + b.radius;
    b.left = b.x - b.radius;
    b.right = b.x + b.radius;

    return p.left < b.right && p.top < b.bottom && p.right > b.left && p.bottom > b.top;
}

// Update game logic
function update() {
    // Move User Paddle
    if (keys.w || keys.ArrowUp) {
        if (user.y > 0) user.y -= 8;
    }
    if (keys.s || keys.ArrowDown) {
        if (user.y + user.height < canvas.height) user.y += 8;
    }

    // Move Ball
    ball.x += ball.velocityX;
    ball.y += ball.velocityY;

    // Simple AI
    let computerLevel = 0.1;
    com.y += (ball.y - (com.y + com.height / 2)) * computerLevel;

    // Wall Collision (Top/Bottom)
    if (ball.y - ball.radius < 0) {
        ball.y = ball.radius;
        ball.velocityY = -ball.velocityY;
    } else if (ball.y + ball.radius > canvas.height) {
        ball.y = canvas.height - ball.radius;
        ball.velocityY = -ball.velocityY;
    }

    // Determine which paddle is being hit
    let player = (ball.x < canvas.width / 2) ? user : com;

    if (collision(ball, player)) {
        // Hit point detection
        // Where the ball hit the paddle (normalized -1 to 1)
        let collidePoint = (ball.y - (player.y + player.height / 2));
        collidePoint = collidePoint / (player.height / 2);

        // Calculate angle in Radian (max 45 deg = PI/4)
        let angleRad = (Math.PI / 4) * collidePoint;

        // Change X and Y velocity direction
        let direction = (ball.x < canvas.width / 2) ? 1 : -1;
        ball.velocityX = direction * ball.speed * Math.cos(angleRad);
        ball.velocityY = ball.speed * Math.sin(angleRad);

        // Reposition ball outside paddle to prevent sticking
        if (direction === 1) {
            ball.x = user.x + user.width + ball.radius;
        } else {
            ball.x = com.x - ball.radius;
        }

        // Increase speed every hit
        ball.speed += 0.2;
        // Cap speed
        if(ball.speed > 15) ball.speed = 15;
    }

    // Score update
    if (ball.x - ball.radius < 0) {
        com.score++;
        updateScore();
        resetBall();
    } else if (ball.x + ball.radius > canvas.width) {
        user.score++;
        updateScore();
        resetBall();
    }
}

// Render game
function render() {
    // Clear canvas
    drawRect(0, 0, canvas.width, canvas.height, "#000");
    
    // Draw Net
    drawNet();
    
    // Draw Score (Visual fallback in canvas, but we use HTML mostly)
    
    // Draw Paddles
    drawRect(user.x, user.y, user.width, user.height, user.color);
    drawRect(com.x, com.y, com.width, com.height, com.color);
    
    // Draw Ball
    drawArc(ball.x, ball.y, ball.radius, ball.color);
}

// Game Loop
function game() {
    update();
    render();
    requestAnimationFrame(game);
}

// Input Listeners
window.addEventListener("keydown", (evt) => {
    const key = evt.key.length === 1 ? evt.key.toLowerCase() : evt.key;
    if (keys.hasOwnProperty(key)) {
        keys[key] = true;
    }
});

window.addEventListener("keyup", (evt) => {
    const key = evt.key.length === 1 ? evt.key.toLowerCase() : evt.key;
    if (keys.hasOwnProperty(key)) {
        keys[key] = false;
    }
});

document.getElementById("restart-btn").addEventListener("click", () => {
    user.score = 0;
    com.score = 0;
    user.y = canvas.height / 2 - 100 / 2;
    com.y = canvas.height / 2 - 100 / 2;
    updateScore();
    resetBall();
});

// Start
resetBall(); // Init ball movement
game();
