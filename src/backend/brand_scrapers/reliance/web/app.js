/**
 * Reliance Digital Pro Intelligence — Frontend Application Controller
 * Handles natural query parsing, live log streaming, metric calculations,
 * dynamic brand grouping, and dual-view rendering.
 */

// Application State
let appState = {
  products: [],
  filteredProducts: [],
  selectedBrand: 'all',
  activeView: 'grid', // 'grid' or 'table'
  sortMode: 'price-asc',
  searchFilter: '',
  isScraping: false,
  pollTimer: null,
  lastLogIndex: 0
};

// DOM Element Selectors
const els = {
  scrapeForm: document.getElementById('scrapeForm'),
  queryInput: document.getElementById('queryInput'),
  searchBadgesPreview: document.getElementById('searchBadgesPreview'),
  clearSearchBtn: document.getElementById('clearSearchBtn'),
  pincodeInput: document.getElementById('pincodeInput'),
  activePincodeText: document.getElementById('activePincodeText'),
  pagesSelect: document.getElementById('pagesSelect'),
  inStockToggle: document.getElementById('inStockToggle'),
  btnExecuteScrape: document.getElementById('btnExecuteScrape'),
  serverStatusBadge: document.getElementById('serverStatusBadge'),
  serverStatusText: document.getElementById('serverStatusText'),
  
  // Progress
  progressPanel: document.getElementById('progressPanel'),
  progressStatusText: document.getElementById('progressStatusText'),
  progressPercentageText: document.getElementById('progressPercentageText'),
  progressBarFill: document.getElementById('progressBarFill'),
  consoleStream: document.getElementById('consoleStream'),
  
  // Metrics
  metricTotalHandsets: document.getElementById('metricTotalHandsets'),
  metricTotalSubtitle: document.getElementById('metricTotalSubtitle'),
  metricLowestPrice: document.getElementById('metricLowestPrice'),
  metricLowestModel: document.getElementById('metricLowestModel'),
  metricAvgPrice: document.getElementById('metricAvgPrice'),
  metricMaxDiscount: document.getElementById('metricMaxDiscount'),
  
  // Explorer
  brandFilterContainer: document.getElementById('brandFilterContainer'),
  localFilterInput: document.getElementById('localFilterInput'),
  sortSelect: document.getElementById('sortSelect'),
  viewBtnGrid: document.getElementById('viewBtnGrid'),
  viewBtnTable: document.getElementById('viewBtnTable'),
  productGrid: document.getElementById('productGrid'),
  productTableWrapper: document.getElementById('productTableWrapper'),
  productTableBody: document.getElementById('productTableBody'),
  emptyState: document.getElementById('emptyState'),
  emptyDescText: document.getElementById('emptyDescText'),
  
  // Export
  btnExportCsv: document.getElementById('btnExportCsv'),
  btnExportJson: document.getElementById('btnExportJson'),
  presetChips: document.querySelectorAll('.preset-chip')
};

// ==========================================================================
// Initialization
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  updateSearchPreviewBadge(els.queryInput.value);
  startPollingStatus();
  refreshIcons();
});

function refreshIcons() {
  if (window.lucide && typeof window.lucide.createIcons === 'function') {
    window.lucide.createIcons();
  }
}

