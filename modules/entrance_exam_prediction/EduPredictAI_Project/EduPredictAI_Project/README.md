# EduPredict AI — University Student Insights Portal

A React web application based on the uploaded EduPredict AI interface. It includes a dashboard, student registration, student records, student report pages, scholarship screening, historical CSV import preview, staff management, and portal settings.

## Requirements

- Node.js 18 or newer
- npm

## Run on Windows

1. Extract `EduPredictAI_Project.zip` (if you downloaded the ZIP).
2. Open the `EduPredictAI_Project` folder in VS Code.
3. Open the VS Code terminal in that folder.
4. Install the dependencies:

   ```bash
   npm install
   ```

5. Start the development server:

   ```bash
   npm run dev
   ```

6. Open the local URL printed in the terminal, usually `http://localhost:5173`.

To make a production build, run `npm run build`. The generated website files will be placed in `dist/`.

## Demo sign-in accounts

| Role | Email | Password |
|---|---|---|
| Administrator | `admin@edupredict.edu` | `Admin@2026` |
| Admission Staff | `staff@edupredict.edu` | `Staff@2026` |
| Academic Counselor | `counselor@edupredict.edu` | `Counselor@2026` |

These are demo credentials from the supplied code. Do not use these credentials or the current client-side authentication for a real university system.

## Main features

- Role-based demo sign-in and staff sign-up
- University dashboard with student counts and Recharts visualizations
- Student registration form and heuristic academic score estimate
- Searchable student records and student reports
- Branch-fit suggestions and merit/financial-need scholarship screening
- CSV import with record count and a sample preview
- Actual CSV report download and PDF report generation
- Administrator-only staff management and portal settings

## Important implementation notes

- This supplied project is currently a **front-end demo**. Authentication, student records, users, settings, and datasets are held in React state and reset on page refresh.
- The GPA/branch estimates are rule-based demo calculations, **not a trained machine-learning model**. Uploaded historical CSV files are parsed for preview only; there is no actual model training or measured model accuracy in this version.
- Scholarship status is an indicative screen only. Authorized university staff must apply the institution's official rules and review each case.
- Before production use, add a backend API, database, server-side authentication with hashed passwords, role-based authorization, input validation, audit logs, and appropriate privacy/security controls.

## Project structure

```text
EduPredictAI_Project/
├── public/
├── src/
│   ├── App.jsx
│   ├── index.css
│   └── main.jsx
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── .gitignore
└── README.md
```
