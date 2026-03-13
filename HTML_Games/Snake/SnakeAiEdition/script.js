const box = 20;
let p1, p2, isPaused = false;

class SnakeInstance {
    constructor(id, containerId, canvasId) {
        this.id = id;
        this.container = document.getElementById(containerId);
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.scoreDisplay = this.container.querySelector('.score');
        this.deathUI = this.container.querySelector(this.id === 1 ? '#death1' : '#death2');
        this.loop = null;
        this.type = 'player';
        this.moveQueue = [];

        const appleSel = this.container.querySelector('.appleCount');
        appleSel.innerHTML = "";
        for (let i = 1; i <= 10; i++) {
            const opt = document.createElement('option');
            opt.value = i;
            opt.innerText = i + (i === 1 ? " Apple" : " Apples");
            if (i === 3) opt.selected = true;
            appleSel.appendChild(opt);
        }

        this.container.querySelectorAll('select').forEach(s => {
            s.addEventListener('change', () => this.init());
        });
    }

    init() {
        if (this.loop) clearInterval(this.loop);
        let size = parseInt(this.container.querySelector('.fieldSize').value);
        if ((size / box) % 2 !== 0) size += box; 

        this.canvas.width = size;
        this.canvas.height = size;
        this.score = 0;
        this.scoreDisplay.innerText = "0";
        this.isDead = false;
        this.deathUI.classList.add('hidden');
        this.direction = "UP";
        this.lastProcessedDir = "UP";
        this.moveQueue = [];

        const centerX = Math.floor(this.canvas.width / (2 * box)) * box;
        const centerY = Math.floor(this.canvas.height / (2 * box)) * box;
        this.snake = [
            {x: centerX, y: centerY}, 
            {x: centerX, y: centerY + box}, 
            {x: centerX, y: centerY + (box * 2)}
        ];

        this.apples = [];
        const count = parseInt(this.container.querySelector('.appleCount').value);
        for (let i = 0; i < count; i++) this.spawnFood();

        const speed = parseInt(this.container.querySelector('.gameSpeed').value);
        this.loop = setInterval(() => this.tick(), speed);
        this.draw();
    }

    spawnFood() {
        const cols = this.canvas.width / box;
        const rows = this.canvas.height / box;
        let newFood, collision;
        do {
            collision = false;
            newFood = { x: Math.floor(Math.random() * cols) * box, y: Math.floor(Math.random() * rows) * box };
            if (this.snake.some(p => p.x === newFood.x && p.y === newFood.y)) collision = true;
            if (this.apples.some(a => a.x === newFood.x && a.y === newFood.y)) collision = true;
        } while (collision);
        this.apples.push(newFood);
    }

    tick() {
        if (isPaused || this.isDead) return;
        if (this.type === 'ai') this.calculateAIMove();
        
        if (this.moveQueue.length > 0) {
            const next = this.moveQueue.shift();
            if (next !== getOpposite(this.lastProcessedDir)) this.direction = next;
        }

        this.lastProcessedDir = this.direction;
        let headX = this.snake[0].x;
        let headY = this.snake[0].y;

        if (this.direction === "UP") headY -= box;
        else if (this.direction === "DOWN") headY += box;
        else if (this.direction === "LEFT") headX -= box;
        else if (this.direction === "RIGHT") headX += box;

        if (headX < 0 || headX >= this.canvas.width || headY < 0 || headY >= this.canvas.height || 
            this.snake.some(p => p.x === headX && p.y === headY)) {
            this.die();
            return;
        }

        const newHead = {x: headX, y: headY};
        this.snake.unshift(newHead);

        const aIdx = this.apples.findIndex(a => a.x === headX && a.y === headY);
        if (aIdx !== -1) {
            this.score++;
            this.scoreDisplay.innerText = this.score;
            this.apples.splice(aIdx, 1);
            if (this.snake.length < (this.canvas.width * this.canvas.height) / (box * box)) {
                this.spawnFood();
            }
        } else {
            this.snake.pop();
        }
        this.draw();
    }

