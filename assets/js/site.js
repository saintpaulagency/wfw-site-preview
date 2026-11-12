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

(function () {
  var d = document, w = window;
  var reduce = w.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var qsa = function (s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); };
  var io = 'IntersectionObserver' in w;

  // Header shadow once the page scrolls
  var hdr = d.querySelector('.site-header');
  if (hdr) { var onS = function () { hdr.classList.toggle('scrolled', w.scrollY > 8); }; w.addEventListener('scroll', onS, { passive: true }); onS(); }

  // Reveal (transform only)
  if (io && !reduce) {
    var rio = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); rio.unobserve(e.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    qsa('.rv, .usmap').forEach(function (el) { rio.observe(el); });
  } else { qsa('.rv, .usmap').forEach(function (el) { el.classList.add('in'); }); }

  // Pause looping animations while off screen
  if (io) {
    var pio = new IntersectionObserver(function (es) { es.forEach(function (e) { e.target.classList.toggle('paused', !e.isIntersecting); }); });
    qsa('.live-anim, .hero, .site-header').forEach(function (el) { pio.observe(el); });
  }

  // Odometer counters
  function buildOdo(el) {
    var txt = el.textContent; el.setAttribute('data-final', txt); el.textContent = '';
    var vis = d.createElement('span'); vis.setAttribute('aria-hidden', 'true'); vis.style.display = 'inline-flex';
    txt.split('').forEach(function (ch, k) {
      if (/\d/.test(ch)) {
        var dd = d.createElement('span'); dd.className = 'd';
        var s = d.createElement('span'); s.className = 's'; s.style.transitionDelay = (k * 60) + 'ms';
        for (var n = 0; n <= 9; n++) { var c = d.createElement('span'); c.textContent = n; s.appendChild(c); }
        dd.appendChild(s); dd.setAttribute('data-v', ch); vis.appendChild(dd);
      } else { var p = d.createElement('span'); p.textContent = ch; vis.appendChild(p); }
    });
    el.appendChild(vis);
    var sr = d.createElement('span'); sr.className = 'skip-list'; sr.textContent = txt; el.appendChild(sr);
  }
  function runOdo(el) { qsa('.d', el).forEach(function (dd) { dd.firstChild.style.transform = 'translateY(' + (-dd.getAttribute('data-v')) + 'em)'; }); setTimeout(function () { el.textContent = el.getAttribute('data-final'); }, 2900); }
  var odos = qsa('[data-odo]');
  if (odos.length && io && !reduce) {
    odos.forEach(buildOdo);
    var oio = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { setTimeout(function () { runOdo(e.target); }, 120); oio.unobserve(e.target); } }); }, { rootMargin: '0px 0px -10% 0px' });
    odos.forEach(function (el) { oio.observe(el); });
  }

  // Journey: the car drives as you scroll
  var j = d.querySelector('[data-journey]');
  if (j) {
    var track = j.querySelector('.j-track'), car = j.querySelector('.j-car'), steps = qsa('.j-step', j), road = j.querySelector('.j-road');
    var ticking = false;
    var update = function () {
      ticking = false;
      var r = track.getBoundingClientRect(), vh = w.innerHeight;
      var horiz = w.matchMedia('(min-width:960px)').matches;
      var p = horiz ? (vh * .82 - r.top) / (vh * .5) : (vh * .62 - r.top) / r.height;
      p = Math.max(0, Math.min(1, p)); if (reduce) p = 1;
      track.style.setProperty('--p', p.toFixed(3));
      if (horiz) {
        var max = road.offsetWidth - car.offsetWidth + 64; track.style.setProperty('--cx', (p * max - 64) + 'px'); track.style.setProperty('--dash', (-p * 420) + 'px');
      } else {
        var maxy = road.offsetHeight - car.offsetHeight + 64; track.style.setProperty('--cy', (p * maxy - 64) + 'px'); track.style.setProperty('--dash', (p * 420) + 'px');
      }
      steps.forEach(function (s, i) { s.classList.toggle('on', p >= (i / (steps.length - 1)) - .04 || p >= .995); });
    };
    var onScroll = function () { if (!ticking) { ticking = true; w.requestAnimationFrame(update); } };
    w.addEventListener('scroll', onScroll, { passive: true }); w.addEventListener('resize', onScroll); update();
  }

  // Desktop headline: word-by-word rise (phones keep the headline static for speed)
  var h1 = d.querySelector('.hero h1.h-split');
  if (h1 && !reduce && w.matchMedia('(min-width:960px)').matches) {
    var words = h1.textContent.trim().split(/\s+/);
    h1.setAttribute('aria-label', h1.textContent.trim());
    h1.innerHTML = words.map(function (wd, i) { return '<span class="w" aria-hidden="true"><span style="--i:' + i + '">' + wd.replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</span></span>'; }).join(' ');
    h1.classList.add('h-split-on');
  }
  d.documentElement.classList.add('h1-ready');

  // Wish cards flip on tap (hover flips them on desktop)
  qsa('.flip').forEach(function (b) { b.addEventListener('click', function () { b.setAttribute('aria-pressed', String(b.getAttribute('aria-pressed') !== 'true')); }); });

  // Chapter search
  var q = d.querySelector('[data-chq]');
  if (q) {
    var items = qsa('[data-chlist] li'), cnt = d.querySelector('[data-chcount]'), empty = d.querySelector('[data-chempty]');
    var AB = {"al": "alabama", "ak": "alaska", "az": "arizona", "ar": "arkansas", "ca": "california", "co": "colorado", "ct": "connecticut", "de": "delaware", "dc": "district of columbia", "fl": "florida", "ga": "georgia", "hi": "hawaii", "id": "idaho", "il": "illinois", "in": "indiana", "ia": "iowa", "ks": "kansas", "ky": "kentucky", "la": "louisiana", "me": "maine", "md": "maryland", "ma": "massachusetts", "mi": "michigan", "mn": "minnesota", "ms": "mississippi", "mo": "missouri", "mt": "montana", "ne": "nebraska", "nv": "nevada", "nh": "new hampshire", "nj": "new jersey", "nm": "new mexico", "ny": "new york", "nc": "north carolina", "nd": "north dakota", "oh": "ohio", "ok": "oklahoma", "or": "oregon", "pa": "pennsylvania", "ri": "rhode island", "sc": "south carolina", "sd": "south dakota", "tn": "tennessee", "tx": "texas", "ut": "utah", "vt": "vermont", "va": "virginia", "wa": "washington", "wv": "west virginia", "wi": "wisconsin", "wy": "wyoming"};
    var list = d.querySelector('[data-chlist]'), more = d.querySelector('[data-chmore]');
    if (more) more.addEventListener('click', function () { list.classList.remove('collapsed'); more.setAttribute('aria-expanded', 'true'); });
    q.addEventListener('input', function () {
      var v = q.value.trim().toLowerCase(); if (AB[v]) v = AB[v];
      if (v) list.classList.remove('collapsed'); else if (more && more.getAttribute('aria-expanded') !== 'true') list.classList.add('collapsed');
      var n = 0;
      items.forEach(function (li) { var t = (li.textContent + ' ' + li.getAttribute('data-k')).toLowerCase(); var ok = !v || t.indexOf(v) > -1; li.hidden = !ok; li.classList.toggle('hit', !!v && ok); if (ok) n++; });
      cnt.textContent = v ? ('Showing ' + n + ' of ' + items.length + ' chapters') : ('Showing all ' + items.length + ' chapters');
      empty.hidden = n > 0;
    });
  }

  // Magnetic buttons (mouse only)
  if (!reduce && w.matchMedia('(hover:hover) and (pointer:fine)').matches) {
    qsa('.magnetic').forEach(function (b) {
      b.addEventListener('mousemove', function (e) { var r = b.getBoundingClientRect(); var x = (e.clientX - r.left - r.width / 2) / r.width, y = (e.clientY - r.top - r.height / 2) / r.height; b.style.transform = 'translate(' + (x * 8) + 'px,' + (y * 6) + 'px)'; });
      b.addEventListener('mouseleave', function () { b.style.transform = ''; });
    });
  }
})();
