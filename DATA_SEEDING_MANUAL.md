# Data Seeding Script - User Manual

## Overview
The data seeding script is a Django management command that automatically populates your placement management system database with realistic test data including students, companies, job postings, applications, interviews, and more.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Usage](#usage)
4. [What Gets Created](#what-gets-created)
5. [Command Options](#command-options)
6. [Generated Files](#generated-files)
7. [Login Credentials](#login-credentials)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Usage](#advanced-usage)

---

## Prerequisites

### Required Python Packages
The seeding script requires the following packages:
- `faker==22.0.0` - For generating realistic Indian names and data
- `reportlab==4.0.9` - For creating PDF resumes
- `python-dateutil==2.8.2` - For date manipulation
- `Pillow` - For generating company logos

These are already listed in `requirements.txt`.

### System Requirements
- Python 3.8 or higher
- Django 5.2.3
- Active virtual environment
- PostgreSQL or SQLite database configured

---

## Installation

### Step 1: Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

Or install packages individually:
```bash
pip install faker==22.0.0 reportlab==4.0.9 python-dateutil==2.8.2 Pillow
```

### Step 3: Verify Installation
```bash
python manage.py help seed_data
```

If successful, you'll see the help text for the `seed_data` command.

---

## Usage

### Basic Command
To seed the database with sample data:

```bash
python manage.py seed_data
```

### Clear and Reseed
To clear existing data and start fresh:

```bash
python manage.py seed_data --clear
```

### Interactive Mode
If you run the command without `--clear` and data already exists, the script will prompt you:

```
Data already exists!
Clear and reseed? (yes/no):
```

Type `yes` to clear and reseed, or `no` to cancel.

---

## What Gets Created

### 1. Admin Users (2)
- **Super Admin**
  - Username: `admin`
  - Password: `admin123`
  - Email: admin@placement.edu
  - Full access to all features

- **Placement Officer**
  - Username: `placement_officer`
  - Password: `placement123`
  - Email: placement@placement.edu
  - Admin privileges for placement operations

### 2. Student Profiles (50)
- **Distribution by Branch:**
  - Computer Science Engineering: 15 students
  - Electronics and Communication Engineering: 10 students
  - Mechanical Engineering: 8 students
  - Electrical and Electronics Engineering: 7 students
  - Civil Engineering: 5 students
  - Chemical Engineering: 5 students

- **CGPA Distribution:**
  - 20% with 9.0-10.0 (High performers)
  - 30% with 8.0-8.99 (Good performers)
  - 30% with 7.0-7.99 (Average performers)
  - 20% with 6.0-6.99 (Below average)

- **Backlogs:**
  - 70% with 0 backlogs
  - 20% with 1 backlog
  - 10% with 2 backlogs

- **Placement Status:**
  - 30% (15 students) are placed
  - 70% (35 students) are actively seeking placement

- **Each Student Has:**
  - Realistic Indian name (Faker library)
  - Unique email address
  - Phone number (+91 format)
  - LinkedIn profile URL
  - GitHub profile URL
  - Branch-specific skills
  - Generated PDF resume

### 3. Company Profiles (20)

#### Product Companies (8):
- Google India
- Microsoft India
- Amazon India
- Adobe India
- Netflix India
- Meta India
- Apple India
- Uber India

#### Service Companies (7):
- TCS
- Infosys
- Wipro
- Cognizant
- Accenture India
- Capgemini India
- HCL Technologies

#### Startups (5):
- Razorpay
- CRED
- Swiggy
- Zomato
- Flipkart

- **90% are approved** (18 companies)
- **10% pending approval** (2 companies)
- Each has HR contact details (name + email)
- Each has a generated company logo (200x200 PNG)

### 4. Job Postings (35-40)

Each approved company posts 2-3 jobs with varied roles:
- Software Development Engineer (SDE)
- Data Analyst
- Data Scientist
- Product Manager
- DevOps Engineer
- Frontend Developer
- Backend Developer
- Business Analyst
- QA Engineer

**Job Characteristics:**
- Salary ranges: 5-25 LPA
- CGPA requirements: 6.5-8.0
- Backlog limits: 0-2
- Branch eligibility criteria
- Application deadlines: 30-180 days from creation
- 80% are approved by admin

### 5. Applications (300-400)

- Each student applies to 8-10 jobs
- Only eligible jobs (based on CGPA, backlogs, branch)
- **Status Distribution:**
  - 40% Applied
  - 25% Shortlisted
  - 20% Rejected
  - 10% Interview
  - 5% Offered
- Placed students have at least one offer

### 6. Interview Schedules (150-180)

- 1-2 rounds per shortlisted/interviewed candidate
- **Round Types:**
  - Technical Round 1
  - Technical Round 2
  - HR Round
  - Managerial Round
- **Interview Modes:**
  - 70% Online (Google Meet, Zoom, Teams)
  - 30% In-person (office locations)
- Scheduled between application and deadline dates
- Includes additional instructions

### 7. Documents (7)

Admin-uploaded documents:
- Resume Template for Students
- Placement Guidelines 2025-26
- Interview Preparation Guide
- Company Research Checklist
- Sample Cover Letter Template
- FAQs for Placement Process
- Dress Code for Interviews

### 8. Audit Logs (40-50)

Sample audit trail entries:
- Student registrations
- Company registrations
- Job postings
- Job applications

---

## Command Options

### `--clear`
Clears all existing data before seeding.

```bash
python manage.py seed_data --clear
```

**Warning:** This will permanently delete:
- All students (except admins)
- All companies
- All job postings
- All applications
- All interview schedules
- All documents
- All audit logs

**Use with caution in production!**

---

## Generated Files

### 1. Student Resumes
- **Location:** `media/resumes/`
- **Format:** PDF
- **Naming:** `firstname_lastname_resume.pdf`
- **Count:** 50 files
- **Contents:**
  - Student name
  - Contact information (email, phone)
  - LinkedIn and GitHub URLs
  - Education details (branch, CGPA, graduation year)
  - Technical skills (word-wrapped)

### 2. Company Logos
- **Location:** `media/company_logos/`
- **Format:** PNG (200x200 pixels)
- **Naming:** `companyname.png`
- **Count:** 20 files
- **Design:** Company initials on colored background

### 3. Admin Documents
- **Location:** `media/documents/`
- **Format:** PDF
- **Count:** 7 files

### 4. Credentials File
- **Location:** `credentials.md` (project root)
- **Contents:**
  - All admin login credentials
  - All student usernames and details
  - All company usernames and details
  - Database statistics
  - Quick login links
  - Test scenarios

---

## Login Credentials

After seeding, check `credentials.md` for complete login details.

### Quick Access

**Admin Login:**
```
Username: admin
Password: admin123
URL: http://localhost:8000/login/
```

**Sample Student Login:**
```
Username: sara.das
Password: student123
Status: Placed
```

**Sample Company Login:**
```
Username: google_india_hr
Password: company123
Status: Approved
```

### Password Pattern
- **All students:** `student123`
- **All companies:** `company123`
- **Admins:** `admin123` or `placement123`

---

## Troubleshooting

### Issue 1: Module Not Found Error
```
ModuleNotFoundError: No module named 'faker'
```

**Solution:**
```bash
pip install faker==22.0.0 reportlab==4.0.9 python-dateutil==2.8.2 Pillow
```

### Issue 2: Permission Error
```
PermissionError: [Errno 13] Permission denied: 'media/resumes/'
```

**Solution:**
Ensure the media directories exist and have write permissions:
```bash
mkdir -p media/resumes media/company_logos media/documents
```

### Issue 3: Database Locked (SQLite)
```
django.db.utils.OperationalError: database is locked
```

**Solution:**
Stop the Django development server before running the seeding script:
```bash
# Stop server (Ctrl+C)
python manage.py seed_data --clear
# Restart server
python manage.py runserver
```

### Issue 4: Timezone Warnings
```
RuntimeWarning: DateTimeField Application.applied_at received a naive datetime
```

**Solution:**
This is a warning, not an error. Data is still created correctly. The script uses naive datetimes which Django converts to timezone-aware automatically.

### Issue 5: Out of Memory
If seeding a very large dataset:

**Solution:**
- Close other applications
- Increase system swap space
- Run seeding in smaller batches (modify the script if needed)

### Issue 6: Slow Performance
```
Seeding takes too long...
```

**Solution:**
- Use SQLite for faster seeding (development)
- Disable database logging temporarily
- Ensure database indexes are created

---

## Advanced Usage

### Modifying Data Quantities

Edit `core/management/commands/seed_data.py`:

```python
# Line 468: Change student count
student_count = 50  # Change to desired number

# Line 470: Adjust branch distribution
branch_distribution = {
    'Computer Science Engineering': 15,  # Modify counts
    'Electronics and Communication Engineering': 10,
    # ...
}

# Line 549: Applications per student
num_applications = random.randint(8, 10)  # Adjust range
```

### Adding Custom Data

You can extend the seeding script by adding custom functions:

```python
def seed_custom_data(self):
    """Add your custom seeding logic"""
    # Your code here
    pass
```

Then call it in the `handle()` method:

```python
def handle(self, *args, **options):
    # ... existing code ...
    self.seed_custom_data()
```

### Running in Production

**Never run with `--clear` in production!**

For production, create a separate management command:
```bash
python manage.py seed_data_production
```

And implement safeguards:
```python
if not settings.DEBUG:
    raise CommandError("Cannot run in production!")
```

---

## Command Output

### Successful Execution

```
==================================================
Placement Management System - Data Seeder
==================================================

Clearing existing data...
✓ Existing data cleared

[1/9] Creating admin users...
✓ Created 2 admin users

[2/9] Creating student users and profiles...
✓ Created 50 students with profiles and resumes

[3/9] Creating company users and profiles...
✓ Created 20 companies with profiles and logos

[4/9] Creating job postings...
✓ Created 38 job postings

[5/9] Creating applications...
✓ Created 320 applications

[6/9] Creating interview schedules...
✓ Created 167 interview schedules

[7/9] Creating documents...
✓ Created 7 documents

[8/9] Creating audit logs...
✓ Created 45 audit logs

[9/9] Generating credentials file...
✓ Generated credentials.md

==================================================
SEEDING COMPLETED SUCCESSFULLY!
==================================================

Statistics:
--------------------------------------------------
Users: 72 (2 admins, 50 students, 20 companies)
Job Postings: 38
Applications: 320
Interview Schedules: 167
Documents: 7
Audit Logs: 45

Files Generated:
--------------------------------------------------
- Resumes: 50 PDFs in media/resumes/
- Logos: 20 PNGs in media/company_logos/
- Documents: 7 PDFs in media/documents/
- Credentials: credentials.md

Next Steps:
--------------------------------------------------
1. Review credentials.md for login details
2. Run: python manage.py runserver
3. Login as admin: admin / admin123
4. Test student flow: [see credentials.md]
5. Test company flow: [see credentials.md]

==================================================
Happy Testing!
==================================================
```

---

## Testing Scenarios

### Scenario 1: Student with Placement
```
Login: sara.das / student123
- View placement status
- Check offered applications
- Access student dashboard
```

### Scenario 2: High CGPA Student
```
Login: rohan.das / student123
- CGPA: 9.5
- Multiple job applications
- Interview schedules
```

### Scenario 3: Company with Active Jobs
```
Login: google_india_hr / company123
- View posted jobs
- Review applicants
- Schedule interviews
```

### Scenario 4: Admin Operations
```
Login: admin / admin123
- Approve pending companies
- Approve pending jobs
- View analytics dashboard
- Generate reports
```

---

## Best Practices

1. **Always run with `--clear` in development** to ensure clean data
2. **Review `credentials.md`** after seeding for login details
3. **Backup your database** before running in production
4. **Test thoroughly** after seeding
5. **Monitor disk space** for generated files (PDFs, images)
6. **Keep the script updated** with your data model changes

---

## Verification Commands

After seeding, verify data was created:

```bash
# Check database counts
python manage.py shell -c "
from core.models import *
print(f'Students: {StudentProfile.objects.count()}')
print(f'Companies: {CompanyProfile.objects.count()}')
print(f'Jobs: {JobPosting.objects.count()}')
print(f'Applications: {Application.objects.count()}')
print(f'Interviews: {InterviewSchedule.objects.count()}')
"

# Check generated files
ls media/resumes/ | wc -l
ls media/company_logos/ | wc -l

# Verify a student can login
python manage.py shell -c "
from django.contrib.auth import authenticate
user = authenticate(username='sara.das', password='student123')
print(f'Login successful: {user is not None}')
"
```

---

## Maintenance

### Re-running the Script
You can safely re-run the script anytime:

```bash
python manage.py seed_data --clear
```

This will:
1. Delete all existing seeded data
2. Create fresh data with new random values
3. Generate new resumes and logos
4. Update credentials.md

### Updating the Script
If you modify models, update the script accordingly:

1. Open `core/management/commands/seed_data.py`
2. Update the relevant seeding functions
3. Test with `python manage.py seed_data --clear`
4. Commit changes to version control

---

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review Django logs for errors
3. Verify all dependencies are installed
4. Check `credentials.md` for test account details

---

## Version History

- **v1.0** - Initial release
  - 50 students, 20 companies
  - 35-40 job postings
  - 300-400 applications
  - PDF resume generation
  - Company logo generation
  - Comprehensive analytics data

---

*Last Updated: November 25, 2025*