// ==========================================================================
// Event Listeners
// ==========================================================================
function setupEventListeners() {
  // Scrape Form Submit
  els.scrapeForm.addEventListener('submit', (e) => {
    e.preventDefault();
    triggerScrape();
  });

  els.btnExecuteScrape.addEventListener('click', () => {
    triggerScrape();
  });

  // Query Input Typing (Live preview badges)
  els.queryInput.addEventListener('input', (e) => {
    updateSearchPreviewBadge(e.target.value);
  });

  // Header Create Button shortcut
  const btnCreate = document.getElementById('btnHeaderCreate');
  if (btnCreate) {
    btnCreate.addEventListener('click', () => {
      els.queryInput.focus();
      els.queryInput.select();
    });
  }

  // Clear search input
  els.clearSearchBtn.addEventListener('click', () => {
    els.queryInput.value = '';
    els.searchBadgesPreview.innerHTML = '';
    els.queryInput.focus();
  });

  // Pincode Input sync
  els.pincodeInput.addEventListener('input', (e) => {
    const val = e.target.value.replace(/\D/g, '').slice(0, 6);
    e.target.value = val;
    if (val.length === 6) {
      els.activePincodeText.textContent = val;
    }
  });

  // Quick Preset Chips
  els.presetChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const q = chip.dataset.query;
      applyPreset(q);
    });
  });

  // Local Filter & Sorting
  els.localFilterInput.addEventListener('input', (e) => {
    appState.searchFilter = e.target.value.trim().toLowerCase();
    applyFiltersAndRender();
  });

  els.sortSelect.addEventListener('change', (e) => {
    appState.sortMode = e.target.value;
    applyFiltersAndRender();
  });

  // Live in-stock toggle
  els.inStockToggle.addEventListener('change', () => {
    applyFiltersAndRender();
  });

  // View Switcher
  els.viewBtnGrid.addEventListener('click', () => {
    setViewMode('grid');
  });

  els.viewBtnTable.addEventListener('click', () => {
    setViewMode('table');
  });

  // Export Buttons
  els.btnExportCsv.addEventListener('click', () => {
    window.location.href = '/api/export-csv';
  });

  els.btnExportJson.addEventListener('click', () => {
    window.location.href = '/api/export-json';
  });
}

function applyPreset(query) {
  els.queryInput.value = query;
  updateSearchPreviewBadge(query);
  
  els.presetChips.forEach(c => {
    c.classList.toggle('active', c.dataset.query === query);
  });

  triggerScrape();
}

// ==========================================================================
// Natural Query Live Badge Preview
// ==========================================================================
function updateSearchPreviewBadge(query) {
  if (!query || !query.trim()) {
    els.searchBadgesPreview.innerHTML = '';
    return; 
  }

  const q = query.toLowerCase();
  const badges = [];

  // Budget detection (e.g. under 30k, < 25000)
  const budgetMatch = q.match(/(?:under|below|less\s+than|<=|<)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k|thousand|lakh|l)?\b/);
  if (budgetMatch) {
    let val = parseFloat(budgetMatch[1]);
    const unit = (budgetMatch[2] || '').toLowerCase();
    if (unit === 'k' || unit === 'thousand') val *= 1000;
    else if (unit === 'l' || unit === 'lakh') val *= 100000;
    badges.push(`<span class="preview-badge budget">Max ₹${val.toLocaleString()}</span>`);
  }

  // Brand detection
  const brands = ['apple', 'oneplus', 'samsung', 'poco', 'realme', 'vivo', 'oppo', 'xiaomi', 'redmi', 'motorola', 'google', 'nothing', 'iqoo'];
  for (const b of brands) {
    if (new RegExp('\\b' + b + '\\b').test(q)) {
      badges.push(`<span class="preview-badge brand">${b.toUpperCase()}</span>`);
      break;
    }
  }

  // Modifier detection
  if (/\b5g\b/.test(q)) badges.push(`<span class="preview-badge">5G</span>`);
  if (/\bpro\b/.test(q)) badges.push(`<span class="preview-badge">PRO</span>`);
  if (/\bultra\b/.test(q)) badges.push(`<span class="preview-badge">ULTRA</span>`);
  if (/\bneo\b/.test(q)) badges.push(`<span class="preview-badge">NEO</span>`);

  els.searchBadgesPreview.innerHTML = badges.join('');
}

