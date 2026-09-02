(function () {
  'use strict';

  const script = document.currentScript;
  const article = script && script.closest('.post-body');
  if (!article || typeof ResizeObserver === 'undefined') return;

  const sizes = new WeakMap();
  const pending = new Set();
  let frame = 0;

  function schedule(canvas) {
    pending.add(canvas);
    if (frame) return;
    frame = requestAnimationFrame(function () {
      frame = 0;
      pending.forEach(function (element) {
        if (!element.isConnected || !window.echarts) return;
        const chart = window.echarts.getInstanceByDom(element);
        if (!chart) return;
        const width = element.clientWidth;
        const height = element.clientHeight;
        const before = sizes.get(element);
        if (width <= 0 || height <= 0) return;
        if (before && before.width === width && before.height === height &&
            chart.getWidth() === width && chart.getHeight() === height) return;
        sizes.set(element, { width: width, height: height });
        chart.resize({ width: width, height: height });
      });
      pending.clear();
    });
  }

  // The sidebar transition changes content width without a window resize event.
  const observer = new ResizeObserver(function (entries) {
    entries.forEach(function (entry) { schedule(entry.target); });
  });
  article.querySelectorAll('.hexo-echarts__canvas').forEach(function (canvas) {
    observer.observe(canvas);
    schedule(canvas);
  });

  // The shared loader may create chart instances after the initial observation.
  const ready = new MutationObserver(function (records) {
    records.forEach(function (record) {
      const canvas = record.target.querySelector('.hexo-echarts__canvas');
      if (canvas) schedule(canvas);
    });
  });
  ready.observe(article, {
    subtree: true,
    attributes: true,
    attributeFilter: ['data-echarts-ready']
  });
})();
