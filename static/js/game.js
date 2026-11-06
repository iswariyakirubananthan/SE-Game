/**
 * static/js/game.js - Interactive Game Engine
 * ============================================
 * Demonstrates:
 *   - Theme C: Event-Driven Programming
 *     * DOMContentLoaded: Initializes game session
 *     * Click Events: Submit button, Quit button, Modal action buttons
 *     * Keyboard Events: Enter key on answer input
 *     * Timer Events: setInterval for 1-second countdown ticks & clearInterval
 *     * Asynchronous Network Events: fetch() API communicating with Flask backend
 *   - Security: Puzzle solution is NEVER known to client JS; only evaluated on Python server.
 */

class BananaGameEngine {
  constructor(difficulty) {
    this.difficulty = difficulty;
    this.timeLimit = 60;
    this.timeRemaining = 60;
    this.timerInterval = null;
    this.isSubmitting = false;

    // Cache DOM Elements
    this.hudTimer = document.getElementById('hud-timer');
    this.hudLives = document.getElementById('hud-lives');
    this.hudScore = document.getElementById('hud-score');
    this.hudQuestion = document.getElementById('hud-question');
    this.puzzleImage = document.getElementById('puzzle-image');
    this.puzzleLoading = document.getElementById('puzzle-loading');
    this.answerInput = document.getElementById('answer-input');
    this.submitBtn = document.getElementById('submit-btn');
    this.quitBtn = document.getElementById('quit-btn');
    this.feedbackBanner = document.getElementById('feedback-banner');
    
    // Modal Elements
    this.gameOverModal = document.getElementById('game-over-modal');
    this.modalFinalScore = document.getElementById('modal-final-score');
    this.modalReason = document.getElementById('modal-reason');

    this.initEventListeners();
    this.startGame();
  }