// ==========================================================================
// Scraper Trigger & Job Dispatch
// ==========================================================================
async function triggerScrape() {
  const query = els.queryInput.value.trim();
  if (!query) {
    els.queryInput.focus();
    return;
  }

  const pincode = els.pincodeInput.value.trim() || '110058';
  const pages = parseInt(els.pagesSelect.value, 10) || 2;
  const inStockOnly = els.inStockToggle.checked;

  els.btnExecuteScrape.disabled = true;
  els.btnExecuteScrape.innerHTML = `<span class="radar-scan-icon"></span> <span>SCANNING...</span>`;
  appState.isScraping = true;
  els.serverStatusText.textContent = "SCRAPING IN PROGRESS";
  els.serverStatusBadge.classList.add("running");

  appendConsoleLog(`[${new Date().toLocaleTimeString()}] Dispatching scrape request for '${query}' to Reliance Digital API...`, 'info');

  try {
    const res = await fetch('/api/scrape', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        pages: pages,
        pincode: pincode,
        in_stock_only: inStockOnly
      })
    });

    const data = await res.json();
    if (!res.ok) {
      appendConsoleLog(`[ERROR] ${data.error || 'Request rejected'}`, 'error');
      appState.isScraping = false;
      els.btnExecuteScrape.disabled = false;
      els.btnExecuteScrape.innerHTML = `<i data-lucide="zap" class="btn-icon"></i> <span>LAUNCH SCRAPER</span>`;
      refreshIcons();
    }
  } catch (err) {
    appendConsoleLog(`[ERROR] Network failed: ${err.message}`, 'error');
    appState.isScraping = false;
    els.btnExecuteScrape.disabled = false;
    els.btnExecuteScrape.innerHTML = `<i data-lucide="zap" class="btn-icon"></i> <span>LAUNCH SCRAPER</span>`;
    refreshIcons();
  }
}

// ==========================================================================
// Status Polling Engine
// ==========================================================================
function startPollingStatus() {
  if (appState.pollTimer) clearInterval(appState.pollTimer);

  const poll = async () => {
    try {
      const res = await fetch('/api/status');
      if (res.ok) {
        const state = await res.json();
        updateUIFromState(state);
      }
    } catch (e) {
      console.warn("Poll status check:", e);
    }
  };

  poll();
  appState.pollTimer = setInterval(poll, 900);
}

function updateUIFromState(state) {
  const isRunning = (state.status === 'running');
  appState.isScraping = isRunning;

  // Update progress bar
  const pct = Math.max(0, Math.min(100, state.progress || 0));
  els.progressBarFill.style.width = `${pct}%`;
  els.progressPercentageText.textContent = `${pct}%`;

  if (isRunning) {
    els.progressStatusText.textContent = "Scanning Reliance Digital Handset Catalog...";
    els.serverStatusText.textContent = "SCANNING LIVE CATALOG";
    els.serverStatusBadge.classList.add("running");
  } else {
    els.progressStatusText.textContent = state.status === 'completed' ? "Scan Complete — Handsets Isolated" : "Engine Ready";
    els.serverStatusText.textContent = "ENGINE READY";
    els.serverStatusBadge.classList.remove("running");
    
    els.btnExecuteScrape.disabled = false;
    els.btnExecuteScrape.innerHTML = `<i data-lucide="zap" class="btn-icon"></i> <span>LAUNCH SCRAPER</span>`;
    refreshIcons();
  }

  // Update Streaming Logs
  if (Array.isArray(state.logs) && state.logs.length > 0) {
    renderConsoleLogs(state.logs);
  }

  // Update Products if changed
  if (Array.isArray(state.products)) {
    // Check if products array changed
    const currentLen = appState.products.length;
    const newLen = state.products.length;
    const currentFirstSlug = currentLen ? appState.products[0].url : '';
    const newFirstSlug = newLen ? state.products[0].url : '';

    if (currentLen !== newLen || currentFirstSlug !== newFirstSlug) {
      appState.products = state.products;
      updateMetrics(state.products);
      renderBrandFilterPills(state.products);
      applyFiltersAndRender();
    }
  }

  // Update Pincode badge
  if (state.pincode) {
    els.activePincodeText.textContent = state.pincode;
  }
}

