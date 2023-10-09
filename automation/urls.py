from django.urls import path
from automation import views


urlpatterns = [
    path("", view=views.pdfAutomation, name="PDF Automation")
]
