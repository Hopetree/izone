const bpmnModeler = new BpmnJS({
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
            await bpmnModeler.importXML(processData.xml);
        } else {
            alert('流程不存在');
            window.location.href = '/flow/';
        }
    } catch (err) {
        console.error('加载流程图失败', err);
    }
}

// 保存流程图
document.getElementById('saveBtn').addEventListener('click', async () => {
    try {
        const { xml } = await bpmnModeler.saveXML({ format: true });
        const processData = JSON.parse(localStorage.getItem(processId));
        processData.xml = xml;
        localStorage.setItem(processId, JSON.stringify(processData));
        alert('保存成功');
        window.location.href = '/flow/';
    } catch (err) {
        console.error('保存失败', err);
        alert('保存失败');
    }
});

// 导入功能
document.getElementById('importBtn').addEventListener('click', () => {
    document.getElementById('importFile').click();
});

document.getElementById('importFile').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
        const reader = new FileReader();
        reader.onload = async (e) => {
            const xml = e.target.result;
            await bpmnModeler.importXML(xml);
        };
        reader.readAsText(file);
    } catch (err) {
        console.error('导入失败', err);
        alert('导入失败');
    }
});

// 加载流程图
if (processId) {
    loadDiagram(processId);
} else {
    window.location.href = '/flow/';
}

// 导出 BPMN 文件
document.getElementById('exportBtn').addEventListener('click', async () => {
    try {
        const { xml } = await bpmnModeler.saveXML({ format: true });
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
        const { svg } = await bpmnModeler.saveSVG();
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