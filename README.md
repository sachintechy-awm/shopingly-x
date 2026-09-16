# ShopinglyX

An AI-powered ecommerce platform built with Django, featuring 100 demo products
across 10 categories, a full-featured header, 3D CSS animations, a session-based
shopping cart, and a Gemini-backed AI shopping assistant.

---

## Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy the environment template and fill it in
cp .env.example .env            # Windows: copy .env.example .env

# 4. Set up the database
python manage.py makemigrations
python manage.py migrate

# 5. Load the 100 demo products
python manage.py seed_products

# 6. (Optional) Create an admin account
python manage.py createsuperuser

# 7. Run the server
python manage.py runserver
```

Then open **http://127.0.0.1:8000/** in your browser.

The Django admin is at **http://127.0.0.1:8000/admin/**.

---

## The AI Assistant

The "Ask AI" button in the header opens a shopping assistant where a customer can
describe what they need in plain language (e.g. *"something to keep my coffee hot
on my commute"*) and get matched with products from the catalog.

**It works out of the box with no API key.** Without a key, it falls back to
keyword matching against the product catalog, so the feature is fully functional
for local development and demos.

To enable real Gemini-powered responses:

1. Get a free API key from https://aistudio.google.com/apikey
2. Add it to your `.env` file:
   ```
   GEMINI_API_KEY=your_key_here
   ```
3. Restart the server.

The relevant code is in `store/ai_assistant.py`. If the API call fails for any
reason (no key, network issue, quota exceeded), it silently falls back to keyword
matching rather than breaking the page.

---

## Project Structure

```
shopinglyx/
├── manage.py
├── requirements.txt
├── .env                        # your real secrets (gitignored)
├── .env.example                # template (safe to commit)
├── .gitignore
├── generate_placeholder_images.py   # regenerates product images
│
├── shopinglyx/                 # project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
└── store/                      # main app
    ├── models.py               # Category, Product, Order, OrderItem
    ├── views.py                # all page + AJAX views
    ├── urls.py
    ├── cart.py                 # session-based cart
    ├── ai_assistant.py         # Gemini integration + fallback
    ├── context_processors.py   # cart + categories in every template
    ├── product_data.py         # the 100-product catalog definition
    ├── admin.py
    ├── management/commands/
    │   └── seed_products.py    # populates the database
    ├── templates/store/
    │   ├── base.html
    │   ├── home.html
    │   ├── product_list.html
    │   ├── product_detail.html
    │   ├── cart.html
    │   ├── checkout.html
    │   ├── order_success.html
    │   ├── login.html
    │   ├── signup.html
    │   └── partials/
    │       ├── header.html
    │       ├── footer.html
    │       ├── product_card.html
    │       └── ai_modal.html
    └── static/store/
        ├── css/style.css
        ├── js/main.js
        └── images/
            ├── products/       # 100 generated product images
            └── categories/     # 10 generated category banners
```

---

## Features

**Header**
- Top utility bar (shipping notice, order tracking, help center links)
- Animated 3D rotating logo
- Live search with a dedicated "Ask AI" button
- Account dropdown (login / signup / logout, changes based on auth state)
- Wishlist and cart icons with a live-updating item count badge
- Horizontally scrollable category navigation bar
- Sticky on scroll, fully responsive with a mobile menu toggle

**3D Animations (pure CSS, no libraries)**
- Four floating, rotating 3D cubes in the hero section (`transform-style: preserve-3d`)
- Mouse-follow tilt on every product card (calculated in `main.js`)
- Spinning logo cube, pulsing glow on the AI button, bobbing hero badge
- Hover lift effects on cards, buttons, and category tiles

**Shopping**
- 100 products across 10 categories, each with its own generated image
- Category filtering, keyword search, and 4 sort options
- Pagination (12 products per page)
- Product detail pages with related-product recommendations
- Session-based cart (no login required) with AJAX add-to-cart
- Checkout flow that creates a real `Order` record
- User registration and login

---

## Regenerating Product Images

The 100 product images and 10 category banners are already included. If you edit
the catalog in `store/product_data.py` and want fresh matching images:

```bash
python generate_placeholder_images.py
```

These are gradient placeholders with the product name rendered on them — swap in
real product photography by replacing the files in
`store/static/store/images/products/`.

---

## Deploying

Before deploying anywhere public:

1. Generate a new `SECRET_KEY`:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
2. Set `DEBUG=False` in your production environment
3. Add your domain to `ALLOWED_HOSTS`
4. Run `python manage.py collectstatic`
5. Never commit your `.env` file — only `.env.example`

---

## Notes

- The checkout is a demo flow: it records an order in the database but processes
  no payment.
- The newsletter signup and wishlist buttons are front-end demos with no backend.
- SQLite is used by default so the project runs with zero database setup.
