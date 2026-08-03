(() => {
  'use strict';

  const loader = document.querySelector('script[data-operator-tabulator-enabled]');
  if (loader?.dataset.operatorTabulatorEnabled !== 'true') return;

  const percentValue = value => {
    const parsed = Number.parseFloat(String(value).replace('%', ''));
    return Number.isFinite(parsed) ? parsed : Number.NEGATIVE_INFINITY;
  };

  const percentSorter = (a, b) => percentValue(a) - percentValue(b);

  function initializeTable(marker) {
    if (marker.dataset.tabulatorReady === 'true' || typeof window.Tabulator !== 'function') return;

    const sibling = marker.nextElementSibling;
    const sourceTable = sibling?.matches('table') ? sibling : sibling?.querySelector('table');
    if (!sourceTable) return;

    const company = marker.dataset.company || '运营商';
    const table = new window.Tabulator(sourceTable, {
      layout: 'fitColumns',
      maxHeight: '560px',
      responsiveLayout: 'collapse',
      responsiveLayoutCollapseStartOpen: false,
      rowHeader: {
        formatter: 'responsiveCollapse',
        width: 34,
        minWidth: 34,
        hozAlign: 'center',
        resizable: false,
        headerSort: false
      },
      columnDefaults: {
        headerHozAlign: 'center',
        vertAlign: 'middle',
        resizable: false
      },
      columns: [
        { title: '业务', field: '业务', width: 104, minWidth: 92, frozen: true, responsive: 0 },
        { title: '情景', field: '情景', width: 70, minWidth: 64, frozen: true, responsive: 0 },
        { title: '2026E', field: '2026E', minWidth: 68, hozAlign: 'right', sorter: percentSorter, responsive: 1 },
        { title: '2027E', field: '2027E', minWidth: 68, hozAlign: 'right', sorter: percentSorter, responsive: 4 },
        { title: '2028E', field: '2028E', minWidth: 68, hozAlign: 'right', sorter: percentSorter, responsive: 3 },
        { title: '2029E', field: '2029E', minWidth: 68, hozAlign: 'right', sorter: percentSorter, responsive: 2 },
        { title: '2030E', field: '2030E', minWidth: 68, hozAlign: 'right', sorter: percentSorter, responsive: 1 },
        {
          title: '2025—2030 CAGR',
          titleFormatter: () => 'CAGR',
          field: '2025—2030 CAGR',
          minWidth: 84,
          hozAlign: 'right',
          sorter: percentSorter,
          responsive: 0
        }
      ],
      rowFormatter(row) {
        const scenario = String(row.getData()['情景'] || '').toLowerCase();
        if (scenario) row.getElement().classList.add(`operator-scenario-${scenario}`);
      }
    });

    table.element.classList.add('operator-tabulator');
    table.element.setAttribute('aria-label', `${company} 2026至2030年分业务收入增速`);
    marker.dataset.tabulatorReady = 'true';
  }

  function initializeTables() {
    document.querySelectorAll('.operator-growth-table-marker').forEach(initializeTable);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTables, { once: true });
  } else {
    initializeTables();
  }
  document.addEventListener('pjax:success', initializeTables);
})();
