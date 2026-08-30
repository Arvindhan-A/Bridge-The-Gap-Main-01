/* ===== SCROLL LOCK =====
   The nav drawer and the lightbox both need the page behind them to hold
   still, and both used to set body.style.overflow themselves — so whichever
   closed first handed scrolling back while the other was still open. One
   counter owns it now.

   `position: fixed` rather than `overflow: hidden` because iOS Safari ignores
   the latter on <body>. The scroll offset is stashed and restored on unlock,
   which is also what removes the need for the old "jump to the top of the page
   before opening the menu" workaround. */
var scrollLock = (function () {
    var depth = 0;
    var offset = 0;
    var body = document.body;
    return {
        lock: function () {
            if (depth++ > 0) return;
            offset = window.scrollY || document.documentElement.scrollTop || 0;
            body.style.position = 'fixed';
            body.style.top = -offset + 'px';
            body.style.left = '0';
            body.style.right = '0';
            body.style.width = '100%';
        },
        unlock: function () {
            if (depth === 0 || --depth > 0) return;
            body.style.position = '';
            body.style.top = '';
            body.style.left = '';
            body.style.right = '';
            body.style.width = '';
            // `html { scroll-behavior: smooth }` would animate this, and the
            // page would visibly fly back down from the top after every close.
            window.scrollTo({ top: offset, left: 0, behavior: 'instant' });
        }
    };
})();

/* ===== MOBILE NAVIGATION =====
   The breakpoint comes from the --nav-breakpoint custom property that
   system.css declares, so this and the CSS media query cannot drift apart —
   they used to (768px here, 1024px there), and the band between them left the
   drawer stuck open with no way to close it. Whether the drawer layout is
   actually in force is read back off the rendered page rather than recomputed
   here; see inDrawerLayout below. */
document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.querySelector('.nav-toggle');
    var drawer = document.querySelector('.nav-links');
    var scrim = document.querySelector('.nav-scrim');
    if (!toggle || !drawer) return;

    var width = parseInt(getComputedStyle(document.documentElement)
        .getPropertyValue('--nav-breakpoint'), 10) || 1260;   // fallback matches the CSS
    var isNarrow = window.matchMedia('(max-width: ' + width + 'px)');

    // per-row entrance delay, read back by the CSS animation
    drawer.querySelectorAll('.nav-link').forEach(function (el, i) {
        el.style.setProperty('--i', i);
    });

    function isOpen() { return drawer.classList.contains('open'); }

    /* Everything in the header that can take focus, in document order — which
       is also tab order. Used to keep Tab inside the menu while it covers the
       page, and to pick the first thing to focus on open. */
    function stops() {
        var nodes = document.querySelectorAll(
            '.site-header .nav-links a[href], .site-header .nav-links button:not([disabled]),' +
            '.site-header .nav-controls a[href], .site-header .nav-controls button:not([disabled])'
        );
        return Array.prototype.filter.call(nodes, function (el) {
            return el.offsetWidth > 0 || el.offsetHeight > 0 || el.getClientRects().length > 0;
        });
    }

    function open() {
        if (isOpen() || !inDrawerLayout()) return;
        drawer.classList.add('open');
        toggle.setAttribute('aria-expanded', 'true');
        document.documentElement.classList.add('nav-open');
        scrollLock.lock();
        var first = drawer.querySelector('a[href]');
        if (first) first.focus({ preventScroll: true });
    }

    function close(returnFocus) {
        if (!isOpen()) return;
        drawer.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        document.documentElement.classList.remove('nav-open');
        scrollLock.unlock();
        if (returnFocus) toggle.focus({ preventScroll: true });
    }

    toggle.addEventListener('click', function (e) {
        e.preventDefault();
        isOpen() ? close(true) : open();
    });

    // the scrim covers everything the drawer does not, so it replaces the old
    // document-wide "click anywhere else" listener
    if (scrim) scrim.addEventListener('click', function () { close(true); });

    drawer.addEventListener('click', function (e) {
        if (e.target.closest('a[href]')) close(false);
    });

    document.addEventListener('keydown', function (e) {
        if (!isOpen()) return;
        if (e.key === 'Escape') { close(true); return; }
        if (e.key !== 'Tab') return;

        var focusable = stops();
        if (!focusable.length) return;
        var first = focusable[0];
        var last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
            e.preventDefault();
            last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
            e.preventDefault();
            first.focus();
        }
    });

    /* Crossing back to the wide layout has to clear the open state, or the
       scroll lock and the .nav-open class survive into a bar that no longer
       has a drawer to close.

       The truth is read off the rendered page — the hamburger is displayed
       only while the drawer layout is active — rather than trusted from the
       event. Two triggers because neither is guaranteed on its own: the media
       query is the precise one, the resize is the fallback. */
    function inDrawerLayout() {
        return getComputedStyle(toggle).display !== 'none';
    }
    function syncToLayout() {
        if (!inDrawerLayout()) close(false);
    }
    if (isNarrow.addEventListener) isNarrow.addEventListener('change', syncToLayout);
    else isNarrow.addListener(syncToLayout);

    window.addEventListener('resize', syncToLayout, { passive: true });
    window.addEventListener('orientationchange', syncToLayout);

    // a back-button restore from bfcache can bring back an open drawer along
    // with a scroll lock that nothing will ever release
    window.addEventListener('pageshow', function () { close(false); });
});

