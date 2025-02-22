// 获取 CSRF Token
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// API 请求封装
const api = {
    // 获取流程列表
    async getProcessList() {
        const response = await fetch('/flow/api/processes/');
        if (!response.ok) throw new Error('获取流程列表失败');
        return await response.json();
    },

    // 获取单个流程
    async getProcess(processId) {
        const response = await fetch(`/flow/api/processes/${processId}/`);
        if (!response.ok) throw new Error('获取流程详情失败');
        return await response.json();
    },

    // 创建流程
    async createProcess(processData) {
        const response = await fetch('/flow/api/processes/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(processData)
        });
        if (!response.ok) throw new Error('创建流程失败');
        return await response.json();
    },

    // 更新流程
    async updateProcess(processId, processData) {
        const response = await fetch(`/flow/api/processes/${processId}/update/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(processData)
        });
        if (!response.ok) throw new Error('更新流程失败');
        return await response.json();
    },

    // 删除流程
    async deleteProcess(processId) {
        const response = await fetch(`/flow/api/processes/${processId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        });
        if (!response.ok) throw new Error('删除流程失败');
        return await response.json();
    }
};