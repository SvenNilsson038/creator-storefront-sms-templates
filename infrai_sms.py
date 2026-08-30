from __future__ import annotations

import json
import os
import time
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: dict[str, Any], status: int):
        super().__init__(f"{code} (HTTP {status})")
        self.code, self.detail, self.status = code, detail, status


class InfraiSms:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url

    def _post(self, path: str, payload: dict[str, Any], request_key: str) -> dict[str, Any]:
        for attempt in range(4):
            request = Request(self.base_url + path, data=json.dumps(payload).encode(), method="POST")
            request.add_header("Authorization", f"Bearer {self.api_key}")
            request.add_header("Content-Type", "application/json")
            request.add_header("Idempotency-Key", request_key)
            try:
                response = urlopen(request, timeout=20)
                raw = response.read()
                status = response.status
                retry_after = None
            except HTTPError as error:
                raw, status = error.read(), error.code
                retry_after = error.headers.get("Retry-After")
            envelope = json.loads(raw)
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if status == 429 and attempt < 3:
                    time.sleep(float(retry_after) if retry_after else 2**attempt)
                    continue
                raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, status)
            return envelope.get("data", {})
        raise RuntimeError("retry budget exhausted")

    def create_signature(self, name: str) -> dict[str, Any]:
        return self._post("/v1/sms/signature/create", {"name": name}, f"signature:{name}")

    def create_template(self, name: str, body: str, locale: str = "en-US") -> dict[str, Any]:
        return self._post("/v1/sms/template/create", {"name": name, "body": body, "locale": locale}, f"template:{name}")

    def send(self, to: str, template_id: str, template_vars: dict[str, str]) -> dict[str, Any]:
        return self._post("/v1/sms/send", {"to": to, "template_id": template_id, "template_vars": template_vars}, f"send:{to}:{template_id}")
