"""v4.77: Am PC verbindet sich Chrome selbst per Bluetooth mit dem Klavier (Web Bluetooth, BLE-MIDI) – ohne Hilfsprogramm, ohne Installation.
Prüft: Tippen auf „Verbinden“ öffnet die Bluetooth-Auswahl, danach „Klavier verbunden“, Töne (auch Laufstatus / mehrere Töne in einem Paket) kommen an,
Loslassen kommt an, Pedal kommt an, Klavier aus → „nicht verbunden“ + Meldung, danach verbindet es sich von selbst wieder."""
import sys,asyncio,json
from playwright.async_api import async_playwright
INIT=r"""(()=>{ /* kein Web-MIDI-Gerät da (wie ohne Hilfsprogramm) */
 const acc={inputs:new Map(),outputs:new Map(),onstatechange:null};navigator.requestMIDIAccess=()=>Promise.resolve(acc);
 const L={};const ch={_l:[],addEventListener(t,f){this._l.push(f)},startNotifications(){return Promise.resolve(this)}};
 const dev={name:'GZUT-MIDI',id:'d1',_l:[],addEventListener(t,f){this._l.push(f)},
  gatt:{connected:false,connect(){if(window.__off)return Promise.reject(new Error('aus'));this.connected=true;window.__conn=(window.__conn||0)+1;
   return Promise.resolve({getPrimaryService:s=>Promise.resolve({getCharacteristic:c=>{window.__svc=s;window.__chr=c;return Promise.resolve(ch)}})})}}};
 window.__dev=dev;window.__ch=ch;window.__req=0;
 navigator.bluetooth={requestDevice(o){window.__req++;window.__opts=o;return Promise.resolve(dev)},getDevices(){return Promise.resolve(window.__granted?[dev]:[])}};
 window.__pkt=a=>{const u=new Uint8Array(a);for(const f of ch._l)f({target:{value:new DataView(u.buffer)}})};
 window.__drop=()=>{dev.gatt.connected=false;window.__off=true;for(const f of dev._l)f({target:dev})};
})()"""
JS=r"""async()=>{const o={};window.playTone=()=>{};const W=ms=>new Promise(r=>setTimeout(r,ms));await W(900);
 o.before=kbInfo().label;
 const toasts=[];const t0=window.toast;window.toast=(m,d)=>{toasts.push(m);try{t0(m,d)}catch(e){}};
 kbTap();await W(300);
 o.req=__req;o.svcFilter=JSON.stringify(window.__opts||{}).includes('03b80e5a');o.svc=window.__svc;o.chr=window.__chr;
 o.label=kbInfo().label;o.name=KB.name;
 /* ein Ton: Kopf, Zeit, Note an C4 */
 __pkt([0x80,0x80,0x90,60,100]);o.n1=[...KB.held];
 /* Laufstatus + zwei Töne in einem Paket: E4, G4 */
 __pkt([0x80,0x81,0x90,64,90,67,80]);o.n2=[...KB.held].sort();
 /* Loslassen (Note an mit Stärke 0 und Note aus) */
 __pkt([0x80,0x82,0x80,60,0,0x83,0x90,64,0,67,0]);o.n3=[...KB.held];
 /* Pedal */
 __pkt([0x80,0x84,0xB0,64,127]);o.ped=KB.pedal;
 /* Klavier aus */
 __drop();await W(100);o.after=kbInfo().label;o.toast=toasts.some(t=>/getrennt/i.test(t));
 /* Klavier wieder an → verbindet sich von selbst */
 window.__off=false;await W(6500);o.back=kbInfo().label;o.conn=window.__conn||0;
 return o}"""
async def main(url):
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        ctx=await b.new_context(viewport={'width':1280,'height':800});await ctx.add_init_script(INIT)
        pg=await ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+url);await pg.wait_for_timeout(600)
        r=await pg.evaluate(JS);print(json.dumps(r,ensure_ascii=False),errs)
        c={'vorher nicht verbunden':r['before']!='Klavier verbunden',
           'Tippen öffnet Bluetooth-Auswahl (MIDI-Dienst)':r['req']==1 and r['svcFilter'],
           'richtiger MIDI-Kanal':(r['svc'] or '').lower()=='03b80e5a-ede8-4b33-a751-6ce34ec4c700' and (r['chr'] or '').lower()=='7772e5db-3868-4112-a1a9-f2669d106bf3',
           'danach verbunden':r['label']=='Klavier verbunden' and r['name']=='GZUT-MIDI',
           'Ton kommt an':r['n1']==[60],'mehrere Töne / Laufstatus':r['n2']==[60,64,67],
           'Loslassen kommt an':r['n3']==[],'Pedal kommt an':r['ped'] is True,
           'Klavier aus → nicht verbunden + Meldung':r['after']!='Klavier verbunden' and r['toast'],
           'verbindet sich von selbst wieder':r['back']=='Klavier verbunden' and r['conn']>=2,'keine Fehler':not errs}
        print(c);print('OK' if all(c.values()) else 'FEHLER');await b.close()
asyncio.run(main(sys.argv[1]))
