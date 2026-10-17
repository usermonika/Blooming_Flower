console.log("✅ toast-message.js loaded");

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('subscribe-form');
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const email = document.getElementById('subscribe-email').value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/subscribe/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams({ email: email })
        })
        .then(res => res.json())
        .then(data => {
            showToast(data.message, data.status);
            if (data.status === 'success') {
                form.reset();
            }
        })
        .catch(err => {
            showToast("Something went wrong!", "error");
        });
    });
});

function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    const container = document.getElementById('toast-container');
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}
