const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://localhost:8765/test.html');await p.waitForTimeout(2000);
await p.getByText('٧٥ · القيامة').first().click();await p.waitForTimeout(3000);
const t=await p.innerText('body');console.log('errs',errs);console.log(t.includes('فالنضرة تزين ظواهرهم')?'OK75':'MISSING75');
await p.setViewportSize({width:390,height:800});await p.screenshot({path:'out/m.png'});await b.close();})();
