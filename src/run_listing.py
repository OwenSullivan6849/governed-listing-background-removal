import argparse
import json

from image_client import ImageClient
from listing_service import ListingRequest, prepare_listing


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a SaaS product listing image")
    parser.add_argument("tenant_id")
    parser.add_argument("image", help="image identifier or input accepted by the API")
    parser.add_argument("--approved", action="store_true")
    args = parser.parse_args()
    output = prepare_listing(ListingRequest(args.tenant_id, args.image, args.approved), ImageClient())
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
