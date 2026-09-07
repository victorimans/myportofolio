// Falling sakura petals
const sakuraLayer = document.getElementById("sakura-layer");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const petalCount = window.innerWidth < 768 ? 18 : 34;
const petals = ["✿", "❀"];

if (sakuraLayer && !reduceMotion) {
  for (let i = 0; i < petalCount; i++) {
    const petal = document.createElement("span");
    petal.className = "sakura-petal";
    petal.textContent = petals[Math.floor(Math.random() * petals.length)];

    petal.style.left = `${Math.random() * 100}vw`;
    petal.style.fontSize = `${8 + Math.random() * 10}px`;
    petal.style.animationDuration = `${10 + Math.random() * 14}s`;
    petal.style.animationDelay = `${-Math.random() * 20}s`;
    petal.style.opacity = `${0.32 + Math.random() * 0.46}`;

    sakuraLayer.appendChild(petal);
  }
}

const copyEmailButton = document.querySelector("[data-copy-email]");

if (copyEmailButton) {
  copyEmailButton.addEventListener("click", async () => {
    const email = copyEmailButton.dataset.copyEmail;
    const status = document.querySelector(".copy-status");

    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(email);
      } else {
        const input = document.createElement("textarea");
        input.value = email;
        document.body.append(input);
        input.select();
        const copied = document.execCommand("copy");
        input.remove();
        if (!copied) throw new Error("Copy failed");
      }
      copyEmailButton.textContent = "Copied";
      status.textContent = "Email address copied to clipboard.";
      window.setTimeout(() => {
        copyEmailButton.textContent = "Copy email";
        status.textContent = "";
      }, 2000);
    } catch {
      status.textContent = "Unable to copy. Please select the email address above.";
    }
  });
}


