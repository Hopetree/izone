// 加载流程列表
// 添加搜索功能
let allProcesses = [];  // 保存所有流程数据

async function loadProcessList() {
    const processList = document.getElementById('processList');
    processList.innerHTML = '';

    try {
        // 获取所有流程数据并保存
        allProcesses = await window.storage.getProcessList();
        
        // 按创建时间倒序排序
        allProcesses.sort((a, b) => b.createTime - a.createTime);
        
        // 渲染流程列表
        renderProcessList(allProcesses);
    } catch (err) {
        console.error('加载流程列表失败:', err);
    }
}

// 渲染流程列表
function renderProcessList(processes) {
    const processList = document.getElementById('processList');
    processList.innerHTML = '';

    processes.forEach(process => {
        if (!process || !process.id) return;
        
        const createTime = new Date(process.createTime)
            .toLocaleString('zh-CN', { 
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        
        const div = document.createElement('div');
        div.className = 'process-item';
        div.innerHTML = `
            <div class="process-info">
                <div class="process-name">
                    <span class="name-text" 
                        onclick="renameProcess('${process.id}', '${process.name || ''}')"
                    >${process.name || '未命名流程'}</span>
                    <span class="create-time">创建于 ${createTime}</span>
                </div>
                <div class="process-tags">
                    ${(process.tags || []).map(tag => `
                        <span class="tag">
                            <span class="tag-text">${tag}</span>
                            <span class="tag-delete" onclick="deleteTag('${process.id}', '${tag}')">×</span>
                        </span>
                    `).join('')}
                    <button class="add-tag-btn" onclick="addTag('${process.id}')">+</button>
                </div>
            </div>
            <div class="process-actions">
                <a href="view?id=${process.id}" class="btn btn-view">查看</a>
                <a href="edit?id=${process.id}" class="btn btn-edit">编辑</a>
                <button onclick="deleteProcess('${process.id}')" class="btn btn-danger">删除</button>
            </div>
        `;
        processList.appendChild(div);
    });
}

// 搜索功能
function searchProcesses(keyword) {
    if (!keyword) {
        renderProcessList(allProcesses);
        return;
    }

    keyword = keyword.toLowerCase();
    const filtered = allProcesses.filter(process => {
        // 搜索名称
        if (process.name && process.name.toLowerCase().includes(keyword)) {
            return true;
        }
        // 搜索标签
        if (process.tags && Array.isArray(process.tags)) {
            return process.tags.some(tag => 
                tag.toLowerCase().includes(keyword)
            );
        }
        return false;
    });

    renderProcessList(filtered);
}

// 添加搜索输入监听
document.getElementById('searchInput').addEventListener('input', (e) => {
    searchProcesses(e.target.value.trim());
});

// 删除流程
async function deleteProcess(processId) {
    if (confirm('确定要删除该流程吗？')) {
        try {
            await window.storage.deleteProcess(processId);
            loadProcessList();
        } catch (err) {
            console.error('删除失败:', err);
            alert('删除失败');
        }
    }
}

// 重命名流程
async function renameProcess(processId, oldName) {
    const newName = prompt('请输入新的流程名称：', oldName);
    if (!newName || newName === oldName) return;

    try {
        const processData = await window.storage.getProcess(processId);
        processData.name = newName;
        await window.storage.updateProcess(processId, processData);
        loadProcessList();
    } catch (err) {
        console.error('重命名失败:', err);
        alert('重命名失败');
    }
}

// 添加标签
async function addTag(processId) {
    const tag = prompt('请输入标签名称：');
    if (!tag) return;

    try {
        const processData = await window.storage.getProcess(processId);
        processData.tags = processData.tags || [];
        if (!processData.tags.includes(tag)) {
            processData.tags.push(tag);
            await window.storage.updateProcess(processId, processData);
            loadProcessList();
        } else {
            alert('标签已存在');
        }
    } catch (err) {
        console.error('添加标签失败:', err);
        alert('添加标签失败');
    }
}

// 删除标签
async function deleteTag(processId, tag) {
    if (!confirm(`确定要删除标签"${tag}"吗？`)) return;

    try {
        const processData = await window.storage.getProcess(processId);
        const tagIndex = processData.tags.indexOf(tag);
        if (tagIndex !== -1) {
            processData.tags.splice(tagIndex, 1);
            await window.storage.updateProcess(processId, processData);
            loadProcessList();
        }
    } catch (err) {
        console.error('删除标签失败:', err);
        alert('删除标签失败');
    }
}

// 页面加载完成后加载流程列表
document.addEventListener('DOMContentLoaded', loadProcessList);