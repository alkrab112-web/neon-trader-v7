/* ========= أمان بسيط: تخزين هاش كلمة المرور محليًا ========= */
// ===== Helpers & Storage =====
const $ = s => document.querySelector(s);
const $$ = s => Array.from(document.querySelectorAll(s));
const LS = {
  get: (k, def) => {
    try {
      const v = localStorage.getItem(k);
      return v ? JSON.parse(v) : def;
    } catch (e) {
      return def;
    }
  },
  set: (k, v) => {
    try {
      localStorage.setItem(k, JSON.stringify(v));
    } catch (e) {
      console.warn('فشل في حفظ localStorage:', e);
    }
  }
};

// ===== State & Settings =====
const state = { loggedIn: true, connected: false };
const settings = LS.get('v77_settings', { startBalance: 10000, feeBps: 4, slipBps: 5, posMode: 'net', oneTradeOnly: true });
let account = LS.get('v77_account', { balance: settings.startBalance, realized: 0 });

const model = {
  pending: LS.get('v77_pending', []),
  open: LS.get('v77_open', []),
  closed: LS.get('v77_closed', []),
  seq: LS.get('v77_seq', 1),
  save() {
    LS.set('v77_pending', this.pending);
    LS.set('v77_open', this.open);
    LS.set('v77_closed', this.closed);
    LS.set('v77_seq', this.seq);
    LS.set('v77_account', account);
    LS.set('v77_settings', settings);
  }
};

// ===== Price Ticker (demo) =====
const price = {
  map: LS.get('v77_prices', { 'BTC/USDT': 60000, 'ETH/USDT': 3000, 'SOL/USDT': 150 }),
  timer: null,
  step() {
    for (const p in this.map) {
      const base = this.map[p];
      const vol = p.startsWith('BTC') ? 80 : p.startsWith('ETH') ? 10 : 2.2;
      const drift = (Math.random() - 0.5) * vol * 0.3;
      this.map[p] = Math.max(0.0001, +(base + drift).toFixed(2));
    }
    LS.set('v77_prices', this.map);
    onTick();
  },
  start() {
    if (this.timer) return;
    this.timer = setInterval(() => this.step(), 1100);
    const status = $('#tickerStatus');
    if (status) status.textContent = 'السوق: يعمل';
  },
  stop() {
    clearInterval(this.timer);
    this.timer = null;
    const status = $('#tickerStatus');
    if (status) status.textContent = 'السوق: متوقف';
  }
};

