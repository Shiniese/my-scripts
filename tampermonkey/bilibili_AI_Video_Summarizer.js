// ==UserScript==
// @name         Bilibili AI Video Summarizer
// @namespace    https://github.com/Shiniese
// @version      1.0
// @description  获取B站视频内容并发送给本地 Ollama/Qwen 进行总结，显示在悬浮窗中
// @author       Shiniese
// @match        https://www.bilibili.com/video/*
// @connect      192.168.168.2
// @require      https://cdn.jsdelivr.net/npm/marked/marked.min.js
// @grant        GM_xmlhttpRequest
// @grant        GM_addStyle
// ==/UserScript==

(function() {
    'use strict';

    // --- 配置区域 ---
    const CONFIG = {
        subtitleApi: "http://192.168.168.2:8000/get_video_text_content",
        llmApi: "http://192.168.168.2:11434/api/chat",
        modelName: "qwen3:4b-instruct-2507-q4_K_M-32k"
    };

    // --- 样式注入 ---
    const styles = `
        #ai-summary-btn {
            position: fixed;
            bottom: 100px;
            right: 20px;
            z-index: 9999;
            padding: 10px 20px;
            background-color: #00AEEC;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            transition: transform 0.2s;
        }
        #ai-summary-btn:hover { transform: scale(1.05); background-color: #009CD6; }

        #ai-floating-window {
            position: fixed;
            top: 100px;
            right: 100px;
            width: 400px;
            max-height: 80vh;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            display: none;
            flex-direction: column;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }

        #ai-window-header {
            padding: 10px 15px;
            background: #f4f5f7;
            border-bottom: 1px solid #e7e7e7;
            border-radius: 8px 8px 0 0;
            cursor: move;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
        }

        #ai-window-title { font-weight: bold; color: #333; }
        #ai-close-btn { cursor: pointer; color: #999; font-size: 18px; }
        #ai-close-btn:hover { color: #f25d8e; }

        #ai-window-content {
            padding: 15px;
            overflow-y: auto;
            color: #333;
            line-height: 1.6;
            font-size: 14px;
        }

        /* Markdown 样式微调 */
        #ai-window-content h3 { margin-top: 10px; margin-bottom: 5px; font-size: 16px; color: #00AEEC; border-bottom: 1px solid #eee; padding-bottom: 5px;}
        #ai-window-content ul { padding-left: 20px; margin: 5px 0; }
        #ai-window-content li { margin-bottom: 4px; }
        .ai-loading { text-align: center; color: #666; padding: 20px; }
        .ai-error { color: red; }
    `;
    GM_addStyle(styles);

    // --- UI 创建 ---
    function createUI() {
        // 1. 创建触发按钮
        const btn = document.createElement('button');
        btn.id = 'ai-summary-btn';
        btn.innerText = 'AI 总结';
        document.body.appendChild(btn);

        // 2. 创建悬浮窗
        const win = document.createElement('div');
        win.id = 'ai-floating-window';
        win.innerHTML = `
            <div id="ai-window-header">
                <span id="ai-window-title">AI 视频总结</span>
                <span id="ai-close-btn">×</span>
            </div>
            <div id="ai-window-content"></div>
        `;
        document.body.appendChild(win);

        // 事件绑定
        btn.onclick = () => {
            win.style.display = 'flex';
            startProcess();
        };

        document.getElementById('ai-close-btn').onclick = () => {
            win.style.display = 'none';
        };

        makeDraggable(win);
    }

    // --- 拖拽逻辑 ---
    function makeDraggable(element) {
        const header = element.querySelector('#ai-window-header');
        let isDragging = false;
        let startX, startY, initialLeft, initialTop;

        header.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            initialLeft = element.offsetLeft;
            initialTop = element.offsetTop;
            header.style.cursor = 'grabbing';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            element.style.left = `${initialLeft + dx}px`;
            element.style.top = `${initialTop + dy}px`;
            // 防止拖出屏幕太远 (可选)
            element.style.right = 'auto';
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
            header.style.cursor = 'move';
        });
    }

    // --- 核心业务逻辑 ---

    function updateStatus(htmlContent) {
        const contentDiv = document.getElementById('ai-window-content');
        contentDiv.innerHTML = htmlContent;
    }

    async function startProcess() {
        const currentUrl = window.location.href;
        updateStatus('<div class="ai-loading">正在获取视频字幕内容...<br>⏳</div>');

        // 第一步：获取字幕内容
        GM_xmlhttpRequest({
            method: "GET",
            url: `${CONFIG.subtitleApi}?video_url=${encodeURIComponent(currentUrl)}`,
            onload: function(response) {
                if (response.status === 200) {
                    try {
                        // 假设返回的是纯文本或者 JSON 中的 content 字段，这里假设整个 body 就是文本
                        // 如果你的 API 返回 JSON {text: "..."}，请修改为 JSON.parse(response.responseText).text
                        const videoContent = response.responseText;
                        if (!videoContent || videoContent.length < 10) {
                            updateStatus('<div class="ai-error">获取到的内容为空或过短，无法总结。</div>');
                            return;
                        }

                        askLLM(videoContent);

                    } catch (e) {
                        updateStatus(`<div class="ai-error">字幕解析错误: ${e.message}</div>`);
                    }
                } else {
                    updateStatus(`<div class="ai-error">获取字幕失败 (Status ${response.status})</div>`);
                }
            },
            onerror: function(err) {
                updateStatus('<div class="ai-error">网络请求错误，请检查 192.168.168.2:8000 服务是否启动</div>');
            }
        });
    }

    function askLLM(content) {
        updateStatus('<div class="ai-loading">AI 正在阅读并总结...<br>🧠</div>');

        const promptText = `「必须使用中文回答！！！」Summarize the following CONTENT into brief sentences of key points, then provide complete highlighted information in a list, choosing an appropriate emoji for each highlight.
Your output should use the following format:
### Summary
{brief summary of this content}
### Highlights
- [Emoji] Bullet point with complete explanation
### keyword
Suggest up to a few tags related to video content.

---

${content}`;

        const payload = {
            model: CONFIG.modelName,
            messages: [
                { role: "user", content: promptText }
            ],
            stream: false
        };

        GM_xmlhttpRequest({
            method: "POST",
            url: CONFIG.llmApi,
            headers: {
                "Content-Type": "application/json"
            },
            data: JSON.stringify(payload),
            onload: function(response) {
                if (response.status === 200) {
                    try {
                        const data = JSON.parse(response.responseText);
                        const aiResponse = data.message.content;
                        // 使用 marked.js 渲染 Markdown
                        updateStatus(marked.parse(aiResponse));
                    } catch (e) {
                        updateStatus(`<div class="ai-error">AI 响应解析错误: ${e.message}</div>`);
                    }
                } else {
                    updateStatus(`<div class="ai-error">AI 请求失败 (Status ${response.status})</div>`);
                }
            },
            onerror: function(err) {
                updateStatus('<div class="ai-error">连接 Ollama 失败，请检查 192.168.168.2:11434 服务</div>');
            }
        });
    }

    // --- 初始化 ---
    // 等待页面稍微加载一下再显示按钮，避免冲突
    window.addEventListener('load', () => {
        setTimeout(createUI, 1500);
    });

})();