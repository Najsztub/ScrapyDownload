# -*- coding: utf-8 -*-
'''
MN: 03/10/16

Automation of database update.
Data taken from ScrapingHub
API key: xxxx
'''
import sys
import os
import codecs
import time
import requests
import syslog
import pymongo

API_key = os.environ['SCH_API']
PRJ = os.environ['SCH_PROJECT']
SPIDER_NAME = os.environ['SCH_SPIDER_NAME']

url_jobs = 'https://app.scrapinghub.com/api/jobs/list.json'
url_data = 'https://storage.scrapinghub.com/items/'

# Get the most recent job number


def getSpider(url, api, header='', **options):
    req = ''
    for idx, op in enumerate(options):
        if idx == 0:
            req += '?' + op + '=' + str(options[op])
        else:
            req += '&' + op + '=' + str(options[op])
    resp = requests.get(url + req, auth=(api, ''))
    return resp


# Get 5 most recent jobs
syslog.syslog("ScrapingHub: starting...")
syslog.syslog("ScrapingHub: Getting jobs info")
try:
    res_jobs = getSpider(url_jobs, API_key, project=PRJ, state='finished',
                         count=5)
except (requests.HTTPError, ConnectionError):
    syslog.syslog("ScrapingHub: Connection error for jobs info")
    print("Connection Error!")
    sys.exit(1)
json_job = res_jobs.json()
# Find latest job
max_time = 0
max_time_id = -1
for idx, j in enumerate(json_job['jobs']):
    if j['close_reason'] != 'finished':
        continue
    job_end = time.mktime(
        time.strptime(
            str(j['updated_time']),
            '%Y-%m-%dT%H:%M:%S'
        )
    )
    if job_end >= max_time:
        max_time = job_end
        max_time_id = idx
last_job = json_job['jobs'][max_time_id]
last_job_id = str(last_job['id'])

# Download data for last job
syslog.syslog("ScrapingHub: downloading data for job %s" % last_job_id)
try:
    spider_data = getSpider(url_data + last_job_id, API_key, format='jl')
except (requests.HTTPError, ConnectionError):
    syslog.syslog("ScrapingHub: Data download fail!")
    print("Connection Error when downloading data!")
    sys.exit(1)

# Save file
try:
    last_time_tup = time.localtime(max_time)
    last_name = SPIDER_NAME + '_' + time.strftime('%d%m%y', last_time_tup)
    file_name = "/home/mateusz/data/%s.jl" % last_name
    out_data = codecs.open(file_name, 'w', "utf-8")
    out_data.write(spider_data.text)
    out_data.close()
    syslog.syslog("ScrapingHub: file %s written succesfully :)" % file_name)
except Exception as e:
    syslog.syslog("ScrapingHub: file writing failed")

# Drop old data and import new to MongoDB
# Setup the connection
try:
    syslog.syslog("ScrapingHub: Flushing MongoDB data for Szczecin")
    key = os.environ['MONGODB_DB_URL']
    conn = pymongo.MongoClient(key)
    db = conn.python

    # Drop the DB
    db.szczecin.drop()
    conn.close()
except Exception as e:
    syslog.syslog("ScrapingHub: MongoDB flush fail!")
    sys.exit(1)

# Populate the new DB
syslog.syslog("ScrapingHub: Populate MongdDB with new data")
pop = os.system("mongoimport -d python -c szczecin --type json %s" % file_name)
if pop != 0:
    syslog.syslog("ScrapingHub: Populating MongoDB failed")
    sys.exit(1)
