from django.test import TestCase, Client
from django.urls import reverse
from core.models import User, StudentProfile

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='student', 
            email='student@example.com', 
            password='password123',
            role='student'
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            branch='Computer Science',
            cgpa=9.0
        )

    def test_home_page(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_login_redirect(self):
        # A logged-in student should be redirected from home to student dashboard
        self.client.login(username='student', password='password123')
        response = self.client.get(reverse('core:home'))
        self.assertRedirects(response, reverse('core:student_dashboard'))
    
    def test_protected_view(self):
        # Accessing dashboard without login should redirect to login page
        response = self.client.get(reverse('core:student_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))
