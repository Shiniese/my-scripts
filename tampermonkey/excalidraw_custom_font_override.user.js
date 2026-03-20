// ==UserScript==
// @name         Excalidraw Custom Font Override
// @namespace    https://github.com/Shiniese
// @version      1.0.1
// @description  Override Excalidraw fonts if URL is provided
// @author       Shiniese
// @license      MIT
// @grant        GM_addStyle
// @match        https://*.excalidraw.com/*
// ==/UserScript==

(function () {
  'use strict';

  console.log("'Excalidraw Custom Font Override' script started");

  // ====== 在这里填写你的字体 URL ======
  const normal_font_url = "https://db.onlinewebfonts.com/t/32441506567156636049eb850b53f02a.woff2"; // Times New Roman Font
  const handdrawn_font_url = "";
  const code_font_url = "";

  // ====== 字体名称映射 ======
  const overrideOptionToFontname = {
    normal: "Nunito",
    handdrawn: "Excalifont",
    code: "Comic Shanns",
  };

  normal_font_url ? GM_addStyle(`
    @font-face {
      font-family: 'CustomNormal';
      font-display: swap;
      src: url('${normal_font_url}') format('woff2');
    }
  `): "";

  handdrawn_font_url ? GM_addStyle(`
    @font-face {
      font-family: 'CustomHanddrawn';
      font-display: swap;
      src: url('${handdrawn_font_url}') format('woff2');
    }
  `): "";

  code_font_url ? GM_addStyle(`
    @font-face {
      font-family: 'CustomCode';
      font-display: swap;
      src: url('${code_font_url}') format('woff2');
    }
  `): "";

  // 核心 Canvas Hack：拦截 context.font 的 setter
  const originalFontDescriptor = Object.getOwnPropertyDescriptor(CanvasRenderingContext2D.prototype, 'font');

  Object.defineProperty(CanvasRenderingContext2D.prototype, 'font', {
    get: function () {
      return originalFontDescriptor.get.call(this);
    },
    set: function (value) {
      let newValue = value;
      if (typeof newValue === 'string') {
        newValue = normal_font_url ? newValue.replace(
          overrideOptionToFontname.normal, 
          'CustomNormal'
        ): newValue;
        newValue = handdrawn_font_url ? newValue.replace(
          overrideOptionToFontname.handdrawn, 
          'CustomHanddrawn'
        ): newValue;
        newValue = code_font_url ? newValue.replace(
          overrideOptionToFontname.code, 
          'CustomCode'
        ): newValue;
      }
      // 调用原生 setter 应用修改后的值
      originalFontDescriptor.set.call(this, newValue);
    }
  });

  console.log("Custom font CSS injected");
})();