document.addEventListener('DOMContentLoaded', () => {
    // Scroll reveal
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.section, .chapter-card').forEach(s => observer.observe(s));

    // Active nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Blog search
    const searchInput = document.querySelector('.blog-search input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const q = e.target.value.toLowerCase();
            document.querySelectorAll('.post-card').forEach(card => {
                const title = card.querySelector('h3')?.textContent.toLowerCase() || '';
                const text = card.querySelector('p')?.textContent.toLowerCase() || '';
                card.style.display = (title.includes(q) || text.includes(q)) ? '' : 'none';
            });
        });
    }

    // Lightbox
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightboxImg');
    const lightboxClose = document.getElementById('lightboxClose');
    const lightboxPrev = document.getElementById('lightboxPrev');
    const lightboxNext = document.getElementById('lightboxNext');
    const lightboxCounter = document.getElementById('lightboxCounter');

    let currentImages = [];
    let currentIndex = 0;

    function openLightbox(images, index) {
        currentImages = images;
        currentIndex = index;
        lightboxImg.src = images[index];
        updateCounter();
        // opening over an already-open lightbox must not take a second lock
        if (!lightbox.classList.contains('open')) {
            lightbox.classList.add('open');
            scrollLock.lock();
        }
    }

    function closeLightbox() {
        if (!lightbox.classList.contains('open')) return;
        lightbox.classList.remove('open');
        scrollLock.unlock();
    }

    function updateCounter() {
        if (currentImages.length <= 1) {
            lightboxCounter.textContent = '';
        } else {
            lightboxCounter.textContent = `${currentIndex + 1} / ${currentImages.length}`;
        }
    }

    function navigate(direction) {
        currentIndex = (currentIndex + direction + currentImages.length) % currentImages.length;
        lightboxImg.src = currentImages[currentIndex];
        updateCounter();
    }

    // Expose openLightbox globally for page-specific scripts
    window.openLightbox = openLightbox;

    // Attach click events to chapter slides
    document.querySelectorAll('.chapter-track').forEach(track => {
        const slides = track.querySelectorAll('.chapter-slide');
        const images = Array.from(slides).map(s => s.dataset.src);

        slides.forEach((slide, i) => {
            slide.addEventListener('click', () => openLightbox(images, i));
        });
    });

    if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
    if (lightboxPrev) lightboxPrev.addEventListener('click', () => navigate(-1));
    if (lightboxNext) lightboxNext.addEventListener('click', () => navigate(1));

    if (lightbox) {
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) closeLightbox();
        });
    }

    document.addEventListener('keydown', (e) => {
        if (!lightbox || !lightbox.classList.contains('open')) return;
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowLeft') navigate(-1);
        if (e.key === 'ArrowRight') navigate(1);
    });
});

/* ===== SCROLL REVEAL =====
   Tags section content with .s-reveal and eases it in once. Skipped entirely
   when the visitor asks for reduced motion, and anything already on screen at
   load is shown immediately so nothing waits for a scroll that never comes. */
document.addEventListener('DOMContentLoaded', function () {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var blocks = document.querySelectorAll(
        '.s-section .s-head, .s-band .s-head, .s-grid > *, .s-media-grid > *, ' +
        '.s-stats > *, .s-nums > *, .s-quotes > *, .s-tiles > *, .s-steps > *, ' +
        '.s-feature > *, .s-contact > *, .s-faq > *'
    );
    if (!blocks.length) return;

    blocks.forEach(function (el) { el.classList.add('s-reveal'); });

    function show(el, i) {
        el.style.setProperty('--s-delay', Math.min(i * 60, 300) + 'ms');
        el.classList.add('is-in');
    }

    // group siblings so a row of cards staggers together rather than by document order
    var seen = new Map();
    var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            var el = entry.target;
            var parent = el.parentElement;
            var n = seen.get(parent) || 0;
            seen.set(parent, n + 1);
            show(el, n);
            io.unobserve(el);
        });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    blocks.forEach(function (el) { io.observe(el); });

    requestAnimationFrame(function () {
        blocks.forEach(function (el) {
            var r = el.getBoundingClientRect();
            if (r.top < window.innerHeight && r.bottom > 0) {
                el.classList.add('is-in');
                io.unobserve(el);
            }
        });
    });
});

