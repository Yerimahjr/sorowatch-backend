"""
Builds and (optionally) submits the on-chain flag_anomaly call using the
real Stellar Python SDK. Building the transaction is fully real and
tested; actual network submission is exercised only when a responder
secret key is configured, since it requires a funded, authorized account.
"""
from stellar_sdk import Keypair, TransactionBuilder, Network, scval
from stellar_sdk.soroban_server import SorobanServer
from stellar_sdk.exceptions import PrepareTransactionException


class FlagSubmissionClient:
    def __init__(
        self,
        rpc_url: str,
        network_passphrase: str,
        contract_id: str,
        responder_secret_key: str | None = None,
    ):
        self.rpc_url = rpc_url
        self.network_passphrase = network_passphrase
        self.contract_id = contract_id
        self.responder_secret_key = responder_secret_key or None

    def is_configured(self) -> bool:
        return bool(self.responder_secret_key)

    def build_flag_transaction(self, subject_address: str, score: int):
        """
        Builds (but does not submit) the flag_anomaly invocation as a
        Soroban transaction. Kept separate from submission so it can be
        unit-tested without a live RPC connection or funded account.
        """
        if not self.responder_secret_key:
            raise ValueError("responder_secret_key is not configured")

        keypair = Keypair.from_secret(self.responder_secret_key)
        server = SorobanServer(self.rpc_url)
        source_account = server.load_account(keypair.public_key)

        tx = (
            TransactionBuilder(
                source_account=source_account,
                network_passphrase=self.network_passphrase,
                base_fee=100,
            )
            .set_timeout(30)
            .append_invoke_contract_function_op(
                contract_id=self.contract_id,
                function_name="flag_anomaly",
                parameters=[
                    scval.to_address(keypair.public_key),
                    scval.to_address(subject_address),
                    scval.to_uint32(score),
                ],
            )
            .build()
        )
        return tx, server, keypair

    def submit_flag(self, subject_address: str, score: int) -> dict:
        """
        Builds, simulates, signs, and submits the flag_anomaly
        transaction. Raises if the responder key isn't configured or the
        simulation fails (e.g. the account isn't actually authorized as a
        Responder on-chain).
        """
        tx, server, keypair = self.build_flag_transaction(subject_address, score)
        try:
            prepared = server.prepare_transaction(tx)
        except PrepareTransactionException as e:
            raise RuntimeError(f"simulation failed: {e}") from e

        prepared.sign(keypair)
        response = server.send_transaction(prepared)
        return {"status": response.status, "hash": response.hash}
