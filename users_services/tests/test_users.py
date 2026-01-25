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
            response = await async_client.get(f"/users/by-email?user_email={user.email}")
            assert response.status_code == 200
            assert response.json()["email"] == user.email


    @pytest.mark.parametrize(
        "url, status_code",
        (
            ["/users/by-email?email=example@email.com", 422],
            ["/users/by-email?user_email=example@email.com", 404]
        )
    )
    async def test_get_user_by_email_handler_exc(
        self, async_client, test_users: list[User], url: str, status_code: int
    ):
        response = await async_client.get(url)
        assert response.status_code == status_code
