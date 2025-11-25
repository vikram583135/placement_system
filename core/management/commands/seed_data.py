# core/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from core.models import StudentProfile, CompanyProfile, JobPosting, Application, InterviewSchedule, Document, AuditLog
from faker import Faker
import random
from datetime import datetime, timedelta, date, time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import traceback
import os

User = get_user_model()
fake = Faker('en_IN')  # Indian locale

# Constants
BRANCHES = [
    'Computer Science Engineering',
    'Electronics and Communication Engineering',
    'Mechanical Engineering',
    'Electrical and Electronics Engineering',
    'Civil Engineering',
    'Chemical Engineering'
]

BRANCH_SHORT = {
    'Computer Science Engineering': 'CSE',
    'Electronics and Communication Engineering': 'ECE',
    'Mechanical Engineering': 'ME',
    'Electrical and Electronics Engineering': 'EEE',
    'Civil Engineering': 'Civil',
    'Chemical Engineering': 'Chemical'
}

COMPANIES = [
    {'name': 'Google India', 'website': 'https://careers.google.com', 'tier': 'product', 'desc': 'Google is a multinational technology company specializing in Internet-related services and products.'},
    {'name': 'Microsoft India', 'website': 'https://careers.microsoft.com', 'tier': 'product', 'desc': 'Microsoft is a global leader in software, cloud computing, and AI innovation.'},
    {'name': 'Amazon India', 'website': 'https://amazon.jobs', 'tier': 'product', 'desc': 'Amazon is an e-commerce and cloud computing giant revolutionizing online retail.'},
    {'name': 'Adobe India', 'website': 'https://adobe.com/careers', 'tier': 'product', 'desc': 'Adobe is a leader in digital media and marketing software solutions.'},
    {'name': 'Netflix India', 'website': 'https://jobs.netflix.com', 'tier': 'product', 'desc': 'Netflix is a global streaming entertainment service provider.'},
    {'name': 'Meta India', 'website': 'https://metacareers.com', 'tier': 'product', 'desc': 'Meta is a social technology company building the future of human connection.'},
    {'name': 'Apple India', 'website': 'https://apple.com/jobs', 'tier': 'product', 'desc': 'Apple is a technology company known for innovative consumer electronics and software.'},
    {'name': 'Uber India', 'website': 'https://uber.com/careers', 'tier': 'product', 'desc': 'Uber is a ride-sharing and food delivery platform transforming urban mobility.'},
    {'name': 'TCS', 'website': 'https://tcs.com/careers', 'tier': 'service', 'desc': 'Tata Consultancy Services is a leading IT services and consulting company.'},
    {'name': 'Infosys', 'website': 'https://infosys.com/careers', 'tier': 'service', 'desc': 'Infosys is a global leader in next-generation digital services and consulting.'},
    {'name': 'Wipro', 'website': 'https://wipro.com/careers', 'tier': 'service', 'desc': 'Wipro is an information technology and consulting services provider.'},
    {'name': 'Cognizant', 'website': 'https://careers.cognizant.com', 'tier': 'service', 'desc': 'Cognizant is a multinational IT services and consulting corporation.'},
    {'name': 'Accenture India', 'website': 'https://accenture.com/careers', 'tier': 'service', 'desc': 'Accenture is a professional services company with leading capabilities in strategy and consulting.'},
    {'name': 'Capgemini India', 'website': 'https://capgemini.com/careers', 'tier': 'service', 'desc': 'Capgemini is a global leader in consulting and IT services.'},
    {'name': 'HCL Technologies', 'website': 'https://hcltech.com/careers', 'tier': 'service', 'desc': 'HCL is an IT services and product engineering company.'},
    {'name': 'Razorpay', 'website': 'https://razorpay.com/jobs', 'tier': 'startup', 'desc': 'Razorpay is a payment gateway and financial services platform.'},
    {'name': 'CRED', 'website': 'https://cred.club/careers', 'tier': 'startup', 'desc': 'CRED is a members-only credit card bill payment platform.'},
    {'name': 'Swiggy', 'website': 'https://swiggy.com/careers', 'tier': 'startup', 'desc': 'Swiggy is a food ordering and delivery platform revolutionizing food tech.'},
    {'name': 'Zomato', 'website': 'https://zomato.com/careers', 'tier': 'startup', 'desc': 'Zomato is a restaurant aggregator and food delivery company.'},
    {'name': 'Flipkart', 'website': 'https://flipkartcareers.com', 'tier': 'startup', 'desc': 'Flipkart is an e-commerce marketplace offering a wide range of products.'},
]

