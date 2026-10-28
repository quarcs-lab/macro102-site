'use strict';
const englishButton=document.getElementById('english-toggle');
const readingsButton=document.getElementById('readings-toggle');
englishButton?.addEventListener('click',()=>{
  const hidden=document.body.classList.toggle('japanese-only');
  englishButton.setAttribute('aria-pressed',String(!hidden));
  englishButton.textContent=hidden?'English: off':'English: on';
});
readingsButton?.addEventListener('click',()=>{
  const hidden=document.body.classList.toggle('hide-readings');
  readingsButton.setAttribute('aria-pressed',String(!hidden));
  readingsButton.textContent=hidden?'ふりがな：非表示':'ふりがな：表示';
});

// Lesson pages only (pages built by write-japanese-lesson carry #lesson-data).
const dataNode=document.getElementById('lesson-data');
if(dataNode){
  const lesson=JSON.parse(dataNode.textContent);
  const $=(s,root=document)=>root.querySelector(s);
  const $$=(s,root=document)=>[...root.querySelectorAll(s)];

  // Progress: kept in this browser only; the page works without storage.
  const key='macro102-ja-lesson-ch'+String(lesson.chapter).padStart(2,'0');
  let progress={steps:{},known:{},quiz:{}};
  try{const saved=JSON.parse(localStorage.getItem(key)||'null');if(saved)progress=Object.assign(progress,saved);}catch(e){}
  const save=()=>{try{localStorage.setItem(key,JSON.stringify(progress));}catch(e){}};

  // Steps
  const renderSteps=()=>{
    $$('.done').forEach(b=>{const on=!!progress.steps[b.dataset.step];b.setAttribute('aria-pressed',String(on));b.textContent=on?'✓ 完了':'このステップを完了にする';});
    $$('.steps a').forEach(a=>a.classList.toggle('complete',!!progress.steps[a.dataset.step]));
    $('#steps-done').textContent=Object.values(progress.steps).filter(Boolean).length;
  };
  $$('.done').forEach(b=>b.addEventListener('click',()=>{progress.steps[b.dataset.step]=!progress.steps[b.dataset.step];save();renderSteps();}));

  // Audio clips: play one turn, loop it, or continue with a pause after each turn.
  const audio=$('#episode');
  const passages=$$('.passage');
  const speed=$('#speed'),autopause=$('#autopause'),now=$('#now-playing');
  let clip=null,timer=null,frame=null;
  let stopSpeech=()=>{};
  const span=id=>{const el=document.getElementById(id);return el?[+el.dataset.start,+el.dataset.end]:null;};
  const clear=()=>{clearTimeout(timer);cancelAnimationFrame(frame);timer=null;
    $$('.passage.playing').forEach(p=>p.classList.remove('playing'));now.textContent='';};
  // The button that started a clip turns into a stop button until the clip (or chain) ends.
  const showPlaying=btn=>$$('button.play').forEach(x=>{
    if(!x.dataset.label){x.dataset.label=x.textContent;x.dataset.aria=x.getAttribute('aria-label')||'';}
    const on=x===btn;x.classList.toggle('active',on);x.setAttribute('aria-pressed',String(on));
    x.textContent=on?(x.dataset.once?'■ 停止':'■'):x.dataset.label;
    if(on)x.setAttribute('aria-label','停止');else if(x.dataset.aria)x.setAttribute('aria-label',x.dataset.aria);});
  const stop=()=>{clip=null;clear();audio.pause();showPlaying(null);
    $$('button.loop').forEach(o=>o.setAttribute('aria-pressed','false'));};
  const watch=()=>{
    if(!clip)return;
    if(audio.currentTime>=clip.end-0.04){audio.pause();finish();return;}
    frame=requestAnimationFrame(watch);
  };
  const finish=()=>{
    const c=clip;if(!c)return;
    const factor=+autopause.value;
    const gap=factor?(c.end-c.start)/audio.playbackRate*factor*1000:600;
    const looping=$(`.loop[data-turn="${c.id}"]`)?.getAttribute('aria-pressed')==='true';
    if(c.once||(!looping&&!factor)){stop();return;}
    now.textContent=factor?'今、声に出して…':'';
    timer=setTimeout(()=>{
      if(clip!==c)return;
      if(looping){play(c.id);return;}
      const i=passages.findIndex(p=>p.id===c.id);
      if(i>=0&&i+1<passages.length)play(passages[i+1].id,{scroll:true});else stop();
    },gap);
  };
  const play=(id,opts={})=>{
    const s=span(id);if(!s)return;
    stopSpeech();clear();clip={id,start:s[0],end:s[1],once:!!opts.once,
      button:opts.button||document.querySelector(`.passage button.play[data-turn="${id}"]`)};
    showPlaying(clip.button);
    audio.playbackRate=+speed.value;
    audio.currentTime=s[0];
    const el=document.getElementById(id);
    if(!opts.once){el.classList.add('playing');if(opts.scroll)el.scrollIntoView({block:'center',behavior:'smooth'});}
    now.textContent='▶ '+id;
    audio.play().then(()=>{frame=requestAnimationFrame(watch);}).catch(()=>stop());
  };
  speed.addEventListener('change',()=>{audio.playbackRate=+speed.value;});
  audio.addEventListener('ratechange',()=>{if(Math.abs(audio.playbackRate-speed.value)>0.01&&!clip)speed.value=String(audio.playbackRate);});
  $('#stop').addEventListener('click',stop);
  // Using the main player's own controls ends clip mode.
  audio.addEventListener('pause',()=>{if(clip&&audio.currentTime<clip.end-0.1&&!timer)stop();});
  audio.addEventListener('seeked',()=>{if(clip&&(audio.currentTime<clip.start-0.3||audio.currentTime>clip.end+0.3))stop();});
  $$('button.play').forEach(b=>b.addEventListener('click',()=>{
    if(clip&&clip.button===b){stop();return;}
    play(b.dataset.turn,{once:b.dataset.once==='1',button:b});}));
  $$('button.loop').forEach(b=>b.addEventListener('click',()=>{
    const on=b.getAttribute('aria-pressed')!=='true';
    $$('button.loop').forEach(o=>o.setAttribute('aria-pressed','false'));
    b.setAttribute('aria-pressed',String(on));
    if(on)play(b.dataset.turn);else if(clip&&clip.id===b.dataset.turn)stop();
  }));

  // N1 passage read-aloud: the browser's own Japanese speech synthesis, one sentence at a time.
  const synth=window.speechSynthesis;const sentences=lesson.passage_sentences||[];
  const voiceSelect=$('#ja-voice'),ttsNote=$('#tts-note');
  let speech=null,keepAlive=null,jaVoices=[];
  const showSaying=btn=>$$('.say-btn').forEach(x=>{
    if(!x.dataset.label)x.dataset.label=x.textContent;
    const on=x===btn;x.classList.toggle('active',on);x.setAttribute('aria-pressed',String(on));
    x.textContent=on?(x.classList.contains('say-all')?'■ 停止':'■'):x.dataset.label;});
  const mark=i=>$$('.say').forEach(e=>e.classList.toggle('saying',+e.dataset.s===i));
  stopSpeech=()=>{if(!speech)return;speech=null;clearInterval(keepAlive);try{synth.cancel();}catch(e){}mark(-1);showSaying(null);};
  const sayNext=run=>{
    if(speech!==run)return;
    if(run.i>run.to){stopSpeech();return;}
    const i=run.i,u=new SpeechSynthesisUtterance(sentences[i]);
    u.lang='ja-JP';u.rate=+speed.value;
    const v=jaVoices.find(x=>x.name===voiceSelect.value);if(v)u.voice=v;
    u.onend=()=>{if(speech===run&&run.i===i){run.i++;sayNext(run);}};
    u.onerror=e=>{if(e.error!=='interrupted'&&e.error!=='canceled'){ttsNote.textContent='読み上げに失敗しました（'+e.error+'）。';stopSpeech();}};
    mark(i);synth.speak(u);
  };
  const say=(from,to,btn)=>{
    stop();stopSpeech();
    speech={i:from,to,button:btn};showSaying(btn);
    // Chrome stops long speech after ~15 s unless it is nudged.
    keepAlive=setInterval(()=>{if(synth.speaking&&!synth.paused){synth.pause();synth.resume();}},10000);
    sayNext(speech);
  };
  if(!synth||!window.SpeechSynthesisUtterance){
    $$('.say-btn').forEach(b=>b.disabled=true);if(voiceSelect)voiceSelect.disabled=true;
    if(ttsNote)ttsNote.textContent='このブラウザは読み上げに対応していません。';
  }else if(voiceSelect){
    const loadVoices=()=>{
      // Natural voices first (Google, Kyoko, O-ren, Otoya, Hattori), novelty voices last.
      const rank=v=>{const i=['Google','Kyoko','O-ren','Otoya','Hattori','Microsoft'].findIndex(n=>v.name.includes(n));return i<0?9:i;};
      jaVoices=synth.getVoices().filter(v=>/^ja/i.test(v.lang)).sort((a,b)=>rank(a)-rank(b));
      const keep=voiceSelect.value||progress.voice;voiceSelect.textContent='';
      jaVoices.forEach(v=>voiceSelect.append(new Option(v.name+(v.localService?'':' (online)'),v.name)));
      if(jaVoices.some(v=>v.name===keep))voiceSelect.value=keep;
      ttsNote.textContent=jaVoices.length?'':'日本語の音声が見つかりません。端末の設定で日本語の音声を追加すると、より自然に読み上げます。';
      voiceSelect.hidden=!jaVoices.length;
    };
    loadVoices();synth.addEventListener?.('voiceschanged',loadVoices);
    voiceSelect.addEventListener('change',()=>{progress.voice=voiceSelect.value;save();});
    $$('.say-btn').forEach(b=>b.addEventListener('click',()=>{
      if(speech&&speech.button===b){stopSpeech();return;}
      say(+b.dataset.from,+b.dataset.to,b);}));
    addEventListener('pagehide',()=>{try{synth.cancel();}catch(e){}});
  }

  // Flashcards
  let filter='all',index=0,flipped=false;
  const deck=()=>lesson.vocab.filter(v=>filter==='all'||(filter==='high'&&(v.level==='N1'||v.level==='超N1'))||(filter==='todo'&&!progress.known[v.term]));
  const card=$('#card');
  const renderCard=()=>{
    const d=deck();
    if(!d.length){card.innerHTML='<span class="front">このグループの語はすべて覚えました。</span>';$('#card-count').textContent='0 / 0';return;}
    index=(index+d.length)%d.length;const v=d[index];
    const esc=s=>s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
    card.classList.toggle('known',!!progress.known[v.term]);
    card.innerHTML=flipped
      ?`<span class="reading">${esc(v.reading)}</span><span class="meaning" lang="en">${esc(v.meaning)}</span><span class="lvl">${esc(v.level)}（推定）</span><span class="example">${esc(v.example)}</span>`
      :`<span class="front">${esc(v.term)}</span><span class="hint">タップしてめくる</span>`;
    $('#card-count').textContent=`${index+1} / ${d.length}`;
  };
  const renderKnown=()=>{
    $$('table.vocab tr[data-term]').forEach(r=>r.classList.toggle('known',!!progress.known[r.dataset.term]));
    $('#known-count').textContent=lesson.vocab.filter(v=>progress.known[v.term]).length;
  };
  card.addEventListener('click',()=>{flipped=!flipped;renderCard();});
  $('#card-prev').addEventListener('click',()=>{index--;flipped=false;renderCard();});
  $('#card-next').addEventListener('click',()=>{index++;flipped=false;renderCard();});
  const markCard=known=>{const d=deck();if(!d.length)return;const v=d[index];
    if(known)progress.known[v.term]=true;else delete progress.known[v.term];save();renderKnown();
    if(!(filter==='todo'&&known))index++;flipped=false;renderCard();};
  $('#card-known').addEventListener('click',()=>markCard(true));
  $('#card-todo').addEventListener('click',()=>markCard(false));
  $$('.filter').forEach(b=>b.addEventListener('click',()=>{filter=b.dataset.filter;index=0;flipped=false;
    $$('.filter').forEach(o=>o.setAttribute('aria-pressed',String(o===b)));renderCard();}));

  // Multiple-choice questions
  const showQuiz=(quiz,chosen)=>{
    const answer=+quiz.dataset.answer;
    $$('.option',quiz).forEach((o,i)=>{o.classList.toggle('right',i===answer);o.classList.toggle('wrong',i===chosen&&i!==answer);o.setAttribute('aria-pressed',String(i===chosen));});
    const fb=$('.feedback',quiz);fb.hidden=false;
    $('.verdict',fb).textContent=chosen===answer?'正解です。':'不正解です。正しい答えは '+(answer+1)+' 番です。';
  };
  $$('.option').forEach(o=>o.addEventListener('click',()=>{
    const quiz=o.closest('.quiz');const i=+o.dataset.i;progress.quiz[quiz.id]=i;save();showQuiz(quiz,i);renderScore();}));
  const renderScore=()=>{
    $$('.step').forEach(s=>{const qs=$$('.quiz[data-answer]',s);if(!qs.length)return;
      const done=qs.filter(q=>q.id in progress.quiz);const right=done.filter(q=>progress.quiz[q.id]===+q.dataset.answer);
      let out=$('.score',s);if(!out){out=document.createElement('p');out.className='score';$('.done-row',s).before(out);}
      out.textContent=`問題：${done.length} / ${qs.length} 回答、正解 ${right.length}`;});
  };

  // Dictation: character diff against the script, punctuation ignored.
  const norm=s=>s.normalize('NFKC').replace(/[\s、。，．,.「」『』（）()？！?!・…ー―:：;；"'“”]/g,'');
  const diff=(a,b)=>{ // a: answer, b: typed
    const n=a.length,m=b.length,L=Array.from({length:n+1},()=>new Uint16Array(m+1));
    for(let i=n-1;i>=0;i--)for(let j=m-1;j>=0;j--)L[i][j]=a[i]===b[j]?L[i+1][j+1]+1:Math.max(L[i+1][j],L[i][j+1]);
    const out=[];let i=0,j=0;
    while(i<n||j<m){
      if(i<n&&j<m&&a[i]===b[j]){out.push(['ok',a[i]]);i++;j++;}
      else if(j<m&&(i===n||L[i][j+1]>=L[i+1][j])){out.push(['extra',b[j]]);j++;}
      else{out.push(['miss',a[i]]);i++;}
    }
    return {parts:out,score:n?L[0][0]/n:1};
  };
  $$('.dictation').forEach(box=>{
    $('.check-dict',box).addEventListener('click',()=>{
      const answer=norm(lesson.dictation[box.dataset.turn]);const typed=norm($('textarea',box).value);
      const {parts,score}=diff(answer,typed);const out=$('.diff',box);out.hidden=false;out.textContent='';
      const p=document.createElement('p');
      parts.forEach(([k,ch])=>{const s=document.createElement('span');s.className=k;s.textContent=ch;p.append(s);});
      const sum=document.createElement('p');sum.className='verdict';
      sum.textContent=`一致：${Math.round(score*100)}%（緑＝正しい、赤＝抜けた文字、取り消し線＝余分な文字）`;
      out.append(sum,p);progress.quiz[box.id+'-score']=Math.round(score*100);save();
    });
  });

  renderSteps();renderCard();renderKnown();
  Object.entries(progress.quiz).forEach(([id,i])=>{const q=document.getElementById(id);if(q&&q.dataset.answer!==undefined)showQuiz(q,i);});
  renderScore();
}
