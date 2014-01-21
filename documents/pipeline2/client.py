import rest

from time import sleep
from urlparse import urlparse

from django.template.loader import render_to_string
# the following assumes that the pipeline is run in local mode, i.e.
# no auth, no multipart upload and the default webservice url

NS = "http://www.daisy.org/ns/pipeline/data"
WS_URL = "http://localhost:8181/ws"

def make_job_request(script, inputs={}, options={}):
    env = {'script': "%s/scripts/%s" % (WS_URL, script),
           'inputs': inputs.iteritems(),
           'options': options.iteritems()}
    request = render_to_string('jobrequest.xml', env)
    return request.encode('utf-8')

def parse_job(job):
    return {'id':       job.xpath("/d:job/@id", namespaces={"d": NS})[0],
            'status':   job.xpath("/d:job/@status", namespaces={"d": NS})[0],
            'messages': [{'level': message.attrib['level'],
                          'index': int(message.attrib['sequence']),
                          'text': message.text}
                         for message in job.xpath("/d:job/d:messages/d:message", namespaces={"d": NS})],
            'results':  [{'type': result.attrib['from'],
                          'name': result.attrib['name'],
                          'href': result.attrib['href'],
                          'files': [{'file': urlparse(file.attrib['file']).path,
                                     'href': file.attrib['href'],
                                     'size': file.attrib['size']}
                                    for file in result.getchildren()]}
                         for result in job.xpath("/d:job/d:results/d:result", namespaces={"d": NS})],
            'log':     job.xpath("/d:job/d:log/@href", namespaces={"d": NS})}

def wait_for_job(job):
    msgIdxs = []
    while True:
        sleep(0.5)
        job = get_job(job['id'])
        for msg in job['messages']:
            if not msg['index'] in msgIdxs:
                msgIdxs.append(msg['index'])
        if job['status'] != "RUNNING":
            break
    return job

def post_job(request):
    return parse_job(rest.post_resource("%s/jobs" % WS_URL, request))

def get_job(id):
    return parse_job(rest.get_resource_as_xml("%s/jobs/%s" % (WS_URL, id)))

def delete_job(id):
    return rest.delete_resource("%s/jobs/%s" % (WS_URL, id))
