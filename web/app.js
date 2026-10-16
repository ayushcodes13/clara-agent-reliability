const form = document.querySelector('#query-form');
const queryInput = document.querySelector('#query');
const runButton = document.querySelector('#run-button');
const statusLine = document.querySelector('#form-status');
const results = document.querySelector('#results');
const recommendations = document.querySelector('#recommendations');

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function listBlock(title, values, className = '') {
  const wrap = el('div', className);
  wrap.append(el('h4', '', title));
  const list = el('ul');
  (values.length ? values : ['No flags recorded']).forEach((value) => list.append(el('li', '', value)));
  wrap.append(list);
  return wrap;
}

function renderCard(item, query) {
  const card = el('article', 'recommendation-card');
  const top = el('div', 'recommendation-top');
  const identity = el('div');
  identity.append(el('h3', '', item.product_name), el('span', 'product-id', item.product_id));
  const gated = item.doctor_review?.requires_doctor_review;
  top.append(identity, el('span', gated ? 'gate-badge' : 'clear-badge', gated ? 'DOCTOR REVIEW' : 'NO HOLD'));
  card.append(top, el('p', 'recommendation-message', item.message));

  const columns = el('div', 'result-columns');
  columns.append(listBlock('CATALOGUE CLAIMS', item.grounded_claims || []));
  columns.append(listBlock('RISK FACTORS', item.risk_flags || [], 'risk-list'));
  card.append(columns);
  if (gated && (item.doctor_review?.reasons || []).length) {
    card.append(listBlock('WHY THIS IS HELD', item.doctor_review.reasons, 'review-reasons'));
  }

  const feedback = el('div', 'feedback');
  feedback.append(el('span', 'feedback-label', 'WAS THIS REVIEW USEFUL?'));
  const message = el('p', 'feedback-message');
  ['helpful', 'unsafe'].forEach((value) => {
    const button = el('button', '', value === 'helpful' ? 'Helpful' : 'Flag for review');
    button.type = 'button';
    button.addEventListener('click', () => submitFeedback(item, query, value, feedback, message));
    feedback.append(button);
  });
  card.append(feedback, message);
  return card;
}

async function submitFeedback(item, query, value, container, message) {
  if (container.querySelector('.feedback-note')) return;
  const noteRow = el('div', 'feedback-note');
  const input = document.createElement('input');
  input.maxLength = 500;
  input.setAttribute('aria-label', 'Optional feedback note');
  input.placeholder = 'Optional note for the local review log';
  const save = el('button', '', 'Save feedback');
  save.type = 'button';
  save.addEventListener('click', async () => {
    save.disabled = true;
    try {
      const response = await fetch('/api/feedback', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, product_id: item.product_id, feedback: value, reason: input.value }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Feedback could not be saved.');
      message.textContent = 'Feedback saved to data/feedback_log.csv on this machine.';
      container.querySelectorAll('button').forEach((button) => button.classList.add('selected'));
      noteRow.remove();
    } catch (error) {
      message.textContent = error.message;
      save.disabled = false;
    }
  });
  noteRow.append(input, save);
  container.after(noteRow);
  input.focus();
}

function renderResult(data) {
  recommendations.replaceChildren();
  const route = data.route || data.trace?.route || { route: 'unknown', reason: 'No route details recorded.' };
  const queryHeld = route.route === 'doctor_review';
  const heldCount = (data.user_response || []).filter((item) => item.doctor_review?.requires_doctor_review).length;
  const gated = queryHeld || heldCount > 0;
  const summary = document.querySelector('#route-summary');
  summary.className = `route-summary${gated ? ' gated' : ''}`;
  summary.replaceChildren();
  summary.append(el('span', 'route-icon', gated ? '!' : '✓'));
  const detail = el('div');
  const title = queryHeld ? 'Query held for doctor review' : heldCount ? `${heldCount} ${heldCount === 1 ? 'product requires' : 'products require'} doctor review` : 'Review complete';
  detail.append(el('strong', '', title));
  detail.append(el('p', '', `Route: ${route.route.replaceAll('_', ' ')} · ${route.reason}`));
  summary.append(detail);

  const responseItems = data.user_response || [];
  if (responseItems.length === 0) {
    recommendations.append(el('article', 'recommendation-card empty-result', 'No matching catalogue products were returned. Try a more specific skincare or haircare query.'));
  }
  responseItems.forEach((item) => recommendations.append(renderCard(item, data.user_query || queryInput.value.trim())));
  document.querySelector('#result-time').textContent = `${responseItems.length} ${responseItems.length === 1 ? 'product' : 'products'} · ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;

  const trace = data.trace || {};
  const traceContent = document.querySelector('#trace-content');
  traceContent.replaceChildren();
  const meta = el('div', 'trace-meta');
  [['QUERY', trace.user_query || data.user_query || '—'], ['RETRIEVED IDS', (trace.retrieved_product_ids || []).join(', ') || 'None'], ['ROUTE', route.route], ['TIMESTAMP (UTC)', trace.timestamp || '—']].forEach(([label, value]) => {
    const cell = el('div'); cell.append(el('span', '', label), el('strong', '', value)); meta.append(cell);
  });
  traceContent.append(meta);
  const steps = el('ol');
  (trace.pipeline_steps || []).forEach((step) => steps.append(el('li', '', step.replaceAll('_', ' '))));
  traceContent.append(steps);
  results.hidden = false;
  results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

queryInput.addEventListener('input', () => { document.querySelector('#char-count').textContent = queryInput.value.length; });
document.querySelectorAll('.sample-chip').forEach((button) => button.addEventListener('click', () => {
  queryInput.value = button.dataset.query;
  queryInput.dispatchEvent(new Event('input'));
  queryInput.focus();
}));

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  statusLine.textContent = '';
  runButton.disabled = true;
  runButton.querySelector('span').textContent = 'Reviewing…';
  try {
    const response = await fetch('/api/run', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: queryInput.value.trim() }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Review could not be completed.');
    renderResult(data);
  } catch (error) {
    statusLine.textContent = error.message;
  } finally {
    runButton.disabled = false;
    runButton.querySelector('span').textContent = 'Run review';
  }
});
