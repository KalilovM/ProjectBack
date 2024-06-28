from __future__ import annotations

from uuid import uuid4


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


async def test_get_user_id_validation_error(
    client,
    create_user_in_db,
    get_user_from_database,
):
    user_data = {
        "user_id": uuid4(),
        "username": "Oxygen",
        "email": "oxygen@gmail.com",
        "password": "oxygen0123",
        "is_active": True,
    }
    not_valid_uuid = 123
    await create_user_in_db(**user_data)
    resp = client.get(f"/users/{not_valid_uuid}/")
    data_from_resp = resp.json()
    assert resp.status_code == 422
    assert data_from_resp == {
        "detail": [
            {
                "type": "uuid_parsing",
                "loc": ["path", "user_id"],
                "msg": "Input should be a valid UUID, invalid length: expected length 32 for simple format, found 3",
                "input": "123",
                "ctx": {
                    "error": "invalid length: expected length 32 for simple format, found 3",
                },
            },
        ],
    }


async def test_get_user_not_found(client, create_user_in_db, get_user_from_database):
    user_data = {
        "user_id": uuid4(),
        "username": "Oxygen",
        "email": "oxygen@gmail.com",
        "password": "oxygen0123",
        "is_active": True,
    }
    not_existing_uuid = uuid4()
    await create_user_in_db(**user_data)
    resp = client.get(f"/users/{not_existing_uuid}")
    assert resp.status_code == 404
    assert resp.json() == {"detail": f"User with id {not_existing_uuid} not found."}
