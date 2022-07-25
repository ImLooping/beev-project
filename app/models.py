from django.db import models
from django.db import models
from django.contrib.auth.models import User


class GlobalQuery(models.Model):
    """
    Display an individual :model:`app.GlobalQuery`.

    **Context**

    ``GlobalQuery``
        The :model:`app.GlobalQuery` to save all necessary data from BigQuery.

    **Template:**

    :template:`app/index.html`
    :template:`app/all-list.html`
    """
    
    date = models.DateField()
    client_id = models.CharField(max_length=100)
    timestamp = models.BigIntegerField()
    event_name = models.CharField(max_length=100)
    device = models.CharField(max_length=100)
    language = models.CharField(max_length=100)
    browser = models.CharField(max_length=100)
    hostname = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    ga_session_id = models.CharField(max_length=100)
    url = models.TextField()
    page_title = models.CharField(max_length=255)
    time_on_page_in_seconds = models.FloatField()
    total_time = models.FloatField(null=True)
    maxi = models.DateTimeField(null=True)
    mini = models.DateTimeField(null=True)
    all_source = models.CharField(max_length=100, null=True)
    brands = models.CharField(max_length=100, null=True)
    modeles = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return self.client_id

    
# class Daily(models.Model):
#     date = models.DateField()
#     nb_client = models.IntegerField()
#     nb_page = models.IntegerField()
#     brands = models.TextField(null=True)
#     modeles = models.TextField(null=True)
#     total_time_on_page = models.FloatField(null=True)
#     total_cs = models.IntegerField(null=True)
#     total_ev = models.IntegerField(null=True)    
#     wc_brands = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=100, null=True)
#     wc_models = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=100, null=True)
    
    