const canvas = document.getElementById("bgCanvas");
const ctx = canvas.getContext("2d");

let width, height;
let points = [];

function resize() {
    // 关键：给全局变量 width 和 height 赋值
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
    initPoints(); // 缩放时重新生成点，防止点卡在屏幕外
}

function initPoints() {
    points = [];
    for (let i = 0; i < 80; i++) {
        points.push({
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5
        });
    }
}

function draw() {
    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < points.length; i++) {
        let p = points[i];
        p.x += p.vx;
        p.y += p.vy;

        // 边界回弹
        if (p.x < 0 || p.x > width) p.vx *= -1;
        if (p.y < 0 || p.y > height) p.vy *= -1;

        // 绘制点
        ctx.beginPath();
        ctx.arc(p.x, p.y, 1.5, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(180,180,255,0.7)";
        ctx.fill();

        // 连线
        for (let j = i + 1; j < points.length; j++) {
            let p2 = points[j];
            let dx = p.x - p2.x;
            let dy = p.y - p2.y;
            let dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < 120) {
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.strokeStyle = `rgba(130, 100, 255, ${1 - dist / 120})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
            }
        }
    }
    requestAnimationFrame(draw);
}

// 启动
window.addEventListener("resize", resize);
resize();
draw();
