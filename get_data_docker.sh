#!/bin/bash
docker run --name dsbmobile-data-scraper --rm -it -v "$PWD"/json/test.json:/app/json/groupedtables.json dsbmobile-data-scraper