  /**
   * Theme C: Event-Driven Programming
   * Attaches event listeners for user inputs and UI interactions.
   */
  initEventListeners() {
    // 1. Submit Button Click Event
    this.submitBtn.addEventListener('click', () => {
      this.handleAnswerSubmit();
    });

    // 2. Keyboard Enter Key Event on Input Field
    this.answerInput.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        this.handleAnswerSubmit();
      }
    });

    // 3. Quit Button Click Event
    this.quitBtn.addEventListener('click', () => {
      if (confirm('Are you sure you want to end this game? Your current score will be saved.')) {
        this.quitGame();
      }
    });

    // Automatically focus on the answer input when the page is ready
    window.addEventListener('load', () => {
      this.answerInput.focus();
    });
  }

  /**
   * Theme B & C: Initiates the game by calling the backend API.
   */
  async startGame() {
    this.setLoading(true);
    try {
      const response = await fetch('/game/api/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ difficulty: this.difficulty })
      });

      const data = await response.json();
      if (data.status === 'success') {
        this.timeLimit = data.time_limit;
        this.updateHUD(data.score, data.lives, data.question_number);
        this.loadPuzzleImage(data.question_image);
        this.startTimer();
      } else {
        alert('Failed to initialize game: ' + (data.message || 'Unknown error'));
      }
    } catch (err) {
      console.error('Error starting game:', err);
      alert('Network error connecting to the game server. Please try again.');
    } finally {
      this.setLoading(false);
    }
  }

  /**
   * Theme C: Countdown Timer using setInterval
   */
  startTimer() {
    this.stopTimer();
    this.timeRemaining = this.timeLimit;
    this.renderTimerDisplay();

    this.timerInterval = setInterval(() => {
      this.timeRemaining -= 1;
      this.renderTimerDisplay();

      if (this.timeRemaining <= 0) {
        this.stopTimer();
        this.handleTimeout();
      }
    }, 1000);
  }

  stopTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }

  renderTimerDisplay() {
    this.hudTimer.textContent = `${this.timeRemaining}s`;

    // Visual urgency cue: turn red and pulse when time <= 10s
    if (this.timeRemaining <= 10) {
      this.hudTimer.classList.add('urgent');
    } else {
      this.hudTimer.classList.remove('urgent');
    }
  }

  /**
   * Handles Timer Expiration Event
   */
  async handleTimeout() {
    this.showFeedback('wrong', 'Time is up! 1 life lost.');
    this.setLoading(true);

    try {
      const response = await fetch('/game/api/timeout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();
      if (data.status === 'game_over') {
        this.triggerGameOver(data.final_score, data.message);
      } else if (data.status === 'timeout') {
        this.updateHUD(data.score, data.lives, data.question_number);
        this.loadPuzzleImage(data.next_question_image);
        this.startTimer();
      }
    } catch (err) {
      console.error('Timeout handler error:', err);
    } finally {
      this.setLoading(false);
    }
  }

  /**
   * Handles Player Answer Submission Event
   */
  async handleAnswerSubmit() {
    if (this.isSubmitting) return;

    const answer = this.answerInput.value.trim();
    if (!answer || isNaN(answer)) {
      this.showFeedback('wrong', 'Please enter a valid number!');
      this.answerInput.focus();
      return;
    }

    this.isSubmitting = true;
    this.stopTimer();

    try {
      const response = await fetch('/game/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answer: parseInt(answer, 10) })
      });

      const data = await response.json();

      if (data.status === 'correct') {
        this.showFeedback('correct', data.message);
        this.updateHUD(data.score, data.lives, data.question_number);
        this.answerInput.value = '';
        this.loadPuzzleImage(data.next_question_image);
        this.startTimer();
      } else if (data.status === 'wrong') {
        this.showFeedback('wrong', data.message);
        this.updateHUD(data.score, data.lives, data.question_number);
        this.answerInput.value = '';
        this.loadPuzzleImage(data.next_question_image);
        this.startTimer();
      } else if (data.status === 'game_over') {
        this.triggerGameOver(data.final_score, data.message);
      } else {
        this.showFeedback('wrong', data.message || 'Error submitting answer');
        this.startTimer();
      }
    } catch (err) {
      console.error('Answer submission error:', err);
      this.showFeedback('wrong', 'Connection error. Retrying timer.');
      this.startTimer();
    } finally {
      this.isSubmitting = false;
      this.answerInput.focus();
    }
  }

  /**
   * Updates HUD UI elements
   */
  updateHUD(score, lives, questionNumber) {
    if (this.hudScore) this.hudScore.textContent = score;
    if (this.hudLives) {
      // Render heart icons for lives
      let hearts = '';
      for (let i = 0; i < lives; i++) hearts += '❤️ ';
      this.hudLives.textContent = hearts || '0';
    }
    if (this.hudQuestion && questionNumber) {
      this.hudQuestion.textContent = `#${questionNumber}`;
    }
  }

  /**
   * Loads image and handles image load event
   */
  loadPuzzleImage(imageUrl) {
    this.setLoading(true);
    this.puzzleImage.src = imageUrl;
    this.puzzleImage.onload = () => {
      this.setLoading(false);
      this.answerInput.focus();
    };
    this.puzzleImage.onerror = () => {
      this.setLoading(false);
      this.showFeedback('wrong', 'Puzzle image preview could not be loaded.');
    };
  }

  setLoading(isLoading) {
    if (isLoading) {
      this.puzzleLoading.style.display = 'flex';
      this.puzzleImage.style.display = 'none';
      this.submitBtn.disabled = true;
    } else {
      this.puzzleLoading.style.display = 'none';
      this.puzzleImage.style.display = 'block';
      this.submitBtn.disabled = false;
    }
  }

  showFeedback(type, text) {
    this.feedbackBanner.className = `feedback-banner ${type}`;
    this.feedbackBanner.textContent = text;
    this.feedbackBanner.style.display = 'block';

    // Auto-clear feedback banner after 2.8 seconds
    setTimeout(() => {
      if (this.feedbackBanner) {
        this.feedbackBanner.style.display = 'none';
      }
    }, 2800);
  }

  triggerGameOver(finalScore, reason) {
    this.stopTimer();
    this.modalFinalScore.textContent = finalScore;
    this.modalReason.textContent = reason;
    this.gameOverModal.classList.add('active');
  }

  async quitGame() {
    this.stopTimer();
    try {
      const response = await fetch('/game/api/quit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      window.location.href = data.redirect || '/dashboard';
    } catch (e) {
      window.location.href = '/dashboard';
    }
  }
}
