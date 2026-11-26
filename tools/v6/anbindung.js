/* Lernen v6 (Prototyp) – Anbindung an die App: Daten holen, Klang, Tasten, Bildschirm. Der Lernablauf selbst steht in lernen.js.
   Eingeschaltet nur mit dem Schalter in den Einstellungen („Neuer Lernmodus“) oder ?v6=1 – sonst ändert sich nichts. */
const V6 = { run: null, M: null, st: null, A: null, id: null, art: '', sitz: null, raf: 0, last: 0, held: new Map(), auto: 0 };
function v6On() { try { return typeof Lernen !== 'undefined' && (/[?&]v6=1/.test(location.search) || localStorage.getItem('kt_v6on') === '1'); } catch (e) { return false; } }
function v6Store() { const s = load('kt_l6') || {}; s.songs = s.songs || {}; s.app = s.app || {}; return s; }
function v6Heute() { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }

/* Rohdaten des geladenen Songs (MEM) für den Kern – Griffe, Takt und der bisherige Zeilen-Schnitt als Vorschlag */
function v6Roh() {
  const ns = MEM.notes, gs = MEM.gs;
  return { griffe: gs.map(g => ({ t: g.start, n: [...g.mids].map(m => { const n = ns.find(x => x.midi === m && x.start >= g.start - 0.001 && x.start <= g.last + 0.001); return [m, g.hands.get(m), n ? n.dur : 0.4]; }) })),
    takt: MEM.takt ? { beat: MEM.takt.beat, S: MEM.takt.S } : null, zeilen: (MEM.C || []).map(c => ({ a: c.a, b: c.b })), formen: (MEM.F || []).map(f => ({ s: f.s, e: f.e })) };
}
/* Start-Tempo aus dem alten Protokoll: so schnell hat er den ganzen Song zuletzt von sich aus gespielt */
function v6AltTempo(id) {
  try { const L = (load('kt_v8log') || []).filter(e => e.zl && e.song === id && e.mode === 'song' && e.waits && e.pos === e.n && !e.a), e = L[L.length - 1]; if (!e) return null;
    const v = []; for (let i = 1; i < e.waits.length && i < MEM.gs.length; i++) { const soll = MEM.gs[i].start - MEM.gs[i - 1].start; if (soll > 0.05 && e.waits[i] > 0) v.push(soll / e.waits[i]); }
    if (v.length < 8) return null; v.sort((a, b) => a - b); return Math.min(10, Math.max(5, Math.floor(v[v.length >> 1] * 10))); } catch (e) { return null; }
}
function v6Laden(id) {
  const it = LIB.find(x => x.id === id); if (!it || !memLoad(it)) return false;
  const S = v6Store(); let st = S.songs[id]; const M = Lernen.modell(v6Roh(), st);
  if (!st) { let alt = null; try { alt = MEM.rec[zlKey()] || null; } catch (e) {} st = Lernen.uebernahme(M, alt); if (st.pos.some(p => p >= 4)) st.tempo = v6AltTempo(id); S.songs[id] = st; save('kt_l6', S); }
  V6.M = M; V6.st = st; V6.id = id; V6.item = it; return true;
}
function v6Sichern() { const S = v6Store(); S.songs[V6.id] = V6.st; if (V6.art === 'wdh') S.app.wdhTag = v6Heute(); else if (V6.art === 'weiter') S.app.aktuell = V6.id; save('kt_l6', S); }

