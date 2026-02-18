// SocialPay v3.0 - app.js

// ===== TOAST =====
function showToast(msg, type = 'info') {
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  let c = document.getElementById('toast-container');
  if (!c) { c = document.createElement('div'); c.id = 'toast-container'; c.className = 'toast-container'; document.body.appendChild(c); }
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span>${icons[type]||'•'}</span><span>${msg}</span>`;
  c.appendChild(t);
  setTimeout(() => t.remove(), 3400);
}

// ===== MODAL =====
function openModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.add('active'); document.body.style.overflow = 'hidden'; }
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.remove('active'); document.body.style.overflow = ''; }
}
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('active');
    document.body.style.overflow = '';
  }
});

// ===== AJAX POST =====
async function postForm(url, fd, btn) {
  const orig = btn ? btn.innerHTML : '';
  if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>'; }
  try {
    const res = await fetch(url, { method: 'POST', body: fd });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'success');
      if (data.redirect) setTimeout(() => location.href = data.redirect, 800);
      if (data.otp_required) {
        setTimeout(() => location.href = '/verify_otp', 600);
      }
    } else {
      showToast(data.message || 'Error', 'error');
    }
    return data;
  } catch (e) {
    showToast('Network error. Check your connection.', 'error');
    return null;
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = orig; }
  }
}

// ===== BALANCE TOGGLE =====
let balHidden = false;
function toggleBalance() {
  balHidden = !balHidden;
  document.querySelectorAll('.balance-amount, .chip-value').forEach(el => {
    el.style.filter = balHidden ? 'blur(10px)' : 'none';
  });
  const eb = document.getElementById('eyeBtn');
  if (eb) eb.textContent = balHidden ? '🙈' : '👁️';
}

// ===== COPY =====
function copyText(text, msg) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => showToast(msg || 'Copied!', 'success'));
  } else {
    const ta = document.createElement('textarea');
    ta.value = text; document.body.appendChild(ta);
    ta.select(); document.execCommand('copy');
    document.body.removeChild(ta);
    showToast(msg || 'Copied!', 'success');
  }
}

// ===== OTP BOXES =====
function initOtpBoxes() {
  const boxes = document.querySelectorAll('.otp-input');
  boxes.forEach((box, i) => {
    box.addEventListener('input', e => {
      const val = e.target.value.replace(/\D/g, '');
      e.target.value = val.slice(-1);
      if (val && i < boxes.length - 1) boxes[i + 1].focus();
      collectOtp();
    });
    box.addEventListener('keydown', e => {
      if (e.key === 'Backspace' && !box.value && i > 0) {
        boxes[i - 1].focus();
      }
    });
    box.addEventListener('paste', e => {
      e.preventDefault();
      const pasted = e.clipboardData.getData('text').replace(/\D/g,'');
      boxes.forEach((b, j) => { b.value = pasted[j] || ''; });
      collectOtp();
      boxes[Math.min(pasted.length, boxes.length - 1)].focus();
    });
  });
}

function collectOtp() {
  const boxes = document.querySelectorAll('.otp-input');
  const otp = Array.from(boxes).map(b => b.value).join('');
  const hidden = document.getElementById('otp-hidden');
  if (hidden) hidden.value = otp;
  if (otp.length === 6) {
    setTimeout(() => document.getElementById('otp-form-btn')?.click(), 100);
  }
}

// ===== USER LOOKUP =====
async function lookupUser(uid, targetId) {
  const el = document.getElementById(targetId);
  if (!uid || uid.length < 5) { if (el) el.textContent = ''; return; }
  try {
    const res = await fetch('/api/user_lookup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: uid })
    });
    const data = await res.json();
    if (el) {
      el.textContent = data.found ? `✅ ${data.name}` : '❌ Not found';
      el.style.color = data.found ? '#06D6A0' : '#EF233C';
    }
  } catch {}
}

// ===== NOTIF BADGE =====
async function updateNotifBadge() {
  try {
    const res = await fetch('/api/notif_count');
    const data = await res.json();
    const el = document.getElementById('notif-badge');
    if (el) {
      if (data.count > 0) {
        el.textContent = data.count > 9 ? '9+' : data.count;
        el.style.display = 'flex';
      } else {
        el.style.display = 'none';
      }
    }
  } catch {}
}

if (document.getElementById('notif-badge')) {
  updateNotifBadge();
  setInterval(updateNotifBadge, 30000);
}

// ===== ACTIVE NAV =====
document.addEventListener('DOMContentLoaded', () => {
  const path = location.pathname;
  document.querySelectorAll('.nav-item').forEach(item => {
    const href = item.getAttribute('href');
    if (href && path === href) item.classList.add('active');
    else if (href && href !== '/' && path.startsWith(href)) item.classList.add('active');
  });
  initOtpBoxes();
});

// ===== TIMER =====
function startResendTimer(btnId, seconds = 60) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  let left = seconds;
  btn.disabled = true;
  const iv = setInterval(() => {
    left--;
    btn.textContent = `Resend (${left}s)`;
    if (left <= 0) {
      clearInterval(iv);
      btn.disabled = false;
      btn.textContent = btn.dataset.label || 'Resend OTP';
    }
  }, 1000);
}

// ===== PASSWORD TOGGLE =====
function togglePw(inputId, btn) {
  const inp = document.getElementById(inputId);
  if (!inp) return;
  if (inp.type === 'password') { inp.type = 'text'; btn.textContent = '🙈'; }
  else { inp.type = 'password'; btn.textContent = '👁️'; }
}

// ===== FORMAT MONEY =====
function fmtMoney(n, curr = 'naira') {
  const num = parseFloat(n);
  if (curr === 'dollar') return `$${num.toFixed(4)}`;
  return `₦${num.toLocaleString('en-NG', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}
