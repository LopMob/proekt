// Плавный переход между страницами
document.addEventListener('DOMContentLoaded', () => {
  const page = document.getElementById('page');
  page.classList.add('fade-in');
});

// Таймер обратного отсчёта
function startTimers() {
  const timers = document.querySelectorAll('.timer');
  timers.forEach((timer, index) => {
    const key = `auction_timer_${index}`;
    let endTime = localStorage.getItem(key);

    if (!endTime) {
      const duration = parseInt(timer.dataset.time); // в секундах
      endTime = Date.now() + duration * 1000;
      localStorage.setItem(key, endTime);
    }

    const interval = setInterval(() => {
      const remaining = Math.floor((endTime - Date.now()) / 1000);
      if (remaining <= 0) {
        timer.textContent = 'Завершено';
        clearInterval(interval);
        return;
      }
      const minutes = Math.floor(remaining / 60).toString().padStart(2, '0');
      const seconds = (remaining % 60).toString().padStart(2, '0');
      timer.textContent = `${minutes}:${seconds}`;
    }, 1000);
  });
}

document.addEventListener('DOMContentLoaded', startTimers);
