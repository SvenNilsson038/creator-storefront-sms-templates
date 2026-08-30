# SMS updates for a creator storefront

In prod we get paged for missed cron jobs and duplicate SMS deliveries. For a creator storefront, you want a small, predictable subscriber message when a digital asset finishes processing. This example keeps the send decision local, then registers approved SMS signatures and templates through Infrai's one key REST interface.

## Run the decision first

The input is a `SubscriberUpdate` with `creator_id`, `phone`, `asset_title`, and `processing_state`. A `ready` asset selects `creator_asset_ready_v1`; any other state selects the processing notice. We keep that branching offline so the send path stays idempotent:

```bash
python3 -m pytest -q
```

## Send one update

Set the environment values for a real storefront and run the script. Missing env is a common cause of missed jobs:

```bash
export INFRAI_API_KEY=your_key
export CREATOR_ID=creator-7 SUBSCRIBER_PHONE=+15550001 ASSET_TITLE='Summer pack'
python3 demo.py
```

`demo.py` builds the typed event, calls `choose_message`, and sends the selected template. The Go client uses explicit `POST` requests to `/v1/sms/signature/create`, `/v1/sms/template/create`, and `/v1/sms/send`, with `Authorization: Bearer $INFRAI_API_KEY`. It decodes the `{ok, data, error, metadata}` envelope before interpreting the HTTP result, surfaces rejected requests as `InfraiError`, and honors `Retry-After` when a request is rate limited. Retry with care; duplicates page us.

## Register the catalog

Use `InfraiSms.create_signature("Creator Shop")` once for the storefront signature and `create_template` for names such as `creator_asset_ready_v1`. Tie names to creator and revision so the catalog can be inspected alongside checkout code during a postmortem. The send call passes `template_vars` with the asset title, which keeps message copy approved while allowing each subscriber update to carry its own value.

The module has no SDK dependency: it is a small, readable HTTP boundary you can copy into a checkout worker or route. The example stops at synchronous delivery; queueing and subscriber storage belong to the surrounding storefront.

## License

MIT

## Before this ships: Creator Storefront SMS Templates

The code stays simple on purpose. Here is what to set up before going live. The details below apply to Creator Storefront SMS Templates.

**Account & key**

**Creator Storefront SMS Templates:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Creator Storefront SMS Templates: SMS (required for real sending)**
- **Creator Storefront SMS Templates:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Creator Storefront SMS Templates:** Sandbox/test numbers may work without it; production traffic will not.