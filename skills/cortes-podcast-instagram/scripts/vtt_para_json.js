const fs=require('fs');const [src,out]=process.argv.slice(2);
const t=fs.readFileSync(src,'utf8').replace(/\r/g,'');const ts=s=>{const p=s.split(':').map(Number);return +(p[0]*3600+p[1]*60+p[2]).toFixed(3)};
const W=[];for(const b of t.split(/\n\n+/)){const L=b.split('\n');const i=L.findIndex(l=>l.includes('-->'));if(i<0)continue;const[a,z]=L[i].split('-->').map(s=>ts(s.trim().split(' ')[0]));const w=L.slice(i+1).join(' ').trim();if(w)W.push({word:w,start:a,end:z})}
// agrupa em frases: quebra em fim de sentenca, pausa > 0.7s ou frase > 12s
const segs=[];let cur=[];const close=()=>{if(!cur.length)return;segs.push({id:segs.length,start:cur[0].start,end:cur.at(-1).end,text:cur.map(w=>w.word).join(' '),speaker:'UNKNOWN',words:cur});cur=[]};
for(const w of W){if(cur.length){const p=cur.at(-1);if(/[.?!…]$/.test(p.word)||w.start-p.end>0.7||w.end-cur[0].start>12)close()}cur.push(w)}close();
fs.writeFileSync(out,JSON.stringify({source:src.split(/[\/]/).pop(),language:'pt',duration:W.at(-1).end,word_timing:true,segments:segs}));
console.log(JSON.stringify({palavras:W.length,frases:segs.length,duracao:W.at(-1).end}));
