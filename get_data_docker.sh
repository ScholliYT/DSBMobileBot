#!/bin/bash
docker run --name dsbmobile-data-scraper --rm -it -v "$PWD"/json/groupedtables.json:/app/json/groupedtables.json dsbmobile-data-scraper

