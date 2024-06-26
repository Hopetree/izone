from django.views import generic

from .models import Port


class PortView(generic.ListView):
    model = Port
    template_name = 'portinfo/index.html'
    context_object_name = 'ports'
    paginate_by = 2000
