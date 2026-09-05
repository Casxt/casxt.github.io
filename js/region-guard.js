(() => {
  let pending;

  function getCountry() {
    if (pending) return pending;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000);

    // Trace is a diagnostic endpoint: missing data or any failure allows access.
    pending = fetch('/cdn-cgi/trace', {
      signal: controller.signal,
      cache: 'no-store',
      credentials: 'omit'
    })
      .then(response => response.ok ? response.text() : '')
      .then(text => text.match(/^loc=([A-Z]{2})\r?$/m)?.[1])
      .catch(() => undefined)
      .finally(() => {
        clearTimeout(timeout);
        pending = null;
      });
    return pending;
  }

  window.bootRegionGuard = async () => {
    const notice = document.querySelector('.region-guard');
    const root = document.documentElement;
    if (notice?.dataset.started) return;
    delete root.dataset.regionGuard;
    if (!notice) return;

    notice.dataset.started = 'true';
    notice.hidden = false;
    root.dataset.regionGuard = 'checking';

    const country = await getCountry();
    // A PJAX navigation may have replaced the article while the request ran.
    if (!notice.isConnected) return;
    if (country !== 'CN') {
      delete root.dataset.regionGuard;
      notice.remove();
      window.dispatchEvent(new Event('resize'));
      return;
    }

    root.dataset.regionGuard = 'blocked';
    notice.querySelector('.region-guard__title').textContent =
      '此页面暂不支持中国大陆地区访问';
    notice.querySelector('.region-guard__message').textContent =
      '你可以返回首页浏览其他内容。';
  };

  document.addEventListener('pjax:success', window.bootRegionGuard);
})();
