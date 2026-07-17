# CRM Portal Frontend

Professional frontend implementation for a CRM product subscription portal. The application is built with React and Vite, and includes product browsing, subscription plan display, registration, login, password recovery, user dashboard, and admin approval screens.

## Tech Stack

- React
- Vite
- Tailwind CSS utility classes
- Oxlint

## Pages

The project currently includes eight frontend screens:

- Landing Page: Displays product image, product name, and description.
- Product Details Page: Displays product details, modules, pricing plans, features, limits, billing cycle, and currency.
- Registration Page: Collects user and company registration details.
- Login Page: Provides email/password login UI and forgot password navigation.
- Forgot Password Page: Provides password recovery request UI.
- Change Password Page: Provides password update UI.
- User Dashboard: Displays user account information.
- Admin Dashboard: Displays company approval requests with approve/reject actions.

## API Integration Points

The frontend is prepared to consume these endpoints:

```txt
GET /api/products/
GET /api/products/<slug>/
```

If the backend is not available, the product pages use local fallback data so the interface can still be reviewed.

## Registration Fields

The registration page includes:

- Full Name
- Email
- Password
- Confirm Password
- Company Name
- Company Logo
- Phone Number
- Country
- Address
- CNIC

The form validates required fields on submit and shows a clear message for the first missing field.

## Getting Started

Install dependencies:

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

Build for production:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## Project Structure

```txt
src/
  components/
    AdminDashboard.jsx
    ChangePassword.jsx
    ForgotPassword.jsx
    LoginPage.jsx
    ProductDetails.jsx
    ProductLanding.jsx
    RegistrationPage.jsx
    UserDashboard.jsx
  App.jsx
  index.css
  main.jsx
```

## Notes

- This branch contains the frontend implementation only.
- Generated files such as `node_modules`, `dist`, logs, and archive exports are ignored through `.gitignore`.
- The UI theme is configured in `src/index.css` using professional light dashboard styling.
