let toastTimer;
let toastHideTimer;

function showToast(title, message, type = "normal", duration = 3000) {
  const toastComponent = document.getElementById("toast-component");
  const toastTitle = document.getElementById("toast-title");
  const toastMessage = document.getElementById("toast-message");

  if (!toastComponent || !toastTitle || !toastMessage) return;

  toastComponent.classList.remove(
    "toast-success",
    "toast-error",
    "toast-normal",
  );
  const toastType = ["success", "error"].includes(type) ? type : "normal";
  toastComponent.classList.add(`toast-${toastType}`);

  toastTitle.textContent = title;
  toastMessage.textContent = message;

  clearTimeout(toastTimer);
  clearTimeout(toastHideTimer);

  if (!toastComponent.matches(":popover-open")) {
    toastComponent.showPopover();
    void toastComponent.offsetHeight;
  }
  toastComponent.classList.remove("toast-hidden");
  toastComponent.classList.add("toast-show");

  toastTimer = setTimeout(() => {
    toastComponent.classList.remove("toast-show");
    toastComponent.classList.add("toast-hidden");
    toastHideTimer = setTimeout(() => toastComponent.hidePopover(), 300);
  }, Math.max(0, duration));
}

window.showToast = showToast;
