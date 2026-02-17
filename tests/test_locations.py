"""Tests for location management endpoints"""
import pytest
from fastapi import status
from app.models.user import User
from app.models.organization import Organization, Location, LocationType, LocationAsset


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing"""
    user = User(
        email="admin@test.com",
        full_name="Admin User",
        hashed_password="hashed_password",
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
def manager_user(db_session, organization):
    """Create a manager user for testing"""
    user = User(
        email="manager@test.com",
        full_name="Manager User",
        hashed_password="hashed_password",
        role="manager",
        organization_id=organization.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client, manager_user):
    """Create an auth token for the manager user"""
    response = client.post(
        "/auth/login",
        json={"email": "manager@test.com", "password": "password"}
    )
    assert response.status_code == status.HTTP_200_OK
    return response.json()["access_token"]


def test_create_location(client, organization, auth_token):
    """Test creating a new location"""
    response = client.post(
        f"/organizations/{organization.id}/locations",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Main Building",
            "address": "123 Main St",
            "status": "active"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Main Building"
    assert data["address"] == "123 Main St"
    assert data["status"] == "active"
    assert data["is_deleted"] is False


def test_create_location_with_details(client, organization, auth_token):
    """Test creating location with all optional fields"""
    response = client.post(
        f"/organizations/{organization.id}/locations",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Scout HQ",
            "address": "456 Scout Lane",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "status": "active",
            "opening_hours": "Mon-Fri 09:00-17:00; Sat 10:00-14:00",
            "capacity": 100,
            "contact_person": "John Doe",
            "contact_phone": "555-1234",
            "contact_email": "john@example.com"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Scout HQ"
    assert data["latitude"] == 51.5074
    assert data["longitude"] == -0.1278
    assert data["capacity"] == 100
    assert data["contact_person"] == "John Doe"


def test_get_location(client, db_session, organization, auth_token):
    """Test retrieving a location"""
    location = Location(
        organization_id=organization.id,
        name="Test Location",
        address="789 Test Ave"
    )
    db_session.add(location)
    db_session.commit()

    response = client.get(
        f"/organizations/locations/{location.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == location.id
    assert data["name"] == "Test Location"


def test_list_locations(client, db_session, organization, auth_token):
    """Test listing locations for an organization"""
    # Create multiple locations
    for i in range(3):
        location = Location(
            organization_id=organization.id,
            name=f"Location {i+1}",
            address=f"{i+1} Test St"
        )
        db_session.add(location)
    db_session.commit()

    response = client.get(
        f"/organizations/{organization.id}/locations",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3


def test_list_locations_excludes_deleted(client, db_session, organization, auth_token):
    """Test that soft-deleted locations are excluded from listing"""
    # Create two locations
    loc1 = Location(organization_id=organization.id, name="Active", address="1 St")
    loc2 = Location(organization_id=organization.id, name="Deleted", address="2 St", is_deleted=True)
    db_session.add(loc1)
    db_session.add(loc2)
    db_session.commit()

    response = client.get(
        f"/organizations/{organization.id}/locations",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Active"


def test_update_location(client, db_session, organization, auth_token):
    """Test updating a location"""
    location = Location(
        organization_id=organization.id,
        name="Original Name",
        address="Original Address"
    )
    db_session.add(location)
    db_session.commit()

    response = client.patch(
        f"/organizations/locations/{location.id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Updated Name",
            "status": "inactive",
            "capacity": 50
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["status"] == "inactive"
    assert data["capacity"] == 50


def test_delete_location(client, db_session, organization, auth_token):
    """Test soft-deleting a location"""
    location = Location(
        organization_id=organization.id,
        name="To Delete",
        address="Delete Me"
    )
    db_session.add(location)
    db_session.commit()

    response = client.delete(
        f"/organizations/locations/{location.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's soft-deleted by checking the flag
    response = client.get(
        f"/organizations/locations/{location.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    # Location should still be retrievable, but marked as deleted
    data = response.json()
    assert data["is_deleted"] is True


def test_search_locations_by_name(client, db_session, organization, auth_token):
    """Test searching locations by name"""
    loc1 = Location(organization_id=organization.id, name="Scout HQ", address="1 St")
    loc2 = Location(organization_id=organization.id, name="Church Hall", address="2 St")
    db_session.add(loc1)
    db_session.add(loc2)
    db_session.commit()

    response = client.get(
        "/organizations/locations/search?q=Scout",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Scout HQ"


def test_search_locations_by_address(client, db_session, organization, auth_token):
    """Test searching locations by address"""
    loc1 = Location(organization_id=organization.id, name="Location A", address="123 Main St")
    loc2 = Location(organization_id=organization.id, name="Location B", address="456 Oak Ave")
    db_session.add(loc1)
    db_session.add(loc2)
    db_session.commit()

    response = client.get(
        "/organizations/locations/search?q=Main",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["address"] == "123 Main St"


def test_filter_locations_by_status(client, db_session, organization, auth_token):
    """Test filtering locations by status"""
    loc1 = Location(organization_id=organization.id, name="Active", address="1 St", status="active")
    loc2 = Location(organization_id=organization.id, name="Inactive", address="2 St", status="inactive")
    db_session.add(loc1)
    db_session.add(loc2)
    db_session.commit()

    response = client.get(
        "/organizations/locations/search?status_filter=active",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "active"


def test_add_asset_to_location(client, db_session, organization, auth_token):
    """Test adding an asset to a location"""
    location = Location(organization_id=organization.id, name="Location", address="St")
    asset_type = LocationType(
        name="Scout HQ",
        description="Scout HQ",
        template="## Area: Test\n- Task 1"
    )
    db_session.add(location)
    db_session.add(asset_type)
    db_session.commit()

    response = client.post(
        f"/organizations/locations/{location.id}/assets/{asset_type.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_get_location_assets(client, db_session, organization, auth_token):
    """Test getting assets for a location"""
    location = Location(organization_id=organization.id, name="Location", address="St")
    asset_type = LocationType(
        name="Scout HQ",
        description="Scout HQ",
        template="## Area: Test\n- Task 1"
    )
    db_session.add(location)
    db_session.add(asset_type)
    db_session.commit()

    # Add asset
    asset = LocationAsset(location_id=location.id, asset_type_id=asset_type.id)
    db_session.add(asset)
    db_session.commit()

    response = client.get(
        f"/organizations/locations/{location.id}/assets",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1


def test_remove_asset_from_location(client, db_session, organization, auth_token):
    """Test removing an asset from a location"""
    location = Location(organization_id=organization.id, name="Location", address="St")
    asset_type = LocationType(
        name="Scout HQ",
        description="Scout HQ",
        template="## Area: Test\n- Task 1"
    )
    db_session.add(location)
    db_session.add(asset_type)
    db_session.commit()

    asset = LocationAsset(location_id=location.id, asset_type_id=asset_type.id)
    db_session.add(asset)
    db_session.commit()

    response = client.delete(
        f"/organizations/locations/{location.id}/assets/{asset.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
