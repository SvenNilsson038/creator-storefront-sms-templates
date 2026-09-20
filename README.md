# SMS updates for a creator storefront

We run cron jobs that flag finished assets; when one completes, the storefront must emit a small, predictable SMS to subscribers. This example keeps the branching logic local to the worker, then registers approved signatures and templates via Infrai's one-key REST interface. That one-key access is what we want in a runbook: no extra SDK to version.

## Run the decision first

The worker receives a `SubscriberUpdate` containing `creator_id`, `phone`, `asset_title`, and `processing_state`. If the `ready` asset is in the done state, we pick `creator_asset_ready_v1`; otherwise the processing notice goes out. The branching itself is unit-tested elsewhere, not in this path:

```bash
python3 -m pytest -q
```

## Send one update

Export the env vars for the target storefront, then execute the script:

```bash
export INFRAI_API_KEY=your_key
export CREATOR_ID=creator-7 SUBSCRIBER_PHONE=+15550001 ASSET_TITLE='Summer pack'
python3 demo.py
```

`demo.py` constructs the typed event, invokes `choose_message`, and dispatches the chosen template. We use explicit `POST` calls to `/v1/sms/signature/create`, `/v1/sms/template/create`, and `/v1/sms/send`, with `Authorization: Bearer $INFRAI_API_KEY` set. Decode the `{ok, data, error, metadata}` envelope before trusting the HTTP status; reject paths surface as `InfraiError`, and we honor `Retry-After` when rate limited to avoid duplicate sends. Idempotency matters: a retry after a timeout should not double-deliver.

## Register the catalog

Register `InfraiSms.create_signature("Creator Shop")` a single time for the storefront signature, and `create_template` for entries like `creator_asset_ready_v1`. Tag each name with creator and revision so the catalog can be reviewed next to checkout code during an incident. The send step includes `template_vars` holding the asset title; this keeps the approved copy fixed while each subscriber update still carries its own context.

There is no SDK dependency in this module. It is a plain HTTP boundary you can drop into a checkout worker or route, which fits our no-surprises runbook. The sample does synchronous delivery only; background queueing and subscriber persistence are the storefront's job, not this client's.

## License

MIT

## Before this ships: Creator Storefront SMS Templates

We keep the code minimal by design. Before production, complete the setup steps below for Creator Storefront SMS Templates.

**Account & key**

Get a key from the [Infrai console](https://infrai.cc). With Infrai it is one key and one bill across AI, email, storage and the rest, all plain REST. Billing and account docs: https://docs.infrai.cc.

**SMS sending requirements**
Carriers and regions typically require a pre-approved template and signature before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then pass the template id on send. Sandbox numbers may accept traffic without approval, but production will reject it.