import pytest
import respx
from httpx import Response

from app.clients.soroban_rpc import SorobanRpcClient


@pytest.mark.asyncio
@respx.mock
async def test_get_events_returns_parsed_events():
    rpc_url = "https://soroban-testnet.stellar.org"
    respx.post(rpc_url).mock(
        return_value=Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "events": [
                        {"contractId": "CABC", "topic": ["flagged"], "value": "80"}
                    ]
                },
            },
        )
    )

    client = SorobanRpcClient(rpc_url)
    events = await client.get_events(contract_id="CABC", start_ledger=1, topic_filter="flagged")
    assert len(events) == 1
    assert events[0]["contractId"] == "CABC"


@pytest.mark.asyncio
@respx.mock
async def test_get_events_returns_empty_list_on_rpc_error():
    rpc_url = "https://soroban-testnet.stellar.org"
    respx.post(rpc_url).mock(
        return_value=Response(
            200,
            json={"jsonrpc": "2.0", "id": 1, "error": {"code": -1, "message": "contract not found"}},
        )
    )

    client = SorobanRpcClient(rpc_url)
    events = await client.get_events(contract_id="UNKNOWN", start_ledger=1)
    assert events == []
