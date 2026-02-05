const holes = document.querySelectorAll('.hole');
const scoreBoard = document.querySelector('#score');
const timerDisplay = document.querySelector('#timer');
const startBtn = document.querySelector('#start-btn');
const moles = document.querySelectorAll('.mole');
const gameOverOverlay = document.querySelector('#game-over');
const finalScoreDisplay = document.querySelector('#final-score');
const restartBtn = document.querySelector('#restart-btn');

let lastHole;
let timeUp = false;
let score = 0;
let countdown;
let peepTimeout;
let gameTime = 30; // seconds

function randomTime(min, max) {
    return Math.round(Math.random() * (max - min) + min);
}

function randomHole(holes) {
    const idx = Math.floor(Math.random() * holes.length);
    const hole = holes[idx];
    if (hole === lastHole) {
        return randomHole(holes);
    }
    lastHole = hole;
    return hole;
}

function peep() {
    const time = randomTime(600, 1200);
    const hole = randomHole(holes);
    const mole = hole.querySelector('.mole');
    mole.classList.remove('whacked');
    mole.classList.add('up');
    
    peepTimeout = setTimeout(() => {
        mole.classList.remove('up');
        if (!timeUp) peep();
    }, time);
}

function startGame() {
    // Reset state
    clearTimeout(peepTimeout);
    clearInterval(countdown);
    
    // Reset moles
    moles.forEach(mole => {
        mole.classList.remove('up');
        mole.classList.remove('whacked');
    });

    score = 0;
    scoreBoard.textContent = 0;
    timeUp = false;
    startBtn.disabled = true;
    gameOverOverlay.classList.add('hidden');
    
    let timeLeft = gameTime;
    timerDisplay.textContent = timeLeft;

    peep();

    countdown = setInterval(() => {
        timeLeft--;
        timerDisplay.textContent = timeLeft;
        if (timeLeft <= 0) {
            clearInterval(countdown);
            endGame();
        }
    }, 1000);
}

function endGame() {
    timeUp = true;
    startBtn.disabled = false;
    finalScoreDisplay.textContent = score;
    gameOverOverlay.classList.remove('hidden');
}

function whack(e) {
    if (!e.isTrusted) return; // cheater!
    if (this.classList.contains('up') && !this.classList.contains('whacked')) {
        score++;
        this.classList.add('whacked');
        setTimeout(() => {
            this.classList.remove('up');
        }, 100);
        scoreBoard.textContent = score;
    }
}

moles.forEach(mole => mole.addEventListener('click', whack));
startBtn.addEventListener('click', startGame);
restartBtn.addEventListener('click', startGame);
