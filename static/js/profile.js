// Enhanced Profile Page JavaScript
document.addEventListener('DOMContentLoaded', function () {

    // Profile Form Handling
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;

            // Show loading state
            submitBtn.innerHTML = '<i class="zmdi zmdi-refresh zmdi-hc-spin"></i> Updating...';
            submitBtn.disabled = true;

            const formData = new FormData(this);

            fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
                .then(response => {
                    if (response.ok) {
                        // Django returns HTML on success, so we don't parse as JSON
                        showNotification('Profile updated successfully!', 'success');

                        // Close modal and refresh page after a short delay
                        setTimeout(() => {
                            const modal = bootstrap.Modal.getInstance(document.getElementById('editProfileModal'));
                            if (modal) {
                                modal.hide();
                            }
                            location.reload();
                        }, 1500);
                    } else {
                        throw new Error('Network response was not ok');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Error updating profile. Please try again.', 'error');
                })
                .finally(() => {
                    // Restore button state
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                });
        });
    }

    // Profile Image Click Handler
    const profileImageContainer = document.querySelector('.profile-image-container');
    if (profileImageContainer) {
        profileImageContainer.addEventListener('click', function () {
            const editModal = new bootstrap.Modal(document.getElementById('editProfileModal'));
            editModal.show();
        });
    }

    // Tab Switching with URL Hash (without auto-scroll)
    const tabTriggers = document.querySelectorAll('#profileTabs button[data-bs-toggle="pill"]');
    tabTriggers.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function (e) {
            const targetId = e.target.getAttribute('data-bs-target').substring(1);
            // Use replaceState instead of changing hash to prevent scrolling
            window.history.replaceState(null, null, '#' + targetId);
        });

        // Prevent default hash behavior on tab click
        tab.addEventListener('click', function (e) {
            e.preventDefault();
            // Store current scroll position
            const scrollPosition = window.pageYOffset || document.documentElement.scrollTop;

            // Activate the tab
            const tabInstance = new bootstrap.Tab(this);
            tabInstance.show();

            // Restore scroll position after a brief delay
            setTimeout(() => {
                window.scrollTo(0, scrollPosition);
            }, 10);
        });
    });

    // Show tab based on URL hash (without scrolling)
    if (window.location.hash) {
        const currentScrollPosition = window.pageYOffset || document.documentElement.scrollTop;
        const tabToShow = document.querySelector(`#profileTabs button[data-bs-target="${window.location.hash}"]`);
        if (tabToShow) {
            const tab = new bootstrap.Tab(tabToShow);
            tab.show();
            // Restore scroll position
            setTimeout(() => {
                window.scrollTo(0, currentScrollPosition);
            }, 10);
        }
    }

    // Image Preview for Profile Image Upload
    const profileImageInput = document.getElementById('profile_image');
    if (profileImageInput) {
        profileImageInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file size (5MB limit)
                if (file.size > 5 * 1024 * 1024) {
                    showNotification('Image file too large. Please keep it under 5MB.', 'error');
                    this.value = '';
                    return;
                }

                // Validate file type
                const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                if (!validTypes.includes(file.type)) {
                    showNotification('Invalid image format. Please use PNG, JPG, JPEG, or GIF.', 'error');
                    this.value = '';
                    return;
                }

                // Create preview
                const reader = new FileReader();
                reader.onload = function (e) {
                    // Update current image preview if it exists
                    const currentImage = document.querySelector('.current-image img');
                    if (currentImage) {
                        currentImage.src = e.target.result;
                    } else {
                        // Create new preview
                        const previewDiv = document.createElement('div');
                        previewDiv.className = 'image-preview mt-2';
                        previewDiv.innerHTML = `
                            <img src="${e.target.result}" alt="Preview" style="width: 60px; height: 60px; object-fit: cover; border-radius: 50%;">
                            <span class="ms-2 text-muted">New image preview</span>
                        `;
                        profileImageInput.parentNode.appendChild(previewDiv);
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Enhanced Settings Modal
    const settingsModal = document.getElementById('settingsModal');
    if (settingsModal) {
        // Email notifications toggle
        const emailNotificationsToggle = document.getElementById('emailNotifications');
        if (emailNotificationsToggle) {
            emailNotificationsToggle.addEventListener('change', function () {
                const status = this.checked ? 'enabled' : 'disabled';
                showNotification(`Email notifications ${status}`, 'info');

                // Here you would typically make an AJAX call to save the preference
                // saveNotificationPreference('email', this.checked);
            });
        }
    }

    // Smooth scroll for internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading states to action buttons
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            if (this.href && !this.href.includes('#')) {
                const originalContent = this.innerHTML;
                this.innerHTML = '<i class="zmdi zmdi-refresh zmdi-hc-spin"></i> Loading...';

                // Restore content if page doesn't change (for debugging)
                setTimeout(() => {
                    this.innerHTML = originalContent;
                }, 3000);
            }
        });
    });

    // Enhanced notification system
    function showNotification(message, type = 'info', duration = 4000) {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.profile-notification');
        existingNotifications.forEach(notification => notification.remove());

        const notification = document.createElement('div');
        notification.className = `profile-notification profile-notification-${type}`;

        const icons = {
            success: 'zmdi-check-circle',
            error: 'zmdi-alert-circle',
            warning: 'zmdi-alert-triangle',
            info: 'zmdi-info'
        };

        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };

        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${colors[type]};
            color: ${type === 'warning' ? '#212529' : 'white'};
            padding: 15px 25px;
            border-radius: 10px;
            z-index: 9999;
            font-weight: 600;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            transform: translateX(400px);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 10px;
            max-width: 400px;
            backdrop-filter: blur(10px);
        `;

        notification.innerHTML = `
            <i class="zmdi ${icons[type]}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()" style="background: none; border: none; color: inherit; margin-left: 10px; cursor: pointer; font-size: 18px;">
                <i class="zmdi zmdi-close"></i>
            </button>
        `;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Auto remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.transform = 'translateX(400px)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        }, duration);
    }

    // Handle page visibility for real-time updates
    document.addEventListener('visibilitychange', function () {
        if (!document.hidden) {
            // Page became visible, you could refresh data here
            // refreshUserStats();
        }
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function (e) {
        // Ctrl/Cmd + E to edit profile
        if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
            e.preventDefault();
            const editModal = new bootstrap.Modal(document.getElementById('editProfileModal'));
            editModal.show();
        }

        // Ctrl/Cmd + S to save profile (when modal is open)
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            const editModal = document.getElementById('editProfileModal');
            if (editModal.classList.contains('show')) {
                e.preventDefault();
                const form = editModal.querySelector('form');
                if (form) {
                    form.dispatchEvent(new Event('submit', { bubbles: true }));
                }
            }
        }
    });

    // Add tooltip functionality for better UX
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enhanced form validation
    function validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });

        // Email validation
        const emailField = form.querySelector('input[type="email"]');
        if (emailField && emailField.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(emailField.value)) {
                emailField.classList.add('is-invalid');
                isValid = false;
            } else {
                emailField.classList.remove('is-invalid');
            }
        }

        return isValid;
    }

    // Add real-time form validation
    const formInputs = document.querySelectorAll('#profileForm input, #profileForm textarea');
    formInputs.forEach(input => {
        input.addEventListener('blur', function () {
            if (this.hasAttribute('required') && !this.value.trim()) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });

        input.addEventListener('input', function () {
            if (this.classList.contains('is-invalid') && this.value.trim()) {
                this.classList.remove('is-invalid');
            }
        });
    });

    console.log('Profile page JavaScript loaded successfully');
});

// Additional utility functions
function refreshUserStats() {
    // This would typically make an AJAX call to get updated user statistics
    console.log('Refreshing user statistics...');
}

function saveNotificationPreference(type, enabled) {
    // This would typically make an AJAX call to save the notification preference
    console.log(`Saving notification preference: ${type} = ${enabled}`);
}
