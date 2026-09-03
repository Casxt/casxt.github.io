/* Article-local progressive enhancement. Tabulator 6.5.0, MIT; see tabulator-license.txt. */
(() => {
  'use strict';
  const loader = document.querySelector('script[data-uranium-tabulator-enabled]');
  if (!loader) return;
  const instances = new Map();
  const scenarioOrder = ['Bear', 'Base', 'Bull', 'Super Bull'];
  const make = (tag, className, text) => {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined) el.textContent = text;
    return el;
  };
  const numeric = value => {
    const text = String(value).trim().replace(/[，,]/g, '').replace(/[−－]/g, '-');
    if (!/^[-+]?\d/.test(text) && !/^\(\d/.test(text)) return null;
    const n = Number.parseFloat(text.replace(/^\(/, '-'));
    return Number.isFinite(n) ? n : null;
  };
  // Compound cells (quantity / growth, volume / price) sort by the first value.
  const numericSort = (a, b, _ar, _br, _column, dir) => {
    const x = numeric(a), y = numeric(b);
    if (x === null && y === null) return 0;
    if (x === null) return dir === 'asc' ? 1 : -1;
    if (y === null) return dir === 'asc' ? -1 : 1;
    return x - y;
  };

  function initialize(marker) {
    if (instances.has(marker) || typeof window.Tabulator !== 'function') return;
    const sibling = marker.nextElementSibling;
    const source = sibling?.matches('table') ? sibling : sibling?.querySelector('table');
    if (!source || !source.tHead) return;
    const headers = [...source.tHead.rows[0].cells].map(c => c.textContent.trim());
    const data = [...source.tBodies].flatMap(b => [...b.rows]).map((row, order) => {
      if (row.cells.length !== headers.length) throw new Error('Unexpected source table width');
      return Object.fromEntries([['id', order], ...[...row.cells].map((c, i) => [`c${i}`, c.textContent.trim()])]);
    });
    const name = marker.dataset.title;
    const scIndex = headers.indexOf('情景');
    const yearIndex = headers.findIndex(h => h === '年度' || h === '年份');
    const yearCols = headers.map((h, i) => ({i, year: h.match(/^(20\d{2})/)?.[1]})).filter(c => c.year);
    // A horizontal year selector is only inferred for genuine multi-year matrices.
    if (yearCols.length < 3) yearCols.length = 0;
    const years = [...new Set(yearIndex >= 0 ? data.map(r => r[`c${yearIndex}`].match(/20\d{2}/)?.[0]).filter(Boolean) : yearCols.map(c => c.year))].sort();
    const scenarios = scenarioOrder.filter(s => data.some(r => r[`c${scIndex}`] === s));
    const selectedYears = new Set(years), selectedScenarios = new Set(scenarios);
    const categoryIndex = headers.findIndex(h => /^(公司|业务|矿山|指标)(?:[：:（(]|$)/.test(h));
    const originalHidden = sibling.hidden;
    const shell = make('section', 'uranium-table-panel');
    shell.setAttribute('aria-label', name + '交互表');
    const bar = make('div', 'uranium-table-bar');
    bar.append(make('strong', '', name));
    const originalButton = make('button', '', '查看原表');
    originalButton.type = 'button';
    bar.append(originalButton); shell.append(bar);
    const interactive = make('div', 'uranium-table-interactive'); shell.append(interactive);
    const details = make('details', 'uranium-table-filters');
    const summary = make('summary', '', '筛选情景 / 年份'); details.append(summary);
    const filters = make('div', 'uranium-filter-content'); details.append(filters);
    const controls = [];
    let table, built = false, active = true, category;
    let visibleYearKey = years.join(',');
    const status = make('p', 'uranium-table-status');
    status.setAttribute('role', 'status'); status.setAttribute('aria-live', 'polite');
    function matches(row) {
      return (scIndex < 0 || selectedScenarios.has(row[`c${scIndex}`])) &&
        (yearIndex < 0 || selectedYears.has(row[`c${yearIndex}`].match(/20\d{2}/)?.[0])) &&
        (!category?.value || row[`c${categoryIndex}`] === category.value);
    }
    function refresh() {
      if (!built) return;
      const nextYearKey = [...selectedYears].sort().join(',');
      // Rebuild the small view after a year selection changes so the responsive module
      // starts with the right hidden-column set. Source data and filter controls stay intact.
      if (yearCols.length && nextYearKey !== visibleYearKey) {
        const sorts = table.getSorters().map(s => ({column: s.field, dir: s.dir}));
        const nextColumns = columns.map(column => {
          const yc = yearCols.find(c => `c${c.i}` === column.field);
          return {...column, visible: !yc || selectedYears.has(yc.year)};
        });
        visibleYearKey = nextYearKey;
        built = false; table.destroy(); mount(nextColumns, sorts); return;
      }
      table.setFilter(matches);
      table.redraw(true);
      status.textContent = `显示 ${data.filter(matches).length} / ${data.length} 行` +
        (years.length ? ` · 年份：${selectedYears.size ? [...selectedYears].sort().join('、') : '未选择'}` : '') +
        ' · 筛选仅影响本表；点击表头排序，窄屏点“＋”展开。';
      summary.textContent = `筛选情景${years.length ? ' / 年份' : ''}（${selectedScenarios.size}/${scenarios.length}情景${years.length ? `，${selectedYears.size}/${years.length}年` : ''}）`;
    }
    function checkboxGroup(label, values, chosen) {
      const fieldset = make('fieldset'); fieldset.append(make('legend', '', label + '（可多选）'));
      for (const value of values) {
        const lab = make('label', 'uranium-filter-choice');
        const input = make('input'); input.type = 'checkbox'; input.checked = true; input.value = value;
        input.addEventListener('change', () => {if (input.checked) chosen.add(value); else chosen.delete(value); refresh();});
        lab.append(input, document.createTextNode(value)); fieldset.append(lab); controls.push(input);
      }
      filters.append(fieldset);
    }
    if (scenarios.length) checkboxGroup('情景', scenarios, selectedScenarios);
    if (years.length) checkboxGroup('年份', years, selectedYears);
    if (categoryIndex >= 0) {
      const label = make('label', 'uranium-category', headers[categoryIndex].split(/[：:（(]/)[0] + ' ');
      category = make('select'); category.append(new Option('全部', ''));
      for (const value of new Set(data.map(r => r[`c${categoryIndex}`]))) category.append(new Option(value, value));
      category.addEventListener('change', refresh); label.append(category); filters.append(label);
    }
    const reset = make('button', '', '重置本表'); reset.type = 'button';
    reset.addEventListener('click', () => {
      controls.forEach(c => {c.checked = true;}); scenarios.forEach(s => selectedScenarios.add(s)); years.forEach(y => selectedYears.add(y));
      if (category) category.value = ''; table.clearSort(); refresh();
    });
    filters.append(reset, make('p', 'uranium-filter-note', '年份筛选保留原表期间口径：H2仍是下半年，E仍是预测；“量/价”等双数值格按第一个数排序。'));
    interactive.append(details, status);
    const target = make('div', 'uranium-tabulator');
    target.setAttribute('aria-label', name); interactive.append(target);
    sibling.before(shell);
    const primary = new Set([scIndex, yearIndex, categoryIndex].filter(i => i >= 0));
    const lastYear = yearCols.at(-1)?.i;
    const columns = headers.map((title, i) => {
      const field = `c${i}`, yearColumn = yearCols.some(c => c.i === i);
      const isNumeric = data.every(r => numeric(r[field]) !== null || /^[-—–]$/.test(r[field]));
      const width = i === scIndex ? 84 : i === yearIndex ? 64 : i === categoryIndex ? 122 : title.includes('量/价') || title.includes('tU/同比') ? 96 : 66;
      return {title, field, minWidth: width, widthGrow: i === categoryIndex ? 1.6 : 1,
        frozen: primary.has(i), responsive: primary.has(i) ? 0 : yearColumn ? (i === lastYear ? 1 : 3) : /^(本次2030价|2030年末合理价)$|归母净利|ROE/.test(title) ? 1 : 3,
        hozAlign: isNumeric ? 'right' : 'left', sorter: isNumeric ? numericSort : 'string',
        headerWordWrap: true, formatter: 'plaintext', variableHeight: true};
    });
    function collapseFormatter(items) {
      const list = make('dl', 'uranium-collapse-list');
      for (const item of items) {
        const c = yearCols.find(c => headers[c.i] === item.title);
        if (c && !selectedYears.has(c.year)) continue;
        list.append(make('dt', '', item.title), make('dd', '', item.value));
      }
      return list;
    }
    function restore() {
      sibling.hidden = originalHidden;
      try {table?.destroy();} catch (_) { /* Source stays available even after plugin failure. */ }
      shell.remove(); instances.delete(marker); delete marker.dataset.tabulatorReady;
    }
    instances.set(marker, {restore});
    function mount(viewColumns = columns, sorts = []) {
     try {
      table = new window.Tabulator(target, {
        data, columns: viewColumns, layout: 'fitColumns', maxHeight: '620px', index: 'id',
        responsiveLayout: 'collapse', responsiveLayoutCollapseStartOpen: false,
        responsiveLayoutCollapseUseFormatters: false, responsiveLayoutCollapseFormatter: collapseFormatter,
        placeholder: '没有匹配数据，请调整筛选或重置本表。',
        rowHeader: {formatter: 'responsiveCollapse', width: 28, minWidth: 28, hozAlign: 'center', resizable: false, headerSort: false},
        columnDefaults: {resizable: false, vertAlign: 'middle', headerHozAlign: 'center'},
        rowFormatter(row) {
          const index = scenarios.indexOf(row.getData()[`c${scIndex}`]);
          if (index >= 0) row.getElement().classList.add(`uranium-scenario-${index}`);
        }
      });
      table.on('tableBuilt', () => {
        if (!shell.isConnected) return;
        built = true; sibling.hidden = true; marker.dataset.tabulatorReady = 'true';
        if (sorts.length) table.setSort(sorts); refresh();
      });
      table.on('renderComplete', () => {
        for (const toggle of target.querySelectorAll('.tabulator-responsive-collapse-toggle')) {
          toggle.setAttribute('role', 'button'); toggle.setAttribute('aria-label', '展开或收起本行其他指标'); toggle.tabIndex = 0;
          if (!toggle.dataset.keyboardReady) {
            toggle.dataset.keyboardReady = 'true';
            toggle.addEventListener('keydown', event => {if (event.key === 'Enter' || event.key === ' ') {event.preventDefault(); toggle.click();}});
          }
        }
      });
     } catch (error) {restore(); console.warn('表格增强失败，已保留原始表格。', error);}
    }
    originalButton.addEventListener('click', () => {
      active = !active; interactive.hidden = !active; sibling.hidden = active ? true : originalHidden;
      originalButton.textContent = active ? '查看原表' : '返回交互表'; if (active) table.redraw(true);
    });
    mount();
  }
  function synchronize() {
    if (loader.dataset.uraniumTabulatorEnabled !== 'true') {for (const item of [...instances.values()]) item.restore(); return;}
    for (const marker of document.querySelectorAll('.uranium-table-marker')) {
      try {initialize(marker);} catch (error) {console.warn('表格保持原样：', error);}
    }
  }
  new MutationObserver(synchronize).observe(loader, {attributes: true, attributeFilter: ['data-uranium-tabulator-enabled']});
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', synchronize, {once: true}); else synchronize();
  document.addEventListener('pjax:success', synchronize);
})();
