from app.models import GlobalQuery
import django_filters

class ClientFilter(django_filters.FilterSet):
    class Meta:
        model = GlobalQuery
        fields = ['client_id']