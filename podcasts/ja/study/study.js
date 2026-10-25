'use strict';
const englishButton=document.getElementById('english-toggle');
const readingsButton=document.getElementById('readings-toggle');
englishButton.addEventListener('click',()=>{
  const hidden=document.body.classList.toggle('japanese-only');
  englishButton.setAttribute('aria-pressed',String(!hidden));
  englishButton.textContent=hidden?'English: off':'English: on';
});
readingsButton.addEventListener('click',()=>{
  const hidden=document.body.classList.toggle('hide-readings');
  readingsButton.setAttribute('aria-pressed',String(!hidden));
  readingsButton.textContent=hidden?'ふりがな：非表示':'ふりがな：表示';
});
