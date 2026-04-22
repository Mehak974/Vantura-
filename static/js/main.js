/**
 * Vantura E-commerce – Main JavaScript
 * Single file for all frontend logic:
 * - Cart (AJAX add/update/remove)
 * - Toast notifications
 * - UI helpers
 * - Vanilla JS micro-interactions (Parallax, Tilt)
 * - Form enhancements
 */

'use strict';

// ─── Background Parallax ──────────────────────────────────────────────────────
function initBackgroundParallax() {
    const blobs = document.querySelectorAll('.blob');
    if (blobs.length === 0) return;

    window.addEventListener('mousemove', (e) => {
        const x = (e.clientX / window.innerWidth) - 0.5;
        const y = (e.clientY / window.innerHeight) - 0.5;

        blobs.forEach((blob, i) => {
            const factor = (i === 0) ? 30 : 15;
            blob.style.transform = `translate(${x * factor}px, ${y * factor}px)`;
        });
    }, { passive: true });
}

// ─── CSRF Token ───────────────────────────────────────────────────────────────

function getCsrf() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

// ─── Toast Notifications ──────────────────────────────────────────────────────
function showToast(message, type = 'info', duration = 4000) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:10px;';
        document.body.appendChild(container);
    }

    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${icons[type] || '📢'}</span>
        <span style="flex:1;">${message}</span>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;color:#64748b;cursor:pointer;font-size:16px;">✕</button>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        toast.style.transition = 'all 0.4s ease';
        setTimeout(() => toast.remove(), 400);
    }, duration);
}

// ─── Cart Badge Update ────────────────────────────────────────────────────────
function updateCartBadge(count) {
    const badge = document.getElementById('cart-badge');
    if (!badge) return;

    badge.textContent = count;

    // Pop animation
    badge.style.transform = 'scale(1.4)';
    setTimeout(() => {
        badge.style.transform = 'scale(1)';
        badge.style.transition = 'transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
    }, 200);
}

// ─── Add to Cart (AJAX) ───────────────────────────────────────────────────────
function addToCart(productId, buttonEl, quantity = 1, callback = null) {
    const originalContent = buttonEl.innerHTML;
    buttonEl.disabled = true;
    buttonEl.style.opacity = '0.7';
    buttonEl.innerHTML = '<span style="display:inline-block;animation:spin 0.6s linear infinite;">⟳</span>';

    const fd = new FormData();
    fd.append('quantity', quantity);
    fd.append('csrfmiddlewaretoken', getCsrf());

    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        body: fd,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(r => {
        if (!r.ok) throw new Error('Network response was not ok');
        return r.json();
    })
    .then(data => {
        if (data.success) {
            updateCartBadge(data.cart_count);

            if (callback) {
                callback(data);
                return;
            }

            showToast(data.message, 'success');
            buttonEl.innerHTML = '✓ Added!';
            buttonEl.style.background = '#9bb2a4';
            
            // Open the drawer after a short delay
            setTimeout(() => {
                toggleCartDrawer();
                buttonEl.innerHTML = originalContent;
                buttonEl.disabled = false;
                buttonEl.style.opacity = '1';
                buttonEl.style.background = '';
            }, 600);
        } else {
            showToast(data.message || 'Could not add to cart.', 'error');
            buttonEl.innerHTML = originalContent;
            buttonEl.disabled = false;
            buttonEl.style.opacity = '1';
        }
    })
    .catch(() => {
        showToast('Something went wrong. Please try again.', 'error');
        buttonEl.innerHTML = originalContent;
        buttonEl.disabled = false;
        buttonEl.style.opacity = '1';
    });
}

function buyNow(productId, buttonEl, quantity = 1) {
    addToCart(productId, buttonEl, quantity, () => {
        window.location.href = '/checkout/';
    });
}

// ─── Cart Drawer Logic ────────────────────────────────────────────────────────
function toggleCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-drawer-overlay');
    if (!drawer || !overlay) return;

    const isOpen = drawer.classList.contains('open');
    if (!isOpen) {
        fetchCartDrawer();
    }
    
    drawer.classList.toggle('open');
    overlay.classList.toggle('open');
    document.body.style.overflow = drawer.classList.contains('open') ? 'hidden' : '';
}

function fetchCartDrawer() {
    const content = document.getElementById('cart-drawer-content');
    if (!content) return;

    content.innerHTML = '<div class="h-full flex items-center justify-center"><span class="animate-spin text-4xl">⟳</span></div>';
    
    fetch('/cart/drawer/', { headers: { 'X-Requested-With': 'XMLHttpRequest' }})
        .then(r => {
            if (!r.ok) throw new Error('Load failed');
            return r.text();
        })
        .then(html => {
            content.innerHTML = html;
        })
        .catch(() => {
            content.innerHTML = '<div class="p-10 text-center text-red-500">Could not load cart. Please try again.</div>';
        });
}

