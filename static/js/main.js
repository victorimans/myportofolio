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


