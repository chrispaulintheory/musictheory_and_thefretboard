/* Music Theory and The Fretboard — site.js
   Mobile nav drawer, figure lightbox, back-to-top */
(function () {
  'use strict';

  // ─── Musical accidentals ───────────────────────────────────────────

  // Newsreader does not supply every accidental glyph in every browser, so
  // fallback fonts can introduce inconsistent positioning. Wrap flats and
  // sharps in chapter content so CSS can correct them consistently.
  var content = document.querySelector('.content');
  if (content) {
    var accidentalWalker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT);
    var accidentalNodes = [];
    var accidentalNode;

    while ((accidentalNode = accidentalWalker.nextNode())) {
      if (/[♭♯]/.test(accidentalNode.nodeValue) &&
          !accidentalNode.parentElement.closest('.accidental, script, style, svg')) {
        accidentalNodes.push(accidentalNode);
      }
    }

    accidentalNodes.forEach(function (textNode) {
      var fragment = document.createDocumentFragment();
      var parts = textNode.nodeValue.split(/([♭♯])/g);

      parts.forEach(function (part) {
        if (part === '♭' || part === '♯') {
          var accidental = document.createElement('span');
          accidental.className = 'accidental accidental-' +
            (part === '♭' ? 'flat' : 'sharp');
          accidental.textContent = part;
          fragment.appendChild(accidental);
        } else if (part) {
          fragment.appendChild(document.createTextNode(part));
        }
      });

      textNode.parentNode.replaceChild(fragment, textNode);
    });
  }

  // ─── Mobile drawer ───────────────────────────────────────────

  var sidebar = document.getElementById('sidebar');
  var toggle = document.getElementById('drawer-toggle');
  var overlay = document.getElementById('sidebar-overlay');

  function openDrawer() {
    if (!sidebar) return;
    sidebar.classList.add('open');
    overlay && overlay.classList.add('open');
    toggle && toggle.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    if (!sidebar) return;
    sidebar.classList.remove('open');
    overlay && overlay.classList.remove('open');
    toggle && toggle.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }

  if (toggle) {
    toggle.addEventListener('click', function () {
      var isOpen = sidebar && sidebar.classList.contains('open');
      isOpen ? closeDrawer() : openDrawer();
    });
  }

  if (overlay) {
    overlay.addEventListener('click', closeDrawer);
  }

  // Close on Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeDrawer();
  });

  // ─── Back to top ─────────────────────────────────────────────

  var btt = document.getElementById('back-to-top');
  if (btt) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 400) {
        btt.classList.add('visible');
      } else {
        btt.classList.remove('visible');
      }
    }, { passive: true });

    btt.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ─── Lightbox ─────────────────────────────────────────────────

  var lightbox = document.getElementById('lightbox');
  var lbImg = document.getElementById('lightbox-img');
  var lbClose = document.getElementById('lightbox-close');

  function openLightbox(src, alt) {
    if (!lightbox || !lbImg) return;
    lbImg.src = src;
    lbImg.alt = alt || '';
    lightbox.removeAttribute('hidden');
    document.body.style.overflow = 'hidden';
    lbClose && lbClose.focus();
  }

  function closeLightbox() {
    if (!lightbox) return;
    lightbox.setAttribute('hidden', '');
    if (lbImg) lbImg.src = '';
    document.body.style.overflow = '';
  }

  // Attach click handlers to all chapter images
  document.querySelectorAll('.chapter-body img, figure img').forEach(function (img) {
    if (img.dataset.missing) return;
    img.addEventListener('click', function () {
      openLightbox(img.src, img.alt);
    });
  });

  if (lbClose) {
    lbClose.addEventListener('click', closeLightbox);
  }

  if (lightbox) {
    lightbox.addEventListener('click', function (e) {
      if (e.target === lightbox) closeLightbox();
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && lightbox && !lightbox.hasAttribute('hidden')) {
      closeLightbox();
    }
  });

  // ─── Smooth anchor scrolling ──────────────────────────────────

  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('href').slice(1);
      var target = document.getElementById(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ─── Staggered content reveal (respects prefers-reduced-motion)

  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    // Observe figures for reveal animation
    document.querySelectorAll('figure, .part-card, .about-card').forEach(function (el) {
      el.classList.add('will-reveal');
      observer.observe(el);
    });
  }

}());
