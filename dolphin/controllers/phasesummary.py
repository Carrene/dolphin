from nanohttp import json, RestController

from ..models import AbstractPhaseSummaryView


class PhaseSummaryController(RestController):
    @json
    def metadata(self):
        return AbstractPhaseSummaryView \
            .create_mapped_class(None) \
            .json_metadata()


