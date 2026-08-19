from __future__ import annotations


def install() -> None:
    from . import ai_providers
    from . import phase49_diagnostics as diagnostics

    client_class = ai_providers.AIProviderClient
    if not getattr(client_class, "_phase49_3b_model_normalizer", False):
        original_choose = client_class.choose_model

        def choose_model(self, preferred: str = "") -> str:
            value = (preferred or self.model or "").strip()
            if " • " in value:
                value = value.split(" • ", 1)[0].strip()
            return original_choose(self, value)

        client_class.choose_model = choose_model
        client_class._phase49_3b_model_normalizer = True

    if not getattr(diagnostics, "_phase49_3b_cost_wrapper", False):
        original_event = diagnostics.ai_request_event

        def ai_request_event(*args, **kwargs):
            cost_usd = kwargs.get("cost_usd")
            cost_irt = kwargs.get("cost_irt")
            if cost_irt is None and cost_usd is not None and getattr(diagnostics, "_DB", None) is not None:
                try:
                    rate = float(str(diagnostics._DB.setting("ai_usd_to_toman", "") or "0").replace(",", ""))
                    if rate > 0:
                        kwargs["cost_irt"] = float(cost_usd) * rate
                        if not kwargs.get("cost_source"):
                            kwargs["cost_source"] = "usd_rate_estimate"
                except Exception:
                    pass
            return original_event(*args, **kwargs)

        diagnostics.ai_request_event = ai_request_event
        ai_providers.ai_request_event = ai_request_event
        diagnostics._phase49_3b_cost_wrapper = True
