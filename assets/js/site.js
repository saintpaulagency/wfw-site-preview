(function () {
  var qs = function (s, r) { return (r || document).querySelector(s); };
  var qsa = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var store = {
    get: function () { try { return JSON.parse(sessionStorage.getItem('donation') || '{}'); } catch (e) { return {}; } },
    set: function (o) { try { var d = store.get(); for (var k in o) d[k] = o[k]; sessionStorage.setItem('donation', JSON.stringify(d)); } catch (e) {} },
    clear: function () { try { sessionStorage.removeItem('donation'); } catch (e) {} }
  };

  // Menu
  var mb = qs('.menu-btn'), nav = qs('#site-nav');
  if (mb && nav) {
    mb.addEventListener('click', function () {
      var open = mb.getAttribute('aria-expanded') === 'true';
      mb.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('open', !open);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) { nav.classList.remove('open'); mb.setAttribute('aria-expanded', 'false'); mb.focus(); }
    });
  }

  // ZIP and number fields: digits only
  qsa('input[data-digits]').forEach(function (i) {
    i.addEventListener('input', function () { var v = i.value.replace(/\D/g, '').slice(0, +i.getAttribute('data-digits')); if (v !== i.value) i.value = v; });
  });

  // Start card on home and state pages
  qsa('form.start-card').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var picked = qs('input[name=vehicle]:checked', f);
      var zip = qs('input[name=zip]', f);
      var err = qs('.form-error', f);
      var msg = '';
      if (!picked) msg = 'Choose what you are donating.';
      else if (!/^\d{5}$/.test(zip.value)) msg = 'Enter the 5-digit ZIP code where we pick up the vehicle.';
      if (msg) { err.textContent = msg; err.hidden = false; (picked ? zip : qs('input[name=vehicle]', f)).focus(); return; }
      err.hidden = true;
      store.set({ vehicle: picked.value, zip: zip.value });
      window.location.href = f.getAttribute('action');
    });
  });

  // Sticky mobile button
  var sticky = qs('.sticky-cta'), card = qs('.start-card');
  if (sticky && card && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      var e = entries[0];
      sticky.classList.toggle('show', !e.isIntersecting && e.boundingClientRect.top < 0);
    }).observe(card);
    var go = qs('[data-to-start]', sticky);
    if (go) go.addEventListener('click', function (e) {
      e.preventDefault();
      card.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'center' });
      var first = qs('input[name=vehicle]', card); if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, 350);
    });
  }

  // Donation flow
  var df = qs('#donate-form');
  if (df) {
    var steps = qsa('.step', df), cur = 0, data = store.get();
    if (data.vehicle) { var r = qs('input[name=vehicle][value="' + data.vehicle + '"]', df); if (r) r.checked = true; }
    if (data.zip) qsa('input[name=zip]', df).forEach(function (i) { i.value = data.zip; });
    var show = function (i, focus) {
      cur = i;
      steps.forEach(function (s, j) { s.hidden = j !== i; });
      qs('.progress-text').textContent = 'Step ' + (i + 1) + ' of ' + steps.length;
      qsa('.progress-bar span').forEach(function (b, j) { b.classList.toggle('done', j <= i); });
      if (focus) { var h = qs('h2', steps[i]); h.setAttribute('tabindex', '-1'); h.focus(); window.scrollTo(0, 0); }
    };
    var clearErrors = function (step) { qsa('.field-error', step).forEach(function (e) { e.remove(); }); qsa('[aria-invalid]', step).forEach(function (e) { e.removeAttribute('aria-invalid'); }); };
    var validate = function (step) {
      clearErrors(step);
      var firstBad = null;
      qsa('[data-check]', step).forEach(function (wrap) {
        var input = qs('input,select', wrap), ok = true, kind = wrap.getAttribute('data-check');
        if (input.type === 'radio') { ok = !!qs('input:checked', wrap); input = qs('input', wrap); }
        else if (kind === 'zip') ok = /^\d{5}$/.test(input.value);
        else if (kind === 'phone') ok = input.value.replace(/\D/g, '').length === 10;
        else if (kind === 'email') ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value.trim());
        else ok = input.value.trim() !== '';
        if (!ok) {
          var id = (input.id || input.name) + '-err', m = document.createElement('span');
          m.className = 'field-error'; m.id = id; m.textContent = wrap.getAttribute('data-msg');
          wrap.appendChild(m);
          if (input.type !== 'radio') { input.setAttribute('aria-invalid', 'true'); input.setAttribute('aria-describedby', id); }
          if (!firstBad) firstBad = input;
        }
      });
      if (firstBad) firstBad.focus();
      return !firstBad;
    };
    var clearOne = function (e) {
      var w = e.target.closest('[data-check]'); if (!w) return;
      var m = qs('.field-error', w); if (m) m.remove();
      e.target.removeAttribute('aria-invalid');
    };
    df.addEventListener('input', clearOne);
    df.addEventListener('change', clearOne);
    qsa('[data-next]', df).forEach(function (b) {
      b.addEventListener('click', function () {
        if (!validate(steps[cur])) return;
        if (cur === 1) store.set({ first: qs('#first', df).value.trim() }); // the live build saves the partial lead here, with consent
        show(cur + 1, true);
      });
    });
    qsa('[data-back]', df).forEach(function (b) { b.addEventListener('click', function () { show(cur - 1, true); }); });
    df.addEventListener('submit', function (e) {
      e.preventDefault(); // preview only: nothing is sent anywhere
      if (!validate(steps[cur])) return;
      window.location.href = df.getAttribute('data-done');
    });
    var started = data.vehicle && /^\d{5}$/.test(data.zip || '');
    show(started ? 1 : 0, false);
  }

  // Thank-you page
  var ty = qs('[data-thanks]');
  if (ty) { var d = store.get(); if (d.first) qs('[data-name]').textContent = ', ' + d.first; store.clear(); }
})();