/* „Los“: fällige Wiederholung (höchstens 1 am Tag), sonst weiter am aktuellen Song */
function v6Los() {
  const S = v6Store(), songs = LIB.filter(x => x.type === 'midi').map(it => ({ id: it.id, stand: S.songs[it.id] })), p = Lernen.los(songs, S.app, v6Heute());
  if (!p) { toast('Noch kein Song in der Bibliothek'); return; }
  if (!V6.sitz) V6.sitz = Lernen.sitzung(Date.now() / 1000);
  if (!v6Laden(p.id)) return; V6.art = p.art; v6Bild(); show('v6');
  V6.A = p.art === 'weiter' ? (Lernen.naechstes(V6.M, V6.st) || Lernen.ganzerSong(V6.st)) : Lernen.ganzerSong(V6.st);
  v6Start();
}
function v6Start() {
  clearTimeout(V6.auto); if (!V6.M.haendeOk && !V6.gesagtH) { V6.gesagtH = 1; toast('Im Video stimmen Farbe und Hand nicht überein – ich trenne die Hände nach der Lage auf der Tastatur', 5000); }
  V6.run = Lernen.lauf(V6.M, V6.A, { ton: (m, d, v) => { try { playTone(m, Math.min(3, d), v, 0.35); } catch (e) {} }, puls: (betont, vor) => { try { playClick(betont); } catch (e) {} } });
  V6.t0 = Date.now(); $('#v6Res').classList.add('hidden'); $('#v6Head').textContent = (V6.art === 'wdh' ? 'Aufwärmen · ' : '') + V6.item.title;
  V6.last = performance.now(); cancelAnimationFrame(V6.raf); V6.raf = requestAnimationFrame(v6Tick);
}
function v6Tick(now) {
  const R = V6.run; if (!R) return; const dt = Math.min(0.1, (now - V6.last) / 1000); V6.last = now; R.tick(dt); v6Zeichne();
  if (R.fertig) { v6Fertig(); return; } V6.raf = requestAnimationFrame(v6Tick);
}
function v6Taste(m) { const R = V6.run; V6.held.set(m, performance.now()); if (R && !R.fertig) { R.taste(m); if (R.fertig) { v6Zeichne(); cancelAnimationFrame(V6.raf); v6Fertig(); } } }
function v6Fertig() {
  const R = V6.run, r = R.ergebnis, A = V6.A; V6.run = null;
  const res = Lernen.abschluss(V6.M, V6.st, A, r, v6Heute(), V6.sitz); v6Sichern();
  try { addTime(V6.id, Math.min(600, r.dauer)); const L = load('kt_v8log') || []; L.push({ t: Date.now(), v: 14, v6: 1, song: V6.id, mode: 'v6-' + (A.k < 0 ? 'song' : 'abschnitt'), k: A.k, stufe: A.stufe, hand: A.hand, tempo: A.tempo, ok: r.ok ? 1 : 0, stocker: r.stocker, erlaubt: r.erlaubt, falsch: r.falsch, n: r.n, dur: Math.round(r.dauer * 1000), wo: r.wo, abw: r.abw, eigen: r.eigenTempo, art: V6.art }); while (L.length > 300) L.shift(); save('kt_v8log', L); setTimeout(() => { try { awLogSync(); } catch (e) {} }, 1500); } catch (e) {}
  try { if (r.ok) (A.k < 0 || A.nr === 6 ? fxBig : fxLine)(); } catch (e) {}
  // was kommt danach?
  let weiter;
  if (V6.art === 'wdh') weiter = res.zurueck != null ? () => { V6.art = 'nach'; V6.A = Lernen.naechstes(V6.M, V6.st); v6Start(); } : v6Los;
  else if (V6.art === 'nach' || V6.art === 'frei') weiter = V6.art === 'nach' ? v6Los : null;
  else weiter = () => { const n = Lernen.naechstes(V6.M, V6.st); if (!n) { v6Los(); return; } V6.A = n; v6Start(); };
  const stop = Lernen.aufhoeren(V6.sitz, Date.now() / 1000), box = $('#v6Res'); box.classList.remove('hidden');
  $('#v6ResT').textContent = (r.ok ? '✓ ' : '') + res.text; $('#v6Stop').classList.toggle('hidden', !stop); if (stop) $('#v6Stop').innerHTML = '<b>' + stop.titel + '</b><br>' + stop.text;
  const nx = $('#v6Next'); nx.textContent = weiter ? 'Weiter' : 'Noch einmal'; nx.onclick = () => { clearTimeout(V6.auto); (weiter || (() => { V6.A = Lernen.ganzerSong(V6.st); v6Start(); }))(); };
  v6Leiste(); if (weiter && !stop) V6.auto = setTimeout(nx.onclick, r.ok ? 2600 : 3200);
}
function v6Zu() { clearTimeout(V6.auto); cancelAnimationFrame(V6.raf); V6.run = null; V6.sitz = null; show('home'); try { renderHome(); } catch (e) {} }
function v6Vor() { if (!V6.A) return; clearTimeout(V6.auto); const was = V6.run; V6.run = null; cancelAnimationFrame(V6.raf); const T = Lernen.vorspiel(V6.M, V6.A, Math.max(0.6, V6.A.tempo || 0.6)); let ende = 0;
  for (const t of T) { ende = Math.max(ende, t.nach + t.d); setTimeout(() => { if (!V6.run) { try { playTone(t.m, Math.min(3, t.d), 0.7); } catch (e) {} V6.held.set(-t.m, performance.now()); v6Zeichne(); } }, t.nach * 1000); }
  $('#v6Stat').textContent = 'Hör zu …'; V6.auto = setTimeout(v6Start, ende * 1000 + 600); }

