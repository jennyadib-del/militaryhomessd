(function () {
  'use strict';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Header: solid on scroll ---------- */
  var header = document.querySelector('[data-header]');
  var mobileCta = document.querySelector('[data-mobile-cta]');
  var ticking = false;
  function onScroll() {
    var y = window.scrollY;
    if (header) header.classList.toggle('is-solid', y > 40);
    if (mobileCta) mobileCta.classList.toggle('show', y > 600);
    ticking = false;
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  /* ---------- Dropdown menus ---------- */
  var toggles = document.querySelectorAll('.nav-toggle');
  function closeAll(except) {
    toggles.forEach(function (t) {
      if (t !== except) { t.setAttribute('aria-expanded', 'false'); t.parentElement.classList.remove('open'); }
    });
  }
  toggles.forEach(function (t) {
    t.addEventListener('click', function () {
      var open = t.getAttribute('aria-expanded') === 'true';
      closeAll(t);
      t.setAttribute('aria-expanded', String(!open));
      t.parentElement.classList.toggle('open', !open);
    });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.has-sub')) closeAll(); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      var openT = document.querySelector('.nav-toggle[aria-expanded="true"]');
      closeAll();
      if (openT) openT.focus();
      if (drawer && drawer.classList.contains('open')) closeDrawer();
    }
  });
  document.querySelectorAll('.has-sub').forEach(function (li) {
    li.addEventListener('focusout', function (e) { if (!li.contains(e.relatedTarget)) { var t = li.querySelector('.nav-toggle'); t.setAttribute('aria-expanded', 'false'); li.classList.remove('open'); } });
  });

  /* ---------- Mobile drawer ---------- */
  var drawer = document.querySelector('[data-drawer]');
  var openBtn = document.querySelector('[data-menu-open]');
  var closeBtn = document.querySelector('[data-menu-close]');
  function openDrawer() {
    drawer.classList.add('open'); openBtn.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden'; closeBtn.focus();
  }
  function closeDrawer() {
    drawer.classList.remove('open'); openBtn.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = ''; openBtn.focus();
  }
  if (drawer && openBtn) {
    openBtn.addEventListener('click', openDrawer);
    closeBtn.addEventListener('click', closeDrawer);
    drawer.addEventListener('click', function (e) { if (e.target.closest('a')) { drawer.classList.remove('open'); document.body.style.overflow = ''; } });
    drawer.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab') return;
      var f = drawer.querySelectorAll('a, button'); var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
  }

  /* ---------- Hero tabs (Buy / Sell / PCS / Contact) ---------- */
  var heroForm = document.querySelector('[data-hero-search]');
  if (heroForm) {
    var input = heroForm.querySelector('input');
    var label = heroForm.querySelector('label');
    var btnText = heroForm.querySelector('[data-btn-text]');
    var tabs = document.querySelectorAll('.hero-tabs [role="tab"]');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        tabs.forEach(function (t) { t.setAttribute('aria-selected', 'false'); t.tabIndex = -1; });
        tab.setAttribute('aria-selected', 'true'); tab.tabIndex = 0;
        heroForm.action = tab.dataset.action;
        input.name = tab.dataset.name;
        input.placeholder = tab.dataset.placeholder;
        label.textContent = tab.dataset.label;
        btnText.textContent = tab.dataset.btn;
      });
      tab.addEventListener('keydown', function (e) {
        var i = Array.prototype.indexOf.call(tabs, tab);
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
          e.preventDefault();
          var n = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
          n.focus(); n.click();
        }
      });
    });
  }

  /* ---------- Prefill forms from URL (?q= / ?address=) ---------- */
  var params = new URLSearchParams(location.search);
  var q = params.get('q'), addr = params.get('address');
  if (q) document.querySelectorAll('input[name="areas"]').forEach(function (i) { i.value = q; });
  if (addr) document.querySelectorAll('input[name="street"]').forEach(function (i) { i.value = addr; });

  /* ---------- Attribution (UTM) kept for the session ---------- */
  try {
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'fbclid'].forEach(function (k) {
      if (params.get(k)) sessionStorage.setItem(k, params.get(k));
    });
    if (!sessionStorage.getItem('landing')) sessionStorage.setItem('landing', location.pathname);
    if (!sessionStorage.getItem('referrer') && document.referrer) sessionStorage.setItem('referrer', document.referrer);
  } catch (e) { /* storage unavailable */ }

  /* ---------- Lead forms ---------- */
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  function setError(field, msg) {
    var err = document.getElementById(field.getAttribute('aria-describedby'));
    field.setAttribute('aria-invalid', msg ? 'true' : 'false');
    if (err) err.textContent = msg || '';
  }
  function validateField(field) {
    var v = field.value.trim();
    var name = (field.labels && field.labels[0] ? field.labels[0].textContent.replace(/[*()]|optional/g, '').trim() : field.name);
    if (field.required && !v) { setError(field, 'Please enter your ' + name.toLowerCase() + '.'); return false; }
    if (field.type === 'email' && v && !EMAIL_RE.test(v)) { setError(field, 'Please enter a valid email, like name@example.com.'); return false; }
    if (field.type === 'tel' && v && v.replace(/\D/g, '').length < 10) { setError(field, 'Please enter a 10-digit phone number, or leave it blank.'); return false; }
    setError(field, '');
    return true;
  }

  document.querySelectorAll('[data-lead-form]').forEach(function (form) {
    var fields = form.querySelectorAll('input[required], input[type=email], input[type=tel], select[required]');
    fields.forEach(function (f) {
      f.addEventListener('blur', function () { if (f.value.trim() || f.getAttribute('aria-invalid') === 'true') validateField(f); });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var status = form.querySelector('.form-status');
      var btn = form.querySelector('button[type=submit]');
      var bad = [];
      fields.forEach(function (f) { if (!validateField(f)) bad.push(f); });
      if (bad.length) {
        var summary = form.querySelector('.form-errors');
        summary.textContent = 'Please fix ' + bad.length + (bad.length > 1 ? ' fields' : ' field') + ' before sending.';
        bad[0].focus();
        return;
      }
      if (form.company && form.company.value) return; // honeypot

      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = String(v).trim(); });
      data.formType = form.dataset.formType;
      data.pageUrl = location.href;
      data.pageTitle = document.title;
      data.smsConsent = !!(form.sms_consent && form.sms_consent.checked);
      data.consentText = form.querySelector('.consent label').textContent.replace(/\s+/g, ' ').trim();
      try {
        ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'fbclid', 'landing', 'referrer'].forEach(function (k) {
          var v = sessionStorage.getItem(k); if (v) data[k] = v;
        });
      } catch (err) { /* ignore */ }

      btn.setAttribute('aria-busy', 'true'); btn.disabled = true;
      var original = btn.textContent; btn.textContent = 'Sending…';
      status.className = 'form-status'; status.textContent = '';

      fetch('/.netlify/functions/lead', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
      }).then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json().catch(function () { return {}; });
      }).then(function () {
        var msgs = {
          pcs_guide: 'Thank you! Your San Diego PCS Guide is ready: <a href="/pcs-guide/">open your guide</a>. A copy is headed to your inbox too.',
          home_value: 'Thank you! I\'m preparing your custom home value report and will reach out within one business day.',
          search: 'Thank you! I\'m building your personalized home search and will send your first matches shortly.',
          contact: 'Thank you! Your message is in. I\'ll get back to you personally, usually the same day.'
        };
        form.reset();
        status.className = 'form-status ok';
        status.innerHTML = msgs[form.dataset.formType] || msgs.contact;
        if (window.dataLayer) window.dataLayer.push({ event: 'lead_submit', form_type: form.dataset.formType });
      }).catch(function () {
        status.className = 'form-status err';
        status.innerHTML = 'Sorry, something went wrong sending your info. Please try again, or reach Jenny directly at <a href="tel:' +
          (document.body.dataset.tel || '') + '">' + (document.body.dataset.phone || 'the phone number below') + '</a>.';
      }).finally(function () {
        btn.removeAttribute('aria-busy'); btn.disabled = false; btn.textContent = original;
      });
    });
  });

  /* ---------- Scroll reveal ---------- */
  var reveals = document.querySelectorAll('.reveal');
  if (!reduce && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('in'); });
  }
})();

/* ---------- Review cards: preview + "Read full review" ---------- */
(function () {
  var cards = document.querySelectorAll('.review-card');
  if (!cards.length) return;
  document.documentElement.classList.add('js-clamp');
  cards.forEach(function (card) {
    var text = card.querySelector('.review-text');
    var btn = card.querySelector('.review-more');
    if (text.scrollHeight > text.clientHeight + 4 || text.querySelectorAll('p').length > 1) btn.classList.add('needed');
    btn.addEventListener('click', function () {
      var open = text.classList.toggle('open');
      btn.setAttribute('aria-expanded', String(open));
      btn.textContent = open ? 'Show less' : 'Read full review';
    });
  });
})();
