import grpc
import pytest

import gRPC.src.users_service_pb2 as pb
import gRPC.src.users_service_pb2_grpc as grpc_pb

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
    "email, expected",
    [
        ("hello@example.com", does_not_raise()),
        ("fail@exampl.com", pytest.raises(grpc.aio.AioRpcError))
    ]
)
async def test_users_grpc_server_test(email, expected):
    with expected:
        channel = grpc.aio.insecure_channel("localhost:50052")
        stub = grpc_pb.UserServiceStub(channel)
        resp = await stub.GetUserByEmail(pb.GetUserByEmailRequest(email=email))
        assert isinstance(resp, pb.GetUserByEmailResponse)

