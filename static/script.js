let chat;
let input;
let sendBtn;
let emptyState;

// Use a relative URL so the frontend works on both localhost and 127.0.0.1 without cross-origin issues.
const API_URL = '/chat';
let entryCount = 0;

function autoGrow(){
  if (!input) return;
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 120) + 'px';
}

function scrollToBottom(){
  chat.scrollTop = chat.scrollHeight;
}

function addUserMessage(text){
  if(emptyState) emptyState.remove();
  const row = document.createElement('div');
  row.className = 'row user';
  row.innerHTML = `<div class="bubble-user"></div>`;
  row.querySelector('.bubble-user').textContent = text;
  chat.appendChild(row);
  scrollToBottom();
}

function addThinking(){
  const row = document.createElement('div');
  row.className = 'row bot thinking';
  row.id = 'thinkingRow';
  row.innerHTML = `
    <div class="entry">
      <div class="entry-body"><span class="tick"></span><span class="tick"></span><span class="tick"></span></div>
    </div>`;
  chat.appendChild(row);
  scrollToBottom();
}

function removeThinking(){
  const el = document.getElementById('thinkingRow');
  if(el) el.remove();
}

function addBotMessage(text){
  entryCount++;
  const tag = 'ENTRY ' + String(entryCount).padStart(3, '0');
  const row = document.createElement('div');
  row.className = 'row bot';
  row.innerHTML = `
    <div class="entry">
      <div class="entry-tag">${tag}</div>
      <div class="entry-body"></div>
    </div>`;
  // Render formatted reply: paragraphs and simple lists. Escape HTML to avoid XSS.
  function escapeHtml(str){
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function formatToHtml(raw){
    const lines = String(raw).split(/\r?\n/);
    let html = '';
    let inList = false;
    let listType = 'ul';

    for(let i=0;i<lines.length;i++){
      const line = lines[i].trim();
      if(line === ''){
        if(inList){ html += `</${listType}>`; inList = false; }
        else html += '<p></p>';
        continue;
      }

      const mUn = line.match(/^[-*]\s+(.*)$/);
      const mOl = line.match(/^(\d+)\.\s+(.*)$/);

      if(mUn){
        if(!inList){ html += '<ul>'; inList = true; listType = 'ul'; }
        html += `<li>${escapeHtml(mUn[1])}</li>`;
      } else if(mOl){
        if(!inList){ html += '<ol>'; inList = true; listType = 'ol'; }
        html += `<li>${escapeHtml(mOl[2])}</li>`;
      } else {
        if(inList){ html += `</${listType}>`; inList = false; }
        html += `<p>${escapeHtml(line)}</p>`;
      }
    }

    if(inList) html += `</${listType}>`;
    return html;
  }

  row.querySelector('.entry-body').innerHTML = formatToHtml(text);
  chat.appendChild(row);
  scrollToBottom();
}

async function sendMessage(text){
  if(!text.trim()) return;
  addUserMessage(text);
  input.value = '';
  autoGrow();
  sendBtn.disabled = true;
  addThinking();

  try{
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        temperature: 0.7,
        top_p: 0.9
      })
    });

    if(!res.ok) {
      const errorText = await res.text();
      throw new Error(`Request failed: ${res.status} ${errorText}`);
    }

    const data = await res.json();
    removeThinking();
    addBotMessage(data.reply || "Ledger couldn't find an answer for that.");
  }catch(err){
    removeThinking();
    console.error('Chat request failed:', err);
    addBotMessage("Couldn't reach the advisor right now — check that the backend is running and try again.");
  }finally{
    sendBtn.disabled = false;
  }
}

function initChat(){
  chat = document.getElementById('chat');
  input = document.getElementById('input');
  sendBtn = document.getElementById('sendBtn');
  emptyState = document.getElementById('emptyState');

  if (!chat || !input || !sendBtn) {
    console.error('Chat app failed to initialize: missing DOM elements');
    return;
  }

  sendBtn.addEventListener('click', () => sendMessage(input.value));

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input.value);
    }
  });

  input.addEventListener('input', autoGrow);

  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => sendMessage(chip.dataset.prompt));
  });
}

document.addEventListener('DOMContentLoaded', initChat);
