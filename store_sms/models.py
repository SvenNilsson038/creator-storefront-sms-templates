from dataclasses import dataclass


@dataclass(frozen=True)
class SubscriberUpdate:
    creator_id: str
    phone: str
    asset_title: str
    processing_state: str


@dataclass(frozen=True)
class ApprovedMessage:
    template_id: str
    template_vars: dict[str, str]


def choose_message(update: SubscriberUpdate) -> ApprovedMessage:
    """Choose copy only after the digital asset has finished processing."""
    if update.processing_state == "ready":
        return ApprovedMessage("creator_asset_ready_v1", {"asset_title": update.asset_title})
    return ApprovedMessage("creator_asset_processing_v1", {"asset_title": update.asset_title})
