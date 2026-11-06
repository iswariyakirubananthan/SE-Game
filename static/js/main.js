/**
 * static/js/main.js - Global Interactions & Flash Message Auto-Dismissal
 * Demonstrates:
 *   - Theme C: Event-Driven Programming (Window load, timeout events, smooth interactions)
 */

document.addEventListener('DOMContentLoaded', () => {
  // Auto-dismiss flash alerts after 4.5 seconds
  const alerts = document.querySelectorAll('.alert');
  if (alerts.length > 0) {
    setTimeout(() => {
      alerts.forEach(alert => {
        alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 400);
      });
    }, 4500);
  }
});
