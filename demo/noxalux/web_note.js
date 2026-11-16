// A note over the canvas for the first visit, while the browser compiles the demo's shaders.
// Godot's own progress bar covers the download; this covers the wait after it, when the page
// is otherwise a still, empty canvas. The demo removes it (window.fxNoteDone) as soon as its
// start panel is on screen.
(function () {
  var el = null;
  function show() {
    el = document.createElement('div');
    el.id = 'fx-note';
    el.style.cssText = 'position:fixed;left:0;right:0;top:6%;text-align:center;z-index:10;' +
      'font:16px/1.5 system-ui,sans-serif;color:#ddd;text-shadow:0 1px 3px #000;pointer-events:none';
    el.innerHTML = 'Preparing the effects for your GPU&hellip;<br>' +
      '<span style="color:#999;font-size:14px">The first visit can take up to a minute. Next time it opens in seconds.</span>';
    document.body.appendChild(el);
  }
  window.fxNoteDone = function () { if (el) { el.remove(); el = null; } };
  if (document.body) show(); else document.addEventListener('DOMContentLoaded', show);
})();
