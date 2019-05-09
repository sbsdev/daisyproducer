import requests
import tempfile
import os.path
import urllib

from zipfile import ZipFile
from time import sleep
from urlparse import urlparse

import xml.etree.ElementTree as ET

# the following assumes that the pipeline is run in remote mode
# without auth and the default webservice url

NS = "http://www.daisy.org/ns/pipeline/data"
WS_URL = "http://localhost:8181/ws"
POLLING_INTERVAL = 2

def job_request(script, inputs, options={}):
    root = ET.Element("jobRequest", {'xmlns': 'http://www.daisy.org/ns/pipeline/data'})
    ET.SubElement(root, "script", {'href': "%s/scripts/%s" % (WS_URL, script)})
    input = ET.SubElement(root, "input", {'name': "source"})
    for item in inputs:
        ET.SubElement(input, "item", {'value': urllib.quote(os.path.basename(item))})
    for name, value in options.iteritems():
        ET.SubElement(root, "option", {'name': name}).text = value

    return ET.tostring(root, encoding="UTF-8")

def parse_log(job):
    log = job.findall(".//d:log", namespaces={"d": NS})
    return log[0].attrib['href'] if log else None

def parse_job(job):
    return {'id':       job.attrib['id'],
            'status':   job.attrib['status'],
            'messages': [{'level': message.attrib['level'],
                          'index': int(message.attrib['sequence']),
                          'text': message.text}
                         for message in job.findall(".//d:message", namespaces={"d": NS})],
            'results':  [{'href': result.attrib['href'],
                          'size': result.attrib['size']}
                         for result in job.findall(".//d:results/d:result/d:result", namespaces={"d": NS})],
            'log': parse_log(job)}

def wait_for_job(job):
    msgIdxs = []
    while True:
        sleep(POLLING_INTERVAL)
        job = get_job(job['id'])
        if not job:
            return None
        for msg in job['messages']:
            if not msg['index'] in msgIdxs:
                msgIdxs.append(msg['index'])
        if job['status'] != "RUNNING":
            break
    return job

def job_data(inputs):
    tempFile = tempfile.NamedTemporaryFile(prefix="pipeline2-client", suffix=".zip", delete=False)
    tempFile.close() # we are only interested in a unique filename

    with ZipFile(tempFile.name, 'w') as myzip:
        for file in inputs:
            myzip.write(file, os.path.basename(file))

    return tempFile.name

def post_job(script, inputs, options={}):
    payload = {'job-request': job_request(script, inputs, options)}
    files = {'job-data': open(job_data(inputs), 'rb')}
    r = requests.post("%s/jobs" % WS_URL, data=payload, files=files)
    root = ET.fromstring(r.text)
    return parse_job(root)

def get_job(id):
    r = requests.get("%s/jobs/%s" % (WS_URL, id))
    root = ET.fromstring(r.text)
    return parse_job(root)

def delete_job(id):
    r = requests.delete("%s/jobs/%s" % (WS_URL, id))
    return r.status_code == requests.codes.ok

