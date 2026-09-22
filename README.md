# Fred's Global Real Estate Management System

A full-featured real estate management and property listing web application built with Django, Celery, and Bootstrap 5. The platform enables users, agents, and administrators to list, browse, manage, and book verified properties, titled lands, and luxury living spaces.

---

## 🌟 Key Features

- **Property Catalog & Listings**: Browse, filter, search, and manage properties for sale and rent (plots, villas, luxury living).
- **Interactive Booking System**: Schedule site visits and property consultations with automated status updates.
- **Client & Lead Management (CRM)**: Manage contact requests, inquiries, and customer interactions.
- **Task Management**: Assign, track, and manage team tasks with priority and due-date workflows.
- **Activity Tracking**: Real-time logging of system and user activities across the platform.
- **Media Vault**: Secure storage and management for property assets, plans, images, and videos.
- **Blockchain / Document Verification**: Land title and document verification tools for security and transparency.
- **Background Tasks & Notifications**: Asynchronous processing with Celery and Redis (with Celery Beat scheduling).
- **Role-Based Access & Security**: Custom user roles, authentication, and secure profile management.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12+, Django 6.x
- **Asynchronous Tasks**: Celery, Redis
- **Frontend**: HTML5, Vanilla CSS, Bootstrap 5, Crispy Forms
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Static & Media Handling**: WhiteNoise, Pillow

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+ installed
- Git installed
- Redis (optional for local Celery development, or set `CELERY_ALWAYS_EAGER=True`)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/FUAFUELAKAMOSCO/FEDSGLOBALREALESTATE-Managementsystem.git
   cd FEDSGLOBALREALESTATE-Managementsystem
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables**:
   Copy the example environment file:
   ```bash
   # Windows PowerShell
   Copy-Item realestate_system\.env.example realestate_system\.env

   # Linux/macOS
   cp realestate_system/.env.example realestate_system/.env
   ```

5. **Run Migrations**:
   ```bash
   cd realestate_system
   python manage.py migrate
   ```

6. **Create a Superuser (Admin)**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000` in your web browser.

---

## 📂 Project Structure

```text
FEDSGLOBALREALESTATE-Managementsystem/
├── realestate_system/          # Main Django project directory
│   ├── accounts/               # User authentication & profile management
│   ├── activity/               # Activity logs & timeline
│   ├── bookings/               # Property booking & visit scheduling
│   ├── contacts/               # Contact & lead management
│   ├── dashboard/              # Admin dashboard, media vault, security
│   ├── properties/             # Property catalog, listings, and filters
│   ├── tasks/                  # Task management system
│   ├── static/                 # Static assets (CSS, images)
│   ├── templates/              # Global templates
│   ├── manage.py               # Django management CLI
│   └── realestate_system/      # Project settings, URLs, WSGI/ASGI, Celery config
├── .env.example                # Sample environment configuration
├── .gitignore                  # Git ignore rules
├── LICENSE                     # Project License
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
