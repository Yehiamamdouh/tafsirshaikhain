const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://localhost:8765/test.html');await p.waitForTimeout(3000);
console.log('title',await p.title());console.log('errs',errs.length,errs.slice(0,3));
console.log((await p.innerText('body')).slice(0,300));await b.close();})();