// ===== UI helpers =====
function toast(msg) {
  const t = $('#toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 1700);
}

const UI = {
  money(v) {
    const s = (v >= 0 ? '+' : '') + v.toFixed(2);
    const c = v >= 0 ? 'var(--ok)' : 'var(--err)';
    return `<span class="pl" style="color:${c}">${s}</span>`;
  },
  pct(v) {
    const s = (v >= 0 ? '+' : '') + v.toFixed(2) + '%';
    const c = v >= 0 ? 'var(--ok)' : 'var(--err)';
    return `<span style="color:${c}">${s}</span>`;
  },
  refreshBadges() {
    let u = 0;
    for (const t of model.open) {
      const now = price.map[t.pair] || t.entryPrice;
      u += (t.side === 'BUY') ? (now - t.entryPrice) * t.qty : (t.entryPrice - now) * t.qty;
    }
    const uPnL = $('#uPnL');
    const eq = $('#eq');
    const rPnL = $('#rPnL');
    if (uPnL) uPnL.textContent = u.toFixed(2);
    if (eq) eq.textContent = '$' + (account.balance + u).toFixed(2);
    if (rPnL) rPnL.textContent = account.realized.toFixed(2);
  },
  refreshOpenPL() {
    $$('#openTbl tbody tr').forEach(tr => {
      const id = +tr.dataset.id;
      const t = model.open.find(x => x.id === id);
      if (!t) return;
      const now = price.map[t.pair] || t.entryPrice;
      const nowCell = tr.querySelector('[data-col="now"]');
      if (nowCell) nowCell.textContent = now.toFixed(2);

      const pnl = (t.side === 'BUY') ? (now - t.entryPrice) * t.qty : (t.entryPrice - now) * t.qty;
      const plCell = tr.querySelector('[data-col="pl"]');
      if (plCell) plCell.innerHTML = UI.money(pnl);

      const capital = (t.entryPrice * t.qty) / t.lev;
      const roi = capital > 0 ? (pnl / capital) * 100 : 0;
      const roiCell = tr.querySelector('[data-col="roi"]');
      if (roiCell) roiCell.innerHTML = UI.pct(roi);
    });
  },
  renderEmptyFlags() {
    const pendEmpty = $('#pendEmpty');
    const openEmpty = $('#openEmpty');
    const closedEmpty = $('#closedEmpty');
    const exEmpty = $('#exEmpty');
    if (pendEmpty) pendEmpty.style.display = model.pending.length ? 'none' : 'block';
    if (openEmpty) openEmpty.style.display = model.open.length ? 'none' : 'block';
    if (closedEmpty) closedEmpty.style.display = model.closed.length ? 'none' : 'block';
    if (exEmpty) exEmpty.style.display = exModel.list.length ? 'none' : 'block';
  },
  renderPending() {
    const tb = $('#pendTbl tbody');
    if (!tb) return;
    tb.innerHTML = '';
    model.pending.forEach(o => {
      const tr = document.createElement('tr');
      tr.dataset.id = o.id;
      const priceCell = o.kind === 'oco-stop' ? (o.stop?.toFixed?.(2) ?? '-') : (o.limit?.toFixed?.(2) ?? '-');
      tr.innerHTML = `<td>${o.id}</td><td>${o.pair}</td><td><span class="plat-badge"><span class="plat-logo ${platformLogoClass(o.ex)}"></span>${o.ex}</span></td><td>${o.side}</td><td>${priceCell}</td><td>${o.qty}</td>
      <td>${o.sl || '-'}</td><td>${o.tp || '-'}</td><td>${o.trailPct || '-'}</td><td>${o.kind || '-'}</td>
      <td><button class="btn" data-act="cancel" title="إلغاء الأمر">إلغاء</button></td>`;
      tb.appendChild(tr);
    });
    const pendCount = $('#pendCount');
    if (pendCount) pendCount.textContent = model.pending.length;
    UI.renderEmptyFlags();
  },
  renderOpen() {
    const tb = $('#openTbl tbody');
    if (!tb) return;
    tb.innerHTML = '';
    model.open.forEach(t => {
      const now = price.map[t.pair] || t.entryPrice;
      const pnl = (t.side === 'BUY') ? (now - t.entryPrice) * t.qty : (t.entryPrice - now) * t.qty;
      const capital = (t.entryPrice * t.qty) / t.lev;
      const roi = capital > 0 ? (pnl / capital) * 100 : 0;
      const tr = document.createElement('tr');
      tr.dataset.id = t.id;
      tr.innerHTML = `<td>${t.id}</td><td>${t.pair}</td><td><span class="plat-badge"><span class="plat-logo ${platformLogoClass(t.ex)}"></span>${t.ex}</span></td><td>${t.side}</td><td>${t.lev}x</td><td>${t.qty}</td>
      <td>${t.entryPrice.toFixed(2)}</td><td data-col="now">${now.toFixed(2)}</td>
      <td data-col="pl">${UI.money(pnl)}</td><td data-col="roi">${UI.pct(roi)}</td>
      <td><input data-edit="sl" class="input" style="width:90px" value="${t.sl ?? ''}" placeholder="-"/></td>
      <td><input data-edit="tp" class="input" style="width:90px" value="${t.tp ?? ''}" placeholder="-"/></td>
      <td><input data-edit="trail" class="input" style="width:80px" value="${t.trailPct ?? ''}" placeholder="-"/></td>
      <td>
        <button class="btn" data-act="be" title="Breakeven">BE</button>
        <button class="btn" data-act="close" title="إغلاق">إغلاق</button>
        <button class="btn" data-act="half" title="إغلاق 50%">50%</button>
      </td>`;
      tb.appendChild(tr);
    });
    const openCount = $('#openCount');
    if (openCount) openCount.textContent = model.open.length;
    UI.renderEmptyFlags();
  },
  renderClosed() {
    const tb = $('#closedTbl tbody');
    if (!tb) return;
    tb.innerHTML = '';
    model.closed.forEach(t => {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${t.id}</td><td>${t.pair}</td><td><span class="plat-badge"><span class="plat-logo ${platformLogoClass(t.ex)}"></span>${t.ex}</span></td><td>${t.side}</td><td>${t.lev}x</td><td>${t.qty}</td>
      <td>${t.entryPrice.toFixed(2)}</td><td>${t.exitPrice.toFixed(2)}</td><td>${t.fees.toFixed(2)}</td>
      <td>${UI.money(t.netPL)}</td><td>${UI.pct(t.roi)}</td><td>${t.reason || '-'}</td><td>${new Date(t.closedAt).toLocaleString()}</td>`;
      tb.appendChild(tr);
    });
    const closedCount = $('#closedCount');
    if (closedCount) closedCount.textContent = model.closed.length;
    UI.renderEmptyFlags();
  }
};

function platformLogoClass(name) {
  const n = (name || '').toLowerCase();
  if (n === 'binance') return 'plat-binance';
  if (n === 'bybit') return 'plat-bybit';
  if (n === 'okx') return 'plat-okx';
  if (n === 'coinbase') return 'plat-coinbase';
  if (n === 'kucoin') return 'plat-kucoin';
  if (n === 'kraken') return 'plat-kraken';
  if (n === 'bitget') return 'plat-bitget';
  if (n === 'gate.io' || n === 'gate') return 'plat-gate';
  return 'plat-okx';
}

// ===== Position Mode =====
const positionMode = {
  addOrAppend(t) {
    if (settings.posMode !== 'net') {
      model.open.push(t);
      model.save();
      return;
    }
    const ex = model.open.find(x => x.pair === t.pair && x.side === t.side && x.lev === t.lev);
    if (!ex) {
      model.open.push(t);
      model.save();
      return;
    }
    const total = ex.qty + t.qty;
    ex.entryPrice = ((ex.entryPrice * ex.qty) + (t.entryPrice * t.qty)) / total;
    ex.qty = +total.toFixed(4);
    ex.feeOpen = (ex.feeOpen || 0) + (t.feeOpen || 0);
    ex.sl = t.sl ?? ex.sl;
    ex.tp = t.tp ?? ex.tp;
    ex.trailPct = t.trailPct ?? ex.trailPct;
    model.save();
  }
};

// ===== Engine =====
function onTick() {
  UI.refreshOpenPL();
  tryFillPending();
  updateTrails();
  checkStopsTargets();
  UI.refreshBadges();
  UI.renderPending();
}

function tryFillPending() {
  const filled = [];
  for (const o of model.pending) {
    if (o.kind === 'oco-limit') {
      const px = price.map[o.pair] || o.limit || null;
      if (!px) continue;
      const fill = (o.side === 'BUY') ? (px <= o.limit) : (px >= o.limit);
      if (fill) {
        const slip = px * (settings.slipBps / 10000) * (o.side === 'BUY' ? +1 : -1);
        const entry = px + slip;
        const id = model.seq++;
        const feeOpen = (entry * o.qty) * (settings.feeBps / 10000);
        const t = {
          id, ex: o.ex, pair: o.pair, side: o.side, qty: o.qty, lev: o.lev,
          entryPrice: entry, sl: o.sl || null, tp: o.tp || null, trailPct: o.trailPct || null,
          trailAnchor: null, openedAt: Date.now(), feeOpen
        };
        positionMode.addOrAppend(t);
        filled.push(o.id);
        model.pending = model.pending.filter(x => !(x.group === o.group && x.id !== o.id));
        toast('OCO: تم تنفيذ Limit وأُلغي Stop');
      }
    } else if (o.kind === 'oco-stop') {
      const px = price.map[o.pair] || o.stop || null;
      if (!px) continue;
      const trig = (o.side === 'BUY') ? (px >= o.stop) : (px <= o.stop);
      if (trig) {
        const slip = px * (settings.slipBps / 10000) * (o.side === 'BUY' ? +1 : -1);
        const entry = px + slip;
        const id = model.seq++;
        const feeOpen = (entry * o.qty) * (settings.feeBps / 10000);
        const t = {
          id, ex: o.ex, pair: o.pair, side: o.side, qty: o.qty, lev: o.lev,
          entryPrice: entry, sl: o.sl || null, tp: o.tp || null, trailPct: o.trailPct || null,
          trailAnchor: null, openedAt: Date.now(), feeOpen
        };
        positionMode.addOrAppend(t);
        filled.push(o.id);
        model.pending = model.pending.filter(x => !(x.group === o.group && x.id !== o.id));
        toast('OCO: تم تنفيذ Stop وأُلغي Limit');
      }
    } else {
      if (o.limit) {
        const px = price.map[o.pair] || o.limit || null;
        if (!px) continue;
        const fill = (o.side === 'BUY') ? (px <= o.limit) : (px >= o.limit);
        if (fill) {
          const slip = px * (settings.slipBps / 10000) * (o.side === 'BUY' ? +1 : -1);
          const entry = px + slip;
          const id = model.seq++;
          const feeOpen = (entry * o.qty) * (settings.feeBps / 10000);
          const t = {
            id, ex: o.ex, pair: o.pair, side: o.side, qty: o.qty, lev: o.lev,
            entryPrice: entry, sl: o.sl || null, tp: o.tp || null, trailPct: o.trailPct || null,
            trailAnchor: null, openedAt: Date.now(), feeOpen
          };
          positionMode.addOrAppend(t);
          filled.push(o.id);
          toast('تم تنفيذ Limit #' + id);
        }
      }
    }
  }
  if (filled.length) {
    model.pending = model.pending.filter(x => !filled.includes(x.id));
    model.save();
    UI.renderPending();
    UI.renderOpen();
    UI.refreshOpenPL();
    UI.refreshBadges();
  }
}

function updateTrails() {
  for (const t of model.open) {
    if (!t.trailPct) continue;
    const now = price.map[t.pair] || t.entryPrice;
    const dist = (t.trailPct / 100) * t.entryPrice;
    if (t.side === 'BUY') {
      if (!t.trailAnchor || now > t.trailAnchor) t.trailAnchor = now;
      const sl = t.trailAnchor - dist;
      if (!t.sl || sl > t.sl) t.sl = +sl.toFixed(2);
    } else {
      if (!t.trailAnchor || now < t.trailAnchor) t.trailAnchor = now;
      const sl = t.trailAnchor + dist;
      if (!t.sl || sl < t.sl) t.sl = +sl.toFixed(2);
    }
  }
}

function checkStopsTargets() {
  const toClose = [];
  for (const t of model.open) {
    const now = price.map[t.pair] || t.entryPrice;
    if (t.tp && ((t.side === 'BUY' && now >= t.tp) || (t.side === 'SELL' && now <= t.tp))) {
      toClose.push({ id: t.id, reason: 'TP' });
      continue;
    }
    if (t.sl && ((t.side === 'BUY' && now <= t.sl) || (t.side === 'SELL' && now >= t.sl))) {
      toClose.push({ id: t.id, reason: 'SL/Trail' });
      continue;
    }
  }
  if (toClose.length) {
    for (const c of toClose) {
      closeTrade(c.id, c.reason);
    }
  }
}

// ===== Exchange helpers =====
window.exModel = window.exModel || {
  list: LS.get('v77_exchanges', [
    { name: 'Binance', key: 'binance', connected: false, sim: true, balance: 10000, apiKey: '', apiSecret: '' },
    { name: 'Bybit', key: 'bybit', connected: false, sim: true, balance: 10000, apiKey: '', apiSecret: '' },
    { name: 'OKX', key: 'okx', connected: false, sim: true, balance: 10000, apiKey: '', apiSecret: '' },
  ])
};

function exSave() {
  LS.set('v77_exchanges', exModel.list);
}

const exBrand = {
  binance: { bg: '#F3BA2F', svg: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none"><path fill="#111" d="M12 2l3.6 3.6-1.8 1.8L12 5.6 10.2 7.4 8.4 5.6 12 2zm-6.4 6.4L9.2 12l-3.6 3.6L2 12l3.6-3.6zm12.8 0L22 12l-3.6 3.6L14.8 12l3.6-3.6zM12 18.4l1.8-1.8L15.6 18.4 12 22l-3.6-3.6 1.8-1.8L12 18.4zm0-8.8l2.4 2.4L12 14.4 9.6 12 12 9.6z"/></svg>' },
  bybit: { bg: '#2D5BFF', svg: '<svg viewBox="0 0 64 24" width="22" height="22"><rect x="8" y="4" width="6" height="16" rx="2" fill="#fff"/><rect x="20" y="4" width="6" height="16" rx="2" fill="#ffb000"/></svg>' },
  okx: { bg: '#111', svg: '<svg viewBox="0 0 24 24" width="18" height="18" fill="#fff"><rect x="2" y="2" width="8" height="8"/><rect x="14" y="2" width="8" height="8"/><rect x="2" y="14" width="8" height="8"/><rect x="14" y="14" width="8" height="8"/></svg>' },
  kraken: { bg: '#5A6EDA', svg: '<svg viewBox="0 0 24 24" width="20" height="20" fill="#fff"><path d="M4,12c0-4.4,3.6-8,8-8s8,3.6,8,8v4h-3v-3c0-2.8-2.2-5-5-5s-5,2.2-5,5v3H4V12z"/></svg>' },
  kucoin: { bg: '#29CC99', svg: '<svg viewBox="0 0 24 24" width="20" height="20" fill="#fff"><path d="M6 4l8 8-8 8-2-2 6-6-6-6zM14 4l6 6-2 2-6-6 2-2z"/></svg>' },
  coinbase: { bg: '#0052FF', svg: '<svg viewBox="0 0 24 24" width="20" height="20" fill="#fff"><circle cx="12" cy="12" r="10"/></svg>' },
  bitget: { bg: '#12B3A8', svg: '<svg viewBox="0 0 24 24" width="20" height="20" fill="#fff"><path d="M4 12l8-8 8 8-8 8-8-8z"/></svg>' },
  htx: { bg: '#001529', svg: '<svg viewBox="0 0 24 24" width="18" height="18" fill="#fff"><path d="M12 2C9 7 9 10 12 14s3 7-2 8c6-1 9-6 9-11S15 3 12 2z"/></svg>' },
  bitfinex: { bg: '#1AA84B', svg: '<svg viewBox="0 0 24 24" width="20" height="20" fill="#fff"><path d="M2 12c6 0 12-6 20-6-6 6-12 12-20 12z"/></svg>' },
  deribit: { bg: '#0BB783', svg: '<svg viewBox="0 0 24 24" width="20" height="20" fill="#fff"><rect x="4" y="4" width="7" height="16"/><rect x="13" y="4" width="7" height="10"/></svg>' }
};

const EX_KNOWN = [
  { name: 'Binance', key: 'binance' },
  { name: 'Bybit', key: 'bybit' },
  { name: 'OKX', key: 'okx' },
  { name: 'Kraken', key: 'kraken' },
  { name: 'KuCoin', key: 'kucoin' },
  { name: 'Coinbase', key: 'coinbase' },
  { name: 'Bitget', key: 'bitget' },
  { name: 'HTX (Huobi)', key: 'htx' },
  { name: 'Bitfinex', key: 'bitfinex' },
  { name: 'Deribit', key: 'deribit' }
];

function getExByName(name) {
  const key = (name || '').toLowerCase();
  return (window.exModel?.list || []).find(x => x.key === key || x.name.toLowerCase() === key);
}

function exIsSim(name) {
  const ex = getExByName(name);
  return ex ? !!ex.sim : true;
}

function exBalance(name) {
  const ex = getExByName(name);
  return (ex && typeof ex.balance === 'number') ? ex.balance : account.balance;
}

function exIsConnected(name) {
  const ex = getExByName(name);
  return ex ? !!ex.connected : false;
}

// ===== Actions =====
function openOrder() {
  const ex = $('#exSel')?.value;
  const pair = $('#pairSel')?.value;
  const side = $('#sideSel')?.value;
  const type = $('#typeSel')?.value;
  const qty = +($('#qtyInp')?.value || 0) || 0;
  const sl = parseFloat($('#slInp')?.value) || null;
  const tp = parseFloat($('#tpInp')?.value) || null;
  const trailPct = parseFloat($('#trailInp')?.value) || null;

  if (qty <= 0) {
    alert('الكمية غير صحيحة');
    return;
  }

  if (!exIsConnected(ex)) {
    alert(`لا يمكن فتح صفقة على ${ex} — المنصّة غير متصلة. الرجاء تسجيل الدخول من صفحة "المنصات".`);
    return;
  }

  if (!exIsSim(ex)) {
    alert('هاي المنصّة غير مشاركة في التداول الوهمي (sim OFF). فعّلها من صفحة المنصّات أولاً.');
    return;
  }

  if (settings.oneTradeOnly && model.open.length > 0) {
    alert('لا يمكن فتح صفقة جديدة — صفقة واحدة فقط مسموحة حاليًا.');
    return;
  }

  const ocoOn = !!(document.body.dataset.oco === '1');
  if (ocoOn) {
    const limit = parseFloat($('#ocoLimit')?.value);
    const stop = parseFloat($('#ocoStop')?.value);
    if (!(limit > 0) || !(stop > 0)) {
      alert('أدخل أسعار OCO صحيحة');
      return;
    }

    const gid = 'OCO-' + (model.seq++);
    model.pending.push({
      id: model.seq++, group: gid, kind: 'oco-limit', ex, pair, side, qty, lev: 3, limit, sl, tp, trailPct, createdAt: Date.now()
    });
    model.pending.push({
      id: model.seq++, group: gid, kind: 'oco-stop', ex, pair, side, qty, lev: 3, stop, sl, tp, trailPct, createdAt: Date.now()
    });
    model.save();
    UI.renderPending();
    toast('أُضيفت أوامر OCO (Limit + Stop)');
    return;
  }

  if (type === 'market') {
    const now = price.map[pair];
    if (!now) {
      alert('لا يوجد سعر');
      return;
    }
    const slip = now * (settings.slipBps / 10000) * (side === 'BUY' ? +1 : -1);
    const entry = now + slip;
    const id = model.seq++;
    const feeOpen = (entry * qty) * (settings.feeBps / 10000);
    const t = {
      id, ex, pair, side, qty, lev: 3, entryPrice: entry, sl, tp, trailPct, trailAnchor: null, openedAt: Date.now(), feeOpen
    };
    positionMode.addOrAppend(t);
    model.save();
    UI.renderOpen();
    UI.refreshOpenPL();
    UI.refreshBadges();
    toast('تم فتح صفقة #' + id);
  } else {
    const limit = parseFloat($('#limitInp')?.value);
    if (!limit || limit <= 0) {
      alert('أدخل سعر Limit صحيح');
      return;
    }
    const id = model.seq++;
    model.pending.push({ id, ex, pair, side, qty, lev: 3, limit, sl, tp, trailPct, createdAt: Date.now() });
    model.save();
    UI.renderPending();
    toast('أُضيف أمر Limit #' + id);
  }
}

function cancelPending(id) {
  model.pending = model.pending.filter(x => x.id !== id);
  model.save();
  UI.renderPending();
  toast('تم إلغاء الأمر #' + id);
}

function closeTrade(id, reason = 'Manual') {
  const idx = model.open.findIndex(x => x.id === id);
  if (idx < 0) return;
  const t = model.open[idx];
  const now = price.map[t.pair] || t.entryPrice;
  const gross = (t.side === 'BUY') ? (now - t.entryPrice) * t.qty : (t.entryPrice - now) * t.qty;
  const feeClose = (now * t.qty) * (settings.feeBps / 10000);
  const fees = (t.feeOpen || 0) + feeClose;
  const net = gross - fees;
  const capital = (t.entryPrice * t.qty) / t.lev;
  const roi = capital > 0 ? (net / capital) * 100 : 0;
  model.open.splice(idx, 1);
  model.closed.unshift({ ...t, exitPrice: now, fees, netPL: net, roi, reason, closedAt: Date.now() });
  account.balance += net;
  account.realized += net;
  model.save();
  UI.renderOpen();
  UI.renderClosed();
  UI.refreshBadges();
  toast('أُغلقت صفقة #' + id);
}

function halfClose(id) {
  const t = model.open.find(x => x.id === id);
  if (!t) return;
  const half = +(t.qty / 2).toFixed(4);
  if (half <= 0) return;
  const now = price.map[t.pair] || t.entryPrice;
  const gross = (t.side === 'BUY') ? (now - t.entryPrice) * half : (t.entryPrice - now) * half;
  const fee = ((t.entryPrice * half) + (now * half)) * (settings.feeBps / 10000);
  const net = gross - fee;
  const roi = ((t.entryPrice * half) / t.lev) > 0 ? (net / ((t.entryPrice * half) / t.lev)) * 100 : 0;
  t.qty = +(t.qty - half).toFixed(4);
  model.closed.unshift({ ...t, qty: half, exitPrice: now, fees: fee, netPL: net, roi, reason: 'Partial 50%', closedAt: Date.now() });
  account.balance += net;
  account.realized += net;
  if (t.qty <= 0) {
    model.open = model.open.filter(x => x.id !== t.id);
  }
  model.save();
  UI.renderOpen();
  UI.renderClosed();
  UI.refreshBadges();
  toast('إغلاق جزئي 50% للصفقة #' + t.id);
}

function breakeven(id) {
  const t = model.open.find(x => x.id === id);
  if (!t) return;
  t.sl = +t.entryPrice.toFixed(2);
  model.save();
  UI.renderOpen();
  toast('ضبط SL على Breakeven');
}

function closeAll() {
  if (!confirm('إغلاق جميع الصفقات المفتوحة؟')) return;
  [...model.open].forEach(x => closeTrade(x.id, 'CloseAll'));
  toast('تم إغلاق جميع الصفقات');
}

function cancelAll() {
  if (!confirm('إلغاء جميع الأوامر المعلّقة؟')) return;
  model.pending = [];
  model.save();
  UI.renderPending();
  toast('تم إلغاء جميع الأوامر');
}

// ===== DOM Loaded: Attach Events & Init =====
document.addEventListener('DOMContentLoaded', () => {
  // تأكد من وجود العناصر
  const pickerBack = $('#pickerBack');
  const pickerClose = $('#pickerClose');
  const pickerSearch = $('#pickerSearch');
  const exAddBtn = $('#exAddBtn');
  const ocoBtn = document.getElementById('ocoBtn');

  // ربط الأحداث
  if (pickerClose) {
    pickerClose.addEventListener('click', () => {
      if (pickerBack) pickerBack.style.display = 'none';
    });
  }

  if (pickerSearch) {
    pickerSearch.addEventListener('input', () => {
      const filter = pickerSearch.value.toLowerCase();
      const grid = $('#pickerGrid');
      if (!grid) return;
      grid.innerHTML = '';
      EX_KNOWN.filter(x => x.name.toLowerCase().includes(filter)).forEach(x => {
        const card = document.createElement('div');
        card.className = 'pick-card';
        card.innerHTML = `${exLogoHTML(x.key)} <div><strong>${x.name}</strong><div class="tag">${x.key}</div></div>`;
        card.addEventListener('click', () => {
          if (!exModel.list.find(e => e.key === x.key)) {
            exModel.list.push({
              name: x.name, key: x.key, connected: false, sim: true, balance: 10000, apiKey: '', apiSecret: ''
            });
          } else {
            toast('المنصة مضافة مسبقًا');
          }
          exSave();
          exRender();
          if (pickerBack) pickerBack.style.display = 'none';
        });
        grid.appendChild(card);
      });
    });
  }

  if (exAddBtn) {
    exAddBtn.addEventListener('click', () => {
      if (pickerBack) {
        pickerBack.style.display = 'flex';
        if (pickerSearch) pickerSearch.focus();
      }
    });
  }

  if (ocoBtn) {
    ocoBtn.addEventListener('click', () => {
      const on = !(document.body.dataset.oco === '1');
      document.body.dataset.oco = on ? '1' : '0';
      ocoBtn.classList.toggle('active', on);
      ocoBtn.style.boxShadow = on
        ? '0 0 10px rgba(0,234,255,.35) inset, 0 0 12px rgba(0,234,255,.35)'
        : 'none';
      const ocoWrap = document.getElementById('ocoWrap');
      if (ocoWrap) ocoWrap.style.display = on ? 'flex' : 'none';
    });
  }

  // Quick quantity buttons
  document.querySelectorAll('button[data-q]').forEach(b => {
    b.addEventListener('click', () => {
      const pct = +b.dataset.q;
      const exName = $('#exSel')?.value;
      const eq = Math.max(0, +exBalance(exName));
      const pair = $('#pairSel')?.value;
      const px = price.map[pair] || 1;
      const notion = (eq / 3) * pct;
      const qty = +(notion / px).toFixed(4);

      // ✅ الإصلاح: لا تستخدم ?. في الإسناد
      const qtyInput = $('#qtyInp');
      if (qtyInput) {
        qtyInput.value = Math.max(qty, 0.0001);
      }

      toast(`حُسبت الكمية على أساس رصيد ${exName}: $${eq.toFixed(2)}`);
    });
  });

  // باقي الأحداث
  $('#mainMenu')?.addEventListener('click', e => {
    const a = e.target.closest('a[data-view]');
    if (!a) return;
    e.preventDefault();
    $$('.view').forEach(v => v.hidden = true);
    $(`#view-${a.dataset.view}`).hidden = false;
    $$('#mainMenu a').forEach(x => x.classList.toggle('active', x === a));
  });

  $('#powerBtn')?.addEventListener('click', () => {
    state.connected = !state.connected;
    renderConn();
  });

  $('#authToggle')?.addEventListener('click', e => {
    e.preventDefault();
    state.loggedIn = !state.loggedIn;
    renderSession();
  });

  $('#openBtn')?.addEventListener('click', openOrder);
  $('#cancelAll')?.addEventListener('click', cancelAll);
  $('#closeAll')?.addEventListener('click', closeAll);

  $('#pendTbl')?.addEventListener('click', e => {
    const b = e.target.closest('button[data-act="cancel"]');
    if (!b) return;
    const tr = e.target.closest('tr');
    cancelPending(+tr.dataset.id);
  });

  $('#openTbl')?.addEventListener('change', e => {
    const inp = e.target.closest('input[data-edit]');
    if (!inp) return;
    const tr = e.target.closest('tr');
    const id = +tr.dataset.id;
    const t = model.open.find(x => x.id === id);
    if (!t) return;
    const val = parseFloat(inp.value) || null;
    if (inp.dataset.edit === 'sl') t.sl = val;
    if (inp.dataset.edit === 'tp') t.tp = val;
    if (inp.dataset.edit === 'trail') t.trailPct = val;
    model.save();
  });

  $('#openTbl')?.addEventListener('click', e => {
    const b = e.target.closest('button');
    if (!b) return;
    const tr = e.target.closest('tr');
    const id = +tr.dataset.id;
    if (b.dataset.act === 'close') closeTrade(id);
    if (b.dataset.act === 'half') halfClose(id);
    if (b.dataset.act === 'be') breakeven(id);
  });

  $('#exConnectAll')?.addEventListener('click', () => {
    exModel.list.forEach(x => x.connected = true);
    exSave();
    exRender();
  });

  $('#exDisconnectAll')?.addEventListener('click', () => {
    exModel.list.forEach(x => x.connected = false);
    exSave();
    exRender();
  });

  // Escape to close modal
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && pickerBack) {
      pickerBack.style.display = 'none';
    }
  });

  // ===== Init =====
  function renderSession() {
    const userName = $('#userName');
    const authLabel = $('#authToggle .label');
    const authIcon = $('#authIcon');
    const avatar = $('#avatar');
    if (userName) userName.textContent = state.loggedIn ? 'Mohammad' : 'Guest';
    if (authLabel) authLabel.textContent = state.loggedIn ? 'تسجيل الخروج' : 'تسجيل الدخول';
    if (authIcon) authIcon.innerHTML = state.loggedIn
      ? '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="14 17 9 12 14 7"/><line x1="9" y1="12" x2="21" y2="12"/></svg>'
      : '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>';
    if (avatar) {
      const n = (userName?.textContent || 'Guest').trim();
      const parts = n.split(' ');
      const init = (parts[0][0] || 'M') + (parts[1]?.[0] || 'K');
      avatar.textContent = init.toUpperCase();
    }
  }

  function renderConn() {
    const connDot = $('#connDot');
    const connLabel = $('#connLabel');
    const powerBtn = $('#powerBtn');
    if (connDot) connDot.className = 'status-dot ' + (state.connected ? 'online' : 'offline');
    if (connLabel) connLabel.textContent = state.connected ? 'متصل' : 'غير متصل';
    if (powerBtn) {
      powerBtn.style.color = state.connected ? 'var(--ok)' : 'var(--muted)';
      powerBtn.style.boxShadow = state.connected ? '0 0 12px var(--ok),0 0 24px var(--ok)' : 'none';
    }
    if (state.connected) price.start();
    else price.stop();
  }

  function exUpdateStats() {
    const el = $('#exStats');
    if (el) el.textContent = `${exModel.list.filter(x => x.connected).length}/${exModel.list.length} متصل`;
  }

  function exLogoHTML(key) {
    const b = exBrand[key] || { bg: '#444', svg: '<span>EX</span>' };
    return `<div class="ex-logo" style="background:${b.bg}">${b.svg}</div>`;
  }

  function exRender() {
    const list = $('#exList');
    if (!list) return;
    list.innerHTML = '';
    if (!exModel.list.length) {
      $('#exEmpty').style.display = 'block';
      exUpdateStats();
      return;
    }
    $('#exEmpty').style.display = 'none';

    exModel.list.forEach((ex, i) => {
      if (typeof ex.balance !== 'number') ex.balance = 10000;
      if (!ex.key) ex.key = ex.name.toLowerCase();
      const card = document.createElement('div');
      card.className = 'card ex-card';
      const brand = exBrand[ex.key] || { bg: '#444' };
      card.style.borderTopColor = brand.bg;

      const statusHTML = `<span class="status-badge">${ex.connected ? '✅ متصل' : '❌ غير متصل'}</span>`;
      const loginBtn = `<button class="btn" data-exact="login" data-i="${i}">${ex.connected ? 'تسجيل الخروج' : 'تسجيل الدخول'}</button>`;

      card.innerHTML = `
        <div class="hd">
          <div class="ex-row">
            ${exLogoHTML(ex.key)}
            <div>
              <strong>${ex.name}</strong>
              <div class="tag">المشاركة في التداول: ${ex.sim ? 'مفعّل' : 'معطّل'}</div>
            </div>
          </div>
          <div class="ex-actions">
            <span class="badge">رصيد: $${(+ex.balance).toFixed(2)}</span>
            ${statusHTML}
            ${loginBtn}
            <button class="btn err" data-exact="del" data-i="${i}">حذف</button>
          </div>
        </div>
        <div class="bd">
          <div class="row" style="gap:10px;flex-wrap:wrap">
            <label>API Key <input class="input" type="text" value="${ex.apiKey || ''}" data-exfield="apiKey" data-i="${i}" placeholder="اختياري"></label>
            <label>Secret <input class="input" type="password" value="${ex.apiSecret || ''}" data-exfield="apiSecret" data-i="${i}" placeholder="اختياري"></label>
            <label>رصيد وهمي $ <input class="input" type="number" step="0.01" value="${ex.balance || 0}" data-exfield="balance" data-i="${i}" style="width:140px"></label>
            <label>شارك في التداول الوهمي <span class="switch ${ex.sim ? 'on' : ''}" data-exswitch="sim" data-i="${i}" title="مشاركة في التداول الوهمي"></span></label>
            <div class="tag warn">تأكد أن المفاتيح بدون صلاحيات سحب</div>
          </div>
        </div>
      `;
      list.appendChild(card);
    });
    exUpdateStats();
  }

  // التهيئة
  renderSession();
  renderConn();
  UI.renderPending();
  UI.renderOpen();
  UI.renderClosed();
  UI.refreshOpenPL();
  UI.refreshBadges();
  UI.renderEmptyFlags();
  exRender();
  if (window.assistant) {
    assistant.init();
  }
});