/* ===== HEADER: condensed state once the page scrolls ===== */
document.addEventListener('DOMContentLoaded', function () {
    var header = document.querySelector('.site-header');
    if (!header) return;
    var ticking = false;
    // hysteresis: separate on/off thresholds so a value hovering at the
    // boundary cannot flip the class back and forth every frame
    function sync() {
        var y = window.scrollY;
        if (y > 24) header.classList.add('is-scrolled');
        else if (y < 8) header.classList.remove('is-scrolled');
        ticking = false;
    }
    window.addEventListener('scroll', function () {
        if (!ticking) { ticking = true; requestAnimationFrame(sync); }
    }, { passive: true });
    sync();
});

/* ===== BACK TO TOP =====
   The control stays out of the tab order until it is useful, then uses the
   browser's native smooth scrolling (or instant motion when reduced motion is
   requested). */
document.addEventListener('DOMContentLoaded', function () {
    var button = document.querySelector('.scroll-top');
    if (!button) return;

    var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    var ticking = false;
    function updateVisibility() {
        button.classList.toggle('is-visible', window.scrollY > 360);
        button.tabIndex = window.scrollY > 360 ? 0 : -1;
        ticking = false;
    }
    window.addEventListener('scroll', function () {
        if (!ticking) {
            ticking = true;
            requestAnimationFrame(updateVisibility);
        }
    }, { passive: true });
    button.addEventListener('click', function () {
        window.scrollTo({ top: 0, left: 0, behavior: reducedMotion.matches ? 'auto' : 'smooth' });
    });
    updateVisibility();
});

/* ===== SHARED CARD VARIANTS =====
   Legacy semantic names remain intact, while every card gets one of the three
   shared visual behaviours: standard, media, or compact. */
document.addEventListener('DOMContentLoaded', function () {
    var variants = {
        standard: '.card, .kit-card, .partner-card, .why-card, .serve-card, .impact-card, .step-card, .scroll-card, .post-card, .advisor-card, .initiative-card, .team-card, .announcement-card, .sidebar-card, .home-card, .s-card, .s-tile, .s-contact-card, .org-card, .list-tile, .user-card, .stat-card, .role-card, .role-create-card, .form-card, .ch-card, .pu-card',
        media: '.hl-card, .s-media-card, .event-card, .chapter-preview, .masonry-item, .photo-card',
        compact: '.hero-stat-card, .pillar, .event-row, .admin-section, .event-card-empty'
    };
    Object.keys(variants).forEach(function (variant) {
        document.querySelectorAll(variants[variant]).forEach(function (card) {
            card.classList.add('c-card', 'c-card--' + variant);
        });
    });
});

/* ===== FAQ ACCORDION =====
   Native details elements keep their keyboard and screen-reader behaviour;
   this only supplies a measured height animation for both opening and closing. */
document.addEventListener('DOMContentLoaded', function () {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    document.querySelectorAll('.s-faq details').forEach(function (details) {
        var summary = details.querySelector('summary');
        var body = details.querySelector('.s-faq-body');
        if (!summary || !body) return;

        var animation = null;
        function finish(closing) {
            if (closing) details.open = false;
            details.style.height = '';
            details.style.overflow = '';
            details.classList.remove('is-animating');
            animation = null;
        }
        function open() {
            details.open = true;
            var start = summary.offsetHeight;
            var end = start + body.offsetHeight;
            details.style.height = start + 'px';
            details.style.overflow = 'hidden';
            details.classList.add('is-animating');
            animation = details.animate(
                { height: [start + 'px', end + 'px'] },
                { duration: 460, easing: 'cubic-bezier(.16, 1, .3, 1)' }
            );
            body.animate(
                { opacity: [0, 1], transform: ['translateY(-8px)', 'translateY(0)'] },
                { duration: 360, delay: 70, easing: 'cubic-bezier(.16, 1, .3, 1)', fill: 'both' }
            );
            animation.onfinish = function () { finish(false); };
        }
        function close() {
            var start = details.offsetHeight;
            var end = summary.offsetHeight;
            details.style.height = start + 'px';
            details.style.overflow = 'hidden';
            details.classList.add('is-animating');
            animation = details.animate(
                { height: [start + 'px', end + 'px'] },
                { duration: 360, easing: 'cubic-bezier(.4, 0, 1, 1)' }
            );
            body.animate(
                { opacity: [1, 0], transform: ['translateY(0)', 'translateY(-6px)'] },
                { duration: 220, easing: 'ease-in', fill: 'both' }
            );
            animation.onfinish = function () { finish(true); };
        }
        summary.addEventListener('click', function (event) {
            event.preventDefault();
            if (animation) animation.cancel();
            details.open ? close() : open();
        });
    });
});
