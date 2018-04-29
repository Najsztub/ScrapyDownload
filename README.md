## Automatic Scrapinghub data downloader

In the begining [Scrapinghub](https://scrapinghub.com/) alowed to automatically schedule jobs on the server side. Some time ago they changed their policy disabling automatic scheduling for their free plan. This short script alows for automatic scheduling of running the scraper as well as downloading the data afterwards from the server using Crontab and Python.

Also the data is uploaded afterwards into a MongoDB database.

This configuration is specific for my needs, but I think that it can be easily adopted.

## Requirements

The script requires couple of environmental variables set:

- SCH_API: Scrapinghub Api key
- SCH_PROJECT: The project identifier
- SCH_SPIDER_NAME: Name of the spider that is supposed to run

This piece of software is released under the MIT licence. Feel free to use.