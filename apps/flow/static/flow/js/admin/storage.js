// 管理员数据存储接口
const adminStorage = {
    async getProcessList() {
        const result = await api.getProcessList();
        return result.processes;
    },

    async getProcess(processId) {
        return await api.getProcess(processId);
    },

    async saveProcess(processData) {
        return await api.createProcess(processData);
    },

    async updateProcess(processId, processData) {
        return await api.updateProcess(processId, processData);
    },

    async deleteProcess(processId) {
        return await api.deleteProcess(processId);
    }
};

// localStorage 存储接口
const localStorageImpl = {
    getProcessList() {
        const processes = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.startsWith('bpmn_')) {
                try {
                    const processData = JSON.parse(localStorage.getItem(key));
                    processes.push({
                        id: key,
                        ...processData
                    });
                } catch (err) {
                    console.error('加载流程数据失败:', err);
                }
            }
        }
        return processes;
    },

    getProcess(processId) {
        return JSON.parse(localStorage.getItem(processId));
    },

    saveProcess(processData) {
        const processId = 'bpmn_' + Date.now();
        localStorage.setItem(processId, JSON.stringify(processData));
        return { id: processId, ...processData };
    },

    updateProcess(processId, processData) {
        localStorage.setItem(processId, JSON.stringify(processData));
        return { id: processId, ...processData };
    },

    deleteProcess(processId) {
        localStorage.removeItem(processId);
    }
};

// 根据角色选择存储实现
window.storage = window.isAdmin ? adminStorage : localStorageImpl;