SKILLS_BY_BRANCH = {
    'Computer Science Engineering': [
        'Python', 'Java', 'C++', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue.js',
        'Django', 'Flask', 'Node.js', 'Express', 'Spring Boot', 'SQL', 'PostgreSQL',
        'MongoDB', 'Redis', 'Git', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'Machine Learning',
        'Data Structures', 'Algorithms', 'REST APIs', 'GraphQL', 'Linux', 'Jenkins', 'Terraform'
    ],
    'Electronics and Communication Engineering': [
        'Python', 'C', 'C++', 'MATLAB', 'Circuit Design', 'Signal Processing', 'Embedded Systems',
        'VLSI Design', 'PCB Design', 'Arduino', 'Raspberry Pi', 'Verilog', 'VHDL', 'Communication Systems',
        'Microcontrollers', 'Linux', 'Git', 'IoT', 'Machine Learning', 'Data Structures'
    ],
    'Mechanical Engineering': [
        'AutoCAD', 'SolidWorks', 'CATIA', 'Ansys', 'MATLAB', 'Finite Element Analysis', 'CAD/CAM',
        'Thermodynamics', 'Fluid Mechanics', 'Manufacturing Processes', 'Material Science',
        'Project Management', 'MS Office', 'Python', 'CNC Programming', '3D Printing'
    ],
    'Electrical and Electronics Engineering': [
        'MATLAB', 'Python', 'C', 'Circuit Design', 'Power Systems', 'Control Systems', 'PLC Programming',
        'Embedded Systems', 'AutoCAD Electrical', 'Simulink', 'PCB Design', 'Electrical Machines',
        'Power Electronics', 'Renewable Energy', 'Arduino', 'Signal Processing'
    ],
    'Civil Engineering': [
        'AutoCAD', 'Revit', 'StaadPro', 'Primavera', 'MS Project', 'Structural Analysis',
        'Surveying', 'Construction Management', 'Quantity Surveying', 'Building Codes',
        'MS Office', 'Geotechnical Engineering', 'Transportation Engineering', 'Water Resources'
    ],
    'Chemical Engineering': [
        'MATLAB', 'Aspen Plus', 'HYSYS', 'Process Design', 'Chemical Reaction Engineering',
        'Thermodynamics', 'Mass Transfer', 'Heat Transfer', 'Process Control', 'Safety Engineering',
        'MS Office', 'Python', 'Process Simulation', 'Unit Operations'
    ]
}

FIRST_NAMES = [
    'Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Arnav', 'Ayaan', 'Krishna', 'Ishaan',
    'Shaurya', 'Atharv', 'Advait', 'Reyansh', 'Rohan', 'Kabir', 'Dhruv', 'Aryan', 'Yash', 'Dev',
    'Aadhya', 'Ananya', 'Diya', 'Saanvi', 'Aarohi', 'Kiara', 'Navya', 'Pari', 'Avni', 'Sara',
    'Myra', 'Riya', 'Prisha', 'Shanaya', 'Zara', 'Aanya', 'Aditi', 'Sneha', 'Priya', 'Kavya',
    'Divya', 'Meera', 'Nisha', 'Pooja', 'Rahul', 'Amit', 'Karan', 'Vikram', 'Nikhil', 'Varun'
]

LAST_NAMES = [
    'Sharma', 'Kumar', 'Singh', 'Patel', 'Gupta', 'Reddy', 'Nair', 'Iyer', 'Joshi', 'Verma',
    'Agarwal', 'Mehta', 'Desai', 'Rao', 'Chopra', 'Bansal', 'Malhotra', 'Sinha', 'Das', 'Bose',
    'Pandey', 'Mishra', 'Saxena', 'Trivedi', 'Shah', 'Kulkarni', 'Menon', 'Pillai', 'Naik', 'Ghosh'
]

HR_NAMES = [
    ('Priya', 'Mehta'), ('Rahul', 'Verma'), ('Sneha', 'Agarwal'), ('Amit', 'Singh'),
    ('Kavya', 'Desai'), ('Karan', 'Patel'), ('Ananya', 'Rao'), ('Rohan', 'Gupta'),
    ('Diya', 'Chopra'), ('Arjun', 'Reddy'), ('Riya', 'Bansal'), ('Vikram', 'Iyer'),
    ('Neha', 'Malhotra'), ('Aditya', 'Joshi'), ('Pooja', 'Sinha'), ('Nikhil', 'Sharma'),
    ('Divya', 'Kumar'), ('Varun', 'Nair'), ('Meera', 'Shah'), ('Dev', 'Menon')
]

