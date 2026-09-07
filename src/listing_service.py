from dataclasses import dataclass
from typing import Any, Dict

from image_client import ImageClient


@dataclass
class ListingRequest:
    tenant_id: str
    image: str
    approved: bool = False


def prepare_listing(request: ListingRequest, client: ImageClient) -> Dict[str, Any]:
    if not request.tenant_id or not request.image:
        raise ValueError("tenant_id and image are required")
    if not request.approved:
        return {"tenant_id": request.tenant_id, "state": "needs_admin_approval"}
    result = client.background_remove(request.image, "png")
    return {"tenant_id": request.tenant_id, "state": "ready_for_publish", "image": result}
