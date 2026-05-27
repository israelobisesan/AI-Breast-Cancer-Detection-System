(function() {
  'use strict';

  // Mobile nav toggle
  var toggleBtn = document.getElementById('navToggle');
  var navLinks = document.getElementById('navLinks');
  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener('click', function() {
      navLinks.classList.toggle('open');
    });
    document.addEventListener('click', function(e) {
      if (!toggleBtn.contains(e.target) && !navLinks.contains(e.target)) {
        navLinks.classList.remove('open');
      }
    });
  }

  // Auto-hide flash messages
  var alerts = document.querySelectorAll('.alert');
  alerts.forEach(function(alert) {
    setTimeout(function() {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.5s';
      setTimeout(function() { alert.remove(); }, 500);
    }, 5000);
  });

  // Sync nav active state with current path
  var currentPath = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(function(link) {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  // Form submit loading state
  document.querySelectorAll('form').forEach(function(form) {
    form.addEventListener('submit', function() {
      var btn = this.querySelector('button[type="submit"]');
      if (btn && !btn.disabled) {
        btn.disabled = true;
      }
    });
  });

  // Unsaved changes warning on assessment form
  var assessmentForm = document.getElementById('assessmentForm');
  if (assessmentForm) {
    var formModified = false;
    assessmentForm.addEventListener('change', function() { formModified = true; });
    window.addEventListener('beforeunload', function(e) {
      if (formModified && !assessmentForm.submitted) {
        e.preventDefault();
        e.returnValue = '';
      }
    });
    assessmentForm.addEventListener('submit', function() {
      assessmentForm.submitted = true;
    });
  }
})();
