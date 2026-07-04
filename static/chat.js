const thread = document.getElementById('thread');
const composer = document.getElementById('composer');
const input = document.getElementById('input');
const sendBtn = document.getElementById('sendBtn');
const starters = document.getElementById('starters');

function addUserMessage(text) {
  const row = document.createElement('div');
  row.className = 'msg-row user';
  const label = document.createElement('span');
  label.className = 'msg-label';
  label.textContent = 'You';
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;
  row.append(label, bubble);
  thread.appendChild(row);
  thread.scrollTop = thread.scrollHeight;
}

function addTypingRow() {
  const row = document.createElement('div');
  row.className = 'msg-row assistant';
  row.innerHTML =
    '<span class="msg-label">Assistant</span><div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
  thread.appendChild(row);
  thread.scrollTop = thread.scrollHeight;
  return row;
}

function renderSources(row, sources) {
  if (!sources || !sources.length) return;
  const src = document.createElement('div');
  src.className = 'sources';
  src.innerHTML = sources.map((s) => `<span class="source-chip">${escapeHtml(s)}</span>`).join('');
  row.appendChild(src);
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

async function streamResponse(question) {
  const typingRow = addTypingRow();
  let row = null;
  let bubble = null;
  let cursor = null;
  let fullText = '';

  try {
    const resp = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: question }),
    });

    if (!resp.ok || !resp.body) {
      throw new Error(`Request failed: ${resp.status}`);
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const frames = buffer.split('\n\n');
      buffer = frames.pop(); // last (possibly incomplete) frame stays in the buffer

      for (const frame of frames) {
        const eventMatch = frame.match(/^event: (.+)$/m);
        const dataMatch = frame.match(/^data: (.+)$/m);
        if (!eventMatch || !dataMatch) continue;

        const eventType = eventMatch[1];
        const data = JSON.parse(dataMatch[1]);

        if (eventType === 'token') {
          if (!row) {
            typingRow.remove();
            row = document.createElement('div');
            row.className = 'msg-row assistant';
            bubble = document.createElement('div');
            bubble.className = 'bubble';
            cursor = document.createElement('span');
            cursor.className = 'cursor';
            bubble.appendChild(cursor);
            row.innerHTML = '<span class="msg-label">Assistant</span>';
            row.appendChild(bubble);
            thread.appendChild(row);
          }
          fullText += data.text;
          bubble.textContent = fullText;
          bubble.appendChild(cursor);
          thread.scrollTop = thread.scrollHeight;
        } else if (eventType === 'done') {
          if (cursor) cursor.remove();
          if (row) renderSources(row, data.sources);
          thread.scrollTop = thread.scrollHeight;
        }
      }
    }
  } catch (err) {
    typingRow.remove();
    const row = document.createElement('div');
    row.className = 'msg-row assistant';
    row.innerHTML = `<span class="msg-label">Assistant</span><div class="bubble">Something went wrong reaching the server. Please try again.</div>`;
    thread.appendChild(row);
    thread.scrollTop = thread.scrollHeight;
  }
}

function ask(text) {
  addUserMessage(text);
  starters.style.display = 'none';
  streamResponse(text);
}

starters.addEventListener('click', (e) => {
  const btn = e.target.closest('.starter-chip');
  if (!btn) return;
  ask(btn.dataset.q);
});

composer.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  input.style.height = 'auto';
  ask(text);
});

input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 120) + 'px';
});

input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    composer.requestSubmit();
  }
});

// ---------- QE / Run Tests panel ----------

const qeToggle = document.getElementById('qeToggle');
const qePanel = document.getElementById('qePanel');
const qeRunBtn = document.getElementById('qeRunBtn');
const qeProgress = document.getElementById('qeProgress');

qeToggle.addEventListener('click', () => {
  const isOpen = !qePanel.hidden;
  qePanel.hidden = isOpen;
  qeToggle.setAttribute('aria-expanded', String(!isOpen));
});

function addToolResultMessage(result) {
  const row = document.createElement('div');
  row.className = 'msg-row assistant';
  const label = document.createElement('span');
  label.className = 'msg-label';
  label.textContent = 'Assistant';
  const bubble = document.createElement('div');
  bubble.className = 'bubble';

  if (result.error) {
    bubble.textContent = result.error;
  } else {
    bubble.textContent = `Ran: ${result.command}\n\n${result.passed} passed, ${result.failed} failed.` +
      (result.failed_test_names && result.failed_test_names.length
        ? `\n\nFailed:\n${result.failed_test_names.map((n) => `- ${n}`).join('\n')}`
        : '');
  }

  row.append(label, bubble);

  const badgeRow = document.createElement('div');
  badgeRow.className = 'sources';
  badgeRow.innerHTML = '<span class="tool-badge">⚙ run_playwright_tests</span>';
  row.appendChild(badgeRow);

  thread.appendChild(row);
  thread.scrollTop = thread.scrollHeight;
}

qeRunBtn.addEventListener('click', async () => {
  const suite = document.getElementById('qeSuite').value || undefined;
  const project = document.getElementById('qeProject').value || undefined;
  const tag = document.getElementById('qeTag').value || undefined;
  const test_file = document.getElementById('qeTestFile').value.trim() || undefined;
  const headed = document.getElementById('qeHeaded').checked;

  const summaryParts = [];
  if (test_file) summaryParts.push(test_file);
  else if (suite) summaryParts.push(`${suite} suite`);
  else summaryParts.push('all tests');
  if (project) summaryParts.push(`on ${project}`);
  if (tag) summaryParts.push(tag);
  addUserMessage(`Run ${summaryParts.join(' ')}`);

  qeRunBtn.disabled = true;
  qeProgress.hidden = false;
  starters.style.display = 'none';

  try {
    const resp = await fetch('/api/run-tests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ suite, project, tag, test_file, headed }),
    });
    const result = await resp.json();
    addToolResultMessage(result);
  } catch (err) {
    addToolResultMessage({ error: 'Something went wrong reaching the server. Please try again.' });
  } finally {
    qeRunBtn.disabled = false;
    qeProgress.hidden = true;
  }
});
