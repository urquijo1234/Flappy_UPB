const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const WIDTH = canvas.width;
const HEIGHT = canvas.height;

const bird = {
  x: 50,
  y: HEIGHT / 2,
  width: 40,
  height: 40,
  velocity: 0,
  gravity: 0.25,
  jumpStrength: -5.5
};

const pipeGap = 150;
const pipeWidth = 52;
const pipeSpacing = 300;
let lastPipeX = WIDTH;

let pipes = [];
let score = 0;
let highScore = parseInt(localStorage.getItem("flappyHighScore")) || 0;
let gameState = "menu";
let pipeSpeed = 1;
let frame = 0;

// Load assets
const bg = new Image();
bg.src = "assets/J PIXEL.jpg";

const birdImg = new Image();
birdImg.src = "assets/bird.png";

const pipeUpImg = new Image();
pipeUpImg.src = "assets/pipeup.png";

const pipeDownImg = new Image();
pipeDownImg.src = "assets/pipedown.png";

// Sounds
const pointSound = new Audio("assets/point.mp3");
const jumpSound = new Audio("assets/jump.mp3");
const deathSound = new Audio("assets/death.mp3")

function resetGame() {
  bird.y = HEIGHT / 2;
  bird.velocity = 0;
  pipes = [];
  score = 0;
  pipeSpeed = 2;
  lastPipeX = WIDTH;

  createPipe(true);

  gameState = "playing";
}

let prevBirdY = bird.y;
const responseFactor = 0.03;

function calculateSlope() {
  const deltaT = 1 / 60; 
  const deltaY = bird.y - prevBirdY;
  const m = deltaY / deltaT;
  prevBirdY = bird.y;
  return Math.abs(m);
}

function createPipe(initial = false) {
  const m = calculateSlope();
  const centerLimit = HEIGHT / 2;
  const noise = Math.random() * 100 - 50; // ±50
  let responsiveY = centerLimit - m * responseFactor + noise;

  const minGapY = 100;
  const maxGapY = HEIGHT - pipeGap - 100;
  responsiveY = Math.max(minGapY, Math.min(maxGapY, responsiveY));

  pipes.push({ x: WIDTH, gapY: responsiveY, scored: initial });
}

function drawBird() {
  ctx.drawImage(birdImg, bird.x, bird.y, bird.width, bird.height);
}

function drawPipes() {
  pipes.forEach(pipe => {
    const topHeight = pipe.gapY;
    const bottomY = pipe.gapY + pipeGap;
    const bottomHeight = HEIGHT - bottomY;

    ctx.drawImage(pipeDownImg, pipe.x, 0, pipeWidth, topHeight);

    ctx.drawImage(pipeUpImg, pipe.x, bottomY, pipeWidth, bottomHeight);
  });
}


function update() {
  if (gameState === "playing") {
    bird.velocity += bird.gravity;
    bird.y += bird.velocity;

    pipes.forEach(pipe => {
      pipe.x -= pipeSpeed;

      if (!pipe.scored && pipe.x + pipeWidth < bird.x) {
        score++;
        pointSound.play();
        pipe.scored = true;

        if (score % 5 === 0) pipeSpeed += 0.5;

        if (score > highScore) {
          highScore = score;
          localStorage.setItem("flappyHighScore", highScore);
        }
      }

      if (
        bird.x + bird.width > pipe.x && bird.x < pipe.x + pipeWidth &&
        (bird.y < pipe.gapY || bird.y + bird.height > pipe.gapY + pipeGap)
      ) {
        gameState = "game_over";
      }
    });

    if (bird.y < 0 || bird.y + bird.height > HEIGHT) {
      gameState = "game_over";
    }

    const lastPipe = pipes[pipes.length - 1];
    if (WIDTH - lastPipe.x >= pipeSpacing) {
      createPipe();
      lastPipeX = WIDTH;
    }

    pipes = pipes.filter(pipe => pipe.x > -pipeWidth);
  }
}

function draw() {
  ctx.drawImage(bg, 0, 0, WIDTH, HEIGHT);

  if (gameState === "menu") {
    ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
    ctx.fillRect(25, HEIGHT/2 - 100, WIDTH - 50, 200);
    ctx.fillStyle = "#fff";
    ctx.font = "36px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("BIENVENIDO A", WIDTH / 2, HEIGHT / 2 - 40);
    ctx.fillText("FLAPPY UPB", WIDTH / 2, HEIGHT / 2);
    ctx.font = "24px sans-serif";
    ctx.fillText("PRESIONE ENTER PARA JUGAR", WIDTH / 2, HEIGHT / 2 + 60);
    ctx.fillText(`Récord: ${highScore}`, WIDTH / 2, HEIGHT / 2 + 100);
  } else if (gameState === "playing") {
    drawPipes();
    drawBird();

    ctx.fillStyle = "#fff";
    ctx.font = "20px sans-serif";
    ctx.fillText(`Puntuación: ${score}`, 70, 30);
    ctx.fillText(`Récord: ${highScore}`, 50, 60);
  } else if (gameState === "game_over") {
    drawPipes();
    drawBird();
    ctx.fillStyle = "rgba(0,0,0,0.5)";
    ctx.fillRect(25, HEIGHT/2 - 75, 350, 150);
    ctx.fillStyle = "#fff";
    ctx.font = "30px sans-serif";
    ctx.fillText("Game Over!", WIDTH / 2, HEIGHT / 2 - 30);
    ctx.fillText(`Puntuación: ${score}`, WIDTH / 2, HEIGHT / 2);
    ctx.fillText(`Récord: ${highScore}`, WIDTH / 2, HEIGHT / 2 + 30);
    ctx.font = "20px sans-serif";
    ctx.fillText("Presione R para reiniciar", WIDTH / 2, HEIGHT / 2 + 70);
  }
}

function gameLoop() {
  update();
  draw();
  requestAnimationFrame(gameLoop);
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && gameState === "menu") {
    resetGame();
  } else if (e.key === " " && gameState === "playing") {
    bird.velocity = bird.jumpStrength;
    jumpSound.play();
  } else if (e.key === "r" && gameState === "game_over") {
    deathSound.play
    resetGame();
  }
});

gameLoop();
