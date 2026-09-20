from fastapi import APIRouter
from pydantic import BaseModel

from app.config import get_settings
from app.clients.ai_agent import AiAgentClient
from app.clients.flag_submission import FlagSubmissionClient

router = APIRouter()


class ScoreRequest(BaseModel):
    address: str
    threshold: int = 50
    submit_on_chain_if_flagged: bool = False


@router.post("/score")
async def score_address(req: ScoreRequest):
    """
    Calls the ai-agent service to score an address. If
    submit_on_chain_if_flagged is true and the address is flagged and a
    responder key is configured, also submits the flag_anomaly
    transaction on-chain.
    """
    settings = get_settings()
    agent_client = AiAgentClient(settings.ai_agent_url)
    result = await agent_client.score_address(req.address, req.threshold)

    submission_result = None
    if req.submit_on_chain_if_flagged and result.get("flagged"):
        flag_client = FlagSubmissionClient(
            rpc_url=settings.soroban_rpc_url,
            network_passphrase=settings.network_passphrase,
            contract_id=settings.contract_id,
            responder_secret_key=settings.responder_secret_key,
        )
        if flag_client.is_configured():
            submission_result = flag_client.submit_flag(req.address, result["score"])
        else:
            submission_result = {"error": "responder_secret_key not configured"}

    return {**result, "on_chain_submission": submission_result}
