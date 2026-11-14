// Testdaten finden: zuerst test/daten (ZIP-Fassung), sonst die Original-Dateien im Repo (tools/bench/…).
'use strict';
const fs = require('fs'), path = require('path');
const ORTE = [path.join(__dirname, 'daten'), path.join(__dirname, 'daten', 'aufnahmen'),
  path.join(__dirname, '..', '..', 'bench', 'refs', 'yt-test'), path.join(__dirname, '..', '..', 'bench', 'refs'),
  path.join(__dirname, '..', '..', 'bench', 'fixtures', 'shots')];
module.exports = name => { name = path.basename(name); for (const o of ORTE) { const p = path.join(o, name); if (fs.existsSync(p)) return p; } throw new Error('Testdatei fehlt: ' + name); };
