import json


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


async def test_create_user_duplicate_email_error(client, get_user_from_database):
    user_data = {
        "username": "Oxygen",
        "email": "oxygen@gmail.com",
        "password": "oxygen0123",
    }
    user_data_same_email = {
        "username": "Houmie",
        "email": "oxygen@gmail.com",
        "password": "oxygen0123",
    }

    resp = client.post("/users/", data=json.dumps(user_data))
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["username"] == user_data["username"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["password"] == user_data["password"]
    assert data_from_resp["is_active"] is True

    users_from_db = await get_user_from_database(data_from_resp["user_id"])
    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert user_from_db["username"] == user_data["username"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["password"] == user_data["password"]
    assert user_from_db["is_active"] is True
    assert str(user_from_db["user_id"]) == data_from_resp["user_id"]
    resp = client.post("/users/", data=json.dumps(user_data_same_email))
    assert resp.status_code == 503
    assert (
        'duplicate key value violates unique constraint "users_email_key"'
        in resp.json()["detail"]
    )
