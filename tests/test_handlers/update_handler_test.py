from __future__ import annotations

import json
import logging
from uuid import uuid4

import pytest


logger = logging.getLogger(__name__)


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
        f"/users/{user_data['user_id']}",
        data=json.dumps(user_data_updated),
    )
    assert resp.status_code == 200
    user_resp = resp.json()
    users_from_db = await get_user_from_database(user_id=user_resp["user_id"])
    updated_user = dict(users_from_db[0])
    assert updated_user["username"] == user_data_updated["username"]
    assert updated_user["email"] == user_data_updated["email"]
    assert updated_user["user_id"] == user_data["user_id"]
    assert updated_user["password"] == user_data["password"]
    assert updated_user["is_active"] is user_data["is_active"]


async def test_update_user_check_one_is_updated(
    client,
    create_user_in_db,
    get_user_from_database,
):
    user_data_1 = {
        "user_id": uuid4(),
        "username": "Oxygen",
        "email": "oxygen@gmail.com",
        "password": "oxygen0123",
        "is_active": True,
    }
    user_data_2 = {
        "user_id": uuid4(),
        "username": "Houmie",
        "email": "houmie@gmail.com",
        "password": "houmie0123",
        "is_active": True,
    }

    user_data_3 = {
        "user_id": uuid4(),
        "username": "Alex",
        "email": "alex@gmail.com",
        "password": "alex0123",
        "is_active": True,
    }
    user_data_updated = {"username": "Steve", "email": "steve@gmail.com"}
    for user_data in [user_data_1, user_data_2, user_data_3]:
        await create_user_in_db(**user_data)
    resp = client.patch(
        f"/users/{user_data_1['user_id']}/",
        data=json.dumps(user_data_updated),
    )
    assert resp.status_code == 200
    user_resp = resp.json()
    assert user_resp["user_id"] == str(user_data_1["user_id"])
    users_from_db = await get_user_from_database(user_id=user_resp["user_id"])
    updated_user = dict(users_from_db[0])
    assert updated_user["username"] == user_data_updated["username"]
    assert updated_user["email"] == user_data_updated["email"]
    assert updated_user["user_id"] == user_data_1["user_id"]
    assert updated_user["password"] == user_data_1["password"]
    assert updated_user["is_active"] is user_data_1["is_active"]

    # check other users that data has not been updated
    users_from_db = await get_user_from_database(user_data_2["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["username"] == user_data_2["username"]
    assert user_from_db["email"] == user_data_2["email"]
    assert user_from_db["password"] == user_data_2["password"]
    assert user_from_db["is_active"] is user_data_2["is_active"]
    assert user_from_db["user_id"] == user_data_2["user_id"]

    users_from_db = await get_user_from_database(user_data_3["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["username"] == user_data_3["username"]
    assert user_from_db["email"] == user_data_3["email"]
    assert user_from_db["password"] == user_data_3["password"]
    assert user_from_db["is_active"] is user_data_3["is_active"]
    assert user_from_db["user_id"] == user_data_3["user_id"]


@pytest.mark.parametrize(
    "user_data_updated, expected_status_code, expected_detail",
    [
        (
            {},
            422,
            {
                "detail": "At least one parameter for user update info should be provided",
            },
        ),
        ({"username": "123"}, 422, {"detail": "Username should contains only letters"}),
        (
            {"email": "123"},
            422,
            {
                "detail": [
                    {
                        "type": "value_error",
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address: The email address is not valid. It must have exactly one @-sign.",
                        "input": "123",
                        "ctx": {
                            "reason": "The email address is not valid. It must have exactly one @-sign.",
                        },
                    },
                ],
            },
        ),
        (
            {"username": ""},
            422,
            {
                "detail": [
                    {
                        "ctx": {"min_length": 1},
                        "input": "",
                        "loc": ["body", "username"],
                        "msg": "String should have at least 1 character",
                        "type": "string_too_short",
                    },
                ],
            },
        ),
        (
            {"email": ""},
            422,
            {
                "detail": [
                    {
                        "type": "value_error",
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address: The email address is not valid. It must have exactly one @-sign.",
                        "input": "",
                        "ctx": {
                            "reason": "The email address is not valid. It must have exactly one @-sign.",
                        },
                    },
                ],
            },
        ),
    ],
)
async def test_update_user_validation_error(
    client,
    create_user_in_db,
    get_user_from_database,
    user_data_updated,
    expected_status_code,
    expected_detail,
):
    user_data = {
        "user_id": uuid4(),
        "username": "Oxygen",
        "email": "oxygen@gmail.com",
        "password": "oxygen0123",
        "is_active": True,
    }
    await create_user_in_db(**user_data)
    user_updating_debug = user_data_updated
    logger.debug(f"updating_data: {user_updating_debug}")
    resp = client.patch(
        f"/users/{user_data['user_id']}",
        data=json.dumps(user_data_updated),
    )
    assert resp.status_code == expected_status_code
    resp_data = resp.json()
    assert resp_data == expected_detail


async def test_update_user_not_found_error(client):
    user_data_updated = {
        "username": "Oxygen",
        "email": "oxygen@gmail.com",
        "password": "oxygen0123",
        "is_active": True,
    }
    user_id = uuid4()

    resp = client.patch(f"/users/{user_id}", data=json.dumps(user_data_updated))
    assert resp.status_code == 404
    resp_data = resp.json()
    assert resp_data == {"detail": f"User with id {user_id} not found."}


async def test_update_user_duplicate_email_error(client, create_user_in_db):
    user_data_1 = {
        "user_id": uuid4(),
        "username": "Oxygen",
        "email": "oxygen@gmail.com",
        "password": "oxygen0123",
        "is_active": True,
    }
    user_data_2 = {
        "user_id": uuid4(),
        "username": "Houmie",
        "email": "houmie@gmail.com",
        "password": "houmie0123",
        "is_active": True,
    }

    user_data_updated = {"email": user_data_2["email"]}
    for user_data in [user_data_1, user_data_2]:
        await create_user_in_db(**user_data)
    resp = client.patch(
        f"/users/{user_data_1['user_id']}",
        data=json.dumps(user_data_updated),
    )
    assert resp.status_code == 503
    resp_data = resp.json()
    assert (
        'duplicate key value violates unique constraint "users_email_key"'
        in resp_data["detail"]
    )
