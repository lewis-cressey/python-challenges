// public/worker.js
let brythonReady = false;

// 1. 同步加载 Brython
importScripts('/brython.js');

// 2. 拦截 console.log (即 Python 的 print)
const originalLog = console.log;
console.log = function(...args) {
  // 将输出发送回主线程
  self.postMessage({ type: 'output', data: args.join(' ') });
  originalLog.apply(console, args);
};

// 3. 通知主线程准备就绪
self.postMessage({ type: 'ready' });

// 4. 监听执行请求
self.onmessage = function(e) {
  if (e.data.type === 'run') {
    try {
      // 执行 Python 代码
      __BRYTHON__.runPythonSource(e.data.code);
      self.postMessage({ type: 'done' });
    } catch (err) {
      self.postMessage({ type: 'error', data: err.toString() });
    }
  }
};
