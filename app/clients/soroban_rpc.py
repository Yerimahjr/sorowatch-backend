"""
Client for the Soroban RPC JSON-RPC API, used to read 'flagged' events
emitted by the sorowatch-contract. Reading events doesn't require signing,
unlike submitting a transaction, so this is fully functional without any
key configuration.
"""
import httpx


class SorobanRpcClient:
    def __init__(self, rpc_url: str, timeout: float = 10.0):
        self.rpc_url = rpc_url
        self.timeout = timeout

    async def get_events(
        self, contract_id: str, start_ledger: int, topic_filter: str | None = None, limit: int = 50
    ) -> list[dict]:
        """
        Calls Soroban RPC's getEvents method, filtered to the given
        contract, from start_ledger onward. Returns the raw event list
        (empty if none found or the contract has no events yet).
        """
        filters = [{"type": "contract", "contractIds": [contract_id]}]
        if topic_filter:
            filters[0]["topics"] = [[topic_filter]]

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getEvents",
            "params": {
                "startLedger": start_ledger,
                "filters": filters,
                "pagination": {"limit": limit},
            },
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.rpc_url, json=payload)
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                return []
            return data.get("result", {}).get("events", [])
