from store_sms.models import SubscriberUpdate, choose_message


def test_ready_asset_uses_ready_template_and_title_variable():
    result = choose_message(SubscriberUpdate("creator-7", "+15550001", "Summer pack", "ready"))
    assert result.template_id == "creator_asset_ready_v1"
    assert result.template_vars == {"asset_title": "Summer pack"}