// Close on Esc
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const drawer = document.getElementById('cart-drawer');
        if (drawer && drawer.classList.contains('open')) {
            toggleCartDrawer();
        }
    }
});

// ─── Scroll-Reveal Animations ─────────────────────────────────────────────────
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                const delay = parseInt(entry.target.dataset.delay) || 0;
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0) scale(1)';
                }, delay);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.animate-on-scroll').forEach((el, i) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(32px) scale(0.98)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s cubic-bezier(0.175,0.885,0.32,1.1)';
        observer.observe(el);
    });
}

// ─── Navbar Scroll Effect ─────────────────────────────────────────────────────
function initNavbar() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const current = window.scrollY;
        navbar.classList.toggle('scrolled', current > 50);
        // Hide navbar on fast scroll down, show on scroll up
        if (current > lastScroll + 10 && current > 200) {
            navbar.style.transform = 'translateY(-100%)';
        } else if (current < lastScroll - 5) {
            navbar.style.transform = 'translateY(0)';
        }
        lastScroll = current;
    }, { passive: true });
}

// ─── Mobile Menu ───────────────────────────────────────────────────────────────
function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    if (!menu) return;
    menu.classList.toggle('open');
}

// Close mobile menu on outside click
document.addEventListener('click', (e) => {
    const menu = document.getElementById('mobile-menu');
    const btn = document.getElementById('menu-btn');
    if (menu && btn && !menu.contains(e.target) && !btn.contains(e.target)) {
        menu.classList.remove('open');
    }
});

// ─── Product Image Zoom ────────────────────────────────────────────────────────
function setMainImage(url) {
    const img = document.getElementById('main-image');
    if (!img) return;
    img.style.opacity = '0';
    img.style.transform = 'scale(0.97)';
    setTimeout(() => {
        img.src = url;
        img.style.opacity = '1';
        img.style.transform = 'scale(1)';
        img.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    }, 150);
}

// ─── Quantity Adjuster ─────────────────────────────────────────────────────────
function adjustQty(delta) {
    const input = document.getElementById('qty-input');
    if (!input) return;
    const max = parseInt(input.max) || 99;
    const newVal = Math.max(1, Math.min(parseInt(input.value || 1) + delta, max));
    input.value = newVal;
}

// ─── Product Detail Tabs ───────────────────────────────────────────────────────
function showTab(tab) {
    ['description', 'reviews'].forEach(t => {
        const panel = document.getElementById('panel-' + t);
        const btn = document.getElementById('tab-' + t);
        if (!panel || !btn) return;
        const active = t === tab;
        panel.classList.toggle('hidden', !active);
        
        // Handle both simple color toggle and border toggle
        if (active) {
            btn.classList.add('text-[var(--h)]');
            btn.classList.remove('text-[var(--muted)]', 'text-slate-400');
            btn.classList.add('border-[var(--h)]');
            btn.classList.remove('border-transparent');
        } else {
            btn.classList.remove('text-[var(--h)]');
            btn.classList.add('text-[var(--muted)]');
            btn.classList.remove('border-[var(--h)]');
            btn.classList.add('border-transparent');
        }
    });
}

// ─── Profile Sections ──────────────────────────────────────────────────────────
function showSection(name) {
    ['profile', 'orders'].forEach(s => {
        const el = document.getElementById('section-' + s);
        const nav = document.getElementById('nav-' + s);
        if (!el) return;
        const active = s === name;
        el.classList.toggle('hidden', !active);
        if (nav) {
            nav.classList.toggle('bg-white/10', active);
            nav.classList.toggle('text-white', active);
        }
    });
}

// ─── Star Rating Interactive ───────────────────────────────────────────────────
function initStarRating() {
    const ratingSelect = document.querySelector('select[name="rating"]');
    if (!ratingSelect) return;

    const container = document.createElement('div');
    container.className = 'flex gap-1 mb-2';
    container.style.fontSize = '28px';

    let currentRating = parseInt(ratingSelect.value) || 0;

    function render(highlighted) {
        container.innerHTML = '';
        for (let i = 1; i <= 5; i++) {
            const star = document.createElement('button');
            star.type = 'button';
            star.textContent = i <= highlighted ? '★' : '☆';
            star.style.cssText = `cursor:pointer;background:none;border:none;color:${i <= highlighted ? '#f59e0b' : '#475569'};font-size:28px;transition:all 0.15s;padding:0 2px;`;
            star.onmouseenter = () => render(i);
            star.onmouseleave = () => render(currentRating);
            star.onclick = () => {
                currentRating = i;
                ratingSelect.value = i;
                render(i);
            };
            container.appendChild(star);
        }
    }

    render(currentRating);
    ratingSelect.style.display = 'none';
    ratingSelect.parentNode.insertBefore(container, ratingSelect);
}

