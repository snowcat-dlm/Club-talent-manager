# This is Project views.py

from django.views.generic import TemplateView

class TopPage(TemplateView):
    template_name = "top_page.html"