function renderConsoleLogs(logs) {
  els.consoleStream.innerHTML = '';
  logs.forEach(item => {
    const div = document.createElement('div');
    div.className = 'log-line';
    if (item.msg.includes('ERROR')) div.classList.add('error');
    else if (item.msg.includes('complete') || item.msg.includes('verified')) div.classList.add('success');
    else if (item.msg.includes('warning') || item.msg.includes('Fallback')) div.classList.add('warn');
    else div.classList.add('info');

    div.textContent = `[${item.time}] ${item.msg}`;
    els.consoleStream.appendChild(div);
  });
  els.consoleStream.scrollTop = els.consoleStream.scrollHeight;
}

function appendConsoleLog(msg, type = 'info') {
  const div = document.createElement('div');
  div.className = `log-line ${type}`;
  div.textContent = msg;
  els.consoleStream.appendChild(div);
  els.consoleStream.scrollTop = els.consoleStream.scrollHeight;
}

// ==========================================================================
// Metrics Calculation
// ==========================================================================
function updateMetrics(products) {
  const inStockList = products.filter(p => p.in_stock);
  const total = inStockList.length;

  els.metricTotalHandsets.textContent = total;
  els.metricTotalSubtitle.textContent = `${products.length} Total Handset Variants Found`;

  if (products.length === 0) {
    els.metricLowestPrice.textContent = '₹0';
    els.metricLowestModel.textContent = '—';
    els.metricAvgPrice.textContent = '₹0';
    els.metricMaxDiscount.textContent = '0%';
    return;
  }

  // Lowest price
  const prices = products.map(p => p.price_num).filter(p => p > 0);
  const minPrice = prices.length ? Math.min(...prices) : 0;
  const lowestProd = products.find(p => p.price_num === minPrice);

  els.metricLowestPrice.textContent = `₹${minPrice.toLocaleString()}`;
  els.metricLowestModel.textContent = lowestProd ? (lowestProd.brand + ' ' + (lowestProd.specs[0] || '')) : '—';

  // Average price
  const sum = prices.reduce((a, b) => a + b, 0);
  const avg = prices.length ? Math.round(sum / prices.length) : 0;
  els.metricAvgPrice.textContent = `₹${avg.toLocaleString()}`;

  // Max discount
  let maxDisc = 0;
  products.forEach(p => {
    const match = (p.discount || '').match(/(\d+)/);
    if (match) {
      const val = parseInt(match[1], 10);
      if (val > maxDisc) maxDisc = val;
    }
  });
  els.metricMaxDiscount.textContent = `${maxDisc}% OFF`;

  // Synchronize Executive Widgets (Figma Frosted Glass Cards)
  const wTotal = document.getElementById('widgetTotalHandsets');
  if (wTotal) wTotal.textContent = products.length;

  const wInStock = document.getElementById('widgetInStockCount');
  if (wInStock) wInStock.textContent = inStockList.length;

  const wOutOfStock = document.getElementById('widgetOutOfStockCount');
  if (wOutOfStock) wOutOfStock.textContent = products.length - inStockList.length;

  const wTrackBar = document.getElementById('widgetTrackBar');
  if (wTrackBar && products.length > 0) {
    const pct = Math.min(100, Math.round((inStockList.length / products.length) * 100));
    wTrackBar.style.width = `${pct}%`;
  }

  const wMonthPct = document.getElementById('widgetMonthPct');
  const ringFill = document.getElementById('ringFillBar');
  const ringPctText = document.getElementById('ringPercentageText');
  if (wMonthPct && products.length > 0) {
    const pct = Math.round((inStockList.length / products.length) * 100);
    wMonthPct.textContent = `${pct}%`;
    if (ringPctText) ringPctText.textContent = `${pct}%`;
    if (ringFill) {
      const offset = 251.2 - (251.2 * pct) / 100;
      ringFill.style.strokeDashoffset = offset;
    }
  }

  const pinDisplay = document.getElementById('widgetPinDisplay');
  if (pinDisplay && els.pincodeInput) {
    pinDisplay.textContent = els.pincodeInput.value || '110058';
  }
}

