# OrbitCRM Base Platform

A modular, multi-tenant backend-first CRM base platform designed with clean domain separation. Built with Django to support catalog management (products, modules, plans) and secure tenant registrations with administrative approval workflows.

---

## Technical Stack
*   **Backend Framework**: Django 6.0+ (Python 3.12/3.14+)
*   **Database**: SQLite (default for development/testing)
*   **Aesthetics & Frontend**: Vanilla HTML5, CSS3, and JavaScript
*   **Testing**: Django TestCase suite using SQLite memory databases

---

## Project Architecture & Directory Layout

The codebase separates product/catalog definitions from user account authentication and tenant registration requests.

```text
crm/
│
├── accounts/                  # User accounts & tenant registration application
│   ├── templates/             # Dashboard, pending, login, and registration templates
│   ├── admin.py               # RegistrationRequest, OwnerProfile, & CustomUser admin maps
│   ├── forms.py               # Owner registration form with email/password validation
│   ├── models.py              # CustomUser, Organization, OwnerProfile, and Request models
│   ├── tests.py               # 17 automated tests (auth APIs, HTML registers, reviews)
│   ├── urls.py                # Session & API auth endpoints, registration routes
│   └── views.py               # Core logic (API view classes and HTML routing)
│
├── catalog/                   # Catalog definitions (products, modules, plans)
│   ├── templates/             # Catalog HTML demo templates
│   ├── models/                # Product, Module, Plan, and Limit models
│   ├── views/                 # API views and Demo views
│   ├── tests.py               # 8 automated tests (product lists, detailed configurations)
│   └── urls.py                # Product catalog API endpoints and demo paths
│
├── myproject/                 # Main configuration directory
│   ├── settings.py            # Custom user models, media uploads, static, mail settings
│   └── urls.py                # Main routing configuration
│
├── media/                     # Uploaded tenant assets (e.g. company logos)
│   └── logos/                 
│
├── manage.py                  # Django execution manager
└── requirements.txt           # Dependency requirements list
```

---

## Features Implemented

### 1. Catalog Management (`catalog` app)
*   **Product Catalog API**: Lists and retrieves products, including descriptions, logos, and features.
*   **Pricing Plans**: Modular plans supporting custom pricing, billing cycles (monthly/yearly), and statuses.
*   **Plan Modules & Limits**: Granular control over enabled modules and quantitative usage limits (e.g. max user seats, storage).
*   **Demo Interface (`/demo/`)**: Interactive list and details viewer presenting modules and plan-specific limits.
*   **Product Image Support**: Complete support for uploading and managing product images:
    *   **Django Admin Uploads**: Administrators can upload, replace, and view live previews of product images directly from the Product details view in the Django Admin dashboard.
    *   **Image Validation**: Uploads are restricted to JPG, JPEG, PNG, and WEBP formats only, and file sizes are strictly capped at a maximum of 5 MB.
    *   **Automatic Cleanup**: When a product image is replaced or the product itself is deleted, the corresponding file is automatically removed from the local filesystem to prevent orphaned media.
    *   **Storage Location**: Image files are stored under `media/products/` on the server filesystem.
    *   **Absolute API URLs**: The product list (`/api/products/`) and detail (`/api/products/<slug>/`) API endpoints return the full, absolute URL path (e.g., `http://127.0.0.1:8000/media/products/filename.png`) in the `image` field (or `null` if no image has been uploaded), allowing direct use by frontend clients.
*   **Professional Services Module**: Dynamic professional service listings (e.g., CRM/AI/ERP Consultations, Custom Software Development, UI/UX Design).
    *   **Services APIs**: Exposes `/api/services/` (active listings summary with slug, status, image URL) and `/api/services/<slug>/` (in-depth descriptions and dynamic features checklist) for frontend client usage. No service data is hardcoded.
    *   **Services Django Admin**: Administrators can create/edit/delete services, manage features inline, upload service banners (format validated, max 5 MB, Pillow verified), and preview images on-the-fly.
    *   **Automatic Image Cleanup**: Adapts filesystem cleanup receivers to prune services media assets immediately on deletions or replacements.
    *   **Demo Dashboard (`/demo/services/`)**: Interactive dashboard listing services and detailing dynamic features lists fetched via APIs.



### 2. Authentication System (`accounts` app)
*   **API Authentication endpoints**: Fully-tested JSON APIs supporting:
    *   `/api/auth/login/` (Session establishment)
    *   `/api/auth/logout/` (Session termination)
    *   `/api/auth/change-password/` (Authenticated password updating)
    *   `/api/auth/forgot-password/` (Password reset email generator)
*   **Password Reset Flow**: Standard token-based recovery template flow (`/auth/reset-password/<uidb64>/<token>/`).
*   **Aesthetics Demo (`/auth-demo/`)**: QA testing dashboard verifying session persistence, CSRF protections, response times, and failure responses.

### 3. Tenant Registration Workflow (`accounts` app)
*   **Registration Portal (`/register/`)**: Registers new business owners and their organization profiles.
*   **Review Dashboard (`/admin-dashboard/`)**: Review queue for superusers to inspect and approve or reject tenant registrations.
*   **Pending Verification (`/login/` / `/pending.html`)**: Logs in registered accounts and redirects to a pending approval notice if the request is not yet approved.
*   **Rejection popup/notifications**: Auto-sends email notifications upon rejection and triggers warning modals on subsequent login attempts.

---

## Installation & Local Development

### 1. Prerequisites
Ensure you have Python 3.12+ and Git installed on your system.

### 2. Environment Setup
Clone the repository and set up a Python virtual environment:
```bash
# Clone the repository
git clone https://github.com/zaid-mian/JTS_project.git
cd JTS_project

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux / macOS:
source venv/bin/activate
```

### 3. Install Dependencies
Install the required packages:
```bash
pip install -r requirements.txt
```

### 4. Database Setup & Migrations
Initialize the SQLite database and create migrations:
```bash
# Generate database schema migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 5. Seed Initial Catalog Data
Load initial seed data for products, modules, and plans:
```bash
python manage.py loaddata catalog_data.json
```

### 6. Create Superuser (Admin Dashboard Access)
Create a superuser to access the Django admin portal and the tenant registration dashboard:
```bash
python manage.py createsuperuser
```

---

## Running the Platform

### Running the Local Development Server
Launch the server on localhost:
```bash
python manage.py runserver
```
The server will start at `http://127.0.0.1:8000/`.

### Running Automated Test Suite
Run the test runner to execute all 25 unit tests:
```bash
python manage.py test
```

---

## Key URLs & Entry Points

*   **Administration Portal**: `http://127.0.0.1:8000/admin/`
*   **Catalog Demo Portal**: `http://127.0.0.1:8000/demo/`
*   **Authentication Demo Dashboard**: `http://127.0.0.1:8000/auth-demo/`
*   **Business Registration Portal**: `http://127.0.0.1:8000/register/`
*   **Business Login Portal**: `http://127.0.0.1:8000/login/`
*   **Admin Approval Dashboard**: `http://127.0.0.1:8000/admin-dashboard/`

---

## Future Integration Points
1.  **Payment Integrations**: Hooking billing cycle plans to checkout platforms (e.g. Stripe checkout) to charge organizations after registration approval.
2.  **Email SMTP Settings**: Replacing Django's console development email backend (`DevelopmentEmailBackend`) with SMTP credentials in `settings.py` for real-world user mailers.
3.  **Android App Clients**: Consuming the JSON endpoints (`/api/auth/...` and `/api/products/...`) inside native Android/mobile client apps.