/**
 * PRINCESSE LARA — Core JavaScript
 * Handles global interactions: age gate, themes, navigation, cookies,
 * gallery, carousel, and scroll animations.
 */
(function() {
  'use strict';

  // --------------------------------------------------------------------------
  // UTILITIES
  // --------------------------------------------------------------------------
  const getEl = (sel, ctx = document) => ctx.querySelector(sel);
  const getEls = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const on = (el, type, handler) => el && el.addEventListener(type, handler);

  // --------------------------------------------------------------------------
  // 1. AGE GATE
  // --------------------------------------------------------------------------
  const initAgeGate = () => {
    const gate = getEl('#age-gate');
    if (!gate) return;

    const TTL_DAYS = 30;
    const enterBtn = getEl('[data-age-enter]', gate);
    const exitBtn = getEl('[data-age-exit]', gate);

    // Check if user already passed gate
    const gateStatus = localStorage.getItem('vq_age_verified');
    if (gateStatus) {
      const parsed = JSON.parse(gateStatus);
      if (Date.now() < parsed.expiry) {
        gate.hidden = true;
        return;
      }
      localStorage.removeItem('vq_age_verified');
    }

    on(enterBtn, 'click', () => {
      const expiry = Date.now() + (TTL_DAYS * 24 * 60 * 60 * 1000);
      localStorage.setItem('vq_age_verified', JSON.stringify({ verified: true, expiry }));
      gate.hidden = true;
    });

    on(exitBtn, 'click', () => {
      window.location.href = 'https://www.google.com';
    });
  };

  // --------------------------------------------------------------------------
  // 2. THEME ENGINE
  // --------------------------------------------------------------------------
  const initThemeEngine = () => {
    const THEMES = [
      { id: 'verre', label: 'Verre' },
      { id: 'peau', label: 'Peau' },
      { id: 'ecailles', label: 'Écailles' }
    ];
    const STORAGE_KEY = 'vq_theme';
    const toggleBtn = getEl('[data-theme-toggle]');
    const labelEl = getEl('[data-theme-label]');
    if (!toggleBtn || !labelEl) return;

    let currentIndex = 0;

    // Load saved theme or use default
    const savedTheme = localStorage.getItem(STORAGE_KEY);
    if (savedTheme) {
      const idx = THEMES.findIndex(t => t.id === savedTheme);
      if (idx !== -1) currentIndex = idx;
    }

    const applyTheme = (index) => {
      const theme = THEMES[index];
      document.documentElement.setAttribute('data-theme', theme.id);
      labelEl.textContent = theme.label;
      localStorage.setItem(STORAGE_KEY, theme.id);
    };

    on(toggleBtn, 'click', () => {
      currentIndex = (currentIndex + 1) % THEMES.length;
      applyTheme(currentIndex);
    });

    applyTheme(currentIndex);
  };

  // --------------------------------------------------------------------------
  // 3. NAVIGATION DRAWER
  // --------------------------------------------------------------------------
  const initNavDrawer = () => {
    const drawer = getEl('#nav-drawer');
    const openBtn = getEl('[data-nav-open]');
    const closeBtn = getEl('[data-nav-close]');
    if (!drawer || !openBtn || !closeBtn) return;

    const openDrawer = () => {
      drawer.classList.add('is-open');
      openBtn.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden'; // Prevent scrolling
    };

    const closeDrawer = () => {
      drawer.classList.remove('is-open');
      openBtn.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    };

    on(openBtn, 'click', openDrawer);
    on(closeBtn, 'click', closeDrawer);
    
    // Close on backdrop click
    on(drawer, 'click', (e) => {
      if (e.target === drawer) closeDrawer();
    });

    // Close on resize to desktop width
    window.addEventListener('resize', () => {
      if (window.innerWidth >= 1024 && drawer.classList.contains('is-open')) {
        closeDrawer();
      }
    });
  };

  // --------------------------------------------------------------------------
  // 4. COOKIE BANNER
  // --------------------------------------------------------------------------
  const initCookieBanner = () => {
    const banner = getEl('#cookie-banner');
    if (!banner) return;

    const STORAGE_KEY = 'vq_cookies';
    const saveBtn = getEl('[data-cookie-save]', banner);
    const necessaryBtn = getEl('[data-cookie-necessary]', banner);
    const cbAnalytics = getEl('[data-cookie-analytics]', banner);
    const cbMarketing = getEl('[data-cookie-marketing]', banner);

    if (localStorage.getItem(STORAGE_KEY)) {
      banner.hidden = true;
      return;
    }

    // Show after slight delay
    setTimeout(() => {
      banner.hidden = false;
      // Trigger animation frame for CSS transition
      requestAnimationFrame(() => {
        banner.classList.add('is-visible');
      });
    }, 1000);

    const savePreferences = (analytics, marketing) => {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        necessary: true,
        analytics,
        marketing,
        timestamp: Date.now()
      }));
      banner.classList.remove('is-visible');
      setTimeout(() => { banner.hidden = true; }, 500); // Wait for transition
    };

    on(saveBtn, 'click', () => savePreferences(cbAnalytics.checked, cbMarketing.checked));
    on(necessaryBtn, 'click', () => savePreferences(false, false));
  };

  // --------------------------------------------------------------------------
  // 5. REVIEWS CAROUSEL
  // --------------------------------------------------------------------------
  const initCarousel = () => {
    const track = getEl('.review-track');
    const dots = getEls('.review-dots span');
    if (!track || dots.length === 0) return;

    let isAutoScrolling = true;
    let autoScrollInterval;

    const updateDots = () => {
      const scrollPos = track.scrollLeft;
      const cardWidth = track.scrollWidth / dots.length;
      let activeIndex = Math.round(scrollPos / cardWidth);
      
      if (activeIndex >= dots.length) activeIndex = dots.length - 1;

      dots.forEach((dot, idx) => {
        dot.classList.toggle('is-active', idx === activeIndex);
      });
    };

    const startAutoScroll = () => {
      if (autoScrollInterval) clearInterval(autoScrollInterval);
      autoScrollInterval = setInterval(() => {
        if (!isAutoScrolling) return;
        
        const cardWidth = track.scrollWidth / dots.length;
        const maxScroll = track.scrollWidth - track.clientWidth;
        
        if (track.scrollLeft >= maxScroll - 10) {
          track.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
          track.scrollBy({ left: cardWidth, behavior: 'smooth' });
        }
      }, 5000);
    };

    on(track, 'scroll', updateDots);
    on(track, 'mouseenter', () => { isAutoScrolling = false; });
    on(track, 'mouseleave', () => { isAutoScrolling = true; });

    dots.forEach((dot, idx) => {
      on(dot, 'click', () => {
        isAutoScrolling = false;
        const cardWidth = track.scrollWidth / dots.length;
        track.scrollTo({ left: cardWidth * idx, behavior: 'smooth' });
        
        // Resume auto scroll after interaction
        setTimeout(() => { isAutoScrolling = true; }, 10000);
      });
    });

    startAutoScroll();
    updateDots(); // Initial state
  };

  // --------------------------------------------------------------------------
  // 6. GALLERY TABS & LIGHTBOX
  // --------------------------------------------------------------------------
  const initGallery = () => {
    // Tabs filtering
    const tabBtns = getEls('.gallery-tabs button');
    const items = getEls('.gallery-item');
    
    if (tabBtns.length > 0 && items.length > 0) {
      tabBtns.forEach(btn => {
        on(btn, 'click', () => {
          // Update active state
          tabBtns.forEach(b => b.classList.remove('is-active'));
          btn.classList.add('is-active');
          
          const targetCat = btn.getAttribute('data-tab');
          
          items.forEach(item => {
            if (targetCat === 'all' || item.getAttribute('data-gallery-item') === targetCat) {
              item.style.display = '';
            } else {
              item.style.display = 'none';
            }
          });
        });
      });
    }

    // Lightbox
    const lightbox = getEl('.lightbox');
    const lightboxClose = getEl('.lightbox__close');
    
    if (lightbox && items.length > 0) {
      items.forEach(item => {
        on(item, 'click', () => {
          lightbox.classList.add('is-open');
        });
      });

      on(lightboxClose, 'click', () => lightbox.classList.remove('is-open'));
      on(lightbox, 'click', (e) => {
        if (e.target === lightbox) lightbox.classList.remove('is-open');
      });
    }

    // Protection for gallery items
    const protectedEls = getEls('[data-protected]');
    protectedEls.forEach(el => {
      on(el, 'contextmenu', e => e.preventDefault());
      on(el, 'dragstart', e => e.preventDefault());
    });
  };

  // --------------------------------------------------------------------------
  // 7. SCROLL ANIMATIONS (Intersection Observer)
  // --------------------------------------------------------------------------
  const initScrollAnimations = () => {
    const animatedElements = getEls('[data-animate]');
    if (animatedElements.length === 0) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target); // Only animate once
        }
      });
    }, {
      root: null,
      threshold: 0.15,
      rootMargin: '0px 0px -50px 0px'
    });

    animatedElements.forEach(el => observer.observe(el));
  };

  // --------------------------------------------------------------------------
  // 8. STATS COUNTER ANIMATION
  // --------------------------------------------------------------------------
  const initStatsCounter = () => {
    const statNums = getEls('.stat .num');
    if (statNums.length === 0) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateValue(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    statNums.forEach(num => observer.observe(num));

    function animateValue(obj) {
      // Extract number and suffix (e.g. "128K", "6.8%")
      const text = obj.textContent;
      const match = text.match(/([0-9.]+)([KM%]?)/);
      if (!match) return;
      
      const endVal = parseFloat(match[1]);
      const suffix = match[2];
      const isFloat = match[1].includes('.');
      
      const duration = 1500;
      const startTime = performance.now();
      
      const update = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing out cubic
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        const currentVal = easeProgress * endVal;
        
        if (isFloat) {
          obj.textContent = currentVal.toFixed(1) + suffix;
        } else {
          obj.textContent = Math.floor(currentVal) + suffix;
        }
        
        if (progress < 1) {
          requestAnimationFrame(update);
        } else {
          obj.textContent = text; // Ensure exact final value
        }
      };
      
      requestAnimationFrame(update);
    }
  };

  // --------------------------------------------------------------------------
  // 9. FOOTER YEAR
  // --------------------------------------------------------------------------
  const initFooterYear = () => {
    const yearEls = getEls('[data-year]');
    const currentYear = new Date().getFullYear();
    yearEls.forEach(el => { el.textContent = currentYear; });
  };

  // --------------------------------------------------------------------------
  // INIT
  // --------------------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', () => {
    initAgeGate();
    initThemeEngine();
    initNavDrawer();
    initCookieBanner();
    initCarousel();
    initGallery();
    initScrollAnimations();
    initStatsCounter();
    initFooterYear();
  });

})();

/* ==========================================================================
   CONTENT PROTECTION (Anti-Right Click)
   ========================================================================== */
document.addEventListener('contextmenu', function(e) {
  if (e.target.tagName === 'IMG' || e.target.tagName === 'VIDEO') {
    e.preventDefault();
  }
});

/* ==========================================================================
   ROBUST CONTENT PROTECTION
   ========================================================================== */
// Kill right click globally
document.addEventListener('contextmenu', function(e) {
  e.preventDefault();
}, { passive: false });

// Kill dragging globally
document.addEventListener('dragstart', function(e) {
  e.preventDefault();
}, { passive: false });

// Kill touch-and-hold (long press) on mobile globally
document.addEventListener('touchstart', function(e) {
  if (e.target.tagName === 'IMG' || e.target.tagName === 'VIDEO' || e.target.tagName === 'A') {
    // We don't preventDefault here normally as it kills scrolling, 
    // but webkit-touch-callout in CSS handles the iOS save menu.
  }
}, { passive: false });

// Extra protection for keyboard shortcuts (Save Page As)
document.addEventListener('keydown', function(e) {
  if (e.ctrlKey && (e.key === 's' || e.key === 'S')) {
    e.preventDefault();
  }
});