// ==========================================================================
// Brand Filter Pills
// ==========================================================================
function renderBrandFilterPills(products) {
  const counts = {};
  products.forEach(p => {
    const b = (p.brand || 'Other').trim();
    counts[b] = (counts[b] || 0) + 1;
  });

  const total = products.length;
  let html = `<button type="button" class="brand-pill ${appState.selectedBrand === 'all' ? 'active' : ''}" data-brand="all">All (${total})</button>`;

  Object.keys(counts).sort().forEach(brand => {
    const isAct = (appState.selectedBrand.toLowerCase() === brand.toLowerCase());
    html += `<button type="button" class="brand-pill ${isAct ? 'active' : ''}" data-brand="${brand}">${brand} (${counts[brand]})</button>`;
  });

  els.brandFilterContainer.innerHTML = html;

  // Add click handlers
  els.brandFilterContainer.querySelectorAll('.brand-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      els.brandFilterContainer.querySelectorAll('.brand-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      appState.selectedBrand = btn.dataset.brand;
      applyFiltersAndRender();
    });
  });
}

// ==========================================================================
// Product Filtering, Sorting & Rendering
// ==========================================================================
function applyFiltersAndRender() {
  let list = [...appState.products];

  // In-Stock Live Filter
  if (els.inStockToggle && els.inStockToggle.checked) {
    list = list.filter(p => p.in_stock);
  }

  // Brand Filter
  if (appState.selectedBrand && appState.selectedBrand !== 'all') {
    list = list.filter(p => (p.brand || '').toLowerCase() === appState.selectedBrand.toLowerCase());
  }

  // Local Search Filter
  if (appState.searchFilter) {
    const sf = appState.searchFilter;
    list = list.filter(p => {
      const titleMatch = (p.title || '').toLowerCase().includes(sf);
      const specsMatch = (p.specs || []).some(s => s.toLowerCase().includes(sf));
      const modelMatch = (p.model || '').toLowerCase().includes(sf);
      return titleMatch || specsMatch || modelMatch;
    });
  }

  // Sorting
  switch (appState.sortMode) {
    case 'price-asc':
      list.sort((a, b) => a.price_num - b.price_num);
      break;
    case 'price-desc':
      list.sort((a, b) => b.price_num - a.price_num);
      break;
    case 'discount-desc':
      list.sort((a, b) => {
        const da = parseInt((a.discount || '0').match(/\d+/) || 0, 10);
        const db = parseInt((b.discount || '0').match(/\d+/) || 0, 10);
        return db - da;
      });
      break;
    case 'rating-desc':
      list.sort((a, b) => (b.rating || 0) - (a.rating || 0));
      break;
  }

  appState.filteredProducts = list;

  if (list.length === 0) {
    els.emptyState.style.display = 'flex';
    els.productGrid.style.display = 'none';
    els.productTableWrapper.style.display = 'none';
    els.emptyDescText.textContent = `No handsets matched your current filters (Brand: ${appState.selectedBrand}, Filter: '${appState.searchFilter || 'none'}').`;
  } else {
    els.emptyState.style.display = 'none';
    if (appState.activeView === 'grid') {
      els.productGrid.style.display = 'grid';
      els.productTableWrapper.style.display = 'none';
      renderGridCards(list);
    } else {
      els.productGrid.style.display = 'none';
      els.productTableWrapper.style.display = 'block';
      renderTableView(list);
    }
  }

  refreshIcons();
}

