from django.http import HttpResponse
import os

def render_to_mimetype_response(mimetype, filename, outputFile):
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

