// ==UserScript==
// @name         Excalidraw Custom Font Override
// @namespace    https://github.com/Shiniese
// @version      1.0.0
// @description  Override Excalidraw fonts if URL is provided
// @author       Shiniese
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

  // ====== 动态生成 CSS ======
  function createFontFace(name, url) {
    if (!url) return ""; // 没填就跳过
    return `
      @font-face {
        font-family: '${name}';
        font-display: swap;
        src: url('${url}') format('woff2');
      }
    `;
  }

  function createOverrideCSS() {
    let css = "";

    css += createFontFace(overrideOptionToFontname.normal, normal_font_url);
    css += createFontFace(overrideOptionToFontname.handdrawn, handdrawn_font_url);
    css += createFontFace(overrideOptionToFontname.code, code_font_url);

    return css;
  }

  function injectStyle() {
    const style = document.createElement("style");
    style.textContent = createOverrideCSS();
    document.head.appendChild(style);
    console.log("Custom font CSS injected");
  }

  injectStyle();
})();
