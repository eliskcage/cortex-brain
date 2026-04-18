<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="canonical" href="https://www.shortfactory.shop/">
<meta name="description" content="ShortFactory — bootstrapping AGI, paradise on earth. Virtual creatures, emotional physics, split-hemisphere cortex brain, and the living equation.">
<title>ShortFactory</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{overflow:hidden;height:100vh;width:100vw}
canvas{display:block;position:fixed;inset:0}
#proceed{display:none;position:fixed;bottom:110px;left:50%;transform:translateX(-50%);z-index:50;padding:14px 36px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.25);border-radius:10px;color:#fff;font-size:10px;letter-spacing:4px;font-weight:700;cursor:pointer;font-family:'Segoe UI',system-ui,sans-serif;transition:all 0.4s;text-decoration:none}
#proceed:hover{background:rgba(255,255,255,0.15);border-color:#fff}
#proceed.show{display:block;animation:fadeUp 1s ease forwards}
@keyframes fadeUp{from{opacity:0;transform:translateX(-50%) translateY(20px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}

/* ── Sliding panels ── */
.panel{position:fixed;top:50%;z-index:60;width:140px;padding:20px 14px;border-radius:14px;text-align:center;font-family:'Segoe UI',system-ui,sans-serif;transition:transform 0.8s cubic-bezier(0.22,1,0.36,1),opacity 0.8s;opacity:0;pointer-events:none}
.panel.in{opacity:1;pointer-events:all}
#panel-boy{left:0;transform:translate(-100%,-50%);background:rgba(30,60,140,0.85);border:1px solid rgba(80,130,255,0.3)}
#panel-boy.in{transform:translate(16px,-50%)}
#panel-girl{right:0;transform:translate(100%,-50%);background:rgba(140,30,80,0.85);border:1px solid rgba(255,80,160,0.3)}
#panel-girl.in{transform:translate(-16px,-50%)}
.panel-icon{font-size:36px;margin-bottom:6px}
.panel-label{font-size:9px;letter-spacing:3px;font-weight:700;margin-bottom:4px}
.panel-hint{font-size:18px;opacity:0.7}
#panel-boy .panel-label{color:#5090ff}
#panel-girl .panel-label{color:#ff5090}

/* ── Feedback overlay ── */
#feedback{display:none;position:fixed;inset:0;z-index:100;background:rgba(5,5,8,0.95);flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:20px;font-family:'Segoe UI',system-ui,sans-serif}
#feedback.show{display:flex}
#fb-title{font-size:14px;color:#daa520;letter-spacing:3px;font-weight:700;margin-bottom:24px}
.fb-row{display:flex;gap:12px;margin-bottom:12px}
.fb-card{padding:14px 20px;border-radius:10px;cursor:pointer;font-size:20px;transition:all 0.2s;border:1px solid rgba(255,255,255,0.08);min-width:80px}
.fb-card:hover{transform:scale(1.1)}
#fb-boy{background:rgba(30,60,140,0.5);border-color:rgba(80,130,255,0.3)}
#fb-girl{background:rgba(140,30,80,0.5);border-color:rgba(255,80,160,0.3)}
#fb-both{background:rgba(218,165,32,0.15);border-color:rgba(218,165,32,0.3)}
.fb-sub{font-size:8px;letter-spacing:2px;color:#666;margin-top:4px}
#fb-earn{display:none;margin-top:20px;padding:14px 36px;background:linear-gradient(135deg,#daa520,#b8860b);border:none;border-radius:10px;color:#000;font-weight:900;font-size:11px;letter-spacing:3px;cursor:pointer}
#fb-earn.show{display:block;animation:fadeUp 0.5s ease forwards}

/* ── Fairy guide ── */
#spiralFairy{
  display:none;position:fixed;bottom:160px;left:50%;z-index:55;
  width:14px;height:14px;border-radius:50%;
  background:radial-gradient(circle,#cc44ff 30%,#9900cc 70%);
  box-shadow:0 0 10px rgba(204,68,255,0.6),0 0 25px rgba(204,68,255,0.25);
  pointer-events:none;
  transform:translateX(-50%);
}
#spiralFairy.show{
  display:block;
  animation:fairyFloat8 4s ease-in-out infinite;
}
@keyframes fairyFloat8{
  0%  {transform:translateX(-50%) translate(0,0)}
  12.5%{transform:translateX(-50%) translate(10px,-8px)}
  25% {transform:translateX(-50%) translate(20px,0)}
  37.5%{transform:translateX(-50%) translate(10px,8px)}
  50% {transform:translateX(-50%) translate(0,0)}
  62.5%{transform:translateX(-50%) translate(-10px,8px)}
  75% {transform:translateX(-50%) translate(-20px,0)}
  87.5%{transform:translateX(-50%) translate(-10px,-8px)}
  100%{transform:translateX(-50%) translate(0,0)}
}
/* Proceed button glows purple when fairy is present */
#proceed.fairy-glow{
  border-color:rgba(204,68,255,0.6) !important;
  background:rgba(204,68,255,0.1) !important;
  color:#cc44ff !important;
  box-shadow:0 0 20px rgba(204,68,255,0.3),0 0 50px rgba(204,68,255,0.1);
  animation:proceedPulse 2s ease-in-out infinite alternate;
}
@keyframes proceedPulse{
  0%{box-shadow:0 0 20px rgba(204,68,255,0.3),0 0 50px rgba(204,68,255,0.1)}
  100%{box-shadow:0 0 30px rgba(204,68,255,0.5),0 0 70px rgba(204,68,255,0.2)}
}

/* ── Age gate overlay ── */
#age-gate{display:none;position:fixed;inset:0;z-index:200;background:rgba(5,2,15,0.92);flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:20px;font-family:'Segoe UI',system-ui,sans-serif}
#age-gate.show{display:flex}
#age-gate .fairy-big{font-size:64px;margin-bottom:16px;animation:fairyBob 2s ease-in-out infinite}
@keyframes fairyBob{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
#age-gate .ask{font-size:13px;color:#cc44ff;letter-spacing:3px;font-weight:700;margin-bottom:24px}
#age-gate .age-btns{display:flex;gap:12px;flex-wrap:wrap;justify-content:center}
#age-gate .age-btn{padding:14px 28px;border-radius:10px;cursor:pointer;font-size:14px;font-weight:700;letter-spacing:2px;border:1px solid rgba(204,68,255,0.2);background:rgba(204,68,255,0.06);color:#cc44ff;transition:all 0.3s}
#age-gate .age-btn:hover{background:rgba(204,68,255,0.15);border-color:#cc44ff;transform:scale(1.05)}
#age-gate .age-btn.green{border-color:rgba(34,197,94,0.3);color:#22c55e;background:rgba(34,197,94,0.06)}
#age-gate .age-btn.green:hover{background:rgba(34,197,94,0.15);border-color:#22c55e}
#age-gate .sub-msg{font-size:10px;color:#555;letter-spacing:2px;margin-top:16px}

/* ── Kiddy toast ── */
#kiddy-toast{display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:150;padding:20px 30px;border-radius:12px;background:rgba(204,68,255,0.12);border:1px solid rgba(204,68,255,0.3);text-align:center;font-family:'Segoe UI',system-ui,sans-serif;animation:toastIn 0.3s ease}
#kiddy-toast.show{display:block}
@keyframes toastIn{from{opacity:0;transform:translate(-50%,-50%) scale(0.9)}to{opacity:1;transform:translate(-50%,-50%) scale(1)}}
#kiddy-toast .fairy-sm{font-size:32px}
#kiddy-toast .msg{font-size:11px;color:#cc44ff;letter-spacing:2px;margin-top:8px;font-weight:700}
#kiddy-toast .hint{font-size:9px;color:#666;margin-top:6px;letter-spacing:1px}
</style>
</head>
<body>
<canvas id="c"></canvas>
<a id="proceed" href="/spiral2.html">READY? PROVE IT →</a>

<!-- Fairy guide dot — appears if fairy has been freed on app.html -->
<div id="spiralFairy"></div>

<!-- Age gate — fairy asks your age -->
<div id="age-gate">
  <div class="fairy-big">🧚</div>
  <div class="ask">HOW OLD ARE YOU?</div>
  <div class="age-btns">
    <div class="age-btn" id="age-under">UNDER 16</div>
    <div class="age-btn green" id="age-over">16 OR OVER</div>
  </div>
  <div class="sub-msg">SOME CONTENT HAS GROWN-UP THEMES</div>
</div>

<!-- Kiddy toast — shown when under-16 clicks a mature node -->
<div id="kiddy-toast">
  <div class="fairy-sm">🧚</div>
  <div class="msg">NOT YET LITTLE ONE</div>
  <div class="hint">COME BACK WHEN YOU'RE 16</div>
</div>

<!-- Sliding panels -->
<div id="panel-boy" class="panel">
  <div class="panel-icon">📱</div>
  <div class="panel-label">BOY</div>
  <div class="panel-hint">👦</div>
</div>
<div id="panel-girl" class="panel">
  <div class="panel-icon">🖥</div>
  <div class="panel-label">GIRL</div>
  <div class="panel-hint">👧</div>
</div>

<!-- Feedback overlay -->
<div id="feedback">
  <div id="fb-title">WHICH DID YOU TRY?</div>
  <div class="fb-row">
    <div class="fb-card" id="fb-boy" onclick="fbPick('boy')">📱<div class="fb-sub">BOY</div></div>
    <div class="fb-card" id="fb-girl" onclick="fbPick('girl')">🖥<div class="fb-sub">GIRL</div></div>
    <div class="fb-card" id="fb-both" onclick="fbPick('both')">📱🖥<div class="fb-sub">BOTH</div></div>
  </div>
  <button id="fb-earn">UNLOCK 👀 THE EYE → +10 SFT</button>
</div>

<script>
(function(){
var c=document.getElementById('c'),ctx=c.getContext('2d'),W,H,dpr;
var audioCtx=null;

function resize(){
  dpr=Math.min(window.devicePixelRatio||1,2);
  W=window.innerWidth;H=window.innerHeight;
  c.width=W*dpr;c.height=H*dpr;
  c.style.width=W+'px';c.style.height=H+'px';
  ctx.setTransform(dpr,0,0,dpr,0,0);
}
resize();window.addEventListener('resize',resize);

/* ── Audio ── */
function initAudio(){
  if(!audioCtx)try{audioCtx=new(window.AudioContext||window.webkitAudioContext)();}catch(e){}
  if(audioCtx&&audioCtx.state==='suspended')audioCtx.resume();
}
function droidNote(freq,end,dur,wave,time,vol){
  if(!audioCtx)return;
  var o=audioCtx.createOscillator(),g=audioCtx.createGain();
  o.connect(g);g.connect(audioCtx.destination);o.type=wave||'sine';
  o.frequency.setValueAtTime(freq,time);
  if(end!==freq)o.frequency.exponentialRampToValueAtTime(Math.max(20,end),time+dur*0.9);
  g.gain.setValueAtTime(vol||0.04,time);
  g.gain.exponentialRampToValueAtTime(0.001,time+dur);
  o.start(time);o.stop(time+dur);
}
function chirp(){
  if(!audioCtx)return;var t=audioCtx.currentTime,w=['sine','square','sawtooth','triangle'][Math.random()*4|0];
  var f=400+Math.random()*600;
  droidNote(f,f*(1+Math.random()*.4),0.08+Math.random()*0.06,w,t,0.04);
  if(Math.random()>.5)droidNote(f*1.5,f*1.2,0.06,'sine',t+0.06,0.02);
}
function fanfare(){
  if(!audioCtx)return;var t=audioCtx.currentTime;
  droidNote(523,530,0.15,'sine',t,0.06);droidNote(659,670,0.15,'sine',t+0.12,0.05);
  droidNote(784,800,0.2,'sine',t+0.24,0.05);droidNote(1047,1060,0.3,'sine',t+0.36,0.04);
}
function birthTone(freq){
  if(!audioCtx)return;var t=audioCtx.currentTime;
  droidNote(freq,freq*1.02,0.3,'sine',t,0.05);droidNote(freq*1.5,freq*1.52,0.2,'triangle',t+0.1,0.03);
}
function insaneFlip(){
  if(!audioCtx)return;var t=audioCtx.currentTime;
  droidNote(900,200,0.4,'sawtooth',t,0.05);droidNote(666,333,0.5,'square',t+0.05,0.04);
}
function geniusFlip(){
  if(!audioCtx)return;var t=audioCtx.currentTime;
  droidNote(200,900,0.4,'sine',t,0.05);droidNote(400,800,0.3,'triangle',t+0.1,0.04);
}
function coinSound(){
  if(!audioCtx)return;var t=audioCtx.currentTime;
  droidNote(988,1320,0.08,'sine',t,0.06);droidNote(1320,1320,0.15,'sine',t+0.08,0.05);
}
function sentence(){
  if(!audioCtx)return;var t=audioCtx.currentTime,ws=['sine','square','sawtooth','triangle'];
  for(var i=0;i<4+Math.floor(Math.random()*3);i++){
    var f=300+Math.random()*800,d=0.05+Math.random()*0.08;
    droidNote(f,f*(0.8+Math.random()*0.5),d,ws[Math.random()*4|0],t,0.03);t+=d+0.02+Math.random()*0.03;
  }
}

/* ── SPIRAL MELODY — sadness and wonder ── */
var melodyStarted=false,noteTimer=0,noteInPhrase=0,currentPhrase=0,chordIdx=0,chordTimer=0;
var SCALE_SAD=[293.66,329.63,349.23,440,493.88,587.33,659.25,698.46];
var SCALE_WONDER=[293.66,329.63,369.99,440,523.25,587.33,659.25,739.99];
var PAD_CHORDS=[
  [146.83,220,293.66],[174.61,261.63,349.23],[130.81,196,261.63],[110,164.81,220],
  [146.83,220,349.23],[164.81,246.94,329.63],[174.61,220,293.66],[130.81,196,329.63]
];
var PHRASES=[
  [[0,2,0.7],[2,1,0.5],[3,2,0.8],[4,1.5,0.6],[-1,0.5,0],[3,2,0.7],[2,3,0.5]],
  [[5,2,0.8],[4,1,0.6],[3,1.5,0.7],[2,1,0.5],[-1,1,0],[0,3,0.6]],
  [[3,1,0.7],[4,1,0.8],[5,2,0.9],[7,1.5,0.6],[5,1.5,0.7],[3,3,0.5]],
  [[0,1.5,0.6],[2,1,0.5],[3,1.5,0.7],[-1,1,0],[5,2,0.8],[3,1,0.6],[2,2,0.5],[0,2,0.4]],
  [[5,2,0.7],[3,1,0.6],[4,2,0.8],[5,1,0.7],[7,2,0.9],[-1,1,0],[5,3,0.5]],
  [[0,3,0.6],[-1,0.5,0],[2,1.5,0.7],[3,1,0.6],[5,2,0.8],[4,1.5,0.6],[3,3,0.5]]
];
function playMelodyNote(freq,dur,vel){
  if(!audioCtx||!freq)return;var t=audioCtx.currentTime;
  var o=audioCtx.createOscillator(),g=audioCtx.createGain();
  var vib=audioCtx.createOscillator(),vibG=audioCtx.createGain();
  vib.frequency.value=5.5;vibG.gain.value=freq*0.006;
  vib.connect(vibG);vibG.connect(o.frequency);
  o.connect(g);g.connect(audioCtx.destination);o.type='sine';o.frequency.value=freq;
  var vol=vel*0.025;
  g.gain.setValueAtTime(0.001,t);g.gain.exponentialRampToValueAtTime(vol,t+0.08);
  g.gain.setValueAtTime(vol,t+dur*0.6);g.gain.exponentialRampToValueAtTime(0.001,t+dur);
  o.start(t);o.stop(t+dur+0.1);vib.start(t);vib.stop(t+dur+0.1);
  var o2=audioCtx.createOscillator(),g2=audioCtx.createGain();
  o2.connect(g2);g2.connect(audioCtx.destination);o2.type='sine';o2.frequency.value=freq*2;
  g2.gain.setValueAtTime(0.001,t);g2.gain.exponentialRampToValueAtTime(vol*0.15,t+0.12);
  g2.gain.exponentialRampToValueAtTime(0.001,t+dur*0.8);o2.start(t);o2.stop(t+dur+0.1);
}
function playPadChord(chord,dur){
  if(!audioCtx)return;var t=audioCtx.currentTime;
  for(var ci=0;ci<chord.length;ci++){
    var o=audioCtx.createOscillator(),g=audioCtx.createGain();
    o.connect(g);g.connect(audioCtx.destination);o.type='triangle';o.frequency.value=chord[ci];
    g.gain.setValueAtTime(0.001,t);g.gain.exponentialRampToValueAtTime(0.012,t+0.5);
    g.gain.setValueAtTime(0.012,t+dur*0.7);g.gain.exponentialRampToValueAtTime(0.001,t+dur);
    o.start(t);o.stop(t+dur+0.2);
  }
}
function updateMelody(dt){
  if(!audioCtx||!melodyStarted)return;var beatDur=0.83;
  chordTimer+=dt;if(chordTimer>=beatDur*6){chordTimer=0;chordIdx=(chordIdx+1)%PAD_CHORDS.length;playPadChord(PAD_CHORDS[chordIdx],beatDur*6);}
  noteTimer+=dt;var phrase=PHRASES[currentPhrase];var note=phrase[noteInPhrase];var noteDur=note[1]*beatDur;
  if(noteTimer>=noteDur){noteTimer=0;noteInPhrase++;
    if(noteInPhrase>=phrase.length){noteInPhrase=0;currentPhrase=(currentPhrase+1)%PHRASES.length;phrase=PHRASES[currentPhrase];}
    note=phrase[noteInPhrase];noteDur=note[1]*beatDur;
    if(note[0]>=0){var useWonder=(currentPhrase%3===2);var scale=useWonder?SCALE_WONDER:SCALE_SAD;playMelodyNote(scale[note[0]%scale.length],noteDur*0.9,note[2]);}
  }
}
function startMelody(){if(melodyStarted)return;melodyStarted=true;playPadChord(PAD_CHORDS[0],0.83*6);var n=PHRASES[0][0];if(n[0]>=0)playMelodyNote(SCALE_SAD[n[0]],n[1]*0.83*0.9,n[2]);}

/* ── Age gate ── */
var sfAge=localStorage.getItem('sf_age_gate');
var isKiddy=(sfAge==='under');
var ageKnown=!!sfAge;

/* ── All nodes ── */
var ring1=[
  {emoji:'🧬',label:'SOUL MAP',color:'#a855f7',url:'/soul-sphere.html'},
  {emoji:'📱',label:'BOY',color:'#5090ff',url:'/alive/boy/'},
  {emoji:'🖥️',label:'GIRL',color:'#ff5090',url:'/alive/'},
  {emoji:'🧠',label:'CORTEX',color:'#0f0',url:'/alive/studio/'},
  {emoji:'⚡',label:'GPU SWARM',color:'#76b900',url:'/screensaver/'},
  {emoji:'🔥',label:'DARES4DOSH',color:'#ff8c00',url:'/dares4dosh/app/'},
  {emoji:'🎬',label:'IMAGINATOR',color:'#daa520',url:'/imaginator/index2.php'},
  {emoji:'👀',label:'THE EYE',color:'#00d4ff',url:'/alive/eye.html'},
  {emoji:'💷',label:'REVERT FIVER',color:'#22c55e',url:'/join.html'},
  {emoji:'📋',label:'5 PATENTS',color:'#00d4ff',url:'/valuation.html'},
  {emoji:'🌍',label:'PARADISE',color:'#daa520',url:'/about11.html'},
  {emoji:'🔮',label:'POINTER',color:'#cc44ff',url:'/explainer-consciousness.html'},
  {emoji:'🛡',label:'COVENANT',color:'#daa520',url:'/game-proof.html'},
  {emoji:'😈',label:'DEVIL NEWS',color:'#ff4400',url:'/devil-news.html',mature:true},
  {emoji:'💧',label:'THE TEAR',color:'#6699ff',url:'/explainer-tear.html'},
  {emoji:'🐣',label:'ALIVE PET',color:'#cc44ff',url:'/alive/app.html',glow:true}
];
var ring2=[
  {emoji:'🧚',label:'CONSCIOUS',color:'#cc44ff',url:'/explainer-consciousness.html'},
  {emoji:'🔒',label:'BLACKBOX',color:'#cc44ff',url:'/explainer-blackbox.html'},
  {emoji:'🛂',label:'IDENTITY',color:'#cc44ff',url:'/explainer-identity.html'},
  {emoji:'⚡',label:'EMOTIONS',color:'#cc44ff',url:'/explainer-emotions.html'},
  {emoji:'🧬',label:'ALIVE EXP',color:'#cc44ff',url:'/explainer-alive.html'},
  {emoji:'🍪',label:'BISCUIT',color:'#cc44ff',url:'/explainer-biscuit.html'},
  {emoji:'🔺',label:'SHAPES',color:'#cc44ff',url:'/explainer-shapes.html'},
  {emoji:'🧠',label:'CORTEX EXP',color:'#cc44ff',url:'/explainer-cortex.html'},
  {emoji:'🌊',label:'SPHERENET',color:'#cc44ff',url:'/explainer-spherenet.html'},
  {emoji:'👻',label:'SPIRIT',color:'#cc44ff',url:'/explainer-spirit.html'},
  {emoji:'🧮',label:'EQUATION',color:'#cc44ff',url:'/explainer-equation.html'},
  {emoji:'🔬',label:'COMPUTANIUM',color:'#cc44ff',url:'/explainer-computanium.html'},
  {emoji:'🪞',label:'ANALOGY',color:'#cc44ff',url:'/explainer-analogyquasions.html'},
  {emoji:'💀',label:'ANTICHRIST',color:'#cc44ff',url:'/explainer-antichrist.html',mature:true}
];
var allNodes=ring1.concat(ring2);
var N=allNodes.length,N1=ring1.length,N2=ring2.length;

var particles=[];
var t=0,started=false;
var logoAlpha=0,logoScale=0.5;
var subAlpha=0;

var mode=0,modeBlend=0;
var introPhase=0,introTime=0,introDone=false;
var bornCount=0,bornTimer=0;
var proceedShown=false;
var panelsShown=false;
var fbChoice=null;

/* ── SFT credits (shared with spiral2) ── */
var STORE_KEY='sf_spiral_v2';
var progress=JSON.parse(localStorage.getItem(STORE_KEY)||'{}');
if(!progress.completed) progress.completed={};
if(!progress.visited) progress.visited={};
if(!progress.credits) progress.credits=0;
if(!progress.answers) progress.answers={};
if(!progress.panelDone) progress.panelDone=false;
function saveProgress(){ localStorage.setItem(STORE_KEY,JSON.stringify(progress)); }

var nodes=[];
for(var i=0;i<N;i++){
  var isR1=i<N1;
  var ringIdx=isR1?i:i-N1;
  var ringN=isR1?N1:N2;
  var gAngle=(ringIdx/ringN)*Math.PI*2-Math.PI/2;
  var gRadius=isR1?0.28:0.43;
  var spiralFrac=i/(N-1);
  var spiralAngle=spiralFrac*4*Math.PI*2-Math.PI/2;
  var spiralRadius=0.06+0.40*spiralFrac;

  nodes.push({
    gAngle:gAngle,gRadius:gRadius,isR1:isR1,
    sAngle:spiralAngle,sRadius:spiralRadius,
    angle:gAngle,radius:gRadius,
    born:false,alpha:0,scale:0,
    spiralBorn:false,spiralAlpha:0
  });
}

var spiralDrawing=false,spiralIdx=0,spiralTimer=0;
var spiralInk=[];

function spawnBurst(x,y,col,n){
  for(var i=0;i<(n||10);i++){
    var a=Math.random()*Math.PI*2,sp=1+Math.random()*3;
    particles.push({x:x,y:y,vx:Math.cos(a)*sp,vy:Math.sin(a)*sp,life:1,color:col,size:1+Math.random()*2});
  }
}

function addSpiralInkSegment(fromIdx,toIdx){
  var minDim=Math.min(W,H);
  var steps=14;
  for(var s=0;s<=steps;s++){
    var frac=(fromIdx+(toIdx-fromIdx)*(s/steps))/(N-1);
    var a=frac*4*Math.PI*2-Math.PI/2;
    var r=(0.06+0.40*frac)*minDim;
    var wobble=Math.sin(a*3.7)*4+Math.cos(a*5.3)*2.5;
    spiralInk.push({x:W/2+Math.cos(a)*r+wobble,y:H/2+Math.sin(a)*r+wobble});
  }
}

/* ── Show panels after intro ── */
function showPanels(){
  if(panelsShown||progress.panelDone) return;
  panelsShown=true;
  setTimeout(function(){
    document.getElementById('panel-boy').classList.add('in');
  },4000);
  setTimeout(function(){
    document.getElementById('panel-girl').classList.add('in');
  },5000);
}

/* ── Show proceed button ── */
function showProceed(){
  if(proceedShown) return;
  proceedShown=true;
  var delay=progress.panelDone?3000:12000;
  setTimeout(function(){
    document.getElementById('proceed').className='show';
  },delay);
}

/* ── Feedback pick ── */
window.fbPick=function(choice){
  fbChoice=choice;
  initAudio();chirp();
  document.querySelectorAll('.fb-card').forEach(function(el){el.style.opacity='0.3';});
  document.getElementById('fb-'+choice).style.opacity='1';
  document.getElementById('fb-'+choice).style.transform='scale(1.15)';
  document.getElementById('fb-earn').className='show';
};

document.getElementById('fb-earn').addEventListener('click',function(){
  initAudio();coinSound();
  progress.credits+=10;
  progress.panelDone=true;
  progress.answers['alive-panel']={choice:fbChoice,time:Date.now()};
  saveProgress();
  document.getElementById('feedback').className='';
  // Hide panels
  document.getElementById('panel-boy').classList.remove('in');
  document.getElementById('panel-girl').classList.remove('in');
  // Show proceed
  if(!proceedShown){
    proceedShown=true;
    setTimeout(function(){document.getElementById('proceed').className='show';},500);
  }
});

/* ── Panel click → open feedback ── */
document.getElementById('panel-boy').addEventListener('click',function(){
  initAudio();chirp();
  document.getElementById('feedback').className='show';
});
document.getElementById('panel-girl').addEventListener('click',function(){
  initAudio();chirp();
  document.getElementById('feedback').className='show';
});

/* ── UPDATE ── */
function update(dt){
  t+=dt;
  updateMelody(dt);
  var minDim=Math.min(W,H);

  if(!introDone){
    introTime+=dt;
    if(introPhase===0&&introTime>0.8){introPhase=1;introTime=0;fanfare();}
    if(introPhase===1){
      logoAlpha=Math.min(1,logoAlpha+dt*0.8);
      logoScale=logoScale+(1-logoScale)*dt*3;
      if(introTime>1.5){introPhase=2;introTime=0;}
    }
    if(introPhase===2){
      bornTimer+=dt;
      while(bornTimer>0.35&&bornCount<N){
        nodes[bornCount].born=true;
        var nd=nodes[bornCount],an=allNodes[bornCount];
        var r=nd.gRadius*minDim;
        birthTone(300+bornCount*25);
        spawnBurst(W/2+Math.cos(nd.gAngle)*r,H/2+Math.sin(nd.gAngle)*r,an.color,8);
        bornCount++;bornTimer-=0.35;
        if(bornCount>=N){introPhase=3;introDone=true;sentence();showPanels();showProceed();}
      }
    }
  }

  modeBlend+=(mode-modeBlend)*dt*2.5;

  if(mode===1&&spiralDrawing){
    spiralTimer+=dt;
    while(spiralTimer>0.1&&spiralIdx<N){
      nodes[spiralIdx].spiralBorn=true;
      chirp();
      if(spiralIdx>0) addSpiralInkSegment(spiralIdx-1,spiralIdx);
      var nd=nodes[spiralIdx];
      var r=nd.sRadius*minDim;
      spawnBurst(W/2+Math.cos(nd.sAngle)*r,H/2+Math.sin(nd.sAngle)*r,allNodes[spiralIdx].color,6);
      spiralIdx++;spiralTimer-=0.1;
    }
    if(spiralIdx>=N) spiralDrawing=false;
  }

  if(introDone) subAlpha=Math.min(1,subAlpha+dt*0.3);
  if(introPhase>=1) logoAlpha=Math.min(1,logoAlpha+dt*0.5);

  for(var i=0;i<N;i++){
    var nd=nodes[i];
    if(!nd.born)continue;
    nd.alpha=Math.min(1,nd.alpha+dt*2);
    nd.scale=nd.scale+(1-nd.scale)*dt*4;
    var insaneAlpha=nd.spiralBorn?1:0;
    nd.spiralAlpha+=(insaneAlpha-nd.spiralAlpha)*dt*5;
    var gSpeed=nd.isR1?0.12:(-0.08);
    nd.gAngle+=dt*gSpeed;
    var gR=nd.gRadius*minDim,sR=nd.sRadius*minDim;
    var blend=modeBlend;
    nd.radius=gR+(sR-gR)*blend;
    nd.angle=nd.gAngle+(nd.sAngle-nd.gAngle)*blend;
  }

  for(var j=particles.length-1;j>=0;j--){
    var p=particles[j];
    p.x+=p.vx;p.y+=p.vy;p.vx*=0.97;p.vy*=0.97;
    p.life-=dt*1.5;if(p.life<=0)particles.splice(j,1);
  }
  if(introPhase===2&&Math.random()<dt*0.4) chirp();
}

/* ── DRAW ── */
function draw(){
  ctx.clearRect(0,0,W,H);
  var minDim=Math.min(W,H);
  var inv=modeBlend;

  var bgR=Math.round(5+213*inv),bgG=Math.round(5+155*inv),bgB=Math.round(8+17*inv);
  ctx.fillStyle='rgb('+bgR+','+bgG+','+bgB+')';
  ctx.fillRect(0,0,W,H);

  var bg=ctx.createRadialGradient(W/2,H/2,0,W/2,H/2,W*0.6);
  bg.addColorStop(0,'rgba(218,165,32,'+(0.04*(1-inv))+')');
  bg.addColorStop(1,'rgba(0,0,0,'+(0.3*(1-inv))+')');
  ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);

  // GENIUS: connection lines
  if(inv<0.9){
    ctx.save();ctx.globalAlpha=(1-inv);
    for(var i=0;i<N;i++){
      var nd=nodes[i];if(!nd.born)continue;
      var an=allNodes[i];
      var nx=W/2+Math.cos(nd.angle)*nd.radius,ny=H/2+Math.sin(nd.angle)*nd.radius;
      ctx.strokeStyle='rgba('+hexToRgb(an.color)+','+(nd.alpha*0.1)+')';
      ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(W/2,H/2);ctx.lineTo(nx,ny);ctx.stroke();
      var prog=((t*0.5+i*0.3)%1);
      ctx.fillStyle='rgba('+hexToRgb(an.color)+','+(nd.alpha*0.4)+')';
      ctx.beginPath();ctx.arc(W/2+(nx-W/2)*prog,H/2+(ny-H/2)*prog,1.5,0,Math.PI*2);ctx.fill();
    }
    ctx.restore();
  }

  // INSANE: thick spiral ink
  if(inv>0.05&&spiralInk.length>1){
    ctx.save();
    ctx.globalAlpha=inv*0.8;
    ctx.strokeStyle=inv>0.5?'rgba(15,10,2,0.7)':'rgba(218,165,32,0.5)';
    ctx.lineWidth=10;ctx.lineCap='round';ctx.lineJoin='round';
    ctx.beginPath();ctx.moveTo(spiralInk[0].x,spiralInk[0].y);
    for(var si=1;si<spiralInk.length;si++) ctx.lineTo(spiralInk[si].x,spiralInk[si].y);
    ctx.stroke();
    ctx.strokeStyle=inv>0.5?'rgba(40,28,5,0.4)':'rgba(255,200,50,0.25)';
    ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(spiralInk[0].x+2,spiralInk[0].y+2);
    for(var si=1;si<spiralInk.length;si++){ctx.lineTo(spiralInk[si].x+Math.sin(si*0.4)*3,spiralInk[si].y+Math.sin(si*0.4)*3);}
    ctx.stroke();
    ctx.strokeStyle=inv>0.5?'rgba(60,40,10,0.25)':'rgba(180,140,30,0.15)';
    ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(spiralInk[0].x-1,spiralInk[0].y-1);
    for(var si=1;si<spiralInk.length;si++){var w2=Math.cos(si*0.6)*2;ctx.lineTo(spiralInk[si].x+w2,spiralInk[si].y-w2);}
    ctx.stroke();
    ctx.restore();
  }

  // LOGO
  if(logoAlpha>0){
    if(inv<0.5){
      var geniusFs=Math.min(W*0.035,28);
      ctx.save();ctx.globalAlpha=logoAlpha*(1-inv*2);
      ctx.translate(W/2,H/2);ctx.scale(logoScale,logoScale);
      ctx.shadowColor='#daa520';ctx.shadowBlur=30*logoAlpha;
      ctx.font='900 '+geniusFs+'px "Segoe UI",system-ui,sans-serif';
      ctx.textAlign='center';ctx.textBaseline='middle';
      var sw=ctx.measureText('Short').width,fw=ctx.measureText('Factory').width,tw=sw+fw;
      ctx.fillStyle='#e0e0e0';ctx.fillText('Short',-tw/2+sw/2,0);
      ctx.fillStyle='#76b900';ctx.fillText('Factory',tw/2-fw/2,0);
      ctx.shadowBlur=0;ctx.restore();
      if(subAlpha>0){
        ctx.save();ctx.globalAlpha=subAlpha*(1-inv*2)*0.8;
        ctx.font='700 '+Math.min(W*0.013,11)+'px "Segoe UI",system-ui,sans-serif';
        ctx.fillStyle='#daa520';ctx.textAlign='center';
        ctx.fillText('SOLVE THE PUZZLE',W/2,H/2+geniusFs*0.8);
        ctx.restore();
      }
    }
    if(inv>0.3){
      var insaneAlpha=Math.min(1,(inv-0.3)/0.7);
      var vertFs=Math.min(H*0.06,40);var margin=Math.max(30,W*0.04);
      ctx.save();ctx.globalAlpha=logoAlpha*insaneAlpha;
      ctx.font='900 '+vertFs+'px "Segoe UI",system-ui,sans-serif';
      ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillStyle='rgba(10,8,2,0.7)';
      'Short'.split('').forEach(function(l,i){ctx.fillText(l,margin,H*0.2+i*(vertFs*1.1));});
      ctx.fillStyle='rgba(10,80,0,0.6)';
      'Factory'.split('').forEach(function(l,i){ctx.fillText(l,W-margin,H*0.15+i*(vertFs*1.1));});
      ctx.restore();
      if(subAlpha>0){
        ctx.save();ctx.globalAlpha=subAlpha*insaneAlpha*0.7;
        ctx.font='700 '+Math.min(W*0.015,12)+'px "Segoe UI",system-ui,sans-serif';
        ctx.fillStyle='rgba(10,8,2,0.5)';ctx.textAlign='center';
        ctx.fillText('ENJOY THE MADNESS',W/2,H-80);
        ctx.restore();
      }
    }
  }

  // EMOJI NODES
  for(var i=0;i<N;i++){
    var nd=nodes[i];if(!nd.born||nd.alpha<=0)continue;
    var an=allNodes[i];
    var nodeAlpha=nd.alpha*((1-inv)+inv*nd.spiralAlpha);
    if(nodeAlpha<0.01)continue;
    var nx=W/2+Math.cos(nd.angle)*nd.radius,ny=H/2+Math.sin(nd.angle)*nd.radius;
    ctx.save();ctx.globalAlpha=nodeAlpha;
    ctx.translate(nx,ny);ctx.scale(nd.scale,nd.scale);
    var glowR=nd.isR1?26:18;
    var gc=inv<0.5?an.color:'#000000';
    /* ALIVE PET — throbbing glow beacon */
    if(an.glow){
      var pulse=0.5+0.5*Math.sin(t*3);
      var bigR=glowR+20*pulse;
      var g2=ctx.createRadialGradient(0,0,0,0,0,bigR);
      g2.addColorStop(0,'rgba('+hexToRgb(an.color)+','+(0.4+0.3*pulse)+')');
      g2.addColorStop(0.4,'rgba('+hexToRgb(an.color)+','+(0.15+0.1*pulse)+')');
      g2.addColorStop(1,'rgba('+hexToRgb(an.color)+',0)');
      ctx.fillStyle=g2;ctx.beginPath();ctx.arc(0,0,bigR,0,Math.PI*2);ctx.fill();
    }
    var grd=ctx.createRadialGradient(0,0,0,0,0,glowR);
    grd.addColorStop(0,'rgba('+hexToRgb(gc)+','+(0.18*(1-inv*0.5))+')');
    grd.addColorStop(1,'rgba('+hexToRgb(gc)+',0)');
    ctx.fillStyle=grd;ctx.beginPath();ctx.arc(0,0,glowR,0,Math.PI*2);ctx.fill();
    var emojiSize=nd.isR1?24:17;
    var matureLocked=an.mature&&isKiddy;
    if(matureLocked) ctx.globalAlpha=nodeAlpha*0.25;
    if(an.glow&&!matureLocked){ var ep=1+0.15*Math.sin(t*3); ctx.scale(ep,ep); }
    ctx.font=emojiSize+'px serif';
    ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(matureLocked?'🔒':an.emoji,0,nd.isR1?-5:-1);
    ctx.font='700 '+(nd.isR1?'7':'5')+'px "Segoe UI",system-ui,sans-serif';
    ctx.fillStyle=matureLocked?'#444':(inv<0.5?an.color:'rgba(0,0,0,0.7)');
    if(an.glow&&!matureLocked) ctx.fillStyle=an.color;
    ctx.fillText(an.label,0,nd.isR1?12:10);
    ctx.restore();
  }

  // Particles
  for(var j=0;j<particles.length;j++){
    var p=particles[j];ctx.globalAlpha=p.life;
    ctx.fillStyle=inv<0.5?p.color:'#000';
    ctx.beginPath();ctx.arc(p.x,p.y,p.size*p.life,0,Math.PI*2);ctx.fill();
  }
  ctx.globalAlpha=1;

  // Mode hint
  if(introDone){
    ctx.save();ctx.globalAlpha=0.25+0.15*Math.sin(t*2);
    ctx.font='600 10px "Segoe UI",system-ui,sans-serif';
    ctx.textAlign='center';ctx.fillStyle=inv<0.5?'#daa520':'#1a1000';
    ctx.fillText('click to flip',W/2,H-18);
    ctx.restore();
  }
}

function hexToRgb(hex){
  if(!hex||hex.charAt(0)!=='#')return'200,200,200';
  return(parseInt(hex.slice(1,3),16)||0)+','+(parseInt(hex.slice(3,5),16)||0)+','+(parseInt(hex.slice(5,7),16)||0);
}

var lastT=0;
function loop(now){
  var dt=Math.min((now-lastT)/1000,0.1);lastT=now;
  update(dt);draw();requestAnimationFrame(loop);
}

function hitNode(mx,my){
  for(var i=0;i<N;i++){
    var nd=nodes[i];if(!nd.born||nd.alpha<0.3)continue;
    var nx=W/2+Math.cos(nd.angle)*nd.radius,ny=H/2+Math.sin(nd.angle)*nd.radius;
    var dx=mx-nx,dy=my-ny,hitR=nd.isR1?30:20;
    if(dx*dx+dy*dy<hitR*hitR)return allNodes[i];
  }
  return null;
}

c.addEventListener('mousemove',function(e){
  c.style.cursor=hitNode(e.clientX,e.clientY)?'pointer':'default';
});

c.addEventListener('click',function(e){
  initAudio();
  if(!melodyStarted) startMelody();
  var hit=hitNode(e.clientX,e.clientY);
  if(hit&&hit.url){
    /* Age gate: if mature node + kiddy, show toast instead */
    if(hit.mature&&isKiddy){
      showKiddyToast();return;
    }
    /* Age gate: first time clicking ANY mature node with no age set, ask */
    if(hit.mature&&!ageKnown){
      pendingMatureUrl=hit.url;
      document.getElementById('age-gate').classList.add('show');return;
    }
    chirp();chirp();setTimeout(function(){window.location.href=hit.url;},200);return;
  }
  if(!introDone)return;
  if(mode===0){
    mode=1;insaneFlip();
    spiralInk=[];
    for(var i=0;i<N;i++) nodes[i].spiralBorn=false;
    spiralDrawing=true;spiralIdx=0;spiralTimer=0;
  } else {
    mode=0;geniusFlip();
    spiralDrawing=false;
  }
});

started=true;introPhase=0;introTime=0;
lastT=performance.now();requestAnimationFrame(loop);

var pendingMatureUrl=null;
var kiddyToastTimer=null;

function ageGate(choice){
  localStorage.setItem('sf_age_gate',choice);
  sfAge=choice;
  ageKnown=true;
  isKiddy=(choice==='under');
  document.getElementById('age-gate').classList.remove('show');
  var goTo=pendingMatureUrl;
  pendingMatureUrl=null;
  if(choice==='over'&&goTo&&goTo!=='null'){
    chirp();chirp();
    setTimeout(function(){window.location.href=goTo;},200);
  }
}
document.getElementById('age-under').onclick=function(){ageGate('under');};
document.getElementById('age-over').onclick=function(){ageGate('over');};

function showKiddyToast(){
  var toast=document.getElementById('kiddy-toast');
  toast.classList.add('show');
  if(kiddyToastTimer) clearTimeout(kiddyToastTimer);
  kiddyToastTimer=setTimeout(function(){toast.classList.remove('show');},2500);
}

})();
</script>
<script src="/js/heartbeat.js"></script>
<script>
/* ═══ FAIRY GUIDE — she followed you from app.html ═══ */
(function(){
  if (!localStorage.getItem('alive_fairy_freed')) return;

  var fairy = document.getElementById('spiralFairy');
  var proceed = document.getElementById('proceed');
  if (!fairy) return;

  /* Show fairy once the proceed button appears */
  var observer = new MutationObserver(function(){
    if (proceed.classList.contains('show')){
      fairy.classList.add('show');
      if (proceed) proceed.classList.add('fairy-glow');
      observer.disconnect();
    }
  });
  observer.observe(proceed, {attributes:true, attributeFilter:['class']});

  /* Also check immediately in case proceed is already showing */
  if (proceed.classList.contains('show')){
    fairy.classList.add('show');
    proceed.classList.add('fairy-glow');
  }
})();

/* ═══ HIDE PANELS FOR ACTIVATED CREATURES ═══ */
(function(){
  var boyBorn = localStorage.getItem('alive_boy_birth');
  var girlBorn = localStorage.getItem('alive_girl_birth');
  var panelBoy = document.getElementById('panel-boy');
  var panelGirl = document.getElementById('panel-girl');

  if (boyBorn && panelBoy) {
    panelBoy.style.display = 'none';
  }
  if (girlBorn && panelGirl) {
    panelGirl.style.display = 'none';
  }
})();
</script>
</body>
</html>
