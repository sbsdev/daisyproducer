import mimetypes
import os

from django.http import HttpResponse
from wsgiref.util import FileWrapper

mimetypes.init()
mimetypes.add_type('application/epub+zip','.epub')
mimetypes.add_type('text/x-brl','.brl')
mimetypes.add_type('text/x-sbsform-g0','.bv')
mimetypes.add_type('text/x-sbsform-g1','.bv')
mimetypes.add_type('text/x-sbsform-g2','.bk')

def render_to_mimetype_response(mimetype, filename, outputFile):
    ext = mimetypes.guess_extension(mimetype)
    assert ext != None
    
    wrapper = FileWrapper(file(outputFile))
    response = HttpResponse(wrapper, content_type=mimetype)
    response['Content-Disposition'] = "attachment; filename=\"%s%s\"" % (filename, ext)
    response['Content-Length'] = os.path.getsize(outputFile)
    
    # remove the tmp file
    os.remove(outputFile)
    
    return response

