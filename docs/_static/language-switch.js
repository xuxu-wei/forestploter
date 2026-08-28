(function () {
  "use strict";

  function installLanguageSwitch() {
    var path = window.location.pathname;
    var current = path.indexOf("/zh_CN/") >= 0 ? "zh_CN" : path.indexOf("/en/") >= 0 ? "en" : null;
    if (!current) return;

    var target = current === "en" ? "zh_CN" : "en";
    var link = document.createElement("a");
    link.className = "forest-language-switch";
    link.href = path.replace("/" + current + "/", "/" + target + "/") + window.location.search + window.location.hash;
    link.textContent = current === "en" ? "中文" : "English";
    link.lang = target === "en" ? "en" : "zh-CN";
    link.setAttribute("aria-label", current === "en" ? "阅读简体中文版本" : "Read this page in English");

    var container = document.querySelector(".wy-side-nav-search") || document.querySelector(".wy-nav-top") || document.body;
    container.appendChild(link);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", installLanguageSwitch);
  } else {
    installLanguageSwitch();
  }
})();
