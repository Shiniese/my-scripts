// ==UserScript==
// @name         Extract Images and Text from Academic Journals
// @namespace    https://github.com/Shiniese
// @version      1.0.0
// @description  Extracts images and text from Academic Journals
// @author       Shiniese
// @match        https://www.sciencedirect.com/science/article/pii/*
// @match        https://pubs.acs.org/doi/*
// @grant        GM_setClipboard
// ==/UserScript==

(function () {
    'use strict';

    // ===================== 平台检测 =====================
    const PLATFORM = {
        SCIENCEDIRECT: 'sciencedirect',
        ACS: 'pubs.acs.org'
    };

    function detectPlatform() {
        const host = window.location.hostname;
        if (host.includes('sciencedirect.com')) return PLATFORM.SCIENCEDIRECT;
        if (host.includes('pubs.acs.org') | host.includes('pubs-acs-org')) return PLATFORM.ACS;
        return null;
    }

    const currentPlatform = detectPlatform();
    console.log('[学术期刊图片和文本提取器] 脚本启动, 平台:', currentPlatform, '域名:', window.location.hostname);
    if (!currentPlatform) {
        console.log('[学术期刊图片和文本提取器] 未识别的平台，退出');
        return;
    }

    /* ========== UI 样式 ========== */
    const style = document.createElement('style');
    style.textContent = `
        .sd-extractor-panel {
            position: fixed;
            top: 120px;
            right: 24px;
            z-index: 9999;
            background: rgba(30, 30, 30, 0.9);
            backdrop-filter: blur(6px);
            border-radius: 12px;
            padding: 12px;
            width: 160px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.35);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        .sd-extractor-title {
            color: #fff;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 10px;
            text-align: center;
            letter-spacing: 0.3px;
        }

        .sd-extractor-btn {
            width: 100%;
            border: none;
            border-radius: 8px;
            padding: 10px 8px;
            margin-bottom: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            color: #fff;
            transition: all 0.2s ease;
        }

        .sd-extractor-btn:last-child {
            margin-bottom: 0;
        }

        .sd-btn-image {
            background: linear-gradient(135deg, #ff7a18, #ff9f43);
        }

        .sd-btn-text {
            background: linear-gradient(135deg, #4facfe, #00f2fe);
        }

        .sd-extractor-btn:hover {
            transform: translateY(-1px);
            filter: brightness(1.08);
            box-shadow: 0 6px 14px rgba(0,0,0,0.25);
        }

        .sd-extractor-btn:active {
            transform: translateY(0);
            box-shadow: 0 3px 8px rgba(0,0,0,0.2);
        }
    `;
    document.head.appendChild(style);

    /* ========== 创建 UI ========== */
    function createPanel() {
        const panel = document.createElement('div');
        panel.className = 'sd-extractor-panel';

        const title = document.createElement('div');
        title.className = 'sd-extractor-title';
        title.textContent = 'Academic Journals Tools';

        const imageBtn = document.createElement('button');
        imageBtn.className = 'sd-extractor-btn sd-btn-image';
        imageBtn.textContent = '🖼 Extract Images';
        imageBtn.addEventListener('click', extractImages);

        const textBtn = document.createElement('button');
        textBtn.className = 'sd-extractor-btn sd-btn-text';
        textBtn.textContent = '📄 Extract Text';
        textBtn.addEventListener('click', extractText);

        panel.appendChild(title);
        panel.appendChild(imageBtn);
        panel.appendChild(textBtn);

        document.body.appendChild(panel);
    }

    /* ========== 提取图片 ========== */
    function extractImages() {
        let imageLinks = [];
        let linksTags = [];

        switch (currentPlatform) {
        case PLATFORM.SCIENCEDIRECT:
            linksTags = document.querySelectorAll(
                'a[href^="https://ars.els-cdn.com/content/image/"][href$="_lrg.jpg"]'
            );
            break;
        case PLATFORM.ACS:
            linksTags = document.querySelectorAll(
                'a[href^="/cms/"][href$=".jpeg"]'
            );
            break;
        default:
            console.log("没有检测到可用平台！");
            break;
        }

        linksTags.forEach(link => imageLinks.push(link.href));

        // 去重：使用 Set
        const uniqueImageLinks = [...new Set(imageLinks)];

        if (uniqueImageLinks.length > 0) {
            const text = uniqueImageLinks.join('\n');
            if (confirm(`Found ${uniqueImageLinks.length} images.\n\nCopy to clipboard?`)) {
                GM_setClipboard(text);
                alert('Image links copied to clipboard.');
            }
        } else {
            alert('No image links found.');
        }
    }

    /* ========== 提取文本 ========== */
    function extractText() {
        let selectors = [];

        switch (currentPlatform) {
        case PLATFORM.SCIENCEDIRECT:
            selectors = [
                '#publication',
                '#screen-reader-main-title',
                '.abstract.author',
                '#body'
            ];
            break;
        case PLATFORM.ACS:
            // 1. 获取所有 class 为 'article__copy' 的元素
            const elements = document.querySelectorAll('.article__copy');
            if (elements) {
                // 2. 遍历每一个元素，移除它
                for (let i = elements.length - 1; i >= 0; i--) {
                    elements[i].remove();
                }
            }
            // 可选：添加一个提示，告诉用户操作已完成
            console.log('✅ 已移除所有 class 为 "article__copy" 的元素。');

            selectors = [
                '.breadcrumbs__item',
                '.article_header-title',
                '.article_header-doiurl',
                'time',
                '#Abstract',
                '.articleBody_abstractText',
                '#sec1',
                '#sec2',
                '#sec3',
                '#sec4',
                '#sec5',
                '#sec6',
                '#sec7',
                '#sec8',
                '#sec9',
                '#sec10',
                '.author-information-subsection-header',
                '.authorItemInformation',
            ];
            break;
        default:
            console.log("没有检测到可用平台！");
            break;
        }

        let text = '';
        selectors.forEach(sel => {
            const el = document.querySelector(sel);
            if (el) {
                text += el.textContent.trim() + '\n\n';
            }
        });

        if (text.trim()) {
            GM_setClipboard(text.trim());
            alert('Text copied to clipboard.');
        } else {
            alert('No text found.');
        }
    }

    /* ========== 初始化 ========== */
    window.addEventListener('load', createPanel);
})();
