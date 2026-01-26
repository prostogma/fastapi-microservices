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
async def test_create_user_handler(
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
            [{"user_email": "example_not_found@gmail.com"}, 404]
        )
    )
    async def test_get_user_by_email_handler_exc(
        self, async_client, test_users: list[User], params: dict[str], status_code: int
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
