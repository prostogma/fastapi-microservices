import grpc
import pytest

import gRPC.src.users_service_pb2 as pb
import gRPC.src.users_service_pb2_grpc as grpc_pb

from unittest.mock import AsyncMock, patch
from contextlib import nullcontext as does_not_raise

from app.core.security import hash_secret, verify_secret

@pytest.mark.parametrize(
    "secret",
    [
        "example_password",
        "example_token",
        "asdlkjrq;w",
        "(!*&@#(*!@&))"
    ]
)
def test_hash_secret(secret: str):
    hashed = hash_secret(secret)
    assert isinstance(hashed, str)
    assert hashed != secret
    assert verify_secret(secret, hashed) is True

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email, expected, response_data",
    [
        ("hello@example.com", does_not_raise(), pb.GetUserByEmailResponse(id="1", is_active=True, is_verified=False)),
        ("not_found@example.com", pytest.raises(grpc.aio.AioRpcError), None)
    ]
)
async def test_get_user_by_email_grpc(email, expected, response_data):
    with patch("gRPC.src.users_service_pb2_grpc.UserServiceStub") as MockStub:
        stub_instance = MockStub.return_value
        stub_instance.GetUserByEmail = AsyncMock()

        if response_data is not None:
            stub_instance.GetUserByEmail.return_value = response_data
        else:
            error = grpc.aio.AioRpcError(
                code=grpc.StatusCode.NOT_FOUND,
                details="User not found",
                initial_metadata=(),
                trailing_metadata=(),
            )
            stub_instance.GetUserByEmail.side_effect = error

        with expected:
            resp = await stub_instance.GetUserByEmail(pb.GetUserByEmailRequest(email=email))

            assert isinstance(resp.id, str)
            assert resp.id == response_data.id
            assert resp.is_active is response_data.is_active
            assert resp.is_verified is response_data.is_verified
