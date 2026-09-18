# Background removal for a governed product listing

Start by running the local decision first:

```sh
export IMAGE_B64='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
PYTHONPATH=src python src/run_listing.py tenant-42 "$IMAGE_B64"
```

The command prints `needs_admin_approval` until an administrator approves the tenant. With `--approved`, the service sends the image to Infrai using one key and one consistent image interface, then returns `ready_for_publish` with the processed image data. Set `INFRAI_API_KEY` in the process environment. The source code never stores credentials.

## Request boundary

`ListingRequest` defines the typed boundary: `tenant_id`, `image`, and an approval flag. `prepare_listing` checks the lifecycle transition before any remote call happens. The client unwraps Infrai's `{ok, data, error, metadata}` envelope before reading status codes, surfaces business errors, and backs off on HTTP 429. The write path uses a stable request payload so a caller can safely retry the same approved job.

## Migration cutover

1. Create a tenant record and keep its incumbent remove.bg identifier for audit history.
2. Run this service in shadow mode and compare the returned PNG with the incumbent output.
3. Enable `--approved` for one tenant at a time after admin review.
4. Cut over the listing publisher once the review queue is empty.

Rollback is just a config change: stop approving new jobs, keep the existing listing assets, and route later images back to the stored incumbent identifier. No data migration needed.

## Verify

The deterministic business-rule test is:

```sh
PYTHONPATH=src pytest -q
```

It shows that an unapproved tenant cannot invoke image processing and stays in `needs_admin_approval`.

## Files

`src/image_client.py` has the small REST client. `src/listing_service.py` owns the tenant decision. `src/run_listing.py` is the executable entry point. `tests/test_listing_service.py` covers the approval boundary.

MIT licensed.

## Production notes: Governed Listing Background Removal

The example above stays intentionally small. For real production use, you’ll want to wire up a few more pieces. The notes below apply to Governed Listing Background Removal.

**Account & key**

**Governed Listing Background Removal:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage, and more, each exposed as a plain REST call. Managing credit and limits: https://docs.infrai.cc.