JOB_TEMPLATES = [
    {
        'title': 'Software Development Engineer - I',
        'role': 'SDE',
        'salary_range': '12-18 LPA',
        'min_cgpa': 7.5,
        'max_backlogs': 0,
        'allowed_branches': 'CSE,ECE,EEE',
        'locations': ['Bangalore', 'Hyderabad', 'Pune'],
        'tier': 'product'
    },
    {
        'title': 'Software Engineer',
        'role': 'SDE',
        'salary_range': '8-12 LPA',
        'min_cgpa': 7.0,
        'max_backlogs': 1,
        'allowed_branches': 'CSE,ECE',
        'locations': ['Bangalore', 'Mumbai', 'Gurgaon'],
        'tier': 'service'
    },
    {
        'title': 'Data Analyst',
        'role': 'Data',
        'salary_range': '8-14 LPA',
        'min_cgpa': 7.5,
        'max_backlogs': 0,
        'allowed_branches': 'CSE,ECE,ME',
        'locations': ['Bangalore', 'Mumbai', 'Delhi'],
        'tier': 'product'
    },
    {
        'title': 'Data Scientist',
        'role': 'Data',
        'salary_range': '15-22 LPA',
        'min_cgpa': 8.0,
        'max_backlogs': 0,
        'allowed_branches': 'CSE,ECE',
        'locations': ['Bangalore', 'Hyderabad'],
        'tier': 'product'
    },
    {
        'title': 'Product Manager - Associate',
        'role': 'PM',
        'salary_range': '15-25 LPA',
        'min_cgpa': 8.0,
        'max_backlogs': 0,
        'allowed_branches': 'CSE,ECE,ME',
        'locations': ['Bangalore', 'Mumbai'],
        'tier': 'product'
    },
    {
        'title': 'DevOps Engineer',
        'role': 'DevOps',
        'salary_range': '10-16 LPA',
        'min_cgpa': 7.0,
        'max_backlogs': 1,
        'allowed_branches': 'CSE,ECE',
        'locations': ['Bangalore', 'Pune', 'Hyderabad'],
        'tier': 'product'
    },
    {
        'title': 'Frontend Developer',
        'role': 'Frontend',
        'salary_range': '8-15 LPA',
        'min_cgpa': 6.5,
        'max_backlogs': 1,
        'allowed_branches': 'CSE,ECE,EEE',
        'locations': ['Bangalore', 'Pune', 'Chennai'],
        'tier': 'startup'
    },
    {
        'title': 'Backend Developer',
        'role': 'Backend',
        'salary_range': '9-16 LPA',
        'min_cgpa': 7.0,
        'max_backlogs': 1,
        'allowed_branches': 'CSE,ECE',
        'locations': ['Bangalore', 'Hyderabad'],
        'tier': 'startup'
    },
    {
        'title': 'Business Analyst',
        'role': 'BA',
        'salary_range': '6-10 LPA',
        'min_cgpa': 6.5,
        'max_backlogs': 1,
        'allowed_branches': 'CSE,ECE,ME,EEE,Civil,Chemical',
        'locations': ['Mumbai', 'Bangalore', 'Delhi'],
        'tier': 'service'
    },
    {
        'title': 'QA Engineer',
        'role': 'QA',
        'salary_range': '5-9 LPA',
        'min_cgpa': 6.5,
        'max_backlogs': 2,
        'allowed_branches': 'CSE,ECE,EEE',
        'locations': ['Pune', 'Bangalore', 'Chennai'],
        'tier': 'service'
    },
]


