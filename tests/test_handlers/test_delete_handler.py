from uuid import uuid4


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


async def test_delete_user_not_found(client):
    user_id = uuid4()
    resp = client.delete(f"/users/{user_id}/")
    assert resp.status_code == 404
    assert resp.json() == {"detail": f"User with id {user_id} not found."}


async def test_delete_user_id_validation_error(client):
    user_id = 123
    resp = client.delete(f"/users/{user_id}/")
    assert resp.status_code == 422
    data_from_resp = resp.json()
    assert data_from_resp == {
        "detail": [
            {
                "type": "uuid_parsing",
                "loc": ["path", "user_id"],
                "msg": "Input should be a valid UUID, invalid length: expected length 32 for simple format, found 3",
                "input": "123",
                "ctx": {
                    "error": "invalid length: expected length 32 for simple format, found 3"
                },
            }
        ]
    }
