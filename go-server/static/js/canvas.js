// 最简 Vanilla JS，用于读取数据并在 Canvas 上画线
window.drawASTGraph = function() {
    const container = document.getElementById('ast-canvas-container');
    const canvas = document.getElementById('astCanvas');
    if (!container || !canvas) return;

    // 确保 Canvas 尺寸正确
    const rect = container.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 获取注入的 JSON 数据
    let graphData;
    try {
        graphData = JSON.parse(container.getAttribute('data-graph') || '{}');
    } catch (e) {
        console.error("Failed to parse graph data", e);
        return;
    }

    if (!graphData.nodes || !graphData.edges) {
        // 画个简单的占位提示
        ctx.fillStyle = '#9ca3af';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('选择器渲染就绪，等待后端返回拓扑坐标...', canvas.width / 2, canvas.height / 2);
        return;
    }

    // 设置线条样式
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth = 2;

    // 绘制边缘
    graphData.edges.forEach(edge => {
        const source = graphData.nodes.find(n => n.id === edge.source);
        const target = graphData.nodes.find(n => n.id === edge.target);
        
        if (source && target) {
            ctx.beginPath();
            ctx.moveTo(source.x, source.y);
            // 可以加些贝塞尔曲线逻辑使连线更柔和，这里为了最简直接直线
            ctx.lineTo(target.x, target.y);
            ctx.stroke();
        }
    });

    // 可以在这里通过 Canvas 绘制节点，或者留给 HTML 绝对定位渲染
    // 如果用 Canvas 画：
    graphData.nodes.forEach(node => {
        ctx.beginPath();
        ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI, false);
        ctx.fillStyle = node.color || '#4f46e5';
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        ctx.fillStyle = '#4b5563';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(node.label || '', node.x, node.y + 18);
    });
};

// 页面加载完成后尝试绘制一次
document.addEventListener('DOMContentLoaded', window.drawASTGraph);
// 监听 htmx 交换事件后重新绘制
document.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === 'analysis-container') {
        window.drawASTGraph();
    }
});
