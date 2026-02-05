const mazes = [
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 'S', 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1],
        [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 'E', 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ],
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 'S', 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 'E', 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
];

const mazeContainer = document.getElementById('maze-container');
const statusMessage = document.getElementById('status-message');
const resetButton = document.getElementById('reset-button');
const stepDisplay = document.getElementById('step-count');
const bestScoreDisplay = document.getElementById('best-score');
const levelDisplay = document.getElementById('level-count');

let currentLevel = 0;
let mazeData = mazes[currentLevel];
let playerPos = { x: 0, y: 0 };
let gameActive = true;
let steps = 0;

function getBestScoreKey() {
    return `mazeBestScore_level_${currentLevel}`;
}

function getBestScore() {
    let score = localStorage.getItem(getBestScoreKey());
    return score ? parseInt(score) : Infinity;
}

let playerElement;

function initGame() {
    mazeData = mazes[currentLevel];
    mazeContainer.innerHTML = '';
    mazeContainer.style.gridTemplateColumns = `repeat(${mazeData[0].length}, var(--cell-size))`;
    
    steps = 0;
    levelDisplay.textContent = currentLevel + 1;
    updateStats();

    for (let y = 0; y < mazeData.length; y++) {
        for (let x = 0; x < mazeData[y].length; x++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            
            if (mazeData[y][x] === 1) {
                cell.classList.add('wall');
            } else {
                cell.classList.add('path');
                if (mazeData[y][x] === 'S') {
                    cell.classList.add('start');
                    playerPos = { x, y };
                } else if (mazeData[y][x] === 'E') {
                    cell.classList.add('exit');
                }
            }
            cell.id = `cell-${x}-${y}`;
            mazeContainer.appendChild(cell);
        }
    }
    
    playerElement = document.createElement('div');
    playerElement.classList.add('player');
    renderPlayer();
    
    statusMessage.textContent = 'Navigate to the green exit!';
    statusMessage.classList.remove('success');
    gameActive = true;
}

function updateStats() {
    stepDisplay.textContent = steps;
    const bestScore = getBestScore();
    bestScoreDisplay.textContent = bestScore === Infinity ? '-' : bestScore;
}

function renderPlayer() {
    const currentCell = document.getElementById(`cell-${playerPos.x}-${playerPos.y}`);
    if (currentCell) {
        currentCell.appendChild(playerElement);
    }
}

function movePlayer(dx, dy) {
    if (!gameActive) return;
    
    const newX = playerPos.x + dx;
    const newY = playerPos.y + dy;
    
    if (newY >= 0 && newY < mazeData.length && 
        newX >= 0 && newX < mazeData[0].length && 
        mazeData[newY][newX] !== 1) {
        
        playerPos.x = newX;
        playerPos.y = newY;
        steps++;
        updateStats();
        renderPlayer();
        
        checkWin();
    }
}

function checkWin() {
    if (mazeData[playerPos.y][playerPos.x] === 'E') {
        gameActive = false;
        
        const bestScore = getBestScore();
        if (steps < bestScore) {
            localStorage.setItem(getBestScoreKey(), steps);
            updateStats();
        }

        if (currentLevel < mazes.length - 1) {
            statusMessage.textContent = `Level Complete! ${steps} steps. Next level loading...`;
            statusMessage.classList.add('success');
            setTimeout(() => {
                currentLevel++;
                initGame();
            }, 2000);
        } else {
            statusMessage.textContent = `YOU WIN! Total Escape! All levels complete!`;
            statusMessage.classList.add('success');
        }
    }
}

document.addEventListener('keydown', (e) => {
    const key = e.key.toLowerCase();
    const moveKeys = ['arrowup', 'arrowdown', 'arrowleft', 'arrowright', 'w', 'a', 's', 'd'];
    
    if (moveKeys.includes(key)) {
        e.preventDefault();
        let dx = 0;
        let dy = 0;
        
        if (key === 'arrowleft' || key === 'a') dx = -1;
        else if (key === 'arrowright' || key === 'd') dx = 1;
        else if (key === 'arrowup' || key === 'w') dy = -1;
        else if (key === 'arrowdown' || key === 's') dy = 1;
        
        movePlayer(dx, dy);
    }
});

resetButton.addEventListener('click', () => {
    initGame();
    resetButton.blur();
});

// Mobile Controls
document.getElementById('up-btn').addEventListener('click', () => movePlayer(0, -1));
document.getElementById('down-btn').addEventListener('click', () => movePlayer(0, 1));
document.getElementById('left-btn').addEventListener('click', () => movePlayer(-1, 0));
document.getElementById('right-btn').addEventListener('click', () => movePlayer(1, 0));

// Initialize on load
initGame();