/* Bildschirm: wird einmal gebaut */
function v6Bild() {
  if ($('#v6')) return; const d = document.createElement('div'); d.id = 'v6'; d.className = 'screen hidden';
  d.innerHTML = '<div style="display:flex;flex-direction:column;height:100%;padding:14px 16px;box-sizing:border-box;gap:10px">' +
    '<div style="display:flex;align-items:center;gap:10px"><button class="btn sm" id="v6X">✕</button><div id="v6Head" class="mu" style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"></div><button class="btn sm" id="v6Play">Vorspielen</button></div>' +
    '<div id="v6Bar" style="display:flex;gap:6px;flex-wrap:wrap"></div>' +
    '<div id="v6T" style="font-size:20px;font-weight:800"></div><div id="v6Stat" class="mu" style="min-height:20px"></div>' +
    '<div id="v6Ak" style="font-size:44px;font-weight:800;min-height:54px;text-align:center"></div>' +
    '<div style="flex:1"></div><div id="v6Res" class="hidden" style="background:var(--s2);border-radius:14px;padding:14px"><div id="v6ResT" style="font-weight:700;margin-bottom:8px"></div><div id="v6Stop" class="hidden mu" style="margin-bottom:10px"></div><div style="display:flex;gap:8px"><button class="btn pri" id="v6Next" style="flex:1">Weiter</button><button class="btn" id="v6End">Fertig für heute</button></div></div>' +
    '<canvas id="v6C" style="width:100%;height:120px;border-radius:8px"></canvas></div>';
  $('#app').appendChild(d); $('#v6X').onclick = v6Zu; $('#v6End').onclick = v6Zu; $('#v6Play').onclick = v6Vor;
}
function v6Leiste() { const f = Lernen.fortschritt(V6.M, V6.st); $('#v6Bar').innerHTML = f.abschnitte.map((s, k) => `<span style="padding:3px 9px;border-radius:9px;font-weight:700;background:${s.pos >= 6 ? 'var(--ac)' : 'var(--s3)'};color:${s.pos >= 6 ? 'var(--ink)' : 'var(--tx)'};outline:${V6.A && V6.A.k === k ? '2px solid var(--ac)' : 'none'};opacity:${s.wie >= 0 ? 0.6 : 1}">${s.name}${s.pos >= 6 ? '' : ' ' + '●'.repeat(Math.min(3, s.pos >= 4 ? 2 : s.pos >= 3 ? 1 : 0)) + '○'.repeat(3 - Math.min(3, s.pos >= 4 ? 2 : s.pos >= 3 ? 1 : 0))}</span>`).join('') + `<span style="padding:3px 9px;border-radius:9px;font-weight:700;background:${f.fertig ? 'var(--ac)' : 'var(--s3)'};color:${f.fertig ? 'var(--ink)' : 'var(--tx)'}">♪${V6.st.stern ? ' ★' : ''}</span>`; }
function v6Zeichne() {
  const R = V6.run, B = R ? R.bild() : null, c = $('#v6C'); if (!c) return;
  if (B) { $('#v6T').textContent = B.titel; $('#v6Ak').textContent = B.einzaehlen ? String(B.einzaehlen) : B.akkord; $('#v6Stat').textContent = B.einzaehlen ? 'Einzählen …' : `Griff ${B.griff} von ${B.von}` + (B.stufe > 1 ? ` · Stocker ${B.stocker}` : '') + (B.falsch ? ` · daneben ${B.falsch}` : '') + (B.hilfe ? ' · Hilfe' : ''); if (V6.lb !== V6.A) { V6.lb = V6.A; v6Leiste(); } }
  const w = c.clientWidth * (window.devicePixelRatio || 1), h = c.clientHeight * (window.devicePixelRatio || 1); if (c.width !== w || c.height !== h) { c.width = w; c.height = h; } const g = c.getContext('2d'), sw = [1, 3, 6, 8, 10], now = performance.now();
  const lit = new Map(); if (B) { for (const m of B.leuchten) lit.set(m, '#F0A93B'); if (B.rot != null) lit.set(B.rot, '#E5484D'); } for (const [m, t] of V6.held) { if (now - t > 350) V6.held.delete(m); else if (!lit.has(Math.abs(m))) lit.set(Math.abs(m), m < 0 ? '#F0A93B' : '#7BC47F'); }
  const weiss = []; for (let m = 21; m <= 108; m++) if (!sw.includes(m % 12)) weiss.push(m); const ww = w / weiss.length; g.clearRect(0, 0, w, h);
  weiss.forEach((m, i) => { g.fillStyle = lit.get(m) || '#E9E4D8'; g.fillRect(i * ww + 0.5, 0, ww - 1, h); });
  weiss.forEach((m, i) => { const s = m + 1; if (s <= 108 && sw.includes(s % 12)) { g.fillStyle = lit.get(s) || '#15161A'; g.fillRect((i + 1) * ww - ww * 0.3, 0, ww * 0.6, h * 0.62); } });
}
/* Startseite: der eine Knopf */
function v6Home() {
  { const sw = $('#v6Sw'); if (sw) sw.textContent = v6On() ? 'An' : 'Aus'; }
  let b = $('#v6Go'); if (!v6On()) { if (b) b.remove(); return; }
  if (!b) { b = document.createElement('button'); b.id = 'v6Go'; b.className = 'btn pri'; b.style.cssText = 'width:100%;height:64px;font-size:22px;font-weight:800;margin:10px 0 14px'; b.onclick = v6Los; const s = $('#vStart'); s.insertBefore(b, s.children[1] || null); }
  const S = v6Store(), h = v6Heute(), due = LIB.some(it => { const st = S.songs[it.id]; return st && st.ivl > 0 && st.due && st.due <= h; }) && S.app.wdhTag !== h; b.textContent = due ? 'Los · erst 1 Song aufwärmen' : 'Los';
}