class Command(BaseCommand):
    help = 'Seed database with realistic placement system data'

    def __init__(self):
        super().__init__()
        self.credentials = {
            'admins': [],
            'students': [],
            'companies': []
        }
        self.stats = {
            'users': 0,
            'students': 0,
            'companies': 0,
            'jobs': 0,
            'applications': 0,
            'interviews': 0,
            'documents': 0,
            'audit_logs': 0
        }

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        self.stdout.write("=" * 50)
        self.stdout.write("Placement Management System - Data Seeder")
        self.stdout.write("=" * 50)
        
        if options['clear']:
            self.clear_data()
        elif User.objects.filter(role='student').exists():
            self.stdout.write(self.style.WARNING('\nData already exists!'))
            self.stdout.write(self.style.WARNING('Use --clear flag to remove existing data and reseed.'))
            self.stdout.write("Seeding cancelled.")
            return
        
        try:
            self.seed_admins()
            self.seed_students()
            self.seed_companies()
            self.seed_jobs()
            self.seed_applications()
            self.seed_interviews()
            self.seed_documents()
            self.seed_audit_logs()
            self.generate_credentials_file()
            
            self.print_summary()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error during seeding: {str(e)}'))
            traceback.print_exc()

    def clear_data(self):
        """Clear existing data"""
        self.stdout.write("\nClearing existing data...")
        
        with transaction.atomic():
            AuditLog.objects.all().delete()
            Document.objects.all().delete()
            InterviewSchedule.objects.all().delete()
            Application.objects.all().delete()
            JobPosting.objects.all().delete()
            CompanyProfile.objects.all().delete()
            StudentProfile.objects.all().delete()
            User.objects.filter(role__in=['student', 'company']).delete()
            
        self.stdout.write(self.style.SUCCESS('✓ Existing data cleared'))

    @transaction.atomic
    def seed_admins(self):
        """Create admin users"""
        self.stdout.write("\n[1/9] Creating admin users...")
        
        # Super admin
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@placement.edu',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            
        self.credentials['admins'].append({
            'username': 'admin',
            'password': 'admin123',
            'email': 'admin@placement.edu',
            'role': 'Super Admin',
            'name': 'System Administrator'
        })
        
        # Placement officer
        officer, created = User.objects.get_or_create(
            username='placement_officer',
            defaults={
                'email': 'placement@placement.edu',
                'first_name': 'Rajesh',
                'last_name': 'Kumar',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': False
            }
        )
        if created:
            officer.set_password('placement123')
            officer.save()
            
        self.credentials['admins'].append({
            'username': 'placement_officer',
            'password': 'placement123',
            'email': 'placement@placement.edu',
            'role': 'Placement Officer',
            'name': 'Rajesh Kumar'
        })
        
        self.stats['users'] += 2
        self.stdout.write(self.style.SUCCESS('✓ Created 2 admin users'))

    @transaction.atomic
    def seed_students(self):
        """Create student users and profiles"""
        self.stdout.write("\n[2/9] Creating student users and profiles...")
        
        student_count = 50
        branch_distribution = {
            'Computer Science Engineering': 15,
            'Electronics and Communication Engineering': 10,
            'Mechanical Engineering': 8,
            'Electrical and Electronics Engineering': 7,
            'Civil Engineering': 5,
            'Chemical Engineering': 5
        }
        
        used_names = set()
        student_num = 0
        
        for branch, count in branch_distribution.items():
            for i in range(count):
                # Generate unique name
                while True:
                    first_name = random.choice(FIRST_NAMES)
                    last_name = random.choice(LAST_NAMES)
                    full_name = f"{first_name} {last_name}"
                    if full_name not in used_names:
                        used_names.add(full_name)
                        break
                
                username = f"{first_name.lower()}.{last_name.lower()}"
                email = f"{username}@student.edu"
                
                # Create user
                user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role='student'
                )
                user.set_password('student123')
                user.save()
                
                # Generate CGPA based on distribution
                rand = random.random()
                if rand < 0.2:  # 20% between 9.0-10.0
                    cgpa = round(random.uniform(9.0, 10.0), 2)
                elif rand < 0.5:  # 30% between 8.0-8.99
                    cgpa = round(random.uniform(8.0, 8.99), 2)
                elif rand < 0.8:  # 30% between 7.0-7.99
                    cgpa = round(random.uniform(7.0, 7.99), 2)
                else:  # 20% between 6.0-6.99
                    cgpa = round(random.uniform(6.0, 6.99), 2)
                
                # Backlogs distribution
                rand = random.random()
                if rand < 0.7:
                    backlogs = 0
                elif rand < 0.9:
                    backlogs = 1
                else:
                    backlogs = 2
                
                # 30% placed
                is_placed = student_num < (student_count * 0.3)
                
                # Random skills from branch pool
                skills_pool = SKILLS_BY_BRANCH[branch]
                num_skills = random.randint(5, 10)
                skills = ', '.join(random.sample(skills_pool, min(num_skills, len(skills_pool))))
                
                phone_number = f"+91{random.choice(['9', '8', '7'])}{random.randint(100000000, 999999999)}"
                linkedin_url = f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}-{random.randint(100, 999)}"
                github_url = f"https://github.com/{first_name.lower()}{last_name.lower()}{random.randint(10, 99)}"
                
                # Create profile
                profile = StudentProfile.objects.create(
                    user=user,
                    phone_number=phone_number,
                    cgpa=cgpa,
                    branch=branch,
                    graduation_year=2026,
                    backlogs=backlogs,
                    skills=skills,
                    linkedin_url=linkedin_url,
                    github_url=github_url,
                    is_placed=is_placed
                )
                
                # Generate and save resume
                resume_buffer = self.generate_resume_pdf(profile)
                resume_filename = f"{first_name.lower()}_{last_name.lower()}_resume.pdf"
                profile.resume.save(resume_filename, ContentFile(resume_buffer.read()), save=True)
                
                self.credentials['students'].append({
                    'username': username,
                    'email': email,
                    'branch': BRANCH_SHORT[branch],
                    'cgpa': cgpa,
                    'placed': 'Yes' if is_placed else 'No'
                })
                
                student_num += 1
                self.stats['users'] += 1
                self.stats['students'] += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {student_count} students with profiles and resumes'))

    def generate_resume_pdf(self, student):
        """Generate a simple resume PDF"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Header
        c.setFont("Helvetica-Bold", 18)
        c.drawString(1*inch, 10.5*inch, f"{student.user.get_full_name()}")
        
        # Contact Info
        c.setFont("Helvetica", 10)
        y = 10.2*inch
        c.drawString(1*inch, y, f"Email: {student.user.email}")
        y -= 0.2*inch
        c.drawString(1*inch, y, f"Phone: {student.phone_number}")
        y -= 0.2*inch
        c.drawString(1*inch, y, f"LinkedIn: {student.linkedin_url}")
        y -= 0.2*inch
        c.drawString(1*inch, y, f"GitHub: {student.github_url}")
        
        # Education
        y -= 0.4*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y, "Education")
        y -= 0.2*inch
        c.setFont("Helvetica", 10)
        c.drawString(1*inch, y, f"{student.branch}")
        y -= 0.15*inch
        c.drawString(1*inch, y, f"CGPA: {student.cgpa} | Graduation Year: {student.graduation_year}")
        
        # Skills
        y -= 0.3*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y, "Technical Skills")
        y -= 0.2*inch
        c.setFont("Helvetica", 10)
        
        # Word wrap skills
        skills_text = student.skills
        max_width = 80
        words = skills_text.split(', ')
        current_line = []
        for word in words:
            test_line = ', '.join(current_line + [word])
            if len(test_line) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    c.drawString(1*inch, y, ', '.join(current_line))
                    y -= 0.15*inch
                current_line = [word]
        if current_line:
            c.drawString(1*inch, y, ', '.join(current_line))
        
        c.save()
        buffer.seek(0)
        return buffer

    @transaction.atomic
    def seed_companies(self):
        """Create company users and profiles"""
        self.stdout.write("\n[3/9] Creating company users and profiles...")
        
        for idx, company_data in enumerate(COMPANIES):
            username = company_data['name'].lower().replace(' ', '_') + '_hr'
            email = f"hr@{company_data['name'].lower().split()[0]}.com"
            
            # Create user
            user = User.objects.create(
                username=username,
                email=email,
                first_name=company_data['name'],
                last_name='HR',
                role='company'
            )
            user.set_password('company123')
            user.save()
            
            # HR details
            hr_first, hr_last = HR_NAMES[idx % len(HR_NAMES)]
            hr_name = f"{hr_first} {hr_last}"
            hr_email = f"{hr_first.lower()}.{hr_last.lower()}@{company_data['name'].lower().split()[0]}.com"
            
            # 90% approved
            is_approved = random.random() < 0.9
            
            # Create profile
            profile = CompanyProfile.objects.create(
                user=user,
                name=company_data['name'],
                description=company_data['desc'],
                website=company_data['website'],
                is_approved=is_approved,
                hr_name=hr_name,
                hr_email=hr_email
            )
            
            # Generate and save logo
            logo_buffer = self.generate_company_logo(company_data['name'])
            logo_filename = f"{company_data['name'].lower().replace(' ', '_')}.png"
            profile.logo.save(logo_filename, ContentFile(logo_buffer.read()), save=True)
            
            self.credentials['companies'].append({
                'username': username,
                'email': email,
                'company': company_data['name'],
                'approved': 'Yes' if is_approved else 'No'
            })
            
            self.stats['users'] += 1
            self.stats['companies'] += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(COMPANIES)} companies with profiles and logos'))

    def generate_company_logo(self, company_name):
        """Generate a simple logo with company initials"""
        colors = ['#4285F4', '#EA4335', '#FBBC05', '#34A853', '#FF6D00', '#7B1FA2', 
                  '#00ACC1', '#C0CA33', '#F4511E', '#8E24AA']
        bg_color = random.choice(colors)
        
        img = Image.new('RGB', (200, 200), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Get initials
        words = company_name.split()
        initials = ''.join([w[0].upper() for w in words[:2]])
        
        # Draw initials
        font_size = 80
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Get text bounding box
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((200 - text_width) // 2, (200 - text_height) // 2 - 10)
        
        draw.text(position, initials, fill='white', font=font)
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer

    @transaction.atomic
    def seed_jobs(self):
        """Create job postings"""
        self.stdout.write("\n[4/9] Creating job postings...")
        
        approved_companies = CompanyProfile.objects.filter(is_approved=True)
        
        for company in approved_companies:
            # 2-3 jobs per company
            num_jobs = random.randint(2, 3)
            
            # Filter templates by company tier
            tier_templates = [t for t in JOB_TEMPLATES if t['tier'] == company.user.username.split('_')[0] 
                             or random.random() < 0.3]  # 30% cross-tier
            
            if not tier_templates:
                tier_templates = JOB_TEMPLATES
            
            for i in range(num_jobs):
                template = random.choice(tier_templates)
                
                location = random.choice(template['locations'])
                
                # Deadline between 30-180 days from now
                days_ahead = random.randint(30, 180)
                deadline = date.today() + timedelta(days=days_ahead)
                
                # 80% approved
                is_approved = random.random() < 0.8
                
                description = f"""We are looking for talented {template['title']} to join our team in {location}.

