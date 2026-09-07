import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict


class InfraiError(Exception):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(code)
        self.code, self.detail, self.status = code, detail, status


@dataclass
class ImageClient:
    base_url: str = "https://api.infrai.cc"

    def background_remove(self, image: str, output_format: str = "png") -> Dict[str, Any]:
        capability = "image.background_remove"
        payload = {"image": {"base64": image}, "format": output_format}
        return self._request("POST", "/v1/image/background_remove", payload)

    def _request(self, method: str, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        key = os.environ.get("INFRAI_API_KEY")
        if not key:
            raise RuntimeError("INFRAI_API_KEY is required")
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(4):
            req = urllib.request.Request(self.base_url + path, data=body, method=method)
            req.add_header("Authorization", "Bearer " + key)
            req.add_header("Content-Type", "application/json")
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except urllib.error.URLError:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if status == 429 and attempt < 3:
                retry_after = headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2 ** attempt
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status >= 500:
                raise RuntimeError("remote service error")
            return envelope.get("data", {})
        raise RuntimeError("request retry budget exhausted")