// ─── Cookie Consent ────────────────────────────────────────────────────────────
function acceptCookies() {
    localStorage.setItem('cookies_accepted', 'true');
    const banner = document.getElementById('cookie-banner');
    if (banner) {
        banner.style.opacity = '0';
        banner.style.transform = 'translateY(20px)';
        banner.style.transition = 'all 0.4s ease';
        setTimeout(() => banner.classList.add('hidden'), 400);
    }
}
function declineCookies() {
    const banner = document.getElementById('cookie-banner');
    if (banner) {
        banner.style.opacity = '0';
        banner.style.transition = 'opacity 0.3s ease';
        setTimeout(() => banner.classList.add('hidden'), 300);
    }
}

// ─── Form Validation Enhancements ─────────────────────────────────────────────
function initFormEnhancements() {
    // Real-time validation feedback
    document.querySelectorAll('.form-input, .form-textarea').forEach(input => {
        input.addEventListener('blur', () => {
            if (input.value.trim()) {
                input.style.borderColor = 'rgba(34,197,94,0.4)';
            }
        });
        input.addEventListener('input', () => {
            input.style.borderColor = '';
        });
    });

    // Prevent double form submission
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn && !submitBtn.dataset.submitting) {
                submitBtn.dataset.submitting = 'true';
                const original = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span style="display:inline-block;animation:spin 0.6s linear infinite;">⟳</span> Processing...';
                submitBtn.disabled = true;

                // Re-enable after 10s as fallback
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = original;
                    delete submitBtn.dataset.submitting;
                }, 10000);
            }
        });
    });
}



// ─── Number Counter Animation ──────────────────────────────────────────────────
function animateCounter(el, target, duration = 1500) {
    const start = parseInt(el.textContent) || 0;
    const range = target - start;
    const startTime = performance.now();
    function update(now) {
        const progress = Math.min((now - startTime) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(start + range * eased);
        if (progress < 1) requestAnimationFrame(update);
        else el.textContent = target;
    }
    requestAnimationFrame(update);
}

function initCounters() {
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.dataset.count);
                if (!isNaN(target)) animateCounter(el, target);
                observer.unobserve(el);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('[data-count]').forEach(el => observer.observe(el));
}

// ─── Smooth Anchor Scrolling ───────────────────────────────────────────────────
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', e => {
            const target = document.querySelector(a.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

// ─── Search Autocomplete Hint ──────────────────────────────────────────────────
function initSearchEnhancement() {
    const searchInputs = document.querySelectorAll('input[name="q"]');
    searchInputs.forEach(input => {
        input.addEventListener('keydown', e => {
            if (e.key === 'Enter') {
                const form = input.closest('form');
                if (form) form.submit();
            }
        });
    });
}

// ─── Lazy Image Loading ────────────────────────────────────────────────────────
function initLazyImages() {
    if ('loading' in HTMLImageElement.prototype) return; // native support

    const imageObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                }
                imageObserver.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => imageObserver.observe(img));
}

// ─── CSS Spin Keyframe (for loading states) ────────────────────────────────────
(function addSpinStyle() {
    if (document.getElementById('vantura-spin-style')) return;
    const style = document.createElement('style');
    style.id = 'vantura-spin-style';
    style.textContent = `
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .animate-float { animation: float 6s ease-in-out infinite; }
        @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-16px)} }
    `;
    document.head.appendChild(style);
})();

// ─── Global AJAX Cart Handler (for inline buttons) ────────────────────────────
document.addEventListener('click', e => {
    // Delegate: any button with data-add-to-cart attribute
    const btn = e.target.closest('[data-add-to-cart]');
    if (btn) {
        e.preventDefault();
        const productId = btn.dataset.addToCart;
        const qty = parseInt(btn.dataset.qty || '1');
        addToCart(productId, btn, qty);
    }
});

// ─── Back To Top Button ────────────────────────────────────────────────────────
function initBackToTop() {
    const btn = document.createElement('button');
    btn.innerHTML = '↑';
    btn.title = 'Back to top';
    btn.style.cssText = `
        position:fixed;bottom:80px;right:24px;width:44px;height:44px;
        background:#9bb2a4 !important;
        color:white !important;border:none;border-radius:12px;font-size:18px;
        cursor:pointer;opacity:0;transition:all 0.3s ease;
        z-index:999;box-shadow:0 4px 20px rgba(155,178,164,0.3);
        display:flex;align-items:center;justify-content:center;
    `;
    btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    document.body.appendChild(btn);

    window.addEventListener('scroll', () => {
        btn.style.opacity = window.scrollY > 500 ? '1' : '0';
        btn.style.pointerEvents = window.scrollY > 500 ? 'auto' : 'none';
    }, { passive: true });
}