// Render Grid Cards
function renderGridCards(products) {
  els.productGrid.innerHTML = products.map(p => {
    const stockClass = p.in_stock ? 'in-stock' : 'out-of-stock';
    const specsHtml = (p.specs || []).map((s, idx) => {
      const isAccent = (idx === 0 || s.includes('GB') || s.includes('5G'));
      return `<span class="spec-chip ${isAccent ? 'accent' : ''}">${escapeHtml(s)}</span>`;
    }).join('');

    return `
      <div class="product-card">
        <div class="card-top">
          <div class="card-media-wrap">
            <img src="${escapeHtml(p.image_url)}" alt="${escapeHtml(p.title)}" class="product-img" loading="lazy" onerror="this.src='https://www.reliancedigital.in/build/client/images/loaders/rd_phone_placeholder.png'">
            <div class="card-badges">
              <span class="badge-brand">${escapeHtml(p.brand)}</span>
              <span class="badge-stock ${stockClass}">${p.availability}</span>
            </div>
            ${p.discount && p.discount !== '0%' ? `<span class="badge-discount-float">${escapeHtml(p.discount)}</span>` : ''}
          </div>

          <div class="card-info">
            <h4 class="product-title" title="${escapeHtml(p.title)}">${escapeHtml(p.title)}</h4>
            <div class="specs-row">
              ${specsHtml}
            </div>
          </div>
        </div>

        <div class="card-bottom">
          <div class="pricing-row">
            <div class="price-main">${escapeHtml(p.price)}</div>
            <div class="price-meta">
              ${p.mrp && p.mrp !== p.price ? `<span class="mrp-strike">${escapeHtml(p.mrp)}</span>` : ''}
              <div class="rating-pill">
                <i data-lucide="star" class="rating-star-icon"></i>
                <span>${p.rating || 4.3}</span>
              </div>
            </div>
          </div>

          <div class="card-actions">
            <a href="${escapeHtml(formatProductUrl(p.url, p.slug))}" target="_blank" rel="noopener noreferrer" class="${p.in_stock ? 'btn-card-cta' : 'btn-card-cta unavail'}">
              <span>${p.in_stock ? 'View on Reliance Digital' : 'Check Store / Notify Me'}</span>
              <i data-lucide="${p.in_stock ? 'external-link' : 'bell'}" class="btn-icon"></i>
            </a>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// Render Data Table View
function renderTableView(products) {
  els.productTableBody.innerHTML = products.map(p => {
    const stockClass = p.in_stock ? 'in-stock' : 'out-of-stock';
    const specsText = (p.specs || []).slice(0, 3).join(', ');

    return `
      <tr>
        <td>
          <img src="${escapeHtml(p.image_url)}" alt="${escapeHtml(p.title)}" class="table-thumb" loading="lazy">
        </td>
        <td>
          <div class="table-title">${escapeHtml(p.title)}</div>
        </td>
        <td><span class="badge-brand">${escapeHtml(p.brand)}</span></td>
        <td><span class="table-price">${escapeHtml(p.price)}</span></td>
        <td><span class="table-mrp">${escapeHtml(p.mrp || '—')}</span></td>
        <td><span class="table-discount">${escapeHtml(p.discount || '0%')}</span></td>
        <td><span class="badge-stock ${stockClass}">${p.availability}</span></td>
        <td><span class="spec-chip">${escapeHtml(specsText || 'Handset')}</span></td>
        <td>
          <a href="${escapeHtml(formatProductUrl(p.url, p.slug))}" target="_blank" rel="noopener noreferrer" class="${p.in_stock ? 'table-action-link' : 'table-action-link unavail'}">
            <span>${p.in_stock ? 'Buy' : 'Notify'}</span>
            <i data-lucide="${p.in_stock ? 'external-link' : 'bell'}" style="width:14px;height:14px;"></i>
          </a>
        </td>
      </tr>
    `;
  }).join('');
}

function setViewMode(mode) {
  appState.activeView = mode;
  els.viewBtnGrid.classList.toggle('active', mode === 'grid');
  els.viewBtnTable.classList.toggle('active', mode === 'table');
  applyFiltersAndRender();
}

function formatProductUrl(url, slug) {
  if (!url && !slug) return 'https://www.reliancedigital.in';
  let target = url || (slug ? `https://www.reliancedigital.in/product/${slug}` : 'https://www.reliancedigital.in');
  // Strip trailing /p or /p?query (e.g. reliancedigital.in/slug/p -> reliancedigital.in/slug)
  target = target.replace(/\/p(?=[\/?#]|$)/g, '');
  // Canonical route format for Reliance Digital products is /product/{slug}
  if (target.includes('reliancedigital.in') && !target.includes('/product/') && !target.includes('/products')) {
    target = target.replace('reliancedigital.in/', 'reliancedigital.in/product/');
  }
  return target;
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
