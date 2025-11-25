# Placement Management System

A comprehensive Django-based web application designed to streamline campus placement processes for educational institutions. This system connects students, companies, and administrators in a unified platform to manage job postings, applications, interviews, and placement outcomes.

![Django](https://img.shields.io/badge/Django-5.2.3-green)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.3-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [User Roles](#user-roles)
- [Database Models](#database-models)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The **Placement Management System** is designed to automate and simplify the entire campus recruitment process. It provides dedicated interfaces for three types of users:

- **Students**: Build profiles, browse jobs, apply, and track applications
- **Companies**: Post jobs, review applications, shortlist candidates, and schedule interviews
- **Administrators (TPO)**: Oversee the entire ecosystem, approve jobs, manage users, and generate reports

## ✨ Features

### For Students
- ✅ **Profile Management**: Create and update comprehensive student profiles
- ✅ **Resume Upload**: Upload and manage resumes (PDF format)
- ✅ **Job Browsing**: View eligible job postings based on CGPA, branch, and backlogs
- ✅ **One-Click Applications**: Apply to jobs with a single click
- ✅ **Application Tracking**: Monitor application status (Applied, Shortlisted, Interview, Offered, Rejected)
- ✅ **Interview Schedules**: View all scheduled interviews with details
- ✅ **Placement Status**: Track final placement outcome

### For Companies
- ✅ **Company Profile**: Manage company information and branding
- ✅ **Job Posting**: Create job postings with specific eligibility criteria
- ✅ **Application Management**: View and filter applications by status
- ✅ **Candidate Shortlisting**: Shortlist candidates for interviews
- ✅ **Interview Scheduling**: Schedule interviews for shortlisted candidates
- ✅ **Offer Management**: Mark candidates as offered
- ✅ **Dashboard Analytics**: View recruitment statistics and metrics

### For Administrators (TPO)
- ✅ **Comprehensive Dashboard**: Overview of entire placement ecosystem
- ✅ **User Management**: Manage students and companies
- ✅ **Job Approval**: Review and approve/reject job postings
- ✅ **Interview Management**: Oversee all scheduled interviews
- ✅ **Analytics**: View placement statistics and trends
- ✅ **Report Generation**: Export data as CSV files
- ✅ **Bulk Upload**: Import student/company data via CSV
- ✅ **Audit Logs**: Track important system actions

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.2.3
- **Database**: SQLite3 (development) - easily upgradable to PostgreSQL/MySQL
- **Authentication**: Django's built-in authentication system with custom User model
- **File Handling**: Pillow for image processing

### Frontend
- **UI Framework**: Bootstrap 5.3.3
- **Icons**: Font Awesome 6.5.2
- **Fonts**: Google Fonts (Poppins)
- **Forms**: Django Crispy Forms with Bootstrap 5 template pack
- **Filtering**: Django Filter

### Additional Tools
- **Version Control**: Git
- **Virtual Environment**: Python venv

## 📁 Project Structure

```
placement-management-system-project/
│
├── core/                           # Main application
│   ├── migrations/                 # Database migrations
│   ├── templates/                  # HTML templates
│   │   ├── admin/                  # Admin panel templates
│   │   ├── company/                # Company panel templates
│   │   ├── student/                # Student panel templates
│   │   ├── registration/           # Auth templates
│   │   ├── partials/               # Reusable components
│   │   ├── utils/                  # Utility templates
│   │   ├── base.html               # Base template
│   │   ├── home.html               # Landing page
│   │   ├── about.html              # About page
│   │   └── notifications.html      # Notifications page
│   │
│   ├── __init__.py
│   ├── admin.py                    # Django admin configuration
│   ├── apps.py                     # App configuration
│   ├── context_processors.py       # Custom context processors
│   ├── decorators.py               # Custom decorators (role-based access)
│   ├── forms.py                    # Django forms
│   ├── models.py                   # Database models
│   ├── tests.py                    # Unit tests
│   ├── urls.py                     # URL routing
│   └── views.py                    # View functions
│
├── placement_system/               # Project configuration
│   ├── __init__.py
│   ├── asgi.py                     # ASGI configuration
│   ├── settings.py                 # Project settings
│   ├── urls.py                     # Root URL configuration
│   └── wsgi.py                     # WSGI configuration
│
├── static/                         # Static files
│   ├── css/
│   │   └── style.css               # Custom styles
│   └── images/
│       ├── LOGO.jpg                # Background image
│       ├── LOGO1.jpg               # Hero image
│       └── 404.svg                 # 404 error image
│
├── media/                          # User-uploaded files
│   ├── resumes/                    # Student resumes
│   └── company_logos/              # Company logos
│
├── db.sqlite3                      # SQLite database
├── manage.py                       # Django management script
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd placement-management-system-project
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin account.

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open your browser and navigate to: `http://127.0.0.1:8000/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

## 📖 Usage

### Initial Setup

1. **Create Admin User**: After running migrations, create a superuser and set their role to 'admin' via Django admin panel.

2. **Student Registration**: Students can register at `/register/student/` and complete their profiles.

3. **Company Registration**: Companies can register at `/register/company/` (requires admin approval).

4. **Admin Approval**: Admin must approve company profiles before they can post jobs.

### Workflow

1. **Company Posts Job** → Admin Approves → Job becomes visible to eligible students
2. **Student Applies** → Company Reviews → Shortlists Candidates
3. **Company Schedules Interview** → Student Receives Notification
4. **Company Makes Offer** → Student's placement status updated

## 👥 User Roles

### Student
- **Access**: Student dashboard, profile, job listings, applications, interviews
- **Capabilities**: Apply to jobs, upload resume, track application status

### Company
- **Access**: Company dashboard, profile, job management, applicant review
- **Capabilities**: Post jobs, review applications, shortlist candidates, schedule interviews, make offers

### Admin (TPO)
- **Access**: Full system access
- **Capabilities**: Manage all users, approve jobs, generate reports, view analytics, bulk operations

## 🗄️ Database Models

### User Model
Custom user model extending Django's `AbstractUser` with role field (admin/student/company).

### StudentProfile
- Personal information (phone, branch, graduation year)
- Academic details (CGPA, backlogs)
- Professional links (LinkedIn, GitHub)
- Resume upload
- Placement status

### CompanyProfile
- Company information (name, description, website)
- HR contact details
- Company logo
- Approval status

### JobPosting
- Job details (title, description, salary range, location)
- Eligibility criteria (min CGPA, max backlogs, allowed branches)
- Application deadline
- Approval status

### Application
- Links student to job posting
- Application status (Applied, Shortlisted, Rejected, Interview, Offered)
- Timestamp tracking

### InterviewSchedule
- Interview details (date, time, round name)
- Mode (Online/In-Person)
- Venue or meeting link
- Additional instructions

### Supporting Models
- **Document**: For admin to upload guidelines/templates
- **AuditLog**: Tracks important system actions

## 🔒 Security Features

- **Role-Based Access Control**: Custom decorators ensure users can only access authorized pages
- **CSRF Protection**: Django's built-in CSRF protection on all forms
- **Password Validation**: Strong password requirements
- **File Upload Validation**: Restricted file types for uploads
- **SQL Injection Protection**: Django ORM prevents SQL injection attacks

## 🎨 UI/UX Features

- **Responsive Design**: Mobile-friendly interface using Bootstrap 5
- **Glassmorphism Effects**: Modern frosted glass design on landing page
- **Intuitive Navigation**: Role-specific navigation menus
- **Form Validation**: Client and server-side validation
- **Flash Messages**: User feedback for all actions
- **Consistent Theming**: Unified color scheme and typography

## 📊 Key Views and URLs

### Authentication
- `/register/student/` - Student registration
- `/register/company/` - Company registration
- `/login/` - User login
- `/logout/` - User logout

### Student Panel
- `/student/dashboard/` - Student dashboard
- `/student/profile/` - Profile management
- `/student/jobs/` - Job listings
- `/student/applied-jobs/` - Application history
- `/student/interviews/` - Interview schedule

### Company Panel
- `/company/dashboard/` - Company dashboard
- `/company/profile/` - Company profile
- `/company/jobs/post/` - Post new job
- `/company/jobs/manage/` - Manage posted jobs
- `/company/jobs/<id>/applicants/` - View applicants

### Admin Panel
- `/tpo/dashboard/` - Admin dashboard
- `/tpo/students/` - Manage students
- `/tpo/companies/` - Manage companies
- `/tpo/jobs/approve/` - Approve jobs
- `/tpo/analytics/` - View analytics
- `/tpo/reports/` - Generate reports

## 🔧 Configuration

### Settings (placement_system/settings.py)

Key configurations:
- `AUTH_USER_MODEL = 'core.User'` - Custom user model
- `MEDIA_ROOT` - User upload directory
- `STATIC_ROOT` - Static files directory
- `CRISPY_TEMPLATE_PACK = "bootstrap5"` - Form styling

### Environment Variables (Production)

For production deployment, set these environment variables:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Set to False
- `ALLOWED_HOSTS` - Your domain names
- `DATABASE_URL` - Database connection string

## 📈 Future Enhancements

- [ ] Email notifications for application status updates
- [ ] Real-time chat between students and companies
- [ ] Advanced analytics with charts and graphs
- [ ] Mobile application (React Native/Flutter)
- [ ] Integration with LinkedIn for profile import
- [ ] Video interview scheduling
- [ ] Automated resume parsing
- [ ] Multi-language support
- [ ] API for third-party integrations

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Developer

Developed with ❤️ for streamlining campus placements.

## 📞 Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Note**: This is a development version. For production deployment, ensure proper security configurations, use a production-grade database (PostgreSQL/MySQL), and set up proper static file serving with a web server like Nginx or Apache.
