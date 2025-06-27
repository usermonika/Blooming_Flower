function showToast(message, type = 'info') {
  const container = document.getElementById("toast-container");

  const toast = document.createElement("div");
  toast.classList.add("toast", type);
  toast.innerText = message;

  container.appendChild(toast);

  // Remove after 5 seconds
  setTimeout(() => {
    toast.remove();
  }, 5000);
}
