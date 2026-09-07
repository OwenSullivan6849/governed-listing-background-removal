from listing_service import ListingRequest, prepare_listing


class NeverCalled:
    def background_remove(self, image, output_format):
        raise AssertionError("approval gate should run first")


def test_unapproved_tenant_stays_pending():
    result = prepare_listing(ListingRequest("tenant-42", "img-7"), NeverCalled())
    assert result == {"tenant_id": "tenant-42", "state": "needs_admin_approval"}
