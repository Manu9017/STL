/* Runs site/setup/visitor-log/Code.gs in Node against stand-ins for the Google services and prints what it would email.
   node tools/test_visitor_log.cjs   (run from the repo root) */
const fs=require('fs'),vm=require('vm');
const src=fs.readFileSync('site/setup/visitor-log/Code.gs','utf8');
function run(opts={}){
  const mails=[],props={},rows={Visits:[],Leads:[]};
  const sheet=n=>({appendRow:r=>rows[n].push(r),getLastRow:()=>rows[n].length+1,getRange:()=>({getValues:()=>[],setValue(){}})});
  const ctx={
    console,JSON,Date,Math,String,Number,Object,isNaN,
    LockService:{getScriptLock:()=>({waitLock(){},releaseLock(){}})},
    CacheService:{getScriptCache:()=>({get:()=>null,put(){}})},
    ContentService:{createTextOutput:t=>t},
    PropertiesService:{getScriptProperties:()=>({getProperty:k=>k in props?props[k]:null,setProperty:(k,v)=>{props[k]=v},deleteProperty:k=>{delete props[k]}})},
    SpreadsheetApp:{getActiveSpreadsheet:()=>({getSheetByName:sheet}),openById:()=>({getSheetByName:sheet})},
    MailApp:{sendEmail:m=>{if(opts.mailFails)throw new Error('quota');mails.push(m)},getRemainingDailyQuota:()=>100},
    Session:{getEffectiveUser:()=>({getEmail:()=>'owner@example.com'})},
    Utilities:{formatDate:(d,tz,f)=>new Date(d).toISOString().slice(0,10)}
  };
  vm.createContext(ctx);vm.runInContext(src,ctx);
  const post=d=>ctx.doPost({postData:{contents:JSON.stringify(Object.assign({at:new Date().toISOString(),page:'index.html',title:'SHIVAS home',device:'Phone',os:'Android',browser:'Chrome',lang:'en-IN',tz:'Asia/Kolkata'},d))}});
  return {post,mails,rows,props};
}
let t=run();
console.log('landing view   ->',t.post({type:'view',landing:1}),'| mails',t.mails.length,'| rows',t.rows.Visits.length);
console.log('  subject:',t.mails[0].subject,'| to:',t.mails[0].to);
console.log('  body has page/device:',/SHIVAS home/.test(t.mails[0].htmlBody)&&/Android/.test(t.mails[0].htmlBody),'| OK-bar note shown:',/pressed OK/.test(t.mails[0].htmlBody));
t.post({type:'view'}); console.log('second page    -> mails',t.mails.length,'(still 1)','| rows',t.rows.Visits.length);
t=run(); t.post({type:'view',landing:1,city:'Ghaziabad',region:'Uttar Pradesh',country:'India',org:'Example Steel Pvt Ltd',visit:3});
console.log('consented view -> subject:',t.mails[0].subject,'| company in body:',/Example Steel Pvt Ltd \(Company network\)/.test(t.mails[0].htmlBody));
t=run(); for(let i=0;i<30;i++) t.post({type:'view',landing:1});
console.log('30 landings    -> mails',t.mails.length,'(cap 25) | rows',t.rows.Visits.length,'(all 30 logged)');
t=run({mailFails:true}); console.log('mail failing   ->',t.post({type:'view',landing:1}),'| rows',t.rows.Visits.length,'(still logged)');
t=run(); t.post({type:'lead',source:'Enquiry form',name:'Test',contact:'+91 0000000000',product:'Kettle'}); console.log('lead           -> mails',t.mails.length,'subject:',t.mails[0].subject);
