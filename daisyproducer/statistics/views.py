import csv
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from daisyproducer.statistics.models import DocumentStatistic
from daisyproducer.documents.models import Document
from daisyproducer.documents.views.utils import render_to_mimetype_response

@login_required
@permission_required("statistics.add_documentstatistic")
def index(request):
    """Statistics index page"""
    stats = DocumentStatistic.objects
    # Only keep first occurence of document
    stats = stats.raw("""
SELECT id,max(statistics_documentstatistic.unknown)
FROM statistics_documentstatistic
GROUP BY statistics_documentstatistic.document_id
ORDER BY statistics_documentstatistic.date;
""")
    return render_to_response('statistics/stats_index.html', locals(), 
                              context_instance=RequestContext(request))

@login_required
@permission_required("statistics.add_documentstatistic")
def all_data_as_csv(request):
    """Get all data as a comma separated values file"""
    outputFileName = "/tmp/stats_data.csv"
    outputFile = open(outputFileName, 'wb')
    writer = csv.writer(outputFile)
    writer.writerow(['Date', 'Document', 'Grade', 'Total', 'Unknown'])
    stats = DocumentStatistic.objects
    # Only keep first occurence of document
    stats = stats.raw("""
SELECT id,max(statistics_documentstatistic.unknown)
FROM statistics_documentstatistic
GROUP BY statistics_documentstatistic.document_id
ORDER BY statistics_documentstatistic.date;
""")
    for stat in stats:
        writer.writerow([stat.date, stat.document.identifier, stat.grade, stat.total, stat.unknown])
    outputFile.close()
    return render_to_mimetype_response('text/csv', 'XMLP Statistical Data', outputFileName)
