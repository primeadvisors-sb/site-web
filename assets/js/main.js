/* ==========================================================================
   PRIME ADVISORS SB, Inc. | Comportements d'interface
   Vanilla JS, sans dépendance. Chaque module se désactive proprement
   si son point d'ancrage est absent de la page.
   ========================================================================== */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Élément déjà présent dans la fenêtre, mesuré de façon synchrone.
     Sert de garantie : le contenu visible au chargement ne dépend jamais
     d'un rappel asynchrone qui pourrait ne pas survenir. */
  function inViewport(el, margin) {
    var r = el.getBoundingClientRect();
    var h = window.innerHeight || document.documentElement.clientHeight;
    var w = window.innerWidth || document.documentElement.clientWidth;
    margin = margin || 0;
    return r.top < h + margin && r.bottom > -margin && r.left < w + margin && r.right > -margin;
  }

  /* ---------------------------------------------------------------------
     1. En-tête : ombre à partir du premier défilement
     --------------------------------------------------------------------- */
  (function header() {
    var el = document.querySelector('.site-header');
    if (!el) return;

    var ticking = false;
    var dernier = window.scrollY;
    var SEUIL = 8;   // ignore les micro-mouvements et le rebond des pavés tactiles

    function update() {
      var y = window.scrollY;
      el.classList.toggle('is-scrolled', y > 8);

      var ecart = y - dernier;
      // Jamais escamotée en haut de page, ni pendant que le menu est ouvert.
      if (y < el.offsetHeight * 1.5 || document.body.classList.contains('nav-open')) {
        el.classList.remove('is-hidden');
      } else if (Math.abs(ecart) > SEUIL) {
        el.classList.toggle('is-hidden', ecart > 0);
      }
      dernier = y;
      ticking = false;
    }

    window.addEventListener('scroll', function () {
      if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
    }, { passive: true });

    // Au clavier, la navigation doit rester atteignable : si le focus entre
    // dans un en-tête escamoté, il redescend.
    el.addEventListener('focusin', function () { el.classList.remove('is-hidden'); });

    update();
  })();

  /* ---------------------------------------------------------------------
     2. Navigation mobile
     --------------------------------------------------------------------- */
  (function mobileNav() {
    var toggle = document.querySelector('.nav-toggle');
    var panel = document.getElementById('site-nav');
    if (!toggle || !panel) return;

    var desktop = window.matchMedia('(min-width: 1081px)');

    var header = document.querySelector('.site-header');

    function setOpen(open) {
      // Le panneau est en position: fixed À L'INTÉRIEUR de l'en-tête. Tant
      // qu'une transformation subsiste sur celui-ci, il en devient le bloc
      // conteneur et le panneau ne couvre plus l'écran. On la fait donc
      // disparaître sans transition avant d'ouvrir.
      if (open && header) {
        header.classList.add('no-transition');
        header.classList.remove('is-hidden');
        void header.offsetHeight;          // force la prise en compte
        header.classList.remove('no-transition');
      }
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
      panel.classList.toggle('is-open', open);
      document.body.classList.toggle('nav-open', open);
    }

    toggle.addEventListener('click', function () {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });

    // Fermer après navigation vers une ancre ou une page
    panel.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        toggle.focus();
      }
    });

    // Repasser en état desktop si l'écran s'élargit
    var onChange = function (e) { if (e.matches) setOpen(false); };
    if (desktop.addEventListener) desktop.addEventListener('change', onChange);
    else desktop.addListener(onChange);
  })();

  /* ---------------------------------------------------------------------
     3. Révélation au défilement (désactivée si mouvement réduit)
     --------------------------------------------------------------------- */
  (function reveal() {
    var items = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
    if (!items.length) return;

    function show(el) { el.classList.add('is-visible'); }
    function showAll() { items.forEach(show); }

    if (reduceMotion || !('IntersectionObserver' in window)) { showAll(); return; }

    // 1. Ce qui est déjà à l'écran s'affiche tout de suite, sans attendre
    //    l'observateur : le haut de page ne peut jamais rester vide.
    var pending = items.filter(function (el) {
      if (inViewport(el)) { show(el); return false; }
      return true;
    });

    if (!pending.length) return;

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          show(entry.target);
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

    pending.forEach(function (el) { io.observe(el); });

    // 2. Filet de sécurité : dans un contexte où l'observateur ne produit
    //    aucun rappel (onglet en arrière-plan, moteur sans composition,
    //    certaines vues web embarquées), on révèle tout plutôt que de
    //    laisser la page vide.
    window.setTimeout(function () {
      var stillHidden = pending.filter(function (el) {
        return !el.classList.contains('is-visible');
      }).length;
      // Aucun des éléments confiés à l'observateur n'a été révélé : il ne
      // répond pas. On affiche tout plutôt que de laisser la page vide.
      if (stillHidden === pending.length) {
        showAll();
        io.disconnect();
      }
    }, 2500);

    // 3. Le premier défilement révèle aussi ce qui est entré dans le cadre,
    //    indépendamment de l'observateur.
    var onScroll = function () {
      var still = false;
      pending.forEach(function (el) {
        if (!el.classList.contains('is-visible') && inViewport(el, -40)) show(el);
        if (!el.classList.contains('is-visible')) still = true;
      });
      if (!still) window.removeEventListener('scroll', onScroll);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
  })();

  /* ---------------------------------------------------------------------
     3 bis. Courbe d'ascension du hero
     La classe .is-animated déclenche le tracé décrit en CSS (section 19).
     Sous mouvement réduit, la CSS affiche directement l'état final : on
     pose quand même la classe pour rester cohérent, sans animation.
     --------------------------------------------------------------------- */
  (function heroCurve() {
    var visual = document.querySelector('.hero__visual');
    if (!visual) return;

    var start = function () { visual.classList.add('is-animated'); };

    // Le hero est en haut de page : dans l'immense majorité des cas il est
    // déjà visible au chargement et le tracé démarre sans observateur.
    if (reduceMotion || !('IntersectionObserver' in window) || inViewport(visual)) { start(); return; }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { start(); io.disconnect(); }
      });
    }, { threshold: 0.25 });
    io.observe(visual);

    window.setTimeout(start, 2500);   // filet de sécurité
  })();

  /* ---------------------------------------------------------------------
     3 ter. Parallaxe discret
     Uniquement des transforms, sous requestAnimationFrame : aucun
     recalcul de mise en page pendant le défilement.
     --------------------------------------------------------------------- */
  (function parallax() {
    var items = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));
    if (!items.length || reduceMotion) return;

    var ticking = false;

    function update() {
      var vh = window.innerHeight;
      items.forEach(function (el) {
        var rect = el.getBoundingClientRect();
        if (rect.bottom < -200 || rect.top > vh + 200) return;
        var speed = parseFloat(el.getAttribute('data-parallax')) || 0.06;
        var offset = (rect.top + rect.height / 2 - vh / 2) * -speed;
        el.style.transform = 'translate3d(0,' + offset.toFixed(1) + 'px,0)';
      });
      ticking = false;
    }

    window.addEventListener('scroll', function () {
      if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    window.addEventListener('resize', update, { passive: true });
    update();
  })();

  /* ---------------------------------------------------------------------
     3 quater. Carrousel coverflow des expertises
     Portage en JS natif d'une mécanique coverflow.

     Principe : `pos` est l'indice fractionnaire de la carte centrée, et
     c'est la seule source de vérité. Le rendu est écrit directement dans
     le DOM plutôt que dans un état applicatif : soixante mises à jour par
     seconde n'ont pas à traverser une couche de rendu.

     Le bouclage ne clone aucun nœud : l'écart de chaque carte est replié
     sur le chemin le plus court autour de l'anneau, et une carte est
     téléportée à l'opposé exactement à une demi-révolution, là où son
     opacité est déjà nulle.
     --------------------------------------------------------------------- */
  (function coverflow() {
    var root = document.querySelector('[data-coverflow]');
    if (!root) return;

    var frame = root.querySelector('.coverflow__frame');
    var cards = Array.prototype.slice.call(root.querySelectorAll('.coverflow__card'));
    var caption = root.querySelector('.coverflow__caption');
    var dotsBar = root.querySelector('.coverflow__dots');
    var count = cards.length;
    if (!frame || count < 2) return;

    // Réglages du rake. Tout est dérivé de la largeur de carte, donc
    // l'effet garde ses proportions à n'importe quelle taille d'écran.
    var ROTATE = 44;      // degrés d'inclinaison de la première voisine
    var DEPTH = 0.6;      // recul, en fraction de la largeur de carte
    var FALLOFF = 0.56;   // sous 1, l'inclinaison s'atténue avec l'éloignement
    var FADE = 0.1;       // opacité perdue par cran d'éloignement
    var GAP = 0.05;       // écartement, en fraction de la largeur de carte

    var pos = 0;          // indice fractionnaire courant
    var target = 0;       // destination de l'amorti en cours
    var width = 0;
    var raf = null;
    var drag = null;
    var selected = -1;

    function indexAt(p) { return ((Math.round(p) % count) + count) % count; }
    function sign(n) { return n > 0 ? 1 : (n < 0 ? -1 : 0); }

    function paint() {
      if (!width) return;
      var pitch = width * (1 + GAP);

      for (var i = 0; i < count; i++) {
        var card = cards[i];
        var offset = i - pos;
        // Repli sur le chemin le plus court : tout le bouclage tient ici.
        offset = ((offset % count) + count) % count;
        if (offset > count / 2) offset -= count;

        var distance = Math.abs(offset);
        // Inclinaison et recul s'atténuent ensemble : doubler la distance
        // n'ajoute qu'environ la moitié de chaque. Une rampe linéaire
        // refermerait la deuxième carte comme un livre.
        var ramp = Math.pow(distance, FALLOFF);
        var tilt = Math.min(ROTATE * ramp, 82) * sign(offset);

        card.style.transform =
          'translateX(calc(-50% + ' + (offset * pitch).toFixed(2) + 'px)) ' +
          'translateZ(' + (-DEPTH * width * ramp).toFixed(2) + 'px) ' +
          'rotateY(' + (-tilt).toFixed(2) + 'deg)';

        // La carte est téléportée à une demi-révolution : elle doit être
        // éteinte à cet instant précis, sinon le saut se voit.
        var edge = Math.min(1, Math.max(0, count / 2 - distance));
        var opacity = Math.max(0, 1 - FADE * distance) * edge;
        card.style.opacity = String(opacity);
        card.style.zIndex = String(100 - Math.round(distance));
        // Une carte éteinte sort aussi de l'arbre d'accessibilité.
        if (opacity < 0.05) card.setAttribute('aria-hidden', 'true');
        else card.removeAttribute('aria-hidden');
      }
    }

    // Les quatre légendes sont empilées dans la même cellule de grille : le
    // bloc prend d'emblée la hauteur de la plus haute, donc changer de
    // diapositive ne décale plus ce qui suit. `visibility` plutôt qu'un
    // simple `opacity` : les légendes inactives sortent aussi du parcours
    // clavier et de l'arbre d'accessibilité.
    var captions = [];
    if (caption) {
      cards.forEach(function (card) {
        var source = card.querySelector('figcaption');
        var block = document.createElement('div');
        block.className = 'coverflow__cap';
        block.innerHTML = source ? source.innerHTML : '';
        caption.appendChild(block);
        captions.push(block);
      });
    }

    function setSelected(index) {
      if (index === selected) return;
      selected = index;
      captions.forEach(function (block, i) {
        block.classList.toggle('is-active', i === index);
      });
      if (dotsBar) {
        Array.prototype.forEach.call(dotsBar.children, function (dot, i) {
          dot.setAttribute('aria-current', String(i === index));
        });
      }
    }

    function settle(to) {
      if (raf !== null) cancelAnimationFrame(raf);
      target = to;
      setSelected(indexAt(to));

      if (reduceMotion) { pos = to; paint(); raf = null; return; }

      var step = function () {
        var remaining = target - pos;
        if (Math.abs(remaining) < 0.0004) {
          pos = target;
          paint();
          raf = null;
          return;
        }
        // Amorti exponentiel plutôt qu'un ressort : pas de dépassement.
        pos += remaining * 0.16;
        paint();
        raf = requestAnimationFrame(step);
      };
      raf = requestAnimationFrame(step);
    }

    function goTo(index) {
      // Prendre le chemin le plus court plutôt que dérouler tout l'anneau.
      settle(index + Math.round((target - index) / count) * count);
    }

    // On repart de `target` et non de `pos` : sinon une touche pressée en
    // plein vol serait avalée par l'arrondi avant d'avoir bougé.
    function nudge(by) { settle(Math.round(target) + by); }

    frame.addEventListener('pointerdown', function (e) {
      if (raf !== null) { cancelAnimationFrame(raf); raf = null; }
      frame.setPointerCapture(e.pointerId);
      target = pos;
      drag = { id: e.pointerId, x: e.clientX, pos: pos, v: 0, t: performance.now() };
    });

    frame.addEventListener('pointermove', function (e) {
      if (!drag || drag.id !== e.pointerId) return;
      var pitch = width * (1 + GAP);
      if (!pitch) return;
      var now = performance.now();
      var previous = pos;
      pos = drag.pos - (e.clientX - drag.x) / pitch;
      // Vitesse en cartes par seconde, pour le lancer.
      drag.v = ((pos - previous) / Math.max(now - drag.t, 1)) * 1000;
      drag.t = now;
      setSelected(indexAt(pos));
      paint();
    });

    function endDrag(e) {
      if (!drag || drag.id !== e.pointerId) return;
      var velocity = drag.v;
      drag = null;
      // Un lancer porte, mais jamais au-delà de deux cartes.
      var carried = Math.max(-2, Math.min(2, velocity * 0.18));
      settle(Math.round(pos + carried));
    }
    frame.addEventListener('pointerup', endDrag);
    frame.addEventListener('pointercancel', endDrag);

    /* ----- Défilement automatique -------------------------------------
       Trois règles le gouvernent :
       1. Il ne démarre pas si le visiteur a demandé de réduire les
          animations : chaque changement serait alors un saut sec.
       2. Il se suspend au survol, dès que le focus entre dans le
          carrousel, et quand l'onglet passe en arrière-plan.
       3. La moindre action explicite (flèche, pastille, glissé, clavier)
          l'arrête pour de bon : le visiteur a pris la main. Le bouton de
          commande permet de le relancer.
       Une commande de pause visible est obligatoire dès qu'un contenu
       s'anime seul plus de cinq secondes (WCAG 2.2.2). ------------------ */
    var AUTOPLAY_MS = 6000;
    var toggle = root.querySelector('[data-cf-toggle]');
    var timer = null;
    var playing = false;

    var ICON_PAUSE = '<rect x="3.5" y="2.5" width="3.5" height="11" rx="1"/>' +
                     '<rect x="9" y="2.5" width="3.5" height="11" rx="1"/>';
    var ICON_PLAY = '<path d="M4.5 2.6 13 8l-8.5 5.4z"/>';

    function tick() { if (!drag) nudge(1); }
    function armTimer() { if (timer === null) timer = window.setInterval(tick, AUTOPLAY_MS); }
    function clearTimer() { if (timer !== null) { window.clearInterval(timer); timer = null; } }

    function syncToggle() {
      if (!toggle) return;
      var svg = toggle.querySelector('svg');
      if (svg) svg.innerHTML = playing ? ICON_PAUSE : ICON_PLAY;
      toggle.setAttribute('aria-label', playing
        ? 'Mettre en pause le défilement automatique'
        : 'Reprendre le défilement automatique');
    }

    function play() {
      if (reduceMotion) return;
      playing = true;
      // Une annonce toutes les six secondes noierait un lecteur d'écran :
      // la légende ne redevient « live » que pour les changements demandés.
      if (caption) caption.setAttribute('aria-live', 'off');
      armTimer();
      syncToggle();
    }

    function stop() {
      playing = false;
      clearTimer();
      if (caption) caption.setAttribute('aria-live', 'polite');
      syncToggle();
    }

    // Suspension temporaire : l'état « en lecture » est conservé.
    function suspend() { if (playing) clearTimer(); }
    function resume() { if (playing) armTimer(); }

    if (toggle) {
      if (reduceMotion) {
        // Sans animation, l'avance automatique serait une succession de
        // sauts : la commande n'aurait rien à piloter.
        toggle.hidden = true;
      } else {
        toggle.addEventListener('click', function () {
          if (playing) stop(); else play();
        });
      }
    }

    root.addEventListener('mouseenter', suspend);
    root.addEventListener('mouseleave', resume);
    root.addEventListener('focusin', suspend);
    root.addEventListener('focusout', function (e) {
      if (!root.contains(e.relatedTarget)) resume();
    });
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) suspend(); else resume();
    });

    frame.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); stop(); nudge(-1); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); stop(); nudge(1); }
    });

    frame.addEventListener('pointerdown', stop);

    Array.prototype.forEach.call(root.querySelectorAll('[data-cf-nav]'), function (btn) {
      btn.addEventListener('click', function () {
        stop();
        nudge(btn.getAttribute('data-cf-nav') === 'next' ? 1 : -1);
      });
    });

    // Pastilles de navigation, construites à partir des cartes présentes.
    if (dotsBar) {
      cards.forEach(function (card, i) {
        var dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'coverflow__dot';
        var title = card.querySelector('h3');
        dot.setAttribute('aria-label', title ? title.textContent.trim() : 'Diapositive ' + (i + 1));
        dot.setAttribute('aria-current', String(i === 0));
        dot.addEventListener('click', function () { stop(); goTo(i); });
        dotsBar.appendChild(dot);
      });
    }

    // La largeur de carte pilote l'écartement, le recul et la perspective :
    // c'est la seule mesure utile, et seulement quand la boîte change.
    var measure = function () {
      if (!cards[0]) return;
      width = cards[0].offsetWidth;
      paint();
    };
    measure();
    setSelected(0);
    if ('ResizeObserver' in window) new ResizeObserver(measure).observe(frame);
    else window.addEventListener('resize', measure, { passive: true });

    // Les images arrivent après coup et peuvent changer la largeur mesurée.
    window.addEventListener('load', measure);

    play();

    // Optimisation : ne pas faire défiler un carrousel hors de l'écran.
    // Purement facultatif : si l'observateur ne répond pas, le défilement
    // continue simplement, ce qui reste le comportement attendu.
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) resume(); else suspend();
        });
      }, { threshold: 0.2 }).observe(root);
    }
  })();

  /* ---------------------------------------------------------------------
     3 quinquies. Ondes de rayonnement : veille hors écran
     Les ondes tournent en boucle sans fin. Les geler quand le bandeau
     n'est pas visible évite d'occuper le compositeur pour rien.
     L'état par défaut reste « en mouvement » : si l'observateur ne répond
     pas, le rendu visible est inchangé.
     --------------------------------------------------------------------- */
  (function idlePause() {
    var layers = Array.prototype.slice.call(document.querySelectorAll('.waves, .reach'));
    if (!layers.length || !('IntersectionObserver' in window)) return;

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        entry.target.classList.toggle('is-idle', !entry.isIntersecting);
      });
    }, { threshold: 0 });

    layers.forEach(function (el) { io.observe(el); });
  })();

  /* ---------------------------------------------------------------------
     4. Année courante dans le pied de page
     --------------------------------------------------------------------- */
  (function year() {
    var el = document.querySelector('[data-current-year]');
    if (!el) return;
    var now = new Date().getFullYear();
    if (now > Number(el.textContent)) el.textContent = String(now);
  })();

  /* ---------------------------------------------------------------------
     5. Références : filtres par secteur (progressive enhancement)
        Les fiches sont du HTML réel : la page reste complète sans JS.
     --------------------------------------------------------------------- */
  (function references() {
    var list = document.getElementById('ref-list');
    var bar = document.getElementById('ref-filters');
    if (!list || !bar) return;

    var cards = Array.prototype.slice.call(list.querySelectorAll('[data-secteur]'));
    if (cards.length < 2) return; // filtres inutiles en dessous de 2 fiches

    var sectors = [];
    cards.forEach(function (c) {
      var s = c.getAttribute('data-secteur');
      if (s && sectors.indexOf(s) === -1) sectors.push(s);
    });
    if (sectors.length < 2) return;
    sectors.sort(function (a, b) { return a.localeCompare(b, 'fr'); });

    var counter = document.getElementById('ref-count');

    function makeBtn(label, value, pressed) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'ref-filter';
      b.textContent = label;
      b.setAttribute('data-value', value);
      b.setAttribute('aria-pressed', String(pressed));
      return b;
    }

    bar.appendChild(makeBtn('Tous les secteurs', '*', true));
    sectors.forEach(function (s) { bar.appendChild(makeBtn(s, s, false)); });
    bar.hidden = false;

    bar.addEventListener('click', function (e) {
      var btn = e.target.closest('.ref-filter');
      if (!btn) return;

      Array.prototype.forEach.call(bar.querySelectorAll('.ref-filter'), function (b) {
        b.setAttribute('aria-pressed', String(b === btn));
      });

      var value = btn.getAttribute('data-value');
      var shown = 0;
      cards.forEach(function (c) {
        var match = value === '*' || c.getAttribute('data-secteur') === value;
        c.hidden = !match;
        if (match) shown++;
      });
      if (counter) {
        counter.textContent = shown + (shown > 1 ? ' références affichées' : ' référence affichée');
      }
    });
  })();

  /* ---------------------------------------------------------------------
     6. Formulaire de contact
        - validation sur blur puis à la soumission
        - résumé d'erreurs focalisable et lié aux champs
        - envoi vers un endpoint si configuré, sinon repli courriel
     --------------------------------------------------------------------- */
  (function contactForm() {
    var form = document.getElementById('contact-form');
    if (!form) return;

    var summary = document.getElementById('form-error-summary');
    var summaryList = summary ? summary.querySelector('ul') : null;
    var status = document.getElementById('form-status');
    var submitBtn = form.querySelector('[type="submit"]');
    var endpoint = (form.getAttribute('data-endpoint') || '').trim();
    // Deux adresses, deux rôles distincts :
    //   data-mailto        : boîte qui reçoit les demandes du formulaire.
    //   data-public-email  : adresse publiée, seule montrée au visiteur.
    // Elles n'ont pas à coïncider. Si la seconde manque, on retombe sur la
    // première plutôt que d'afficher un message tronqué.
    var mailto = form.getAttribute('data-mailto') || '';
    var publicEmail = form.getAttribute('data-public-email') || mailto.replace('mailto:', '');

    var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

    // Pré-sélection de l'objet depuis l'URL (contact.html?objet=gouvernance),
    // utilisée par les appels à l'action des pages Expertises et Solutions.
    (function prefillObjet() {
      var select = form.querySelector('#objet');
      if (!select || !window.URLSearchParams) return;
      var wanted = new URLSearchParams(window.location.search).get('objet');
      if (!wanted) return;
      var match = Array.prototype.filter.call(select.options, function (o) {
        return o.value === wanted;
      })[0];
      if (match) select.value = match.value;
    })();

    function fieldOf(input) { return input.closest('.field'); }
    function errorNode(input) {
      var f = fieldOf(input);
      return f ? f.querySelector('.field__error') : null;
    }

    function validate(input) {
      var value = (input.value || '').trim();
      var required = input.hasAttribute('required');
      var label = input.getAttribute('data-label') || input.name;
      var msg = '';

      if (required && !value) {
        msg = 'Le champ « ' + label + ' » est obligatoire.';
      } else if (value && input.type === 'email' && !EMAIL_RE.test(value)) {
        msg = 'Saisissez une adresse e-mail valide, au format nom@domaine.com.';
      } else if (value && input.name === 'message' && value.length < 20) {
        msg = 'Décrivez votre demande en 20 caractères minimum.';
      }

      var node = errorNode(input);
      if (msg) {
        input.setAttribute('aria-invalid', 'true');
        if (node) {
          node.textContent = msg;
          node.classList.add('is-shown');
          if (node.id) input.setAttribute('aria-describedby', node.id);
        }
        return msg;
      }
      input.removeAttribute('aria-invalid');
      input.removeAttribute('aria-describedby');
      if (node) { node.textContent = ''; node.classList.remove('is-shown'); }
      return '';
    }

    var controls = Array.prototype.slice.call(
      form.querySelectorAll('input[name], select[name], textarea[name]')
    );

    controls.forEach(function (input) {
      input.addEventListener('blur', function () { validate(input); });
      input.addEventListener('input', function () {
        // n'efface l'erreur qu'une fois le champ redevenu valide
        if (input.getAttribute('aria-invalid') === 'true') validate(input);
      });
    });

    function showStatus(kind, title, text) {
      if (!status) return;
      status.className = 'form-status is-shown is-' + kind;
      status.innerHTML = '';
      var strong = document.createElement('strong');
      strong.textContent = title;
      var p = document.createElement('p');
      p.textContent = text;
      p.style.margin = '0';
      status.appendChild(strong);
      status.appendChild(p);
      status.setAttribute('role', 'status');
    }

    function buildMailto(data) {
      var lines = [
        'Nom : ' + data.nom,
        'Prénom : ' + data.prenom,
        'Entreprise / Organisation : ' + (data.entreprise || 'Non renseigné'),
        'Fonction : ' + (data.fonction || 'Non renseigné'),
        'E-mail : ' + data.email,
        'Téléphone : ' + (data.telephone || 'Non renseigné'),
        'Objet de la demande : ' + data.objet,
        '',
        'Message :',
        data.message
      ];
      return mailto +
        '?subject=' + encodeURIComponent('Demande : ' + data.objet + ' (' + data.prenom + ' ' + data.nom + ')') +
        '&body=' + encodeURIComponent(lines.join('\n'));
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var errors = [];
      controls.forEach(function (input) {
        var msg = validate(input);
        if (msg) errors.push({ id: input.id, msg: msg });
      });

      if (errors.length && summary && summaryList) {
        summaryList.innerHTML = '';
        errors.forEach(function (err) {
          var li = document.createElement('li');
          var a = document.createElement('a');
          a.href = '#' + err.id;
          a.textContent = err.msg;
          a.addEventListener('click', function (ev) {
            ev.preventDefault();
            var target = document.getElementById(err.id);
            if (target) target.focus();
          });
          li.appendChild(a);
          summaryList.appendChild(li);
        });
        summary.classList.add('is-shown');
        summary.focus();
        return;
      }

      if (summary) summary.classList.remove('is-shown');

      var data = {};
      controls.forEach(function (input) { data[input.name] = (input.value || '').trim(); });

      if (!endpoint) {
        // Repli : ouvre le client de messagerie avec la demande pré-remplie.
        window.location.href = buildMailto(data);
        showStatus(
          'success',
          'Votre demande est prête à être envoyée.',
          'Votre logiciel de messagerie vient de s’ouvrir avec le message pré-rempli. ' +
          'Si rien ne s’est produit, écrivez directement à ' + publicEmail + '.'
        );
        return;
      }

      if (submitBtn) { submitBtn.disabled = true; submitBtn.dataset.label = submitBtn.textContent; submitBtn.textContent = 'Envoi en cours…'; }
      showStatus('info', 'Envoi en cours…', 'Merci de patienter quelques instants.');

      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(data)
      })
        .then(function (res) {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          form.reset();
          controls.forEach(function (i) { i.removeAttribute('aria-invalid'); });
          showStatus(
            'success',
            'Votre demande a bien été transmise.',
            'Nos équipes reviennent vers vous dans les meilleurs délais.'
          );
        })
        .catch(function () {
          showStatus(
            'error',
            'L’envoi n’a pas abouti.',
            'Réessayez dans quelques instants ou écrivez-nous à ' + publicEmail + '.'
          );
        })
        .finally(function () {
          if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = submitBtn.dataset.label || 'Envoyer ma demande'; }
        });
    });
  })();
})();
