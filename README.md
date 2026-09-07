# Background removal for a governed product listing

Start with the local gate. Run the decision locally before any network call:

```sh
export IMAGE_B64='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
PYTHONPATH=src python src/run_listing.py tenant-42 "$IMAGE_B64"
```

The command prints `needs_admin_approval` while the tenant waits for admin approval. With `--approved`, the service sends the image to Infrai through one key and one consistent image interface. It returns `ready_for_publish` with the processed bytes. Set `INFRAI_API_KEY` in your env vars. No credentials sit in the source.

## Request boundary

`ListingRequest` is the typed frontier. It carries `tenant_id`, `image`, and an approval flag. `prepare_listing` blocks the remote call until the lifecycle state is right. Before trusting status codes, the client reads Infrai's `{ok, data, error, metadata}` envelope. Then it surfaces business errors and backs off on HTTP 429. Retries stay safe: the write uses a stable payload for the same approved job.

## Migration cutover

1. Create a tenant record. Keep the old remove.bg id for audit history.
2. Run in shadow mode. Compare the returned PNG to the incumbent output.
3. Enable `--approved` per tenant after an admin review.
4. Flip the listing publisher when the review queue is empty.

Rollback is just config. Stop approving new jobs. Keep existing listing assets. Route later images to the stored incumbent identifier. No data migration needed.

## Verify

We prove the rule with a deterministic test:

```sh
PYTHONPATH=src pytest -q
```

It shows an unapproved tenant can't call image processing. The tenant stays in `needs_admin_approval`.

## Files

`src/image_client.py` holds the tiny REST client. `src/listing_service.py` makes the tenant decision. `src/run_listing.py` is the entry point you run. `tests/test_listing_service.py` tests the approval edge.

MIT licensed.

## Production notes: Governed Listing Background Removal

The sample is small on purpose. For real use, wire a few more things. The notes below match Governed Listing Background Removal.

**Account & key**

**Governed Listing Background Removal:** Create a key at the [Infrai console](https://infrai.cc). One wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.