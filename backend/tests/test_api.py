import os
import uuid

import pytest
from httpx import AsyncClient

# Skip all tests in CI/CD environment since they require a running backend server
pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true", reason="Skipping integration tests in CI/CD - requires running backend server"
)


def get_unique_email():
    """Generate a unique email address for testing"""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


@pytest.mark.asyncio
async def test_register_user():
    """Test user registration"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # Use unique email to avoid conflicts
        unique_email = get_unique_email()
        response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_user_duplicate_email():
    """Test user registration with duplicate email"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # First register a user
        unique_email = get_unique_email()
        response1 = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert response1.status_code == 200

        # Try to register again with same email
        response2 = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "differentpassword"},
        )
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_register_user_invalid_email():
    """Test user registration with invalid email"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = await ac.post(
            "/api/v1/auth/register",
            json={"email": "invalid-email", "password": "testpassword123"},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_user():
    """Test user login"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # First register a user, then login
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        # Now login with the same credentials
        response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "testpassword123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_user_wrong_password():
    """Test user login with wrong password"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # First register a user
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        # Try to login with wrong password
        response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_user_nonexistent():
    """Test user login with nonexistent email"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = await ac.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "testpassword123"},
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_protected_endpoint_without_token():
    """Test that protected endpoints return 401 without token"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = await ac.get("/api/v1/children/")
        # The endpoint returns 403 Forbidden instead of 401 Unauthorized
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_token():
    """Test that protected endpoints return 401 with invalid token"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = await ac.get("/api/v1/children/", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_child_with_auth():
    """Test creating a child with authentication"""
    # First register and login to get token
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        login_response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # Create child with token
        response = await ac.post(
            "/api/v1/children/",
            json={"name": "Test Child", "birthdate": "2015-01-01"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Test Child"
        assert len(data["accounts"]) == 2
        assert any(acc["account_type"] == "checking" for acc in data["accounts"])
        assert any(acc["account_type"] == "savings" for acc in data["accounts"])
        assert all(acc["balance_cents"] == "0" for acc in data["accounts"])  # balance_cents is returned as string


@pytest.mark.asyncio
async def test_create_child_invalid_data():
    """Test creating a child with invalid data"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # First register and login to get token
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        login_response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # Try to create child with missing name
        response = await ac.post(
            "/api/v1/children/",
            json={"birthdate": "2015-01-01"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_children():
    """Test listing children"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # First register and login to get token
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        login_response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # List children (should be empty initially)
        response = await ac.get("/api/v1/children/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


@pytest.mark.asyncio
async def test_transaction_pagination():
    """Test transaction pagination with cursor"""
    # First register and login to get token
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        login_response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # First create a child to get account IDs
        child_response = await ac.post(
            "/api/v1/children/",
            json={"name": "Test Child", "birthdate": "2015-01-01"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert child_response.status_code == 200
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use the first account

        # Get transactions with pagination
        response = await ac.get(
            f"/api/v1/accounts/{account_id}/transactions?limit=10",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert "next_cursor" in data
        assert "has_more" in data
        assert isinstance(data["transactions"], list)
        assert len(data["transactions"]) <= 10


@pytest.mark.asyncio
async def test_transaction_pagination_with_cursor():
    """Test transaction pagination with cursor parameter"""
    # First register and login to get token
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        login_response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # First create a child to get account IDs
        child_response = await ac.post(
            "/api/v1/children/",
            json={"name": "Test Child", "birthdate": "2015-01-01"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert child_response.status_code == 200
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use the first account

        # Get transactions with cursor
        response = await ac.get(
            f"/api/v1/accounts/{account_id}/transactions?limit=5&cursor=invalid_cursor",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should handle invalid cursor gracefully
        assert response.status_code == 400
        assert "Invalid cursor" in response.json()["detail"]


@pytest.mark.asyncio
async def test_deposit_with_idempotency():
    """Test deposit with idempotency key"""
    # First register and login to get token
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        login_response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # First create a child to get account IDs
        child_response = await ac.post(
            "/api/v1/children/",
            json={"name": "Test Child", "birthdate": "2015-01-01"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert child_response.status_code == 200
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use the first account

        # Create deposit with idempotency key
        idempotency_key = f"test_key_{uuid.uuid4().hex[:8]}"
        response = await ac.post(
            f"/api/v1/accounts/{account_id}/deposit",
            json={"amount_cents": 1000, "idempotency_key": idempotency_key},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "transaction" in data
        assert data["transaction"]["amount_cents"] == "1000"  # amount_cents is returned as string
        assert data["transaction"]["idempotency_key"] == idempotency_key


@pytest.mark.asyncio
async def test_deposit_amount_validation():
    """Test deposit amount validation"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # First register and login to get token
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        login_response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # First create a child to get account IDs
        child_response = await ac.post(
            "/api/v1/children/",
            json={"name": "Test Child", "birthdate": "2015-01-01"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert child_response.status_code == 200
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use the first account

        # Try to deposit 0 cents (below minimum)
        response = await ac.post(
            f"/api/v1/accounts/{account_id}/deposit",
            json={
                "amount_cents": 0,
                "idempotency_key": f"test_key_{uuid.uuid4().hex[:8]}",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
        assert "Amount must be at least" in response.json()["detail"]


@pytest.mark.asyncio
async def test_deposit_duplicate_idempotency():
    """Test deposit with duplicate idempotency key returns existing transaction"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # First register and login to get token
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        login_response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # First create a child to get account IDs
        child_response = await ac.post(
            "/api/v1/children/",
            json={"name": "Test Child", "birthdate": "2015-01-01"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert child_response.status_code == 200
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use the first account

        # Create first deposit
        idempotency_key = f"test_key_{uuid.uuid4().hex[:8]}"
        response1 = await ac.post(
            f"/api/v1/accounts/{account_id}/deposit",
            json={"amount_cents": 1000, "idempotency_key": idempotency_key},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response1.status_code == 200

        # Try to deposit again with same idempotency key
        response2 = await ac.post(
            f"/api/v1/accounts/{account_id}/deposit",
            json={"amount_cents": 1000, "idempotency_key": idempotency_key},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response2.status_code == 200

        # Should return same transaction
        data1 = response1.json()
        data2 = response2.json()
        assert data1["transaction"]["id"] == data2["transaction"]["id"]
        assert data1["transaction"]["amount_cents"] == data2["transaction"]["amount_cents"]


@pytest.mark.asyncio
async def test_deposit_invalid_account():
    """Test deposit with invalid account ID"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # First register and login to get token
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        login_response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # Try to deposit to non-existent account
        response = await ac.post(
            "/api/v1/accounts/99999/deposit",
            json={
                "amount_cents": 1000,
                "idempotency_key": f"test_key_{uuid.uuid4().hex[:8]}",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
        assert "Account not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_deposit_unauthorized_account():
    """Test deposit to account that doesn't belong to current user"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # First register and login to get token
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        login_response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # Create a child to get an account
        child_response = await ac.post(
            "/api/v1/children/",
            json={"name": "Test Child", "birthdate": "2015-01-01"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert child_response.status_code == 200
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]

        # Create another user and try to access the first user's account
        unique_email2 = get_unique_email()
        register_response2 = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email2, "password": "testpassword123"},
        )
        assert register_response2.status_code == 200

        login_response2 = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email2, "password": "testpassword123"},
        )
        token2 = login_response2.json()["access_token"]

        # Try to deposit to first user's account with second user's token
        response = await ac.post(
            f"/api/v1/accounts/{account_id}/deposit",
            json={
                "amount_cents": 1000,
                "idempotency_key": f"test_key_{uuid.uuid4().hex[:8]}",
            },
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == 404
        assert "Account not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_transactions_invalid_account():
    """Test getting transactions from invalid account ID"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # First register and login to get token
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        login_response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # Try to get transactions from non-existent account
        response = await ac.get(
            "/api/v1/accounts/99999/transactions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
        assert "Account not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_transactions_unauthorized_account():
    """Test getting transactions from account that doesn't belong to current user"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # First register and login to get token
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        login_response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # Create a child to get an account
        child_response = await ac.post(
            "/api/v1/children/",
            json={"name": "Test Child", "birthdate": "2015-01-01"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert child_response.status_code == 200
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]

        # Create another user and try to access the first user's account
        unique_email2 = get_unique_email()
        register_response2 = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email2, "password": "testpassword123"},
        )
        assert register_response2.status_code == 200

        login_response2 = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email2, "password": "testpassword123"},
        )
        token2 = login_response2.json()["access_token"]

        # Try to get transactions from first user's account with second user's token
        response = await ac.get(
            f"/api/v1/accounts/{account_id}/transactions",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == 404
        assert "Account not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_deposit_max_amount_exceeded():
    """Test deposit with amount exceeding maximum limit"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # First register and login to get token
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        login_response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # First create a child to get account IDs
        child_response = await ac.post(
            "/api/v1/children/",
            json={"name": "Test Child", "birthdate": "2015-01-01"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert child_response.status_code == 200
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use the first account

        # Try to deposit amount exceeding maximum (1000001 cents = $10,000.01)
        response = await ac.post(
            f"/api/v1/accounts/{account_id}/deposit",
            json={
                "amount_cents": 1000001,
                "idempotency_key": f"test_key_{uuid.uuid4().hex[:8]}",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
        assert "Amount cannot exceed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_transactions_with_valid_cursor():
    """Test transaction pagination with valid cursor"""
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # First register and login to get token
        unique_email = get_unique_email()
        register_response = await ac.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "password": "testpassword123"},
        )
        assert register_response.status_code == 200

        login_response = await ac.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # First create a child to get account IDs
        child_response = await ac.post(
            "/api/v1/children/",
            json={"name": "Test Child", "birthdate": "2015-01-01"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert child_response.status_code == 200
        child_data = child_response.json()
        account_id = child_data["accounts"][0]["id"]  # Use the first account

        # Make a deposit to create a transaction
        response = await ac.post(
            f"/api/v1/accounts/{account_id}/deposit",
            json={
                "amount_cents": 1000,
                "idempotency_key": f"test_key_{uuid.uuid4().hex[:8]}",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        # Get transactions with limit 1 to test pagination
        response = await ac.get(
            f"/api/v1/accounts/{account_id}/transactions?limit=1",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["transactions"]) == 1
        assert data["has_more"] is False  # Should be false since we only have 1 transaction

        # Test with cursor if available
        if data["next_cursor"]:
            response2 = await ac.get(
                f"/api/v1/accounts/{account_id}/transactions?limit=1&cursor={data['next_cursor']}",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response2.status_code == 200
