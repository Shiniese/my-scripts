// ==UserScript==
// @name         Extract Images and Text from ScienceDirect
// @namespace    https://github.com/Shiniese
// @version      1.0.0
// @description  Extracts images and text from ScienceDirect pages
// @author       Shiniese
// @match        https://www.sciencedirect.com/science/article/pii/*
// @grant        GM_setClipboard
// ==/UserScript==

(function () {
    'use strict';

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
        title.textContent = 'ScienceDirect Tools';

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
        const imageLinks = [];
        let links = document.querySelectorAll(
            'a[href^="https://ars.els-cdn.com/content/image/"][href$="_lrg.jpg"]'
        );

        if (links.length === 0) {
            links = document.querySelectorAll(
                'a[href^="http://hs.ars.els-cdn.com"][href$="_lrg.jpg"]'
            );
        }

        links.forEach(link => imageLinks.push(link.href));

        if (imageLinks.length > 0) {
            const text = imageLinks.join('\n');
            if (confirm(`Found ${imageLinks.length} images.\n\nCopy to clipboard?`)) {
                GM_setClipboard(text);
                alert('Image links copied to clipboard.');
            }
        } else {
            alert('No image links found.');
        }
    }

    /* ========== 提取文本 ========== */
    function extractText() {
        const selectors = [
            '#publication',
            '#screen-reader-main-title',
            '.abstract.author',
            '#body'
        ];

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
