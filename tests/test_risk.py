import pytest
import respx
from httpx import Response

from app.clients.ai_agent import AiAgentClient
from app.clients.flag_submission import FlagSubmissionClient


@pytest.mark.asyncio
@respx.mock
async def test_ai_agent_client_returns_score():
    respx.post("http://localhost:8001/score").mock(
        return_value=Response(
            200, json={"address": "GABC", "score": 75, "flagged": True}
        )
    )
    client = AiAgentClient("http://localhost:8001")
    result = await client.score_address("GABC", threshold=50)
    assert result["score"] == 75
    assert result["flagged"] is True


def test_flag_submission_client_reports_not_configured():
    client = FlagSubmissionClient(
        rpc_url="https://soroban-testnet.stellar.org",
        network_passphrase="Test SDF Network ; September 2015",
        contract_id="CABC",
        responder_secret_key=None,
    )
    assert client.is_configured() is False


def test_flag_submission_client_raises_when_building_without_key():
    client = FlagSubmissionClient(
        rpc_url="https://soroban-testnet.stellar.org",
        network_passphrase="Test SDF Network ; September 2015",
        contract_id="CABC",
        responder_secret_key=None,
    )
    with pytest.raises(ValueError):
        client.build_flag_transaction("GSUBJECT", 80)
