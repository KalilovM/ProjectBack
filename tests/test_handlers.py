import json
from uuid import uuid4

import pytest


@pytest.mark.asyncio(scope="function")
async def test_create_user(client, get_user_from_database):
    user_data = {
        "username": "Oxygen",
        "email": "oxygen@gmail.com",
        "password": "oxygen0123",
    }
    resp = client.post("/users/", data=json.dumps(user_data))
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["username"] == user_data["username"]
    assert data_from_resp["email"] == user_data["email"]
    # TODO: add assert for password (hashing)
    assert data_from_resp["password"] == user_data["password"]
    assert data_from_resp["is_active"] is True
    users_from_db = await get_user_from_database(data_from_resp["user_id"])
    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert user_from_db["username"] == user_data["username"]
    assert user_from_db["email"] == user_data["email"]
    # TODO: add assert for password (hashing)
    assert user_from_db["password"] == user_data["password"]
    assert user_from_db["is_active"] is True
    assert str(user_from_db["user_id"]) == data_from_resp["user_id"]


async def test_delete_user(client, create_user_in_db, get_user_from_database):
    user_data = {
        "user_id": uuid4(),
        "username": "Oxygen",
        "email": "oxygen@gmail.com",
        "password": "oxygen0123",
        "is_active": True,
    }
    await create_user_in_db(**user_data)
    resp = client.delete(f"/users/{user_data['user_id']}")
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp == {"user_id": str(user_data["user_id"])}
    users_from_db = await get_user_from_database(user_data["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["username"] == user_data["username"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["password"] == user_data["password"]
    assert user_from_db["user_id"] == user_data["user_id"]
    assert user_from_db["is_active"] is False


async def test_get_user(client, create_user_in_db):
    user_data = {
        "user_id": uuid4(),
        "username": "Oxygen",
        "email": "oxygen@gmail.com",
        "password": "oxygen0123",
        "is_active": True,
    }
    await create_user_in_db(**user_data)
    resp = client.get(f"/users/{user_data['user_id']}")
    user_from_resp = resp.json()
    assert resp.status_code == 200
    assert user_from_resp["username"] == user_data["username"]
    assert user_from_resp["email"] == user_data["email"]
    assert user_from_resp["password"] == user_data["password"]
    assert user_from_resp["user_id"] == str(user_data["user_id"])
    assert user_from_resp["is_active"] is True


async def test_update_user(client, create_user_in_db, get_user_from_database):
    user_data = {
        "user_id": uuid4(),
        "username": "Oxygen",
        "email": "oxygen@gmail.com",
        "password": "oxygen0123",
        "is_active": True,
    }
    user_data_updated = {
        "username": "Houmie",
        "email": "houmie@gmail.com",
    }

    await create_user_in_db(**user_data)
    resp = client.patch(
        f"/users/{user_data['user_id']}", data=json.dumps(user_data_updated)
    )
    assert resp.status_code == 200
    user_resp = resp.json()
    users_from_db = await get_user_from_database(user_id=user_resp["user_id"])
    updated_user = dict(users_from_db[0])
    assert updated_user["username"] == user_data_updated["username"]
    assert updated_user["email"] == user_data_updated["email"]
    assert updated_user["user_id"] == user_data["user_id"]
    assert updated_user["password"] == user_data["password"]
    assert updated_user["is_active"] == user_data["is_active"]
