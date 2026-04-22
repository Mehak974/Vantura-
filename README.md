# 🛍️ Vantura — Peak Lifestyle Curations

A modern, secure, full-stack e-commerce platform built with **Django** + **Tailwind CSS** + **Vanilla JS**.

![Vantura](https://img.shields.io/badge/Django-4.2-green) ![Tailwind](https://img.shields.io/badge/Tailwind-CDN-blue) ![JS](https://img.shields.io/badge/Vanilla_JS-ES6-orange) ![Security](https://img.shields.io/badge/Security-Hardened-red)

---

## 🚀 Quick Start (5 minutes)

### 1. Clone / Extract

```bash
cd Vantura/
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Seed categories, subcategories & sample products

```bash
# Seed data + create admin user (admin / admin123)
python manage.py seed_data --admin

# Or just seed data without admin:
python manage.py seed_data
```

### 6. (Optional) Create your own superuser

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Open your browser:
- **Store:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin/

---

## 📁 Project Structure

```
Vantura/
├── manage.py
├── requirements.txt
├── README.md
│
├── vantura_project/          # Django project config
│   ├── settings.py           # All settings (security hardened)
│   ├── urls.py               # Root URL config
│   └── wsgi.py
│
├── store/                    # Main store app
│   ├── models.py             # Category, Product, Cart, Order, Review...
│   ├── views.py              # All page views (CSRF protected)
│   ├── admin.py              # Full admin panel config
│   ├── forms.py              # Checkout, Review, Contact forms
│   ├── urls.py               # Store URL patterns
│   ├── context_processors.py # Cart count + categories global injection
│   ├── migrations/
│   └── management/commands/
│       └── seed_data.py      # Database seeder
│
├── accounts/                 # Auth app
│   ├── models.py             # UserProfile
│   ├── views.py              # Login, Register, Profile
│   ├── forms.py              # Auth forms
│   ├── admin.py
│   └── migrations/
│
├── templates/                # All HTML templates
│   ├── base.html             # Base layout (navbar, footer, toasts)
│   ├── store/
│   │   ├── home.html         # Home page with 3D Three.js hero
│   │   ├── catalog.html      # Product catalog with filters
│   │   ├── product_detail.html
│   │   ├── category.html
│   │   ├── cart.html         # AJAX cart
│   │   ├── checkout.html
│   │   ├── order_confirmation.html
│   │   ├── search.html
│   │   ├── about.html
│   │   └── contact.html
│   ├── accounts/
│   │   ├── login.html
│   │   ├── signup.html
│   │   └── profile.html
│   ├── legal/
│   │   ├── privacy.html
│   │   ├── cookies.html
│   │   ├── terms.html
│   │   └── return.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
│
├── static/
│   └── js/
│       └── main.js           # All frontend JS (single file)
│
└── media/                    # Uploaded product images (auto-created)
```

---

## 🏪 Store Categories

| Category | Subcategories |
|---|---|
| Health & Supplements | Energy, Fat Burner, Herbal Formula, Magnesium, Muscle Builder, Pre Workout, Protein, Recovery, Snacks |
| Pet Care | Pet Convincer |
| Home & Outdoor | Fishing Accessories, Furniture, Hozon, Kitchen, Lightening, Sonars |
| Beauty & Personal Care | Bloodline Blacks, Conditioner, Ink Sets, Keratin, Shampoo, Tattoo Ink, UV Blacklight Colors |
| Tools | Chemical Injector, Deburring Tool, Filters, Flow Switch, Ladder Level, Spray Gun, Trimmer, Unloaders |
| Toys | Cards, Dragon Ball Z, Full Metal Alchemist, Key Ring, Naruto, One Piece, Plush Toys, Sonic |

---

## 🔒 Security Features

| Feature | Implementation |
|---|---|
| **CSRF Protection** | Django's built-in CSRF middleware on all POST requests |
| **XSS Prevention** | Auto-escaping in all templates + `escape()` in forms |
| **SQL Injection** | Django ORM — no raw SQL |
| **Secure Passwords** | Django's `PBKDF2PasswordHasher` with salt |
| **Session Security** | `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE='Lax'` |
| **File Upload** | Extension whitelist (`jpg`, `jpeg`, `png`, `webp`), 5MB limit |
| **Access Control** | `@login_required` on profile/checkout, staff-only admin |
| **Input Validation** | All form fields validated and sanitized before save |
| **Error Handling** | Custom 404/500 pages — no debug info exposed |
| **HTTPS Ready** | All security headers pre-configured for production |

---

## 🎨 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 4.2 |
| **Frontend CSS** | Tailwind CSS (CDN) |
| **3D Graphics** | CSS Blobs + Parallax JS |
| **Fonts** | Syne (display) + DM Sans (body) via Google Fonts |
| **Database** | SQLite (dev) → PostgreSQL recommended for production |
| **Image Storage** | Local media/ (dev) → S3/Cloudinary for production |

---

## ⚙️ Admin Panel

Access at `/admin/` with your superuser credentials.

**Manage:**
- 📦 Products — Add/edit/delete with image upload and bulk actions
- 🗂️ Categories & Subcategories — Full CRUD with slug auto-generation
- 📋 Orders — View order details, update status, see order items
- 👥 Users — Full user management via Django admin
- ⭐ Reviews — Approve/reject customer reviews
- 📬 Contact Messages — Read customer messages, mark as read

---

## 🌐 URL Reference

| URL | View |
|---|---|
| `/` | Home page |
| `/products/` | Product catalog |
| `/products/<slug>/` | Product detail |
| `/category/<slug>/` | Category page |
| `/cart/` | Shopping cart |
| `/checkout/` | Checkout (login required) |
| `/search/?q=` | Search |
| `/about/` | About page |
| `/contact/` | Contact page |
| `/accounts/login/` | Login |
| `/accounts/register/` | Sign up |
| `/accounts/profile/` | Profile (login required) |
| `/privacy-policy/` | Privacy policy |
| `/cookies-policy/` | Cookie policy |
| `/terms-conditions/` | Terms & conditions |
| `/return-exchange/` | Return policy |
| `/admin/` | Admin panel |

---

## 🚀 Production Deployment

### 1. Environment variables

Create a `.env` file (never commit this):

```bash
DJANGO_SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 2. Collect static files

```bash
python manage.py collectstatic
```

### 3. Use a production database

In `settings.py`, replace SQLite with PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

### 4. Use Gunicorn + Nginx

```bash
pip install gunicorn
gunicorn vantura_project.wsgi:application --workers 3 --bind 0.0.0.0:8000
```

### 5. SSL/HTTPS

All security headers (`SECURE_SSL_REDIRECT`, `HSTS`, `SECURE_COOKIES`) are already configured and activate automatically when `DEBUG=False`.

### 6. Stripe Payment Setup

To enable credit card payments:
1. Create a [Stripe Account](https://stripe.com).
2. Get your **Publishable Key** and **Secret Key** from the Stripe Dashboard.
3. Add them to your environment variables:
   ```bash
   STRIPE_PUBLIC_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   ```
4. The system will now automatically handle secure card payments.

---

## 📸 Adding Products

1. Log in at `/admin/`
2. Go to **Store → Products → Add Product**
3. Fill in: name, category, subcategory, price, stock, description
4. Upload product image (JPG/PNG/WEBP, max 5MB)
5. Toggle **Is Featured** to show on homepage
6. Toggle **Is New** for New Arrivals section
7. Save

---

## 🔧 Customization

### Change store name
Edit `base.html` — search for `VANTURA`

### Add a new category
```bash
python manage.py shell
>>> from store.models import Category
>>> Category.objects.create(name='Electronics', icon='💻')
```

### Change colors
Edit the Tailwind config in `base.html`:
```javascript
tailwind.config = {
    theme: { extend: { colors: { brand: { 500: '#your-color' } } } }
}
```

---

## 📄 License

© 2026 Vantura. All rights reserved.

---

*Built with ❤️ — From essentials to extra.*
