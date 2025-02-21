// 初始化 BPMN Modeler
const bpmnModeler = new BpmnJS({
    container: '#canvas'
});

// 创建新的空白流程图
async function createNewDiagram() {
    try {
        await bpmnModeler.createDiagram();
    } catch (err) {
        console.error('创建流程图失败', err);
    }
}

// 保存流程图
document.getElementById('saveBtn').addEventListener('click', async () => {
    try {
        const processName = prompt('请输入流程名称：');
        if (!processName) return;  // 如果用户取消或未输入，则不保存

        const { xml } = await bpmnModeler.saveXML({ format: true });
        const processId = 'bpmn_' + Date.now();
        const processData = {
            xml: xml,
            name: processName,
            createTime: Date.now()
        };
        localStorage.setItem(processId, JSON.stringify(processData));
        alert('保存成功');
        window.location.href = '/flow/';
    } catch (err) {
        console.error('保存失败', err);
        alert('保存失败');
    }
});

// 页面加载完成后创建新的流程图
createNewDiagram();

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