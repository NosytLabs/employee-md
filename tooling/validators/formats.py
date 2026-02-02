"""Format validation (dates, URLs, wallets, emails)."""

from typing import Any, Dict
from .base import BaseValidator, ValidationResult
from ..utils import validate_iso_date, validate_url, validate_wallet


class FormatValidator(BaseValidator):
    """Validates field formats."""

    def validate(self, config: Dict[str, Any]) -> ValidationResult:
        self.reset()

        if "identity" in config:
            identity = config["identity"]

            if "wallet" in identity and identity["wallet"]:
                if not validate_wallet(identity["wallet"]):
                    self.add_error(
                        field="identity.wallet", message="Invalid wallet address format"
                    )

            if "created_at" in identity and identity["created_at"]:
                if not validate_iso_date(identity["created_at"]):
                    self.add_error(
                        field="identity.created_at",
                        message="Invalid created_at format (must be ISO 8601)",
                    )

            if "updated_at" in identity and identity["updated_at"]:
                if not validate_iso_date(identity["updated_at"]):
                    self.add_error(
                        field="identity.updated_at",
                        message="Invalid updated_at format (must be ISO 8601)",
                    )

        if "lifecycle" in config:
            lifecycle = config["lifecycle"]
            date_fields = ["start_date", "end_date", "probation_end", "next_review"]

            for field in date_fields:
                if field in lifecycle and lifecycle[field]:
                    if not validate_iso_date(lifecycle[field]):
                        self.add_error(
                            field=f"lifecycle.{field}",
                            message=f"Invalid lifecycle.{field} format (must be ISO 8601)",
                        )

        if "knowledge_base" in config:
            kb = config["knowledge_base"]

            if "documentation_urls" in kb:
                for i, url in enumerate(kb["documentation_urls"]):
                    if not validate_url(url):
                        self.add_error(
                            field=f"knowledge_base.documentation_urls[{i}]",
                            message=f"Invalid URL: {url}",
                        )

        if "spec" in config:
            spec = config["spec"]

            if "schema" in spec and spec["schema"]:
                if not validate_url(spec["schema"]):
                    self.add_error(
                        field="spec.schema",
                        message="Invalid spec.schema format (must be URL)",
                    )

            if "homepage" in spec and spec["homepage"]:
                if not validate_url(spec["homepage"]):
                    self.add_error(
                        field="spec.homepage",
                        message="Invalid spec.homepage format (must be URL)",
                    )

        if "economy" in config:
            economy = config["economy"]

            if "wallets" in economy and isinstance(economy["wallets"], dict):
                for wallet_type, wallet in economy["wallets"].items():
                    if wallet and not validate_wallet(wallet):
                        self.add_error(
                            field=f"economy.wallets.{wallet_type}",
                            message=f"Invalid wallet address format in economy.wallets.{wallet_type}",
                        )

        if "protocols" in config:
            protocols = config["protocols"]

            if "x402" in protocols and isinstance(protocols["x402"], dict):
                wallet = protocols["x402"].get("wallet_address")
                if wallet and not validate_wallet(wallet):
                    self.add_error(
                        field="protocols.x402.wallet_address",
                        message="Invalid wallet address format in protocols.x402.wallet_address",
                    )

        return self._create_result()
