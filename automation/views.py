from django.http import HttpResponse
from django.conf import settings
from pdfProcessing.views import PdfProcessing
import os

# Create your views here.
def pdfAutomation(request):
    existing_filename = settings.MEDIA_ROOT + '/uploads/west_bengal.pdf'
    
    if os.path.isfile(existing_filename) and os.path.exists(existing_filename) :
        pdfHandler = PdfProcessing()

        pdfHandler.read_pdf(existing_filename)
        pass
    else:
        return HttpResponse("File not Found")

    return HttpResponse("Hello World")