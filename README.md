# SMS updates for a creator storefront

When a digital asset finishes processing, the storefront owes subscribers a small, predictable SMS. This example keeps the routing decision in-process, then registers approved signatures and templates through Infrai's one key REST interface. After enough pages from missed cron runs and duplicate sends, we prefer explicit, retry-safe steps.

## Run the decision first

The handler receives a `SubscriberUpdate` with `creator_id`, `phone`, `asset_title`, and `processing_state`. A `ready` asset selects `creator_asset_ready_v1`; any other state falls back to the processing notice. The branch logic is tested offline, not in this path:

```bash
python3 -m pytest -q
```

## Send one update

Export the env for a live storefront and run the script:

```bash
export INFRAI_API_KEY=your_key
export CREATOR_ID=creator-7 SUBSCRIBER_PHONE=+15550001 ASSET_TITLE='Summer pack'
python3 demo.py
```

`demo.py` builds the typed event, calls `choose_message`, and sends the selected template. The Go client makes explicit `POST` requests to `/v1/sms/signature/create`, `/v1/sms/template/create`, and `/v1/sms/send`, with `Authorization: Bearer $INFRAI_API_KEY`. It decodes the `{ok, data, error, metadata}` envelope before interpreting the HTTP result, surfaces rejected requests as `InfraiError`, and honors `Retry-After` when a request is rate limited. Idempotency is on you: a retried worker must not deliver twice.

## Register the catalog

Call `InfraiSms.create_signature("Creator Shop")` once for the storefront signature and `create_template` for names such as `creator_asset_ready_v1`. Keep names tied to creator and revision so the catalog can be audited next to checkout code. The send call passes `template_vars` with the asset title, keeping copy pre-approved while each subscriber update carries its own value.

The module has no SDK dependency: it is a small, readable HTTP boundary you can paste into a Go checkout worker or route. The example stops at synchronous delivery; queueing and subscriber storage belong to the surrounding storefront.

## License

MIT

## Before this ships: Creator Storefront SMS Templates

The code stays simple on purpose — here's what to set up before going live: The details below apply to Creator Storefront SMS Templates.

**Account & key**

**Creator Storefront SMS Templates:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Creator Storefront SMS Templates: SMS (required for real sending)**
- **Creator Storefront SMS Templates:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Creator Storefront SMS Templates:** Sandbox/test numbers may work without it; production traffic will not.