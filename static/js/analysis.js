const pieChart = echarts.init(document.getElementById("pieChart"));

pieChart.setOption({
    title: {
        text: '情感分布',
        left: 'center'
    },
    tooltip: {
        trigger: 'item'
    },
    series: [{
        type: 'pie',
        radius: '60%',
        data: sentimentStats.map(item => ({
            name: item.label_name,
            value: item.count
        })),
        emphasis: {
            itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0
            }
        }
    }]
});
const barChart = echarts.init(document.getElementById("barChart"));

barChart.setOption({
    title: {
        text: '关键词权重 Top10'
    },
    tooltip: {},
    xAxis: {
        type: 'category',
        data: keywords.map(k => k.keyword),
        axisLabel: { rotate: 30 }
    },
    yAxis: {
        type: 'value'
    },
    series: [{
        type: 'bar',
        data: keywords.map(k => k.weight)
    }]
});
