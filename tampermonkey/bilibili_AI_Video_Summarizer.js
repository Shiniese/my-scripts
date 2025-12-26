// ==UserScript==
// @name         Bilibili AI Video Summarizer
// @namespace    https://github.com/Shiniese
// @version      1.0.1
// @description  B站视频AI总结：支持拖拽按钮、最小化窗口、复制字幕/总结内容
// @author       Shiniese
// @match        https://www.bilibili.com/video/*
// @connect      192.168.168.2
// @require      https://cdn.jsdelivr.net/npm/marked/marked.min.js
// @grant        GM_xmlhttpRequest
// @grant        GM_addStyle
// @grant        GM_setClipboard
// ==/UserScript==

(function() {
    'use strict';

    // --- 配置区域 ---
    const CONFIG = {
        subtitleApi: "http://192.168.168.2:8000/get_video_text_content",
        llmApi: "http://192.168.168.2:11434/api/chat",
        modelName: "qwen3:4b-instruct-2507-q4_K_M-32k"
    };

    // --- 全局状态 ---
    let cachedSubtitle = ""; // 缓存字幕原文
    let cachedSummary = "";  // 缓存总结结果
    let isMinimized = false; // 最小化状态

    // --- 样式注入 ---
    const styles = `
        /* 主按钮样式 */
        #ai-summary-btn {
            position: fixed;
            top: 80%;
            right: 50px;
            z-index: 9999;
            width: 60px;
            height: 60px;
            background-color: #00AEEC;
            color: white;
            border: none;
            border-radius: 50%;
            cursor: move; /* 鼠标变为移动图标 */
            font-weight: bold;
            font-size: 14px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            user-select: none;
            transition: background-color 0.2s;
        }
        #ai-summary-btn:hover { background-color: #009CD6; }
        #ai-summary-btn:active { box-shadow: 0 2px 5px rgba(0,0,0,0.3); }

        /* 悬浮窗样式 */
        #ai-floating-window {
            position: fixed;
            top: 100px;
            right: 100px;
            width: 400px;
            max-height: 80vh;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            z-index: 10000;
            display: none;
            flex-direction: column;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            transition: height 0.3s ease;
        }

        /* 标题栏 */
        #ai-window-header {
            padding: 12px 15px;
            background: #f4f5f7;
            border-bottom: 1px solid #e7e7e7;
            border-radius: 8px 8px 0 0;
            cursor: move;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
            flex-shrink: 0;
        }
        #ai-window-title { font-weight: bold; color: #333; }
        .ai-win-ctrls { display: flex; gap: 10px; }
        .ai-ctrl-btn { cursor: pointer; color: #666; font-size: 16px; font-weight: bold; padding: 0 5px;}
        .ai-ctrl-btn:hover { color: #00AEEC; }
        #ai-close-btn:hover { color: #f25d8e; }

        /* 内容区域 */
        #ai-window-content {
            padding: 15px;
            overflow-y: auto;
            color: #333;
            line-height: 1.6;
            font-size: 14px;
            flex-grow: 1;
            min-height: 100px; /* 最小高度 */
        }

        /* 底部操作栏 */
        #ai-window-footer {
            padding: 10px 15px;
            border-top: 1px solid #eee;
            background: #fff;
            border-radius: 0 0 8px 8px;
            display: flex;
            gap: 10px;
            flex-shrink: 0;
        }
        
        .ai-action-btn {
            flex: 1;
            padding: 8px 0;
            border: 1px solid #ddd;
            background: #f9f9f9;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            color: #333;
            transition: all 0.2s;
        }
        .ai-action-btn:hover { background: #eef6fc; border-color: #00AEEC; color: #00AEEC; }
        .ai-action-btn:active { background: #e0e0e0; }

        /* 最小化时的样式 */
        #ai-floating-window.minimized #ai-window-content,
        #ai-floating-window.minimized #ai-window-footer {
            display: none;
        }
        #ai-floating-window.minimized {
            height: auto !important;
            max-height: none;
        }

        /* Markdown & Loading 样式 */
        #ai-window-content h3 { margin-top: 10px; margin-bottom: 5px; font-size: 16px; color: #00AEEC; border-bottom: 1px solid #eee; padding-bottom: 5px;}
        #ai-window-content ul { padding-left: 20px; margin: 5px 0; }
        #ai-window-content li { margin-bottom: 4px; }
        .ai-loading { text-align: center; color: #666; padding: 20px; }
        .ai-error { color: red; }
    `;
    GM_addStyle(styles);

    // --- UI 创建 ---
    function createUI() {
        // 1. 创建触发按钮 (现在是圆形的)
        const btn = document.createElement('button');
        btn.id = 'ai-summary-btn';
        btn.innerHTML = 'AI<br>总结'; // 换行显示
        document.body.appendChild(btn);

        // 2. 创建悬浮窗
        const win = document.createElement('div');
        win.id = 'ai-floating-window';
        win.innerHTML = `
            <div id="ai-window-header">
                <span id="ai-window-title">AI 视频总结</span>
                <div class="ai-win-ctrls">
                    <span id="ai-min-btn" class="ai-ctrl-btn" title="最小化">_</span>
                    <span id="ai-close-btn" class="ai-ctrl-btn" title="关闭">×</span>
                </div>
            </div>
            <div id="ai-window-content"></div>
            <div id="ai-window-footer">
                <button class="ai-action-btn" id="btn-copy-sub">复制字幕原文</button>
                <button class="ai-action-btn" id="btn-copy-sum">复制AI总结</button>
            </div>
        `;
        document.body.appendChild(win);

        // --- 事件绑定 ---
        
        // 1. 拖拽逻辑：按钮和窗口都可拖拽
        // 注意：传入回调函数，仅当是“点击”而非“拖拽结束”时触发
        makeDraggable(btn, btn, () => {
            // 点击回调：打开窗口
            win.style.display = 'flex';
            // 如果窗口之前被关闭，重置最小化状态
            if(isMinimized) toggleMinimize(win); 
            startProcess();
        });
        
        makeDraggable(win, win.querySelector('#ai-window-header'), null);

        // 2. 窗口控制按钮
        document.getElementById('ai-close-btn').onclick = () => {
            win.style.display = 'none';
        };

        document.getElementById('ai-min-btn').onclick = () => {
            toggleMinimize(win);
        };

        // 3. 复制功能
        document.getElementById('btn-copy-sub').onclick = function() {
            copyText(this, cachedSubtitle, "字幕");
        };
        document.getElementById('btn-copy-sum').onclick = function() {
            copyText(this, cachedSummary, "总结");
        };
    }

    // --- 功能函数 ---

    function toggleMinimize(win) {
        isMinimized = !isMinimized;
        const minBtn = document.getElementById('ai-min-btn');
        if (isMinimized) {
            win.classList.add('minimized');
            minBtn.innerText = '□'; // 还原图标
        } else {
            win.classList.remove('minimized');
            minBtn.innerText = '_'; // 最小化图标
        }
    }

    async function copyText(btnElement, text, typeName) {
        if (!text) {
            alert(`暂无${typeName}内容可复制，请等待生成完成。`);
            return;
        }
        try {
            await navigator.clipboard.writeText(text);
            const originalText = btnElement.innerText;
            btnElement.innerText = "已复制 ✅";
            setTimeout(() => {
                btnElement.innerText = originalText;
            }, 2000);
        } catch (err) {
            console.error('复制失败', err);
            // 降级处理
            GM_setClipboard(text);
            alert('已通过GM_setClipboard复制');
        }
    }

    // --- 通用拖拽逻辑 (支持点击判断) ---
    // element: 被移动的整体
    // handle: 鼠标按下的把手区域
    // onClickCallback: 如果判断为点击而非拖拽，执行此回调
    function makeDraggable(element, handle, onClickCallback) {
        let isDragging = false;
        let hasMoved = false; // 用于区分点击和拖拽
        let startX, startY, initialLeft, initialTop;

        handle.addEventListener('mousedown', (e) => {
            // 只有左键可以拖拽
            if(e.button !== 0) return;
            
            isDragging = true;
            hasMoved = false;
            startX = e.clientX;
            startY = e.clientY;
            
            // 获取计算后的样式位置
            const rect = element.getBoundingClientRect();
            initialLeft = rect.left;
            initialTop = rect.top;
            
            handle.style.cursor = 'grabbing';
            
            // 阻止默认选中文本行为
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;

            // 只有移动超过一定像素才算拖拽，避免手抖
            if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
                hasMoved = true;
                element.style.left = `${initialLeft + dx}px`;
                element.style.top = `${initialTop + dy}px`;
                element.style.bottom = 'auto'; // 清除定位干扰
                element.style.right = 'auto';
            }
        });

        document.addEventListener('mouseup', (e) => {
            if (!isDragging) return;
            isDragging = false;
            handle.style.cursor = 'move';
            
            // 如果没有发生显著位移，且传了回调，则视为点击
            if (!hasMoved && onClickCallback) {
                onClickCallback();
            }
        });
    }

    // --- 核心业务逻辑 ---

    function updateStatus(htmlContent) {
        const contentDiv = document.getElementById('ai-window-content');
        contentDiv.innerHTML = htmlContent;
    }

    async function startProcess() {
        const currentUrl = window.location.href;
        
        // 重置缓存
        cachedSubtitle = "";
        cachedSummary = "";
        
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

                        // 保存字幕到缓存
                        cachedSubtitle = videoContent;

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
        updateStatus('<div class="ai-loading">AI 正在阅读并总结...<br>🧠<br><small>内容较长时可能需要几十秒</small></div>');

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
                        
                        // 保存总结到缓存
                        cachedSummary = aiResponse;

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