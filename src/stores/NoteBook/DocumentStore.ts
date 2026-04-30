import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Document, Content } from '../../types/document'
import { ProjectParams } from './ProjectParams'
import { SideBarParams } from './SideBarParams'
// 添加API基础URL
const API_BASE_URL = 'http://localhost:5000/api'

export const DocStore = defineStore("DocStore", () => {
  const documents = ref([] as Document[])
  const currentDocId = ref('')
  const selectedDocId = ref('') // 用于存储选中的文档ID
  const deletedDocuments = ref([] as Document[]) // 存储已删除的文档
  const docChanged = ref(false)
  const contentCache = ref([] as Content[])

  // 初始化时获取所有文档（包括已删除的）
  async function initializeDocuments() {
    try {
      const response = await fetch(`${API_BASE_URL}/documents`)
      if (response.ok) {
        const docs = await response.json()
        // 分离正常文档和已删除文档
        documents.value = docs.filter((doc: Document) => !doc.deletedAt)
        deletedDocuments.value = docs.filter((doc: Document) => doc.deletedAt)
      } else {
        console.error('获取文档失败:', await response.text())
      }
    } catch (error) {
      console.error('获取文档时出错:', error)
    }
  }

  async function fetchDocuments() {
    try {
      const response = await fetch(`${API_BASE_URL}/documents`)
      if (response.ok) {
        const docs = await response.json()
        // 只显示未删除的文档
        documents.value = docs.filter((doc: Document) => !doc.deletedAt)
      } else {
        console.error('获取文档失败:', await response.text())
      }
    } catch (error) {
      console.error('获取文档时出错:', error)
    }
  }

  async function createDocumentFromEvent(eventId: string, eventName: string, eventStart: string) {
    // 检查是否已存在相同事件ID的文档
    const useProjectParams = ProjectParams()

    const exists = documents.value.some(doc => doc.eventId === eventId)
    if (exists) return
    
    const eventDate = new Date(eventStart || Date.now())
    const title = `${eventName}`
    const docId = crypto.randomUUID() // 使用UUID生成唯一ID

    const newDocument = {
      id: docId,
      title: title,
      eventId: eventId,
      projectId: "rcwd", // 默认项目ID
      eventName,
      createdAt: eventDate.toISOString(),
      deletedAt: null
    }

    try {
      const response = await fetch(`${API_BASE_URL}/documents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({...newDocument, content:`<h1>${eventName}</h1>`})
      })
      
      if (response.ok) {
        const createdDoc = await response.json()
        documents.value.push(createdDoc)
        contentCache.value.push({id:docId, content: `<h1>${eventName}</h1>`})
        useProjectParams.addDocumentToProject("rcwd", createdDoc)
        currentDocId.value = docId

        const sideBarParams = SideBarParams()
        sideBarParams.resetViews()
        sideBarParams.isShowPage = true;
        docChanged.value = !docChanged.value
      } else {
        console.error('创建文档失败:', await response.text())
      }
    } catch (error) {
      console.error('创建文档时出错:', error)
    }
  }

  async function createDocumentToProject(projectId: string, title: string) {
    const docId = crypto.randomUUID() // 使用UUID生成唯一ID
    const newDocument = {
      id: docId,
      title: title,
      eventId: null,
      projectId: projectId,
      eventName: null,
      createdAt: new Date().toISOString(),
      content: `<h1>${title}</h1>`,
      deletedAt: null
    }

    try {
      const response = await fetch(`${API_BASE_URL}/documents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newDocument)
      })
      
      if (response.ok) {
        const createdDoc = await response.json()
        documents.value.push(createdDoc)
        contentCache.value.push({id:docId, content: `<h1>${title}</h1>`})
        currentDocId.value = docId

        // 将文档添加到项目中
        try {
          const projectStore = ProjectParams();
          await projectStore.addDocumentToProject(projectId, createdDoc);
        } catch (error) {
          console.error('向项目添加文档失败:', error);
        }

        return createdDoc;
      } else {
        console.error('创建文档失败:', await response.text())
      }
    } catch (error) {
      console.error('创建文档时出错:', error)
    }
  }
  async function saveCurrentDocument(content: string) {
    const doc = documents.value.find(d => d.id === currentDocId.value)
    if (doc) {
      // 更新缓存
      const cacheItem = contentCache.value.find(c => c.id === doc.id)
      if (cacheItem) {
        cacheItem.content = content
      } else {
        contentCache.value.push({id:doc.id, content})
      }
      
      // 更新文档标题为H1标题（最多10个字）
      const h1Match = content.match(/<h1>(.*?)<\/h1>/);
      if (h1Match && h1Match[1]) {
        const h1Text = h1Match[1].substring(0, 10);
        if (doc.title !== h1Text) {
          doc.title = h1Text;
        }
      }
      
      // 保存文档元数据到后端
      try {
        const response = await fetch(`${API_BASE_URL}/documents/${doc.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: doc.title
          })
        })
        
        if (!response.ok) {
          console.error('保存文档失败:', await response.text())
        }
      } catch (error) {
        console.error('保存文档时出错:', error)
      }
      
      // 保存文档内容到后端
      try {
        const contentResponse = await fetch(`${API_BASE_URL}/contents/${doc.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            content: content
          })
        })
        
        if (!contentResponse.ok) {
          console.error('保存文档内容失败:', await contentResponse.text())
        }
      } catch (error) {
        console.error('保存文档内容时出错:', error)
      }
    }
  }

  function findDocByEventId(eventId: string) {
    return documents.value.find(doc => doc.eventId === eventId)
  }
  

  function getGroupedDocuments() {
    const grouped = {} as Record<number, Record<number, Document[]>>;

    documents.value.forEach(doc => {
      // 修复时区问题：将UTC时间转换为本地时间
      if(doc.projectId !== "rcwd") return;

      const date = new Date(doc.createdAt);
      const year = date.getFullYear();
      const month = date.getMonth() + 1; // 月份从0开始，需要加1
      
      if (!grouped[year]) grouped[year] = {};
      if (!grouped[year][month]) grouped[year][month] = [];
      
      // 按创建时间排序文档
      grouped[year][month].push(doc);
      grouped[year][month].sort((a, b) => 
        new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
      );
    });

    // 对年份和月份进行排序
    const sortedGrouped = {} as Record<number, Record<number, Document[]>>;
    Object.keys(grouped)
      .map(Number)
      .sort((a, b) => a - b) // 年份升序排列
      .forEach(year => {
        sortedGrouped[year] = {};
        Object.keys(grouped[year])
          .map(Number)
          .sort((a, b) => a - b) // 月份升序排列
          .forEach(month => {
            sortedGrouped[year][month] = grouped[year][month];
          });
      });

    return sortedGrouped;
  }

  // 修改删除文档方法：只标记删除，不真正删除
  async function deleteDocument(docId: string) {
    const docIndex = documents.value.findIndex(d => d.id === docId);
    if (docIndex > -1) {
      const doc = documents.value[docIndex];
      // 添加删除时间戳
      const deletedDoc = { 
        ...doc, 
        deletedAt: new Date().toISOString() 
      };
      
      // 将文档移到已删除列表
      deletedDocuments.value.push(deletedDoc);
      documents.value.splice(docIndex, 1);
      
      // 更新后端状态
      try {
        const response = await fetch(`${API_BASE_URL}/documents/${docId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            deletedAt: deletedDoc.deletedAt
          })
        });
        
        if (!response.ok) {
          console.error('更新文档删除状态失败:', await response.text());
        }
      } catch (error) {
        console.error('更新文档删除状态时出错:', error);
      }
      
      // 从项目中移除文档ID
      try {
        const projectStore = ProjectParams();
        if(!doc.projectId) return;
        await projectStore.removeDocumentFromProject(doc.projectId, docId);
      } catch (error) {
        console.error('从项目中移除文档失败:', error);
      }
    }
  }

  // 恢复文档
  async function restoreDocument(docId: string) {
    const deletedIndex = deletedDocuments.value.findIndex(d => d.id === docId);
    if (deletedIndex > -1) {
      const doc = deletedDocuments.value[deletedIndex];
      // 移除删除时间戳
      const restoredDoc = { ...doc };
      delete restoredDoc.deletedAt;
      
      // 将文档移回正常列表
      documents.value.push(restoredDoc);
      deletedDocuments.value.splice(deletedIndex, 1);
      
      // 更新后端状态
      try {
        const response = await fetch(`${API_BASE_URL}/documents/${docId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            deletedAt: null
          })
        });
        
        if (!response.ok) {
          console.error('恢复文档失败:', await response.text());
        }
      } catch (error) {
        console.error('恢复文档时出错:', error);
      }
      
      // 将文档ID添加回项目
      try {
        const projectStore = ProjectParams();
        if(!doc.projectId) return;
        await projectStore.addDocumentToProject(doc.projectId, restoredDoc as Document);
      } catch (error) {
        console.error('向项目中添加文档失败:', error);
      }
    }
  }

  // 永久删除文档（从后端真正删除）
  async function permanentDelete(docId: string) {
    const deletedIndex = deletedDocuments.value.findIndex(d => d.id === docId);
    if (deletedIndex > -1) {
      // 从已删除列表中移除
      deletedDocuments.value.splice(deletedIndex, 1);
      
      // 从后端真正删除
      try {
        const response = await fetch(`${API_BASE_URL}/documents/${docId}`, {
          method: 'DELETE'
        });
        
        if (!response.ok) {
          console.error('永久删除文档失败:', await response.text());
        }
      } catch (error) {
        console.error('永久删除文档时出错:', error);
      }
    }
  }

  // 搜索文档
  async function searchDocuments(query: string) {
    if (!query.trim()) {
      return [];
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/contents/search?query=${encodeURIComponent(query)}`);
      if (response.ok) {
        const results = await response.json();
        // 处理搜索结果，确保片段是纯文本且长度不超过8个字符
        return results.map((result: any) => {
          // 移除HTML标签
          const cleanSnippet = result.snippet.replace(/<[^>]*>/g, '');
          
          // 如果片段长度超过8个字符，截取前8个字符并添加省略号
          const truncatedSnippet = cleanSnippet.length > 8 
            ? cleanSnippet.substring(0, 8) + '...' 
            : cleanSnippet;
          
          return {
            ...result,
            snippet: truncatedSnippet
          };
        });
      } else {
        console.error('搜索文档失败:', await response.text());
        return [];
      }
    } catch (error) {
      console.error('搜索文档时出错:', error);
      return [];
    }
  }

  // 获取文档内容（先从缓存获取，没有再从后端获取）
  async function getDocumentContent(docId: string) {
    // 先从缓存获取
    if (contentCache.value.find(c => c.id === docId)) {
      return contentCache.value.find(c => c.id === docId)?.content;
    }
    
    // 从后端获取
    try {
      const response = await fetch(`${API_BASE_URL}/contents/${docId}`);
      if (response.ok) {
        const contentData = await response.json();
        // 添加到缓存
        contentCache.value.push({id: docId, content: contentData.content});
        return contentData.content;
      } else {
        console.error('获取文档内容失败:', await response.text());
        return '';
      }
    } catch (error) {
      console.error('获取文档内容时出错:', error);
      return '';
    }
  }

  const isLoading = ref(false);
  async function updateDatabase() {
    try {
      isLoading.value = true;

      const response = await fetch(`${API_BASE_URL}/rag/update`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            'update': true
          })
        });
      if (response.ok) {
        console.log('知识库更新成功');
        isLoading.value = false;
      } else {
        console.error('知识库更新失败:', await response.text());
        isLoading.value = false;
      }
    } catch (error) {
      console.error('知识库更新时出错:', error);
      isLoading.value = false;
    }
  }
  return {
    documents,
    currentDocId,
    deletedDocuments,
    contentCache,
    docChanged,
    selectedDocId,
    isLoading,
    updateDatabase,
    createDocumentToProject,
    initializeDocuments,
    fetchDocuments,
    createDocumentFromEvent,
    saveCurrentDocument,
    findDocByEventId,
    getGroupedDocuments,
    deleteDocument,
    restoreDocument,
    permanentDelete,
    searchDocuments,
    getDocumentContent,
  }
})