"""
Integration tests using TestClient with in-memory database.
These tests can run in CI/CD without external dependencies.
"""

import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.models.account import Account
from app.models.child import Child
from app.models.transaction import Transaction
from app.models.user import User


def get_unique_email() -> str:
    """Generate a unique email address for testing."""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_register_user(self, client: TestClient, db_session):
        """Test user registration."""
        email = get_unique_email()
        user_data = {
            "email": email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == email
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_user_duplicate_email(self, client: TestClient, db_session):
        """Test user registration with duplicate email."""
        email = get_unique_email()
        user_data = {
            "email": email,
            "password": "testpassword123"
        }
        
        # First registration
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        
        # Second registration with same email
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_user_invalid_email(self, client: TestClient, db_session):
        """Test user registration with invalid email."""
        user_data = {
            "email": "invalid-email",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_login_user(self, client: TestClient, db_session):
        """Test user login."""
        email = get_unique_email()
        password = "testpassword123"
        
        # Register user first
        user_data = {"email": email, "password": password}
        client.post("/api/v1/auth/register", json=user_data)
        
        # Login
        login_data = {"email": email, "password": password}
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == email
        assert "access_token" in data

    def test_login_user_wrong_password(self, client: TestClient, db_session):
        """Test user login with wrong password."""
        email = get_unique_email()
        password = "testpassword123"
        
        # Register user first
        user_data = {"email": email, "password": password}
        client.post("/api/v1/auth/register", json=user_data)
        
        # Login with wrong password
        login_data = {"email": email, "password": "wrongpassword"}
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401

    def test_login_user_nonexistent(self, client: TestClient, db_session):
        """Test user login with nonexistent email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401

    def test_protected_endpoint_without_token(self, client: TestClient, db_session):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/v1/children/")
        assert response.status_code == 401

    def test_protected_endpoint_with_invalid_token(self, client: TestClient, db_session):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/children/", headers=headers)
        assert response.status_code == 401


class TestChildEndpoints:
    """Test child management endpoints."""

    def test_create_child_with_auth(self, client: TestClient, db_session):
        """Test creating a child with authentication."""
        # First register and login to get token
        email = get_unique_email()
        user_data = {"email": email, "password": "testpassword123"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create child
        child_data = {
            "name": "Test Child",
            "birthdate": "2015-01-01"
        }
        response = client.post("/api/v1/children/", json=child_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test Child"
        assert data["birthdate"] == "2015-01-01"
        assert len(data["accounts"]) == 2  # checking and savings
        assert any(acc["account_type"] == "checking" for acc in data["accounts"])
        assert any(acc["account_type"] == "savings" for acc in data["accounts"])

    def test_create_child_invalid_data(self, client: TestClient, db_session):
        """Test creating a child with invalid data."""
        # First register and login to get token
        email = get_unique_email()
        user_data = {"email": email, "password": "testpassword123"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create child with invalid data
        child_data = {
            "name": "",  # Empty name
            "birthdate": "2015-01-01"
        }
        response = client.post("/api/v1/children/", json=child_data, headers=headers)
        assert response.status_code == 422

    def test_list_children(self, client: TestClient, db_session):
        """Test listing children."""
        # First register and login to get token
        email = get_unique_email()
        user_data = {"email": email, "password": "testpassword123"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a child first
        child_data = {
            "name": "Test Child",
            "birthdate": "2015-01-01"
        }
        client.post("/api/v1/children/", json=child_data, headers=headers)
        
        # List children
        response = client.get("/api/v1/children/", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Child"


class TestTransactionEndpoints:
    """Test transaction and account endpoints."""

    def test_transaction_pagination(self, client: TestClient, db_session):
        """Test transaction pagination."""
        # First register and login to get token
        email = get_unique_email()
        user_data = {"email": email, "password": "testpassword123"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a child (which creates accounts)
        child_data = {
            "name": "Test Child",
            "birthdate": "2015-01-01"
        }
        child_response = client.post("/api/v1/children/", json=child_data, headers=headers)
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use checking account
        
        # Test pagination
        response = client.get(f"/api/v1/accounts/{account_id}/transactions?limit=10", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "transactions" in data
        assert "next_cursor" in data
        assert "has_more" in data

    def test_transaction_pagination_with_cursor(self, client: TestClient, db_session):
        """Test transaction pagination with cursor."""
        # First register and login to get token
        email = get_unique_email()
        user_data = {"email": email, "password": "testpassword123"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a child (which creates accounts)
        child_data = {
            "name": "Test Child",
            "birthdate": "2015-01-01"
        }
        child_response = client.post("/api/v1/children/", json=child_data, headers=headers)
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use checking account
        
        # Test pagination with cursor
        response = client.get(f"/api/v1/accounts/{account_id}/transactions?limit=5", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        if data["next_cursor"]:
            # Test with cursor
            cursor_response = client.get(
                f"/api/v1/accounts/{account_id}/transactions?limit=5&cursor={data['next_cursor']}", 
                headers=headers
            )
            assert cursor_response.status_code == 200

    def test_deposit_with_idempotency(self, client: TestClient, db_session):
        """Test deposit with idempotency."""
        # First register and login to get token
        email = get_unique_email()
        user_data = {"email": email, "password": "testpassword123"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a child (which creates accounts)
        child_data = {
            "name": "Test Child",
            "birthdate": "2015-01-01"
        }
        child_response = client.post("/api/v1/children/", json=child_data, headers=headers)
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use checking account
        
        # Make deposit
        deposit_data = {
            "amount_cents": 1000,
            "transaction_type": "deposit",
            "idempotency_key": "test_key_123"
        }
        response = client.post(f"/api/v1/accounts/{account_id}/deposit", json=deposit_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["new_balance_cents"] == 1000
        assert data["transaction"]["amount_cents"] == 1000

    def test_deposit_amount_validation(self, client: TestClient, db_session):
        """Test deposit amount validation."""
        # First register and login to get token
        email = get_unique_email()
        user_data = {"email": email, "password": "testpassword123"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a child (which creates accounts)
        child_data = {
            "name": "Test Child",
            "birthdate": "2015-01-01"
        }
        child_response = client.post("/api/v1/children/", json=child_data, headers=headers)
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use checking account
        
        # Test minimum amount
        deposit_data = {
            "amount_cents": 0,  # Below minimum
            "transaction_type": "deposit",
            "idempotency_key": "test_key_min"
        }
        response = client.post(f"/api/v1/accounts/{account_id}/deposit", json=deposit_data, headers=headers)
        assert response.status_code == 400

    def test_deposit_duplicate_idempotency(self, client: TestClient, db_session):
        """Test deposit with duplicate idempotency key."""
        # First register and login to get token
        email = get_unique_email()
        user_data = {"email": email, "password": "testpassword123"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a child (which creates accounts)
        child_data = {
            "name": "Test Child",
            "birthdate": "2015-01-01"
        }
        child_response = client.post("/api/v1/children/", json=child_data, headers=headers)
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use checking account
        
        # Make first deposit
        deposit_data = {
            "amount_cents": 1000,
            "transaction_type": "deposit",
            "idempotency_key": "test_key_dup"
        }
        response1 = client.post(f"/api/v1/accounts/{account_id}/deposit", json=deposit_data, headers=headers)
        assert response1.status_code == 200
        
        # Make second deposit with same idempotency key
        response2 = client.post(f"/api/v1/accounts/{account_id}/deposit", json=deposit_data, headers=headers)
        assert response2.status_code == 200
        
        # Should return same transaction (idempotency)
        data1 = response1.json()
        data2 = response2.json()
        assert data1["transaction"]["id"] == data2["transaction"]["id"]

    def test_deposit_invalid_account(self, client: TestClient, db_session):
        """Test deposit to invalid account."""
        # First register and login to get token
        email = get_unique_email()
        user_data = {"email": email, "password": "testpassword123"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to deposit to non-existent account
        deposit_data = {
            "amount_cents": 1000,
            "transaction_type": "deposit",
            "idempotency_key": "test_key_invalid"
        }
        response = client.post("/api/v1/accounts/99999/deposit", json=deposit_data, headers=headers)
        assert response.status_code == 404

    def test_deposit_unauthorized_account(self, client: TestClient, db_session):
        """Test deposit to unauthorized account."""
        # First register and login to get token
        email = get_unique_email()
        user_data = {"email": email, "password": "testpassword123"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a child (which creates accounts)
        child_data = {
            "name": "Test Child",
            "birthdate": "2015-01-01"
        }
        child_response = client.post("/api/v1/children/", json=child_data, headers=headers)
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use checking account
        
        # Create another user and try to access first user's account
        email2 = get_unique_email()
        user_data2 = {"email": email2, "password": "testpassword123"}
        register_response2 = client.post("/api/v1/auth/register", json=user_data2)
        token2 = register_response2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        deposit_data = {
            "amount_cents": 1000,
            "transaction_type": "deposit",
            "idempotency_key": "test_key_unauthorized"
        }
        response = client.post(f"/api/v1/accounts/{account_id}/deposit", json=deposit_data, headers=headers2)
        assert response.status_code == 404  # Account not found for this user

    def test_transactions_invalid_account(self, client: TestClient, db_session):
        """Test getting transactions for invalid account."""
        # First register and login to get token
        email = get_unique_email()
        user_data = {"email": email, "password": "testpassword123"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to get transactions for non-existent account
        response = client.get("/api/v1/accounts/99999/transactions", headers=headers)
        assert response.status_code == 404

    def test_transactions_unauthorized_account(self, client: TestClient, db_session):
        """Test getting transactions for unauthorized account."""
        # First register and login to get token
        email = get_unique_email()
        user_data = {"email": email, "password": "testpassword123"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a child (which creates accounts)
        child_data = {
            "name": "Test Child",
            "birthdate": "2015-01-01"
        }
        child_response = client.post("/api/v1/children/", json=child_data, headers=headers)
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use checking account
        
        # Create another user and try to access first user's account
        email2 = get_unique_email()
        user_data2 = {"email": email2, "password": "testpassword123"}
        register_response2 = client.post("/api/v1/auth/register", json=user_data2)
        token2 = register_response2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        response = client.get(f"/api/v1/accounts/{account_id}/transactions", headers=headers2)
        assert response.status_code == 404  # Account not found for this user

    def test_deposit_max_amount_exceeded(self, client: TestClient, db_session):
        """Test deposit exceeding maximum amount."""
        # First register and login to get token
        email = get_unique_email()
        user_data = {"email": email, "password": "testpassword123"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a child (which creates accounts)
        child_data = {
            "name": "Test Child",
            "birthdate": "2015-01-01"
        }
        child_response = client.post("/api/v1/children/", json=child_data, headers=headers)
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use checking account
        
        # Test maximum amount (assuming MAX_DEPOSIT_AMOUNT_CENTS is 1000000)
        deposit_data = {
            "amount_cents": 1000001,  # Above maximum
            "transaction_type": "deposit",
            "idempotency_key": "test_key_max"
        }
        response = client.post(f"/api/v1/accounts/{account_id}/deposit", json=deposit_data, headers=headers)
        assert response.status_code == 400

    def test_transactions_with_valid_cursor(self, client: TestClient, db_session):
        """Test transactions with valid cursor pagination."""
        # First register and login to get token
        email = get_unique_email()
        user_data = {"email": email, "password": "testpassword123"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a child (which creates accounts)
        child_data = {
            "name": "Test Child",
            "birthdate": "2015-01-01"
        }
        child_response = client.post("/api/v1/children/", json=child_data, headers=headers)
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use checking account
        
        # Test cursor pagination
        response = client.get(f"/api/v1/accounts/{account_id}/transactions?limit=1", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "transactions" in data
        assert "next_cursor" in data
        assert "has_more" in data
