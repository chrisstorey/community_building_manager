"""Tests for asset type management endpoints"""
import pytest
from fastapi import status
from app.models.user import User
from app.models.organization import Organization, LocationType
from app.core.security import get_password_hash


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing"""
    user = User(
        email="admin@test.com",
        full_name="Admin User",
        hashed_password=get_password_hash("password"),
        role="admin",
        organization_id=1
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def organization(db_session):
    """Create an organization for testing"""
    org = Organization(
        name="Test Organization",
        address="123 Test St"
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def auth_token(client, admin_user):
    """Create an auth token for the admin user"""
    response = client.post(
        "/auth/login",
        json={"email": "admin@test.com", "password": "password"}
    )
    assert response.status_code == status.HTTP_200_OK
    return response.json()["access_token"]


def test_create_asset_type(client, auth_token):
    """Test creating a new asset type"""
    response = client.post(
        "/asset-types",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Scout HQ",
            "description": "Scout headquarters building",
            "template": "## Area: Roof\n- Check for leaks\n\n## Area: HVAC\n- Replace filters"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Scout HQ"
    assert data["description"] == "Scout headquarters building"
    assert "## Area: Roof" in data["template"]


def test_create_asset_type_duplicate_name(client, db_session, auth_token):
    """Test that duplicate asset type names are rejected"""
    # Create first asset type
    asset = LocationType(
        name="Scout HQ",
        description="Test",
        template="## Test\n- Task"
    )
    db_session.add(asset)
    db_session.commit()

    # Try to create another with same name
    response = client.post(
        "/asset-types",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Scout HQ",
            "description": "Different",
            "template": "## Different\n- Task"
        }
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_get_asset_type(client, db_session, auth_token):
    """Test retrieving an asset type"""
    asset = LocationType(
        name="Church",
        description="Church building",
        template="## Area: Altar\n- Clean"
    )
    db_session.add(asset)
    db_session.commit()

    response = client.get(
        f"/asset-types/{asset.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Church"
    assert data["description"] == "Church building"


def test_list_asset_types(client, db_session, auth_token):
    """Test listing all asset types"""
    # Create multiple asset types
    for i, name in enumerate(["Scout HQ", "Church", "Church Hall"]):
        asset = LocationType(
            name=name,
            description=f"{name} description",
            template=f"## Area: {name}\n- Task"
        )
        db_session.add(asset)
    db_session.commit()

    response = client.get(
        "/asset-types",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Scout HQ"
    assert data[1]["name"] == "Church"
    assert data[2]["name"] == "Church Hall"


def test_list_asset_types_pagination(client, db_session, auth_token):
    """Test pagination of asset types"""
    # Create 5 asset types
    for i in range(5):
        asset = LocationType(
            name=f"Asset {i+1}",
            description=f"Description {i+1}",
            template=f"## Area: {i+1}\n- Task"
        )
        db_session.add(asset)
    db_session.commit()

    response = client.get(
        "/asset-types?skip=0&limit=2",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2


def test_initialize_default_asset_types(client, auth_token):
    """Test initializing default scout asset types"""
    response = client.post(
        "/asset-types/initialize-defaults",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    # Should have 4 default asset types
    assert len(data) == 4

    # Check for specific asset types
    names = [asset["name"] for asset in data]
    assert "Scout HQ" in names
    assert "Church" in names
    assert "Church Hall" in names
    assert "Scout Activity Centre" in names


def test_initialize_default_asset_types_idempotent(client, auth_token):
    """Test that initializing defaults is idempotent"""
    # First initialization
    response1 = client.post(
        "/asset-types/initialize-defaults",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response1.status_code == status.HTTP_201_CREATED
    count1 = len(response1.json())

    # Second initialization
    response2 = client.post(
        "/asset-types/initialize-defaults",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response2.status_code == status.HTTP_201_CREATED
    count2 = len(response2.json())

    # Should return the same count (no duplicates)
    assert count1 == count2 == 4


def test_scout_hq_template_has_maintenance_areas(client, auth_token):
    """Test that Scout HQ default template has maintenance areas"""
    response = client.post(
        "/asset-types/initialize-defaults",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    scout_hq = next(asset for asset in data if asset["name"] == "Scout HQ")
    template = scout_hq["template"]

    # Check for expected maintenance areas
    assert "## Area: Roof" in template or "## Area:" in template
    assert "- " in template  # Should have tasks listed


def test_church_template_has_maintenance_areas(client, auth_token):
    """Test that Church default template has maintenance areas"""
    response = client.post(
        "/asset-types/initialize-defaults",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    church = next(asset for asset in data if asset["name"] == "Church")
    template = church["template"]

    # Check for expected maintenance areas
    assert "## Area:" in template
    assert "- " in template  # Should have tasks listed


def test_church_hall_template_has_maintenance_areas(client, auth_token):
    """Test that Church Hall default template has maintenance areas"""
    response = client.post(
        "/asset-types/initialize-defaults",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    church_hall = next(asset for asset in data if asset["name"] == "Church Hall")
    template = church_hall["template"]

    # Check for expected maintenance areas
    assert "## Area:" in template
    assert "- " in template  # Should have tasks listed


def test_scout_activity_centre_template_has_maintenance_areas(client, auth_token):
    """Test that Scout Activity Centre default template has maintenance areas"""
    response = client.post(
        "/asset-types/initialize-defaults",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    centre = next(asset for asset in data if asset["name"] == "Scout Activity Centre")
    template = centre["template"]

    # Check for expected maintenance areas
    assert "## Area:" in template
    assert "- " in template  # Should have tasks listed


def test_asset_type_template_markdown_format(client, auth_token):
    """Test creating asset type with proper markdown template"""
    template = """## Area: Roof
- Inspect for leaks
- Check gutters
- Clear debris

## Area: HVAC System
- Change filters
- Service system
- Check thermostat"""

    response = client.post(
        "/asset-types",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Test Building",
            "description": "Test building with multiple areas",
            "template": template
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["template"] == template

    # Verify it has proper structure
    assert data["template"].count("## Area:") == 2
    assert data["template"].count("- ") == 6


def test_get_nonexistent_asset_type(client, auth_token):
    """Test getting a non-existent asset type returns 404"""
    response = client.get(
        "/asset-types/99999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
