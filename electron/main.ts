import { app, BrowserWindow, ipcMain, dialog, shell } from 'electron'
//import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import fs from 'fs'

//const require = createRequire(import.meta.url)
const __dirname = path.dirname(fileURLToPath(import.meta.url))
// The built directory structure
//
// ├─┬─┬ dist
// │ │ └── index.html
// │ │
// │ ├─┬ dist-electron
// │ │ ├── main.js
// │ │ └── preload.mjs
// │
process.env.APP_ROOT = path.join(__dirname, '..')

// 🚧 Use ['ENV_NAME'] avoid vite:define plugin - Vite@2.x
export const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
export const MAIN_DIST = path.join(process.env.APP_ROOT, 'dist-electron')
export const RENDERER_DIST = path.join(process.env.APP_ROOT, 'dist')

process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL ? path.join(process.env.APP_ROOT, 'public') : RENDERER_DIST

let win: BrowserWindow | null

function createWindow() {
  win = new BrowserWindow({
    width: 1280,
    height: 800,
    icon: "./resource/Calendar.ico",
    autoHideMenuBar: true,
     webPreferences: {
      nodeIntegration: true,
      contextIsolation: true,
      preload: path.resolve(__dirname, "preload.mjs")
    },
    titleBarStyle: "hidden",
    titleBarOverlay: {
      color: "white",
      // 自定义标题栏颜色
      symbolColor: "3D3D3D"
      // 控制按钮颜色
    },
    minWidth: 1e3,
    minHeight: 600,
    useContentSize: true
  });
  // Test active push message to Renderer-process.
  win.webContents.on('did-finish-load', () => {
    win?.webContents.send('main-process-message', (new Date).toLocaleString())
    
  })

  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL)
  } else {
    // win.loadFile('dist/index.html')
    win.loadFile(path.join(RENDERER_DIST, 'index.html'))
  }

  // 监听窗口关闭事件（不拦截刷新操作）
  win.on('closed', () => {
    win = null;
  })

  ipcMain.on('set-theme', (_, theme) => {
  if (win) {
    if (theme === 'dark') {
      win.setTitleBarOverlay({
        color: '#1E1E1E', // 暗色主题的颜色
        symbolColor: '#CCCCCC' // 暗色主题的符号颜色
      });
    } else {
      win.setTitleBarOverlay({
        color: 'white', // 亮色主题的颜色
        symbolColor: '#3D3D3D' // 亮色主题的符号颜色
      });
    }
  }
});
}


// 添加文件保存IPC处理程序
ipcMain.handle('save-file', async (_, { fileName, fileData }) => {
  try {
    // 文件大小限制 (50MB)
    const maxSize = 50 * 1024 * 1024;
    
    // 验证文件大小
    if (fileData.length > maxSize) {
      throw new Error('文件过大，最大支持50MB');
    }
    
    // 默认保存到用户文档目录下的FlowCalendar/resources文件夹
    const userDocumentsPath = app.getPath('documents');
    const filePath = path.join(userDocumentsPath, "FlowCalendar/resources", fileName);

    // 确保目录存在
    const dirPath = path.dirname(filePath);
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }

    // 保存文件
    fs.writeFileSync(filePath, Buffer.from(fileData));

    console.log('文件已保存:', filePath);
    return { success: true, filePath };
  } catch (error: any) {
    console.error('保存文件时出错:', error);
    return { success: false, error: error.message };
  }
});

// 添加选择保存路径的IPC处理程序
ipcMain.handle('save-file-dialog', async (_, { fileName }) => {
  const result = await dialog.showSaveDialog({
    defaultPath: fileName,
    filters: [
      { name: '所有文件', extensions: ['*'] }
    ]
  });
  
  return result;
});

// 添加打开文件的IPC处理程序
ipcMain.handle('open-file', async (_, filePath) => {
  try {
    // 验证文件是否存在
    if (!fs.existsSync(filePath)) {
      throw new Error('文件不存在');
    }
    
    // 使用系统默认应用打开文件
    await shell.openPath(filePath);
    
    return { success: true };
  } catch (error: any) {
    console.error('打开文件失败:', error);
    return { success: false, error: error.message };
  }
});



app.on('window-all-closed', () => {
  // 终止Python进程
  // if (pythonProcess && !pythonProcess.killed) {
  //   pythonProcess.kill('SIGTERM');
  // }
  
  if (process.platform !== 'darwin') {
    app.quit()
    win = null
  }
})

// app.on('activate', () => {
//   // On OS X it's common to re-create a window in the app when the
//   // dock icon is clicked and there are no other windows open.
//   if (BrowserWindow.getAllWindows().length === 0) {
//     createWindow()
//   }
// })

app.whenReady().then(() => {
  
  createWindow();

});