Responsibilities:
- Design and develop high-quality software solutions
- Collaborate with cross-functional teams
- Participate in code reviews and technical discussions
- Contribute to architectural decisions

Required Skills:
- Strong problem-solving abilities
- Excellent communication skills
- Team player with leadership potential

Eligibility:
- CGPA: {template['min_cgpa']}+
- Maximum Backlogs: {template['max_backlogs']}
- Branches: {template['allowed_branches']}
"""
                
                job = JobPosting.objects.create(
                    company=company,
                    title=template['title'],
                    description=description,
                    salary_range=template['salary_range'],
                    location=location,
                    application_deadline=deadline,
                    min_cgpa=template['min_cgpa'],
                    max_backlogs=template['max_backlogs'],
                    allowed_branches=template['allowed_branches'],
                    is_approved=is_approved
                )
                
                self.stats['jobs'] += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {self.stats["jobs"]} job postings'))

    @transaction.atomic
    def seed_applications(self):
        """Create applications"""
        self.stdout.write("\n[5/9] Creating applications...")
        
        students = StudentProfile.objects.all()
        approved_jobs = JobPosting.objects.filter(is_approved=True)
        
        status_choices = ['Applied', 'Shortlisted', 'Rejected', 'Interview', 'Offered']
        status_weights = [0.4, 0.25, 0.2, 0.1, 0.05]
        
        for student in students:
            # 8-10 applications per student
            num_applications = random.randint(8, 10)
            
            # Find eligible jobs
            eligible_jobs = []
            for job in approved_jobs:
                if self.is_student_eligible(student, job):
                    eligible_jobs.append(job)
            
            if not eligible_jobs:
                continue
            
            # Sample random jobs
            jobs_to_apply = random.sample(eligible_jobs, min(num_applications, len(eligible_jobs)))
            
            has_offer = False
            for job in jobs_to_apply:
                # Select status
                if student.is_placed and not has_offer and random.random() < 0.5:
                    status = 'Offered'
                    has_offer = True
                else:
                    status = random.choices(status_choices, weights=status_weights)[0]
                
                # Application date before deadline
                days_before = random.randint(5, 60)
                applied_date = job.application_deadline - timedelta(days=days_before)
                
                app = Application.objects.create(
                    job=job,
                    student=student,
                    status=status
                )
                # Manually set applied_at
                app.applied_at = datetime.combine(applied_date, datetime.min.time())
                app.save()
                
                self.stats['applications'] += 1
            
            # Ensure placed students have at least one offer
            if student.is_placed and not has_offer and jobs_to_apply:
                app = Application.objects.filter(student=student).first()
                if app:
                    app.status = 'Offered'
                    app.save()
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {self.stats["applications"]} applications'))

    def is_student_eligible(self, student, job):
        """Check if student is eligible for job"""
        if student.cgpa < job.min_cgpa:
            return False
        if student.backlogs > job.max_backlogs:
            return False
        
        allowed_branches = [b.strip() for b in job.allowed_branches.split(',')]
        branch_short = BRANCH_SHORT.get(student.branch, '')
        
        if branch_short not in allowed_branches:
            return False
        
        return True

    @transaction.atomic
    def seed_interviews(self):
        """Create interview schedules"""
        self.stdout.write("\n[6/9] Creating interview schedules...")
        
        eligible_apps = Application.objects.filter(status__in=['Shortlisted', 'Interview'])
        
        round_names = ['Technical Round 1', 'Technical Round 2', 'HR Round', 'Managerial Round']
        modes = ['Online', 'In-Person']
        time_slots = [time(9, 0), time(10, 0), time(11, 0), time(14, 0), time(15, 0), time(16, 0), time(17, 0)]
        
        online_links = [
            'https://meet.google.com/abc-defg-hij',
            'https://zoom.us/j/123456789',
            'https://teams.microsoft.com/l/meetup-join/xyz'
        ]
        
        venues = [
            'Google Office, Block A, 4th Floor, RMZ Infinity, Bangalore',
            'Microsoft Building, Gachibowli, Hyderabad',
            'Company Headquarters, Cyber City, Gurgaon',
            'Office Campus, Whitefield, Bangalore',
            'Tech Park, HITEC City, Hyderabad'
        ]
        
        instructions = [
            'Please join 5 minutes before the scheduled time.',
            'Bring your resume, ID card, and all academic certificates.',
            'The interview will be approximately 45-60 minutes long.',
            'Prepare for coding questions on data structures and algorithms.',
            'Be ready to discuss your projects and technical skills.'
        ]
        
        for app in eligible_apps:
            # 1-2 rounds per application
            num_rounds = random.randint(1, 2)
            
            for i in range(num_rounds):
                # Interview date between application and deadline
                days_after = random.randint(7, 30)
                interview_date = app.applied_at.date() + timedelta(days=days_after)
                
                if interview_date >= app.job.application_deadline:
                    interview_date = app.job.application_deadline - timedelta(days=random.randint(1, 5))
                
                mode = random.choices(modes, weights=[0.7, 0.3])[0]
                venue_or_link = random.choice(online_links) if mode == 'Online' else random.choice(venues)
                
                InterviewSchedule.objects.create(
                    application=app,
                    interview_date=interview_date,
                    interview_time=random.choice(time_slots),
                    round_name=random.choice(round_names),
                    mode=mode,
                    venue_or_link=venue_or_link,
                    additional_instructions=random.choice(instructions)
                )
                
                self.stats['interviews'] += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {self.stats["interviews"]} interview schedules'))

    @transaction.atomic
    def seed_documents(self):
        """Create admin documents"""
        self.stdout.write("\n[7/9] Creating documents...")
        
        docs = [
            ('Resume Template for Students', 'Use this template to create your professional resume.'),
            ('Placement Guidelines 2025-26', 'Important guidelines for the placement process.'),
            ('Interview Preparation Guide', 'Tips and tricks to ace your interviews.'),
            ('Company Research Checklist', 'How to research companies before applying.'),
            ('Sample Cover Letter Template', 'Template for writing effective cover letters.'),
            ('FAQs for Placement Process', 'Frequently asked questions answered.'),
            ('Dress Code for Interviews', 'Professional attire guidelines.')
        ]
        
        for title, content in docs:
            doc_buffer = self.generate_document_pdf(title, content)
            filename = f"{title.lower().replace(' ', '_')}.pdf"
            
            doc = Document.objects.create(title=title)
            doc.file.save(filename, ContentFile(doc_buffer.read()), save=True)
            
            self.stats['documents'] += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {self.stats["documents"]} documents'))

    def generate_document_pdf(self, title, content):
        """Generate a simple PDF document"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, 10.5*inch, title)
        
        c.setFont("Helvetica", 11)
        y_position = 10*inch
        for line in content.split('\n'):
            c.drawString(1*inch, y_position, line[:80])
            y_position -= 0.2*inch
        
        c.save()
        buffer.seek(0)
        return buffer

    @transaction.atomic
    def seed_audit_logs(self):
        """Create audit logs"""
        self.stdout.write("\n[8/9] Creating audit logs...")
        
        # Log student registrations
        for student_cred in self.credentials['students'][:10]:  # Sample
            user = User.objects.filter(username=student_cred['username']).first()
            if user:
                AuditLog.objects.create(
                    user=user,
                    action=f"Student {student_cred['username']} registered"
                )
                self.stats['audit_logs'] += 1
        
        # Log company registrations
        for company_cred in self.credentials['companies'][:5]:  # Sample
            user = User.objects.filter(username=company_cred['username']).first()
            if user:
                AuditLog.objects.create(
                    user=user,
                    action=f"Company {company_cred['company']} registered"
                )
                self.stats['audit_logs'] += 1
        
        # Log job postings
        jobs = JobPosting.objects.all()[:10]
        for job in jobs:
            AuditLog.objects.create(
                user=job.company.user,
                action=f"Posted job: {job.title}"
            )
            self.stats['audit_logs'] += 1
        
        # Log some applications
        apps = Application.objects.all()[:20]
        for app in apps:
            AuditLog.objects.create(
                user=app.student.user,
                action=f"Applied for {app.job.title} at {app.job.company.name}"
            )
            self.stats['audit_logs'] += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {self.stats["audit_logs"]} audit logs'))

    def generate_credentials_file(self):
        """Generate credentials.md file"""
        self.stdout.write("\n[9/9] Generating credentials file...")
        
        filepath = 'credentials.md'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Placement Management System - Login Credentials\n\n")
            f.write(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # Admin credentials
            f.write("## Admin Accounts\n\n")
            for admin in self.credentials['admins']:
                f.write(f"### {admin['role']}\n")
                f.write(f"- **Username:** {admin['username']}\n")
                f.write(f"- **Password:** {admin['password']}\n")
                f.write(f"- **Email:** {admin['email']}\n")
                f.write(f"- **Name:** {admin['name']}\n\n")
            
            # Student credentials
            f.write("## Student Accounts (50 total)\n\n")
            f.write("| Username | Email | Branch | CGPA | Placed |\n")
            f.write("|----------|-------|--------|------|--------|\n")
            for student in self.credentials['students']:
                f.write(f"| {student['username']} | {student['email']} | {student['branch']} | {student['cgpa']} | {student['placed']} |\n")
            
            f.write("\n**Note:** All students use password: `student123`\n\n")
            
            # Company credentials
            f.write("## Company Accounts (20 total)\n\n")
            f.write("| Username | Email | Company Name | Approved |\n")
            f.write("|----------|-------|--------------|----------|\n")
            for company in self.credentials['companies']:
                f.write(f"| {company['username']} | {company['email']} | {company['company']} | {company['approved']} |\n")
            
            f.write("\n**Note:** All companies use password: `company123`\n\n")
            
            # Quick links
            f.write("---\n\n")
            f.write("## Quick Login Links\n\n")
            f.write("- **Admin Panel:** http://localhost:8000/admin/\n")
            f.write("- **Student Login:** http://localhost:8000/login/\n")
            f.write("- **Company Login:** http://localhost:8000/login/\n\n")
            
            # Statistics
            f.write("---\n\n")
            f.write("## Database Statistics\n\n")
            f.write(f"- **Total Users:** {self.stats['users']}\n")
            f.write(f"- **Students:** {self.stats['students']}\n")
            f.write(f"- **Companies:** {self.stats['companies']}\n")
            f.write(f"- **Job Postings:** {self.stats['jobs']}\n")
            f.write(f"- **Applications:** {self.stats['applications']}\n")
            f.write(f"- **Interview Schedules:** {self.stats['interviews']}\n")
            f.write(f"- **Documents:** {self.stats['documents']}\n")
            f.write(f"- **Audit Logs:** {self.stats['audit_logs']}\n\n")
            
            # Test scenarios
            f.write("---\n\n")
            f.write("## Test Scenarios\n\n")
            
            placed_student = next((s for s in self.credentials['students'] if s['placed'] == 'Yes'), None)
            if placed_student:
                f.write(f"### Scenario 1: Student with Placement\n")
                f.write(f"- Login as: `{placed_student['username']}` / `student123`\n")
                f.write(f"- Has: Complete profile, multiple applications, placed status\n\n")
            
            high_cgpa = next((s for s in self.credentials['students'] if s['cgpa'] >= 9.0), None)
            if high_cgpa:
                f.write(f"### Scenario 2: High CGPA Student\n")
                f.write(f"- Login as: `{high_cgpa['username']}` / `student123`\n")
                f.write(f"- Has: CGPA {high_cgpa['cgpa']}, excellent profile\n\n")
            
            approved_company = next((c for c in self.credentials['companies'] if c['approved'] == 'Yes'), None)
            if approved_company:
                f.write(f"### Scenario 3: Company with Active Jobs\n")
                f.write(f"- Login as: `{approved_company['username']}` / `company123`\n")
                f.write(f"- Has: Approved status, job postings, applicants\n\n")
            
            f.write("### Scenario 4: Admin Testing\n")
            f.write("- Login as: `admin` / `admin123`\n")
            f.write("- Action: Approve pending companies and jobs\n\n")
            
            f.write("---\n\n")
            f.write("*This file is auto-generated. Do not edit manually.*\n")
        
        self.stdout.write(self.style.SUCCESS(f'✓ Generated credentials.md'))

    def print_summary(self):
        """Print seeding summary"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("SEEDING COMPLETED SUCCESSFULLY!"))
        self.stdout.write("=" * 50)
        
        self.stdout.write("\nStatistics:")
        self.stdout.write("-" * 50)
        self.stdout.write(f"Users: {self.stats['users']} (2 admins, {self.stats['students']} students, {self.stats['companies']} companies)")
        self.stdout.write(f"Job Postings: {self.stats['jobs']}")
        self.stdout.write(f"Applications: {self.stats['applications']}")
        self.stdout.write(f"Interview Schedules: {self.stats['interviews']}")
        self.stdout.write(f"Documents: {self.stats['documents']}")
        self.stdout.write(f"Audit Logs: {self.stats['audit_logs']}")
        
        self.stdout.write("\nFiles Generated:")
        self.stdout.write("-" * 50)
        self.stdout.write(f"- Resumes: {self.stats['students']} PDFs in media/resumes/")
        self.stdout.write(f"- Logos: {self.stats['companies']} PNGs in media/company_logos/")
        self.stdout.write(f"- Documents: {self.stats['documents']} PDFs in media/documents/")
        self.stdout.write("- Credentials: credentials.md")
        
        self.stdout.write("\nNext Steps:")
        self.stdout.write("-" * 50)
        self.stdout.write("1. Review credentials.md for login details")
        self.stdout.write("2. Run: python manage.py runserver")
        self.stdout.write("3. Login as admin: admin / admin123")
        self.stdout.write("4. Test student flow: [see credentials.md]")
        self.stdout.write("5. Test company flow: [see credentials.md]")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Happy Testing!")
        self.stdout.write("=" * 50 + "\n")
