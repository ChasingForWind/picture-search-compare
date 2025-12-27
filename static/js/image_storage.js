// 浏览器端图片存储管理（使用 IndexedDB）
// 图片存储在浏览器中，不占用服务器资源

const DB_NAME = 'pictureSearchDB';
const DB_VERSION = 1;
const STORE_NAME = 'images';

class ImageStorage {
    constructor() {
        this.db = null;
    }

    // 初始化数据库
    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onerror = () => {
                console.error('IndexedDB 初始化失败');
                reject(request.error);
            };

            request.onsuccess = () => {
                this.db = request.result;
                resolve();
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // 创建对象存储
                if (!db.objectStoreNames.contains(STORE_NAME)) {
                    const objectStore = db.createObjectStore(STORE_NAME, { keyPath: 'id' });
                    objectStore.createIndex('timestamp', 'timestamp', { unique: false });
                }
            };
        });
    }

    // 将文件转换为 base64
    async fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    // 保存图片对
    async saveImagePair(image1File, image2File, description = '') {
        if (!this.db) {
            await this.init();
        }

        const id = 'pair_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const timestamp = Date.now();

        // 转换为 base64
        const [image1Data, image2Data] = await Promise.all([
            this.fileToBase64(image1File),
            this.fileToBase64(image2File)
        ]);

        const imagePair = {
            id: id,
            timestamp: timestamp,
            description: description,
            image1: image1Data,
            image2: image2Data,
            image1Name: image1File.name,
            image2Name: image2File.name
        };

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readwrite');
            const objectStore = transaction.objectStore(STORE_NAME);
            const request = objectStore.add(imagePair);

            request.onsuccess = () => resolve(id);
            request.onerror = () => reject(request.error);
        });
    }

    // 获取图片对
    async getImagePair(id) {
        if (!this.db) {
            await this.init();
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readonly');
            const objectStore = transaction.objectStore(STORE_NAME);
            const request = objectStore.get(id);

            request.onsuccess = () => {
                if (request.result) {
                    resolve(request.result);
                } else {
                    reject(new Error('图片对不存在'));
                }
            };

            request.onerror = () => reject(request.error);
        });
    }

    // 获取所有图片对（用于历史记录）
    async getAllPairs() {
        if (!this.db) {
            await this.init();
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readonly');
            const objectStore = transaction.objectStore(STORE_NAME);
            const request = objectStore.getAll();

            request.onsuccess = () => {
                // 按时间倒序排列
                const pairs = request.result.sort((a, b) => b.timestamp - a.timestamp);
                resolve(pairs);
            };

            request.onerror = () => reject(request.error);
        });
    }

    // 删除图片对
    async deleteImagePair(id) {
        if (!this.db) {
            await this.init();
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readwrite');
            const objectStore = transaction.objectStore(STORE_NAME);
            const request = objectStore.delete(id);

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    // 清空所有数据
    async clearAll() {
        if (!this.db) {
            await this.init();
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readwrite');
            const objectStore = transaction.objectStore(STORE_NAME);
            const request = objectStore.clear();

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }
}

// 全局实例
const imageStorage = new ImageStorage();