// ─── Cookie Banner ─────────────────────────────────────────────────────────────
function initCookieBanner() {
    if (localStorage.getItem('cookies_accepted')) return;
    const banner = document.getElementById('cookie-banner');
    if (banner) {
        setTimeout(() => {
            banner.classList.remove('hidden');
            banner.style.animation = 'slideUp 0.5s ease forwards';
        }, 2500);
    }
}

// ─── Page Load Progress Bar ───────────────────────────────────────────────────
function initProgressBar() {
    const bar = document.createElement('div');
    bar.style.cssText = `
        position:fixed;top:0;left:0;height:2px;width:0%;
        background:#9bb2a4;
        z-index:99999;transition:width 0.3s ease;border-radius:0 2px 2px 0;
    `;
    document.body.appendChild(bar);

    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        bar.style.width = progress + '%';
    }, 200);

    window.addEventListener('load', () => {
        clearInterval(interval);
        bar.style.width = '100%';
        setTimeout(() => { bar.style.opacity = '0'; setTimeout(() => bar.remove(), 300); }, 300);
    });
}

// ─── Dark/Light Theme Switcher ────────────────────────────────────────────────
function toggleTheme() {
    const isDark = !document.documentElement.classList.contains('light-mode');
    if (isDark) {
        document.documentElement.classList.add('light-mode');
        localStorage.setItem('vantura-theme', 'light');
    } else {
        document.documentElement.classList.remove('light-mode');
        localStorage.setItem('vantura-theme', 'dark');
    }
    updateThemeUI();
}

function updateThemeUI() {
    const isLight = document.documentElement.classList.contains('light-mode');
    const sunIcon = document.getElementById('sun-icon');
    const moonIcon = document.getElementById('moon-icon');

    if (sunIcon && moonIcon) {
        sunIcon.classList.toggle('hidden', !isLight);
        moonIcon.classList.toggle('hidden', isLight);
    }
}

function initTheme() {
    const saved = localStorage.getItem('vantura-theme');
    if (saved === 'light') {
        document.documentElement.classList.add('light-mode');
    } else {
        // Default to dark or check system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (!saved && !prefersDark) {
            document.documentElement.classList.add('light-mode');
        }
    }
    updateThemeUI();
}

// ─── Initialize Everything ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initProgressBar();
    initBackgroundParallax();
    initNavbar();
    initScrollAnimations();

    initCounters();
    initSmoothScroll();
    initSearchEnhancement();
    initLazyImages();
    initFormEnhancements();
    initStarRating();
    initBackToTop();
    initCookieBanner();

    // Show default profile section if on profile page
    if (document.getElementById('section-profile')) {
        showSection('profile');
    }

    // AJAX Category Filtering
    const productContainer = document.getElementById('product-container');
    if (productContainer) {
        document.addEventListener('click', e => {
            const link = e.target.closest('.subcat-link, .ajax-link');
            if (link) {
                e.preventDefault();
                const url = link.href;
                
                // Active state management for subcategories
                if (link.classList.contains('subcat-link')) {
                    document.querySelectorAll('.subcat-link').forEach(l => {
                        l.classList.remove('bg-[var(--h)]', 'text-[var(--bg)]');
                        l.classList.add('bg-[var(--card-hover)]', 'text-[var(--p)]');
                    });
                    link.classList.remove('bg-[var(--card-hover)]', 'text-[var(--p)]');
                    link.classList.add('bg-[var(--h)]', 'text-[var(--bg)]');
                }

                productContainer.style.opacity = '0.5';
                productContainer.style.pointerEvents = 'none';

                // Show Skeleton
                const skeletonGrid = `
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                        ${Array(8).fill('<div class="aspect-square rounded-3xl skeleton"></div>').join('')}
                    </div>
                `;
                productContainer.innerHTML = skeletonGrid;

                fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' }})
                .then(r => r.text())
                .then(html => {
                    productContainer.innerHTML = html;
                    productContainer.style.opacity = '1';
                    productContainer.style.pointerEvents = 'auto';
                    window.history.pushState({}, '', url);
                    
                    // Re-init animations for new content
                    initScrollAnimations();

                    // Scroll to top of grid
                    productContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                })
                .catch(err => {
                    console.error('AJAX Error:', err);
                    window.location.href = url; // Fallback
                });
            }
        });

        // Handle Back/Forward buttons
        window.addEventListener('popstate', () => {
            const url = window.location.href;
            if (url.includes('/products/') || url.includes('/category/')) {
                productContainer.style.opacity = '0.5';
                fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' }})
                .then(r => r.text())
                .then(html => {
                    productContainer.innerHTML = html;
                    productContainer.style.opacity = '1';
                    initScrollAnimations();

                });
            }
        });
    }
});