    calculateAIMove() {
        const head = this.snake[0];
        const diffValue = parseFloat(document.getElementById('difficulty').value);
        const x = head.x / box;
        const y = head.y / box;
        const cols = this.canvas.width / box;
        const rows = this.canvas.height / box;

        // IMPOSSIBLE MODE (Threshold 2.5 to be safe)
        if (diffValue > 2.5) {
            if (x === 0) {
                // Return path to start (Left-most column)
                this.direction = (y === 0) ? "RIGHT" : "UP";
            } else if (y === 0) {
                // Shortcut path back to Column 0 (Top-most row)
                this.direction = "LEFT";
            } else if (y === 1 && x % 2 === 0) {
                // Top boundary of lanes: turn RIGHT if in an even column
                this.direction = "RIGHT";
            } else if (y === rows - 1 && x % 2 === 1) {
                // Bottom boundary of lanes: turn RIGHT if in an odd column
                // Special safety for bottom-right corner
                this.direction = (x === cols - 1) ? "UP" : "RIGHT";
            } else {
                // Standard Lane Flow: Odd Down, Even Up
                this.direction = (x % 2 === 1) ? "DOWN" : "UP";
            }
            return;
        }

        // GREEDY LOGIC (Standard AI)
        const apple = this.apples[0];
        const moves = [{dir:"UP",x:head.x,y:head.y-box},{dir:"DOWN",x:head.x,y:head.y+box},{dir:"LEFT",x:head.x-box,y:head.y},{dir:"RIGHT",x:head.x+box,y:head.y}]
            .filter(m => m.x>=0 && m.x<this.canvas.width && m.y>=0 && m.y<this.canvas.height && !this.snake.some(s=>s.x===m.x && s.y===m.y) && m.dir !== getOpposite(this.lastProcessedDir));
        
        moves.sort((a, b) => {
            const d1 = Math.abs(a.x - apple.x) + Math.abs(a.y - apple.y);
            const d2 = Math.abs(b.x - apple.x) + Math.abs(b.y - apple.y);
            return (Math.random() < (3 - diffValue) / 3) ? Math.random() - 0.5 : d1 - d2;
        });
        if (moves[0]) this.direction = moves[0].dir;
    }

    draw() {
        this.ctx.fillStyle = "#111"; 
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // PATH OVERLAY (Brighter for visibility)
        const diffValue = parseFloat(document.getElementById('difficulty').value);
        if (diffValue > 2.5) {
            this.ctx.strokeStyle = "rgba(255, 255, 255, 0.2)";
            this.ctx.setLineDash([5, 5]); // Dashed lines for better contrast
            for(let i=0; i < this.canvas.width; i += box) {
                for(let j=0; j < this.canvas.height; j += box) {
                    this.ctx.strokeRect(i, j, box, box);
                }
            }
            this.ctx.setLineDash([]); // Reset dash
        }

        this.ctx.fillStyle = "#FF5252"; 
        this.apples.forEach(a => this.ctx.fillRect(a.x+2, a.y+2, box-4, box-4));
        this.snake.forEach((p, i) => {
            this.ctx.fillStyle = i === 0 ? (this.id === 1 ? "#4CAF50" : "#2196F3") : "#2E7D32";
            this.ctx.fillRect(p.x+1, p.y+1, box-2, box-2);
        });
    }

    die() {
        this.isDead = true; clearInterval(this.loop);
        const hi = localStorage.getItem(`snake_hi_${this.id}`) || 0;
        if (this.score > hi) localStorage.setItem(`snake_hi_${this.id}`, this.score);
        this.deathUI.querySelector('.last-score').innerText = this.score;
        this.deathUI.querySelector('.high-score').innerText = Math.max(hi, this.score);
        this.deathUI.classList.remove('hidden');
    }
}

function getOpposite(d) { return {UP:"DOWN", DOWN:"UP", LEFT:"RIGHT", RIGHT:"LEFT"}[d] || null; }

window.addEventListener('keydown', e => {
    if (p1 && p1.isDead) p1.init();
    if (p2 && p2.isDead && document.getElementById('gameMode').value !== 'single') p2.init();
    if (e.code === "Space") { isPaused = !isPaused; e.preventDefault(); return; }
    const p1Keys = {KeyW:"UP", KeyS:"DOWN", KeyA:"LEFT", KeyD:"RIGHT"};
    const p2Keys = {ArrowUp:"UP", ArrowDown:"DOWN", ArrowLeft:"LEFT", ArrowRight:"RIGHT"};
    if (p1 && p1.type === 'player' && p1Keys[e.code]) p1.moveQueue.push(p1Keys[e.code]);
    if (p2 && p2.type === 'player' && p2Keys[e.code]) p2.moveQueue.push(p2Keys[e.code]);
});

function updateUI() {
    const mode = document.getElementById('gameMode').value, matchup = document.getElementById('matchup').value;
    document.getElementById('p2-container').style.display = (mode === 'single') ? 'none' : 'flex';
    document.getElementById('ai-ui-group').style.display = (mode === 'single') ? 'none' : 'flex';
    if (!p1) p1 = new SnakeInstance(1, 'p1-container', 'can1');
    if (!p2) p2 = new SnakeInstance(2, 'p2-container', 'can2');
    p1.type = (matchup === 'ava') ? 'ai' : 'player'; p2.type = (matchup === 'pvp') ? 'player' : 'ai';
    p1.init(); if (mode !== 'single') p2.init();
}

updateUI();
