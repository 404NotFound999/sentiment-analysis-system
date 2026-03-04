function startCrawl() {
    const keyword = document.getElementById("keywordInput").value;

    fetch("/start_crawl", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keyword: keyword })
    });

    window.location.href = "/crawl";
}

function loadLogs() {
    const box = document.getElementById("logBox");

    // ⭐ 关键：如果页面没有 logBox，直接返回
    if (!box) return;

    fetch("/get_progress")
        .then(res => res.json())
        .then(data => {
            box.innerHTML = "";
            data.reverse().forEach(item => {
                if (item.message) {
                    const p = document.createElement("p");
                    p.innerText = item.message;
                    box.appendChild(p);
                }
            });
            box.scrollTop = box.scrollHeight;
            if (data.done && !hasJumped) {
                hasJumped = true;

                // ⭐ 跳转到分析页
               window.location.href = "/analysis";

            }
        });
}

// ⭐ 只有 crawling 页面才会真正执行
setInterval(loadLogs, 1000);
