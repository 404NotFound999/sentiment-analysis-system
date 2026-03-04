let hasJumped = false;  // 防止重复跳转

// 开始爬虫
function startCrawl() {
    const keyword = document.getElementById("keywordInput").value;

    fetch("/start_crawl", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keyword: keyword })
    });

    // 跳转到爬虫日志页
    window.location.href = "/crawl";
}

// 轮询爬虫日志
function loadLogs() {
    const box = document.getElementById("logBox");

    // 如果页面没有 logBox，直接返回
    if (!box) return;

    fetch("/get_progress")
        .then(res => res.json())
        .then(data => {
            box.innerHTML = "";

            // 显示日志
            data.reverse().forEach(item => {
                if (item.message) {
                    const p = document.createElement("p");
                    p.innerText = item.message;
                    box.appendChild(p);
                }
            });

            box.scrollTop = box.scrollHeight;

            // ⭐ 判断爬虫是否完成（根据最后一条日志）

            if (!hasJumped && data.some(item => item.message?.includes("爬虫任务完成"))) {
                hasJumped = true;

                // 自动调用分析接口，然后跳转 dashboard
                fetch("/analysis/run")
                    .then(() => {
                        window.location.href = "/analysis";
                    })
                    .catch(err => {
                        console.error("分析失败：", err);
                        alert("自动分析失败，请刷新页面手动查看");
                    });
            }
        })
        .catch(err => {
            console.error("获取日志失败：", err);
        });
}

// ⭐ 每秒轮询一次
setInterval(loadLogs, 1000);