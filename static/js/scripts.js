// static/js/scripts.js

/**
 * Switches <body> class to the chosen theme.
 * Saves the choice in localStorage, so it persists across reloads.
 */
function setTheme(themeClass) {
    // Remove any previous theme-* classes
    document.body.classList.remove("theme-dark", "theme-light", "theme-high-contrast");
    // Add the new one
    document.body.classList.add(themeClass);
    // Store the user’s choice
    localStorage.setItem('vuluruTodoTheme', themeClass);
  }
  
  document.addEventListener("DOMContentLoaded", function() {
    // -------------------------------------------------
    // 1. Auto-Dismissing Flash Messages
    // -------------------------------------------------
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
      // Fade out & remove after 5 seconds
      setTimeout(function() {
        alert.classList.add('fade');
        alert.classList.remove('show');
        setTimeout(function() {
          alert.remove();
        }, 150); // match Bootstrap fade transition
      }, 5000);
    });
  
    // -------------------------------------------------
    // 2. Delete (Task/Contact) Modal & Hidden Input
    // -------------------------------------------------
    const deleteTaskModal = document.getElementById('deleteTaskModal');
    if (deleteTaskModal) {
      const deleteTaskForm = document.getElementById('deleteTaskForm');
      const deleteTaskIdInput = document.getElementById('delete_task_id');
      const deleteButtons = document.querySelectorAll('.delete-btn');
  
      deleteButtons.forEach(function(button) {
        button.addEventListener('click', function() {
          // Either "data-task-id" or "data-contact-id", adapt as needed
          const itemId = button.getAttribute('data-task-id') || button.getAttribute('data-contact-id');
          if (deleteTaskIdInput) {
            deleteTaskIdInput.value = itemId;
          }
        });
      });
  
      // If you want purely AJAX removal, you could override the form submission here.
    }
  
    // -------------------------------------------------
    // 3. Real-Time Form Validation
    // -------------------------------------------------
    function setupRealTimeValidation() {
      const descriptionInput = document.getElementById('description');
      const dueDateInput = document.getElementById('due_date');
      const priorityInput = document.getElementById('priority');
      const statusInput = document.getElementById('status');
      const nameInput = document.getElementById('name'); // e.g., for contact forms
      // Add any other fields if needed
  
      // Validate Description (non-empty)
      if (descriptionInput) {
        descriptionInput.addEventListener('input', function() {
          if (this.value.trim() === '') {
            this.classList.add('is-invalid');
          } else {
            this.classList.remove('is-invalid');
          }
        });
      }
  
      // Validate Due Date Format (YYYY-MM-DD)
      if (dueDateInput) {
        dueDateInput.addEventListener('change', function() {
          const dateValue = this.value;
          if (dateValue) {
            const regex = /^\d{4}-\d{2}-\d{2}$/;
            if (!regex.test(dateValue)) {
              this.classList.add('is-invalid');
            } else {
              this.classList.remove('is-invalid');
            }
          } else {
            this.classList.remove('is-invalid');
          }
        });
      }
  
      // Validate Priority (could be optional or required)
      if (priorityInput) {
        priorityInput.addEventListener('change', function() {
          // If optional, skip. If you want mandatory, do:
          if (this.value === '') {
            this.classList.add('is-invalid');
          } else {
            this.classList.remove('is-invalid');
          }
        });
      }
  
      // Validate Status Input (Pending/Completed)
      if (statusInput) {
        statusInput.addEventListener('change', function() {
          // If your app only has two statuses, you might check that here
        });
      }
  
      // Validate Contact Name (non-empty)
      if (nameInput) {
        nameInput.addEventListener('input', function() {
          if (this.value.trim() === '') {
            this.classList.add('is-invalid');
          } else {
            this.classList.remove('is-invalid');
          }
        });
      }
    }
    setupRealTimeValidation();
  
    // -------------------------------------------------
    // 4. Tooltip Initialization
    // -------------------------------------------------
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  
    // -------------------------------------------------
    // 5. Theme Toggle Handler with Local Storage
    // -------------------------------------------------
    const themeSelect = document.getElementById('themeSelect');
    if (themeSelect) {
      // Attempt to restore previously saved theme
      const savedTheme = localStorage.getItem('vuluruTodoTheme');
      if (savedTheme) {
        themeSelect.value = savedTheme;
        setTheme(savedTheme);
      } else {
        // If none saved, ensure the body class matches the current select's default
        setTheme(themeSelect.value);
      }
  
      // Listen for changes on the theme dropdown
      themeSelect.addEventListener('change', function() {
        setTheme(this.value);
      });
    }
  });