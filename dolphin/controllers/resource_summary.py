from nanohttp import json, RestController

from ..models import AbstractResourceSummaryView


class ResourceSummaryController(RestController):
    @json
    def metadata(self):
        return AbstractResourceSummaryView \
            .create_mapped_class(None, None) \
            .json_metadata()

