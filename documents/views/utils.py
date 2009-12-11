from django.http import HttpResponse
import os
import mimetypes

def render_to_mimetype_response(filename, outputFile, mimetype=None):
    if mimetype == None:
        mimetype, ignore = mimetypes.guess_type(filename)
    assert mimetype != None

    response = HttpResponse(mimetype=mimetype)
    response['Content-Disposition'] = "attachment; filename=\"%s\"" % (filename)

    f = open(outputFile)
    try:
        content = f.read()
        response.write(content)
    finally:
        f.close()

    # remove the tmp file
    os.remove(outputFile)

    return response

