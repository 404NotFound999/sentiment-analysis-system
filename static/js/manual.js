function submitManual(isNext) {
    const title = document.getElementById("titleInput").value;
    const content = document.getElementById("contentInput").value;
    const msg = document.getElementById("manualMsg");

    if (!content.trim()) {
        msg.innerText = "⚠ 正文内容不能为空";
        msg.style.color = "#ff9b9b";
        return;
    }

    fetch("/manual/submit", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            title: title,
            content: content
        })
    })
    .then(res => res.json())
    .then(data => {

        if (data.msg !== "ok") {
            msg.innerText = "❌ 提交失败";
            msg.style.color = "#ff9b9b";
            return;
        }

        if (isNext) {
            // ➕ 下一条：入库 + 清空
            msg.innerText = "✅ 已保存，继续输入下一条";
            msg.style.color = "#9cffc7";

            document.getElementById("titleInput").value = "";
            document.getElementById("contentInput").value = "";
        } else {

            window.location.href = "/analysis";

        }

    })
    .catch(err => {
        msg.innerText = "❌ 提交失败，请检查后端";
        msg.style.color = "#ff9b9b";
        console.error(err);
    });
}



function nextOne() {
    document.getElementById("titleInput").value = "";
    document.getElementById("contentInput").value = "";
    document.getElementById("manualMsg").innerText = "";
}
