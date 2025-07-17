// Scale fix for mobile devices
(function (document) {
  var metas = document.getElementsByTagName("meta"),
    changeViewportContent = function (content) {
      for (var i = 0; i < metas.length; i++) {
        if (metas[i].name == "viewport") {
          metas[i].content = content;
        }
      }
    },
    initialize = function () {
      changeViewportContent(
        "width=device-width, minimum-scale=1.0, maximum-scale=1.0",
      );
    },
    gestureStart = function () {
      changeViewportContent(
        "width=device-width, minimum-scale=0.25, maximum-scale=1.6",
      );
    },
    gestureEnd = function () {
      initialize();
    };

  if (navigator.userAgent.match(/iPhone/i)) {
    initialize();
    document.addEventListener("touchstart", gestureStart, false);
    document.addEventListener("touchend", gestureEnd, false);
  }
})(document);

// Smooth scrolling for anchor links
document.addEventListener("DOMContentLoaded", function () {
  // Get all anchor links
  var links = document.querySelectorAll('a[href^="#"]');

  links.forEach(function (link) {
    link.addEventListener("click", function (e) {
      e.preventDefault();

      var targetId = this.getAttribute("href").substring(1);
      var targetElement = document.getElementById(targetId);

      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });

  // Add copy button to code blocks
  var codeBlocks = document.querySelectorAll("pre code");

  codeBlocks.forEach(function (codeBlock) {
    var button = document.createElement("button");
    button.className = "copy-button";
    button.textContent = "Copy";

    button.addEventListener("click", function () {
      var text = codeBlock.textContent;
      navigator.clipboard.writeText(text).then(function () {
        button.textContent = "Copied!";
        setTimeout(function () {
          button.textContent = "Copy";
        }, 2000);
      });
    });

    var pre = codeBlock.parentNode;
    pre.style.position = "relative";
    pre.appendChild(button);
  });
});
