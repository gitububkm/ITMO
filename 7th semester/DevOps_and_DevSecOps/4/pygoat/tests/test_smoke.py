"""Smoke tests for the CI `test` stage.

They check that the application works (pages render, users can register and
log in), not that the labs are vulnerable, so fixing a finding must not break them.
"""

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

LAB_PAGES = [
    "/",
    "/xss",
    "/sql",
    "/sql_lab",
    "/insec_des",
    "/xxe",
    "/auth",
    "/ba",
    "/data_exp",
    "/cmd",
    "/cmd_lab",
    "/bau",
]

# Upstream templates reference static files that do not exist (e.g. css/dark-theme.css).
# The app runs with DEBUG=True, where that is harmless, but the test runner forces
# DEBUG=False and the manifest storage then raises, so tests use plain storage.
SmokeTestCase = override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)(TestCase)


class AnonymousAccessTests(SmokeTestCase):
    def test_login_page_renders(self):
        self.assertEqual(self.client.get("/login/").status_code, 200)

    def test_register_page_renders(self):
        self.assertEqual(self.client.get("/register").status_code, 200)

    def test_home_redirects_anonymous_to_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response["Location"])


class AuthFlowTests(SmokeTestCase):
    def test_register_creates_user_who_can_log_in(self):
        # Upstream shadows django.contrib.auth.login with a model import
        # (introduction/views.py), so registration does not start a session.
        response = self.client.post(
            "/register",
            {
                "username": "student",
                "email": "student@example.com",
                "password1": "Sm0ke-Test-Passw0rd",
                "password2": "Sm0ke-Test-Passw0rd",
            },
        )
        self.assertRedirects(response, "/", fetch_redirect_response=False)
        self.assertTrue(User.objects.filter(username="student").exists())
        self.assertTrue(
            self.client.login(username="student", password="Sm0ke-Test-Passw0rd")
        )
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_login_with_valid_credentials(self):
        User.objects.create_user("alice", "alice@example.com", "Sm0ke-Test-Passw0rd")
        response = self.client.post(
            "/login/", {"username": "alice", "password": "Sm0ke-Test-Passw0rd"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get("/").status_code, 200)


class LabPagesTests(SmokeTestCase):
    def setUp(self):
        user = User.objects.create_user("bob", "bob@example.com", "Sm0ke-Test-Passw0rd")
        self.client.force_login(user)

    def test_lab_pages_render_for_logged_in_user(self):
        for url in LAB_PAGES:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
