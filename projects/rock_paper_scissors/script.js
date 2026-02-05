document.addEventListener('DOMContentLoaded', () => {
    let playerScore = 0;
    let computerScore = 0;

    const playerScoreSpan = document.getElementById('player-score');
    const computerScoreSpan = document.getElementById('computer-score');
    const playerChoiceP = document.getElementById('player-choice');
    const computerChoiceP = document.getElementById('computer-choice');
    const resultMessage = document.getElementById('result-message');
    const resetBtn = document.getElementById('reset-btn');
    const choiceButtons = document.querySelectorAll('.choice-btn');

    const choices = ['rock', 'paper', 'scissors'];

    function getComputerChoice() {
        const randomIndex = Math.floor(Math.random() * choices.length);
        return choices[randomIndex];
    }

    function determineWinner(player, computer) {
        if (player === computer) {
            return 'draw';
        }
        if (
            (player === 'rock' && computer === 'scissors') ||
            (player === 'paper' && computer === 'rock') ||
            (player === 'scissors' && computer === 'paper')
        ) {
            return 'player';
        }
        return 'computer';
    }

    function updateUI(playerChoice, computerChoice, winner) {
        const emojiMap = {
            'rock': '✊',
            'paper': '✋',
            'scissors': '✌️'
        };

        playerChoiceP.innerHTML = `Player: <span class="choice-emoji">${emojiMap[playerChoice]}</span> ${playerChoice.charAt(0).toUpperCase() + playerChoice.slice(1)}`;
        computerChoiceP.innerHTML = `Computer: <span class="choice-emoji">${emojiMap[computerChoice]}</span> ${computerChoice.charAt(0).toUpperCase() + computerChoice.slice(1)}`;

        resultMessage.classList.remove('win', 'lose', 'draw');
        // Trigger reflow for animation
        void resultMessage.offsetWidth;

        if (winner === 'player') {
            playerScore++;
            playerScoreSpan.textContent = playerScore;
            resultMessage.textContent = '🎉 You Win!';
            resultMessage.classList.add('win');
        } else if (winner === 'computer') {
            computerScore++;
            computerScoreSpan.textContent = computerScore;
            resultMessage.textContent = '💀 You Lose!';
            resultMessage.classList.add('lose');
        } else {
            resultMessage.textContent = "🤝 It's a Draw!";
            resultMessage.classList.add('draw');
        }
    }

    choiceButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove selected class from all buttons
            choiceButtons.forEach(btn => btn.classList.remove('selected'));
            // Add selected class to clicked button
            button.classList.add('selected');

            const playerChoice = button.id;
            const computerChoice = getComputerChoice();
            const winner = determineWinner(playerChoice, computerChoice);
            updateUI(playerChoice, computerChoice, winner);
        });
    });

    resetBtn.addEventListener('click', () => {
        playerScore = 0;
        computerScore = 0;
        playerScoreSpan.textContent = '0';
        computerScoreSpan.textContent = '0';
        playerChoiceP.textContent = 'Player: -';
        computerChoiceP.textContent = 'Computer: -';
        resultMessage.textContent = 'Choose an option to start!';
        resultMessage.classList.remove('win', 'lose', 'draw');
        choiceButtons.forEach(btn => btn.classList.remove('selected'));
    });
});