import mimetypes
import os

from django.http import HttpResponse


mimetypes.init()
mimetypes.add_type('application/epub+zip','.epub')
mimetypes.add_type('text/x-brl','.brl')
mimetypes.add_type('text/x-sbsform-g0','.bv')
mimetypes.add_type('text/x-sbsform-g1','.bv')
mimetypes.add_type('text/x-sbsform-g2','.bk')

def render_to_mimetype_response(mimetype, filename, outputFile):
    ext = mimetypes.guess_extension(mimetype)
    assert ext != None

    response = HttpResponse(mimetype=mimetype)
    response['Content-Disposition'] = "attachment; filename=\"%s%s\"" % (filename, ext)

    f = open(outputFile)
    try:
        content = f.read()
        response.write(content)
    finally:
        f.close()

    # remove the tmp file
    os.remove(outputFile)

    return response

