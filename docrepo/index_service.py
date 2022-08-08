#!/usr/bin/env python

import logging
import sys
import time

from index_tracker import IndexTracker
from repo.models.content import ContentFile

FREQUENCY = 15

if __name__ == "__main__":
    LOGGER = logging.getLogger(__name__)
    LOGGER.info("Running Documendous Index Tracker Service.")

    unindexed_documents = ContentFile.objects.filter(
        index_error__isnull=False, is_acknowledged=False
    )

    if unindexed_documents:
        LOGGER.debug(
            "The following content files have index issues. Please investigate."
        )
        for doc in unindexed_documents:
            LOGGER.debug("  {}".format(doc))

    index_tracker = IndexTracker()
    while True:
        index_tracker.run()
        LOGGER.info("Waiting {} seconds to track.".format(FREQUENCY))
        try:
            time.sleep(FREQUENCY)
        except KeyboardInterrupt:
            LOGGER.info("Keyboard interrupt ... Shutting down ...")
            LOGGER.info("  Done.")
            sys.exit(0)
