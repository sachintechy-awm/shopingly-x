// ============================================================
// ShopinglyX — Main JS
// Handles: mobile menu, 3D product card tilt, AI search modal,
// quantity selectors, AJAX add-to-cart, toasts, back-to-top.
// ============================================================

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const CSRF_TOKEN = getCookie('csrftoken');

document.addEventListener('DOMContentLoaded', function () {
  initMobileMenu();
  init3DTilt();
  initAISearch();
  initQuantitySelectors();
  initAjaxAddToCart();
  initBackToTop();
  autoHideToasts();
  initNewsletterForm();
});

// ------------------------------------------------------------
// Mobile menu toggle
// ------------------------------------------------------------
function initMobileMenu() {
  const toggle = document.querySelector('.mobile-menu-toggle');
  const nav = document.querySelector('.category-nav');
  if (!toggle || !nav) return;
  toggle.addEventListener('click', function () {
    nav.classList.toggle('mobile-open');
  });
}

// ------------------------------------------------------------
// 3D tilt effect on product cards (mouse-follow perspective tilt)
// ------------------------------------------------------------
function init3DTilt() {
  const cards = document.querySelectorAll('.product-card');
  const maxTilt = 8; // degrees

  cards.forEach((card) => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateY = ((x - centerX) / centerX) * maxTilt;
      const rotateX = -((y - centerY) / centerY) * maxTilt;
      card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(800px) rotateX(0deg) rotateY(0deg) translateY(0)';
    });
  });
}

// ------------------------------------------------------------
// AI Search modal
// ------------------------------------------------------------
function initAISearch() {
  const openBtns = document.querySelectorAll('[data-ai-open]');
  const overlay = document.querySelector('.ai-modal-overlay');
  const closeBtn = document.querySelector('.ai-modal-close');
  const form = document.querySelector('.ai-modal form');
  const input = document.querySelector('.ai-modal input[type="text"]');
  const responseBox = document.querySelector('.ai-response');
  const resultsGrid = document.querySelector('.ai-results-grid');
  const loading = document.querySelector('.ai-loading');

  if (!overlay) return;

  openBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      overlay.classList.add('open');
      input.focus();
    });
  });

  closeBtn.addEventListener('click', () => overlay.classList.remove('open'));
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) overlay.classList.remove('open');
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') overlay.classList.remove('open');
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const query = input.value.trim();
    if (!query) return;

    responseBox.classList.remove('show');
    resultsGrid.innerHTML = '';
    loading.classList.add('show');

    const formData = new FormData();
    formData.append('query', query);

    fetch(form.dataset.url, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN },
      body: formData,
    })
      .then((res) => res.json())
      .then((data) => {
        loading.classList.remove('show');
        responseBox.textContent = data.message;
        responseBox.classList.add('show');

        resultsGrid.innerHTML = '';
        (data.products || []).forEach((p) => {
          const card = document.createElement('a');
          card.href = p.url;
          card.className = 'ai-result-card';
          card.innerHTML = `
            <img src="/static/${p.image}" alt="${p.name}">
            <div class="ai-result-info">
              <div class="ai-result-name">${p.name}</div>
              <div class="ai-result-price">₹${p.price}</div>
            </div>
          `;
          resultsGrid.appendChild(card);
        });
      })
      .catch(() => {
        loading.classList.remove('show');
        responseBox.textContent = "Something went wrong. Please try again.";
        responseBox.classList.add('show');
      });
  });
}

// ------------------------------------------------------------
// Quantity selectors (product detail + cart)
// ------------------------------------------------------------
function initQuantitySelectors() {
  document.querySelectorAll('.qty-selector').forEach((selector) => {
    const input = selector.querySelector('input');
    const decrease = selector.querySelector('.qty-decrease');
    const increase = selector.querySelector('.qty-increase');

    decrease.addEventListener('click', () => {
      const value = Math.max(1, parseInt(input.value || '1', 10) - 1);
      input.value = value;
      input.dispatchEvent(new Event('change'));
    });
    increase.addEventListener('click', () => {
      const value = parseInt(input.value || '1', 10) + 1;
      input.value = value;
      input.dispatchEvent(new Event('change'));
    });
  });

  // Auto-submit cart quantity updates when changed
  document.querySelectorAll('.cart-qty-form').forEach((form) => {
    const input = form.querySelector('input[type="number"]');
    input.addEventListener('change', () => form.submit());
  });
}

// ------------------------------------------------------------
// AJAX add-to-cart (updates the header badge without a page reload)
// ------------------------------------------------------------
function initAjaxAddToCart() {
  document.querySelectorAll('.add-to-cart-form[data-ajax="true"]').forEach((form) => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(form);
      const btn = form.querySelector('button[type="submit"]');
      const originalText = btn ? btn.innerHTML : '';
      if (btn) btn.innerHTML = 'Adding...';

      fetch(form.action, {
        method: 'POST',
        headers: {
          'X-CSRFToken': CSRF_TOKEN,
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData,
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            document.querySelectorAll('.cart-count-badge').forEach((el) => {
              el.textContent = data.cart_count;
              el.style.display = data.cart_count > 0 ? 'flex' : 'none';
            });
            showToast(`"${data.product_name}" added to cart.`, 'success');
          }
          if (btn) btn.innerHTML = originalText;
        })
        .catch(() => {
          if (btn) btn.innerHTML = originalText;
          showToast('Could not add item to cart.', 'error');
        });
    });
  });
}

// ------------------------------------------------------------
// Toasts
// ------------------------------------------------------------
function showToast(message, type = 'success') {
  let container = document.querySelector('.messages');
  if (!container) {
    container = document.createElement('div');
    container.className = 'messages';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

function autoHideToasts() {
  document.querySelectorAll('.messages .toast').forEach((toast) => {
    setTimeout(() => toast.remove(), 4000);
  });
}

// ------------------------------------------------------------
// Back to top button
// ------------------------------------------------------------
function initBackToTop() {
  const btn = document.querySelector('.back-to-top');
  if (!btn) return;
  window.addEventListener('scroll', () => {
    if (window.scrollY > 400) {
      btn.classList.add('show');
    } else {
      btn.classList.remove('show');
    }
  });
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

// ------------------------------------------------------------
// Newsletter form (demo only — no backend endpoint)
// ------------------------------------------------------------
function initNewsletterForm() {
  const form = document.querySelector('.newsletter form');
  if (!form) return;
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const input = form.querySelector('input[type="email"]');
    if (input && input.value.trim()) {
      showToast("Thanks for subscribing! Check your inbox soon.", 'success');
      input.value = '';
    }
  });
}
