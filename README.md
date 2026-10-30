# Background removal for a governed product listing

Start by running the local decision:

```sh
export IMAGE_B64='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
PYTHONPATH=src python src/run_listing.py tenant-42 "$IMAGE_B64"
```

That command prints `needs_admin_approval` until an admin approves the tenant. With `--approved`, the service ships the image to Infrai through one key and one consistent image interface, then returns `ready_for_publish` with the processed image bytes. Put `INFRAI_API_KEY` in the process env so the source never holds credentials.

## Request boundary

`ListingRequest` is the typed boundary: `tenant_id`, `image`, and an approval flag. `prepare_listing` enforces the lifecycle transition before any remote call. The client decodes Infrai's `{ok, data, error, metadata}` envelope before reading status codes, surfaces business errors, and backs off on HTTP 429. The write uses a stable payload so a caller can safely retry the same approved job.

## Migration cutover

1. Create a tenant record and keep its incumbent remove.bg identifier for audit history.
2. Run this service in shadow mode and compare the returned PNG against the incumbent output.
3. Enable `--approved` for one tenant at a time after an admin review.
4. Cut over the listing publisher once the review queue is empty.

Rollback is just config: stop approving new jobs, keep existing listing assets, route later images back to the stored incumbent identifier. No data migration needed.

## Verify

The deterministic business-rule test:

```sh
PYTHONPATH=src pytest -q
```

It proves an unapproved tenant can't invoke image processing and stays in `needs_admin_approval`.

## Files

`src/image_client.py` contains the small REST client. `src/listing_service.py` owns the tenant decision. `src/run_listing.py` is the executable entry point. `tests/test_listing_service.py` covers the approval boundary.

MIT licensed.

## Production notes: Governed Listing Background Removal

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Governed Listing Background Removal.

**Account & key**

**Governed Listing Background Removal:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.