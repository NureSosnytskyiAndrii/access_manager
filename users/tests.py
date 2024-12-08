import time
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse
from .models import User, Role, BlockchainBlock


class UserRegistrationTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_users_url = reverse("list_users")
        self.register_url = "/register/"

        self.admin_role = Role.objects.create(name="admin", permissions={"can_edit": True, "can_register": True})
        self.user_role = Role.objects.create(name="user", permissions={"can_register": True})

        self.admin_user = User.objects.create_user(
            username="admin",
            password="admin_password",
            role=self.admin_role,
            access_level=10
        )

        self.admin_token = Token.objects.create(user=self.admin_user).key
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")

        BlockchainBlock.create_genesis_block()

    def perform_test(self, test_type, additional_params=None):

        start_time = time.time()

        if test_type == "registration_success":
            user_data = {
                "username": "test_user",
                "password": "test_password",
                "first_name": "Test",
                "last_name": "User",
                "email": "testuser@example.com",
                "role_id": self.user_role.id,
                "access_level": 1,
            }
            response = self.client.post(self.register_url, user_data, format="json")

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertIn("message", response.data)
            self.assertEqual(response.data["message"], "User registered successfully")

            user = User.objects.get(username="test_user")
            self.assertEqual(user.email, "testuser@example.com")

            last_block = BlockchainBlock.get_last_block()
            self.assertEqual(last_block.data["username"], "test_user")

        elif test_type == "invalid_role":
            invalid_user_data = {
                "username": "invalid_user",
                "password": "invalid_password",
                "first_name": "Invalid",
                "last_name": "User",
                "email": "invaliduser@example.com",
                "role_id": 999,
                "access_level": 1,
            }
            response = self.client.post(self.register_url, invalid_user_data, format="json")

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)
            self.assertEqual(response.data["error"], "Role does not exist")

        elif test_type == "performance":
            max_time = 1.0
            response = self.client.get(self.list_users_url)
            execution_time = time.time() - start_time

            self.assertEqual(response.status_code, 200)

            self.assertLessEqual(execution_time, max_time, f"Query exceeded time limit: {execution_time:.2f}s")
            print(f"Performance Test: Query completed in {execution_time:.2f} seconds")

        elif test_type == "many_users_performance":
            num_users = additional_params.get("num_users", 100)
            for i in range(num_users):
                User.objects.create_user(
                    username=f"user_{i}",
                    password="password",
                    role=self.user_role,
                    access_level=1
                )

            response = self.client.get(self.list_users_url)
            execution_time = time.time() - start_time
            self.assertEqual(response.status_code, 200)
            print(f"Performance with {num_users} users: Query completed in {execution_time:.2f} seconds")

        elif test_type == "unauthorized_access":
            self.client.credentials()
            response = self.client.get(self.list_users_url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertIn("detail", response.data)
            self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")

        execution_time = time.time() - start_time
        print(f"Test '{test_type}' completed in {execution_time:.2f} seconds")

    def test_registration_success(self):
        self.perform_test("registration_success")

    def test_registration_invalid_role(self):
        self.perform_test("invalid_role")

    def test_list_users_performance(self):
        self.perform_test("performance")

    def test_many_users_performance(self):
        self.perform_test("many_users_performance", additional_params={"num_users": 100})

    def test_unauthorized_access(self):
        self.perform_test("unauthorized_access")
