// static/js/scripts.js

document.addEventListener("DOMContentLoaded", function() {
    // 1. Auto-Dismissing Flash Messages
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.classList.add('fade');
            alert.classList.remove('show');
            setTimeout(function() {
                alert.remove();
            }, 150);
        }, 5000);
    });

    // 2. (Removed) Add Task Form Submission via AJAX
    // We do a normal POST now, so no fetch call is needed.

    // 3. Delete Task via Modal
    const deleteTaskModal = document.getElementById('deleteTaskModal');
    if (deleteTaskModal) {
        const deleteTaskForm = document.getElementById('deleteTaskForm');
        const deleteTaskIdInput = document.getElementById('delete_task_id');
        const deleteButtons = document.querySelectorAll('.delete-btn');

        deleteButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                const taskId = button.getAttribute('data-task-id');
                deleteTaskIdInput.value = taskId;
            });
        });
    }

    // 4. Real-Time Form Validation
    function setupRealTimeValidation() {
        const descriptionInput = document.getElementById('description');
        const dueDateInput = document.getElementById('due_date');
        const priorityInput = document.getElementById('priority');

        if (descriptionInput) {
            descriptionInput.addEventListener('input', function() {
                if (this.value.trim() === '') {
                    this.classList.add('is-invalid');
                } else {
                    this.classList.remove('is-invalid');
                }
            });
        }

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

        if (priorityInput) {
            priorityInput.addEventListener('change', function() {
                if (this.value === '') {
                    this.classList.add('is-invalid');
                } else {
                    this.classList.remove('is-invalid');
                }
            });
        }
    }
    setupRealTimeValidation();

    // 5. Initialize Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});