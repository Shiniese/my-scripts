// ==UserScript==
// @name         Excalidraw Custom Font Override
// @namespace    https://github.com/Shiniese
// @version      1.0.0
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
      font-family: '${overrideOptionToFontname.normal}';
      font-display: swap;
      src: url('${normal_font_url}') format('woff2');
    }
  `): "";

  handdrawn_font_url ? GM_addStyle(`
    @font-face {
      font-family: '${overrideOptionToFontname.handdrawn}';
      font-display: swap;
      src: url('${handdrawn_font_url}') format('woff2');
    }
  `): "";

  code_font_url ? GM_addStyle(`
    @font-face {
      font-family: '${overrideOptionToFontname.code}';
      font-display: swap;
      src: url('${code_font_url}') format('woff2');
    }
  `): "";

  console.log("Custom font CSS injected");
})();
