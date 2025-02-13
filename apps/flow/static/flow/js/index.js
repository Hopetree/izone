// 加载流程列表
function loadProcessList() {
    const processList = document.getElementById('processList');
    processList.innerHTML = '';

    // 获取所有流程并转换为数组以便排序
    const processes = [];
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key.startsWith('bpmn_')) {
            try {
                const processData = JSON.parse(localStorage.getItem(key));
                processes.push({
                    id: key,
                    data: processData,
                    createTime: processData.createTime || parseInt(key.replace('bpmn_', ''))
                });
            } catch (err) {
                console.error('加载流程数据失败:', err);
            }
        }
    }

    // 按创建时间倒序排序
    processes.sort((a, b) => b.createTime - a.createTime);

    // 渲染流程列表
    processes.forEach(process => {
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
                        onclick="renameProcess('${process.id}', '${process.data.name || ''}')"
                    >${process.data.name || '未命名流程'}</span>
                    <span class="create-time">创建于 ${createTime}</span>
                </div>
                <div class="process-tags">
                    ${(process.data.tags || []).map(tag => `
                        <span class="tag">
                            <span class="tag-text">${tag}</span>
                            <span class="tag-delete" onclick="deleteTag('${process.id}', '${tag}')">×</span>
                        </span>
                    `).join('')}
                    <button class="add-tag-btn" onclick="addTag('${process.id}')">+</button>
                </div>
            </div>
            <div class="process-actions">
                <a href="view/?id=${process.id}" class="btn btn-view">查看</a>
                <a href="edit/?id=${process.id}" class="btn btn-edit">编辑</a>
                <button onclick="deleteProcess('${process.id}')" class="btn btn-danger">删除</button>
            </div>
        `;
        processList.appendChild(div);
    });
}

// 添加标签
function addTag(processId) {
    const tag = prompt('请输入标签名称：');
    if (!tag) return;

    const processData = JSON.parse(localStorage.getItem(processId));
    processData.tags = processData.tags || [];
    if (!processData.tags.includes(tag)) {
        processData.tags.push(tag);
        localStorage.setItem(processId, JSON.stringify(processData));
        loadProcessList();
    } else {
        alert('标签已存在');
    }
}

// 编辑标签
function editTag(processId, oldTag) {
    const newTag = prompt('请输入新的标签名称：', oldTag);
    if (!newTag || newTag === oldTag) return;

    const processData = JSON.parse(localStorage.getItem(processId));
    const tagIndex = processData.tags.indexOf(oldTag);
    if (tagIndex !== -1) {
        if (processData.tags.includes(newTag)) {
            alert('标签已存在');
            return;
        }
        processData.tags[tagIndex] = newTag;
        localStorage.setItem(processId, JSON.stringify(processData));
        loadProcessList();
    }
}

// 删除标签
function deleteTag(processId, tag) {
    if (!confirm(`确定要删除标签"${tag}"吗？`)) return;

    const processData = JSON.parse(localStorage.getItem(processId));
    const tagIndex = processData.tags.indexOf(tag);
    if (tagIndex !== -1) {
        processData.tags.splice(tagIndex, 1);
        localStorage.setItem(processId, JSON.stringify(processData));
        loadProcessList();
    }
}

// 删除流程
function deleteProcess(processId) {
    if (confirm('确定要删除该流程吗？')) {
        localStorage.removeItem(processId);
        loadProcessList();
    }
}

// 页面加载完成后加载流程列表
document.addEventListener('DOMContentLoaded', loadProcessList);

// 添加重命名流程函数
function renameProcess(processId, oldName) {
    const newName = prompt('请输入新的流程名称：', oldName);
    if (!newName || newName === oldName) return;

    try {
        const processData = JSON.parse(localStorage.getItem(processId));
        processData.name = newName;
        localStorage.setItem(processId, JSON.stringify(processData));
        loadProcessList();
    } catch (err) {
        console.error('重命名失败', err);
        alert('重命名失败');
    }
}