import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_allowance_rule(client, db_session: AsyncSession):
    """Test creating an allowance rule for a child."""
    # Register and login to get token
    unique_email = f"test_{hash('test_create_allowance_rule') % 10000}@example.com"
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": unique_email, "password": "testpassword123"},
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": "testpassword123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create a child first
    child_response = client.post(
        "/api/v1/children/",
        json={"name": "Test Child", "birthdate": "2015-01-01"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert child_response.status_code == 200
    child_data = child_response.json()
    child_id = child_data["id"]

    # Create allowance rule
    allowance_data = {"base_amount_cents": 1000, "frequency": "weekly", "pay_day": "friday", "active": True}  # $10.00

    response = client.post(
        f"/api/v1/children/{child_id}/allowance-rules",
        json=allowance_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["base_amount_cents"] == 1000
    assert data["frequency"] == "weekly"
    assert data["pay_day"] == "friday"
    assert data["child_id"] == child_id


@pytest.mark.asyncio
async def test_create_chore(client, db_session: AsyncSession):
    """Test creating a chore for a child."""
    # Register and login to get token
    unique_email = f"test_{hash('test_create_chore') % 10000}@example.com"
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": unique_email, "password": "testpassword123"},
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": "testpassword123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create a child first
    child_response = client.post(
        "/api/v1/children/",
        json={"name": "Test Child", "birthdate": "2015-01-01"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert child_response.status_code == 200
    child_data = child_response.json()
    child_id = child_data["id"]

    # Create chore
    chore_data = {
        "name": "Clean Room",
        "description": "Clean and organize bedroom",
        "expected_per_week": 3,
        "penalty_cents": 100,  # $1.00 penalty
        "active": True,
    }

    response = client.post(
        f"/api/v1/children/{child_id}/chores", json=chore_data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Clean Room"
    assert data["expected_per_week"] == 3
    assert data["penalty_cents"] == 100
    assert data["child_id"] == child_id


@pytest.mark.asyncio
async def test_complete_chore(client, db_session: AsyncSession):
    """Test marking a chore as completed."""
    # Register and login to get token
    unique_email = f"test_{hash('test_complete_chore') % 10000}@example.com"
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": unique_email, "password": "testpassword123"},
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": "testpassword123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create a child first
    child_response = client.post(
        "/api/v1/children/",
        json={"name": "Test Child", "birthdate": "2015-01-01"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert child_response.status_code == 200
    child_data = child_response.json()
    child_id = child_data["id"]

    # Create chore
    chore_data = {
        "name": "Clean Room",
        "description": "Clean and organize bedroom",
        "expected_per_week": 3,
        "penalty_cents": 100,
    }

    chore_response = client.post(
        f"/api/v1/children/{child_id}/chores", json=chore_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert chore_response.status_code == 200
    chore_data_response = chore_response.json()
    chore_id = chore_data_response["id"]

    # Complete the chore
    completion_data = {"notes": "Room cleaned thoroughly"}

    response = client.post(
        f"/api/v1/chores/{chore_id}/complete", json=completion_data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["chore_id"] == chore_id
    assert data["notes"] == "Room cleaned thoroughly"
    assert data["verified_by"] is not None


@pytest.mark.asyncio
async def test_get_chore_summary(client, db_session: AsyncSession):
    """Test getting a summary of chores and completions for a child."""
    # Register and login to get token
    unique_email = f"test_{hash('test_get_chore_summary') % 10000}@example.com"
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": unique_email, "password": "testpassword123"},
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": "testpassword123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create a child first
    child_response = client.post(
        "/api/v1/children/",
        json={"name": "Test Child", "birthdate": "2015-01-01"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert child_response.status_code == 200
    child_data = child_response.json()
    child_id = child_data["id"]

    # Create chore
    chore_data = {
        "name": "Clean Room",
        "description": "Clean and organize bedroom",
        "expected_per_week": 3,
        "penalty_cents": 100,
    }

    chore_response = client.post(
        f"/api/v1/children/{child_id}/chores", json=chore_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert chore_response.status_code == 200
    chore_data_response = chore_response.json()
    chore_id = chore_data_response["id"]

    # Complete the chore twice this week
    for i in range(2):
        completion_data = {"notes": f"Completion {i+1}"}
        completion_response = client.post(
            f"/api/v1/chores/{chore_id}/complete", json=completion_data, headers={"Authorization": f"Bearer {token}"}
        )
        assert completion_response.status_code == 200

    # Get chore summary
    response = client.get(f"/api/v1/children/{child_id}/chore-summary", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["child_id"] == child_id
    assert len(data["chores"]) == 1

    chore_summary = data["chores"][0]
    assert chore_summary["name"] == "Clean Room"
    assert chore_summary["expected_per_week"] == 3
    assert chore_summary["completed_this_week"] == 2
    assert chore_summary["missed_this_week"] == 1
    assert chore_summary["penalty_cents"] == 100  # 1 missed * 100 cents


@pytest.mark.asyncio
async def test_allowance_payout(client, db_session: AsyncSession):
    """Test processing allowance payout for a child."""
    # Register and login to get token
    unique_email = f"test_{hash('test_allowance_payout') % 10000}@example.com"
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": unique_email, "password": "testpassword123"},
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": "testpassword123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create a child first
    child_response = client.post(
        "/api/v1/children/",
        json={"name": "Test Child", "birthdate": "2015-01-01"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert child_response.status_code == 200
    child_data = child_response.json()
    child_id = child_data["id"]

    # Create allowance rule
    allowance_data = {
        "base_amount_cents": 1000,  # $10.00 weekly allowance
        "frequency": "weekly",
        "pay_day": "friday",
        "active": True,
    }

    allowance_response = client.post(
        f"/api/v1/children/{child_id}/allowance-rules",
        json=allowance_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert allowance_response.status_code == 200

    # Process allowance payout
    response = client.post(
        f"/api/v1/children/{child_id}/allowance-payout", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["amount_cents"] == 1000
    assert "transaction_id" in data


@pytest.mark.asyncio
async def test_allowance_rule_ownership_validation(client, db_session: AsyncSession):
    """Test that users can only access allowance rules for their own children."""
    # Create two users
    unique_email1 = f"user1_{hash('test_ownership') % 10000}@example.com"
    unique_email2 = f"user2_{hash('test_ownership') % 10000}@example.com"

    # Register user1
    register_response1 = client.post(
        "/api/v1/auth/register",
        json={"email": unique_email1, "password": "testpassword123"},
    )
    assert register_response1.status_code == 200

    login_response1 = client.post(
        "/api/v1/auth/login",
        json={"email": unique_email1, "password": "testpassword123"},
    )
    assert login_response1.status_code == 200
    token1 = login_response1.json()["access_token"]

    # Register user2
    register_response2 = client.post(
        "/api/v1/auth/register",
        json={"email": unique_email2, "password": "testpassword123"},
    )
    assert register_response2.status_code == 200

    login_response2 = client.post(
        "/api/v1/auth/login",
        json={"email": unique_email2, "password": "testpassword123"},
    )
    assert login_response2.status_code == 200
    token2 = login_response2.json()["access_token"]

    # Create child for user1
    child_response = client.post(
        "/api/v1/children/",
        json={"name": "Test Child", "birthdate": "2015-01-01"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert child_response.status_code == 200
    child_data = child_response.json()
    child_id = child_data["id"]

    # Try to create allowance rule as user2
    allowance_data = {"base_amount_cents": 1000, "frequency": "weekly", "pay_day": "friday"}

    response = client.post(
        f"/api/v1/children/{child_id}/allowance-rules",
        json=allowance_data,
        headers={"Authorization": f"Bearer {token2}"},  # Wrong user
    )

    assert response.status_code == 404  # Child not found for this user
