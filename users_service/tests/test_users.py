import pytest

from app.db.models import User


@pytest.mark.parametrize(
    "params, result_len, expected_status_code",
    [
        ({}, 4, 200),
        ({"limit": 2}, 2, 200),
        ({"offset": 2}, 2, 200),
        ({"limit": 2, "offset": 1}, 2, 200),
        ({"is_verified": True}, 2, 200),
        ({"limit": 10000}, 1, 422),
        ({"offset": -1}, 1, 422),
    ],
)
async def test_get_users_handler(
    params: dict,
    result_len: int,
    expected_status_code: int,
    async_client,
    test_users,
):
    response = await async_client.get("/users/", params=params)
    assert response.status_code == expected_status_code
    if response.status_code == 200:
        data = response.json()
        assert len(data) == result_len

        for user in data:
            assert "email" in user
            assert "is_verified" in user
            assert "is_active" in user


class TestGetUserByEmail:
    async def test_get_user_by_email_handler(self, async_client, test_users):
        for user in test_users:
            params = {"user_email": user.email}
            response = await async_client.get(f"/users/by-email", params=params)
            assert response.status_code == 200
            assert response.json()["email"] == user.email

    @pytest.mark.parametrize(
        "params, status_code",
        (
            [{"email": "example@gmail.com"}, 422],
            [{"user_email": "example_not_found@gmail.com"}, 404],
        ),
    )
    async def test_get_user_by_email_handler_exc(
        self, async_client, test_users: list[User], params: dict, status_code: int
    ):
        response = await async_client.get("/users/by-email", params=params)
        assert response.status_code == status_code


async def test_get_user_by_id_handler(async_client, test_users: list[User]):
    for user in test_users:
        response = await async_client.get(f"/users/{user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(user.id)
        assert "password" not in data

    response = await async_client.get("/users/9af1d544-c43d-4845-ae36-ad331e3a2d31")
    assert response.status_code == 404

class TestCreateUserHandler:
    @pytest.mark.parametrize(
        "user_data, status_code",
        [
            ({"email": "correct@email.com"}, 201),
            ({"email": "correct2@email.com", "is_verified": True}, 201),
            ({"email": "example@email.com", "is_active": True, "is_verified": True}, 201),
            ({"email": "example_email@email.com", "is_active": False}, 201)
        ],
    )
    async def test_create_user_handler(
        self, async_client, user_data: dict, status_code: int
    ):
        response = await async_client.post("/users/", json=user_data)
        assert response.status_code == status_code
        
        data = response.json()
        assert data["email"] == user_data["email"]
        
        if user_data.get("is_active") is not None:
            assert user_data["is_active"] == data["is_active"]
        else:
            assert data["is_active"] == True
                
        if user_data.get("is_verified") is not None:
            assert user_data["is_verified"] == data["is_verified"]
        else:
            assert data["is_verified"] == False
    
    async def test_create_user_duplicate_email(self, async_client):
        r1 = await async_client.post("/users/", json={"email": "duplicate@email.com"})
        assert r1.status_code == 201
        
        r2 = await async_client.post("/users/", json={"email": "duplicate@email.com"})
        assert r2.status_code == 400

async def test_deactivate_user_handler(async_client, test_users: list[User]):
    for user in test_users:
        response = await async_client.patch(f"/users/{user.id}/deactivate")
        assert response.status_code == 200
        
        data = response.json()
        if user.is_active is not False:
            assert data["is_active"] is False
        else:
            assert data["is_active"] is user.is_active

class TestUpdateUserHandler:
    @pytest.mark.parametrize(
        "user_data, status_code",
        [
            ({"email": "new_email@email.com"}, 200),
            ({"email": "new_email@email.com", "is_active": True, "is_verified": True}, 200),
            ({"is_active": True, "is_verified": True}, 200),
            ({}, 200)
        ]
    )
    async def test_update_user_handler(self, user_data: dict, status_code: int, async_client, test_user: User):
        response = await async_client.patch(f"/users/{test_user.id}", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        
        if user_data.get("email") is not None:
            assert user_data["email"] == data["email"]
        
        if user_data.get("is_active") is not None:
            assert user_data["is_active"] == data["is_active"]
        
        if user_data.get("is_verified") is not None:
            assert user_data["is_verified"] == data["is_verified"]

    async def test_update_user_handler_exc(self, async_client, test_user: User):
        
        r1 = await async_client.patch("/users/9af1d544-c43d-4845-ae36-ad331e3a2d31", json={"email": "example@email.com"})
        assert r1.status_code == 404
        
        user_data = {"email": "bad_EMAIL_example.com"}
        
        r2 = await async_client.patch(f"/users/{test_user.id}", json=user_data)
        assert r2.status_code == 422
