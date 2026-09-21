from django.test import TestCase
from core.models import User, StudentProfile, CompanyProfile, JobPosting

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='password123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('password123'))

class StudentProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student', 
            email='student@example.com', 
            password='password123',
            role='student'
        )
    
    def test_student_profile_creation(self):
        profile = StudentProfile.objects.create(
            user=self.user,
            branch='Computer Science',
            cgpa=9.0
        )
        self.assertEqual(profile.user.username, 'student')
        self.assertEqual(profile.branch, 'Computer Science')
        self.assertEqual(profile.cgpa, 9.0)

class CompanyProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='company', 
            email='company@example.com', 
            password='password123',
            role='company'
        )
    
    def test_company_profile_creation(self):
        profile = CompanyProfile.objects.create(
            user=self.user,
            name='Tech Corp',
            description='A tech company'
        )
        self.assertEqual(profile.name, 'Tech Corp')
        self.assertEqual(profile.user.role, 'company')
