const bpmnViewer = new BpmnJS({
    container: '#canvas'
});

// 获取URL参数中的流程ID
const urlParams = new URLSearchParams(window.location.search);
const processId = urlParams.get('id');

// 加载流程图
async function loadDiagram(processId) {
    try {
        const processData = JSON.parse(localStorage.getItem(processId));
        if (processData && processData.xml) {
            await bpmnViewer.importXML(processData.xml);
            const canvas = bpmnViewer.get('canvas');
            
            // 先设置视图缩放以适应视口
            canvas.zoom('fit-viewport');
            
            // 获取当前视图框
            const viewbox = canvas.viewbox();
            
            // 添加边距
            canvas.viewbox({
                x: viewbox.x - 30,      // 左边距设为 30
                y: viewbox.y - 50,      // 上边距保持 50
                width: viewbox.width,
                height: viewbox.height + 35
            });
        } else {
            alert('流程不存在');
            window.location.href = '/flow/';
        }
    } catch (err) {
        console.error('加载流程图失败', err);
    }
}

// 加载流程图
if (processId) {
    loadDiagram(processId);
} else {
    window.location.href = '/flow/';
}

// 导出 BPMN 文件
document.getElementById('exportBtn').addEventListener('click', async () => {
    try {
        const { xml } = await bpmnViewer.saveXML({ format: true });
        const blob = new Blob([xml], { type: 'application/xml' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `process_${Date.now()}.xml`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (err) {
        console.error('导出失败', err);
        alert('导出失败');
    }
});

// 导出 SVG 图片
document.getElementById('exportSvgBtn').addEventListener('click', async () => {
    try {
        const { svg } = await bpmnViewer.saveSVG();
        const blob = new Blob([svg], { type: 'image/svg+xml' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `process_${Date.now()}.svg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (err) {
        console.error('导出SVG失败', err);
        alert('导出SVG失败');
    }
});