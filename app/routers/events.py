from fastapi import APIRouter, Query
from app.config import get_settings
from app.clients.soroban_rpc import SorobanRpcClient

router = APIRouter()


@router.get("/")
async def list_events(start_ledger: int = Query(default=1, ge=1)):
    """
    Return 'flagged' events emitted by the sorowatch-contract, read live
    from Soroban RPC. Returns an empty list (not an error) if the
    contract ID isn't configured yet or has no events.
    """
    settings = get_settings()
    if not settings.contract_id:
        return {"events": [], "note": "CONTRACT_ID not configured"}

    client = SorobanRpcClient(settings.soroban_rpc_url)
    events = await client.get_events(
        contract_id=settings.contract_id,
        start_ledger=start_ledger,
        topic_filter="flagged",
    )
    return {"events": events}
