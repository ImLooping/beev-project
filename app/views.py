from modulefinder import packagePathMap
from turtle import bgcolor
from django.shortcuts import redirect, render
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import os
from app.graph import Dash

from app.models import GlobalQuery
from django.views.generic.list import ListView

from scripts import get_data, save_data

from django.db.models import Max, Count

from wordcloud import WordCloud
from PIL import Image

from django.contrib import messages


def index(request):
    """
    Display an individual :model:`app.GlobalQuery`.\n
    Render the index page with a Dashboard.
    
    **Context**

    ``GlobalQuery``
        The :model:`app.GlobalQuery` to save all necessary data if the database not contains the yesterday date.\n
        Check all data, create a dataframe and calculate various rate to render graphs in the template :url`app:index.html`

    **Template:**

    :template:`app/index.html`
    """
    data = request.GET.get('date-dropdown')

    if data == 'yesterday':
        date_start = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    elif data == 'week':
        date_start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    elif data == 'month':
        date_start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    # Get the last Date from the database
    last_date = GlobalQuery.objects.aggregate(Max('date'))['date__max']
    """If not exist we get all date since the beginning of the database"""
    if last_date is None:
        last_date = datetime.strptime('2022-06-01', '%Y-%m-%d')
    # Get the day before the last date
    day_before = last_date - timedelta(days=1)
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (date.today() - timedelta(days=1))
    
    print('last_date: ', last_date, 'day_before: ', day_before, 'today: ', today, 'yesterday: ', yesterday)
    """
        Check for the last date in the database and update the data if necessary
    """
    if yesterday != last_date:
        GlobalQuery.objects.filter(date__range=(last_date, yesterday)).delete()
        start = last_date
        end = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        get_data.run(start, end)
        print('Data has been updated')
        save_data.run(start)
        print('Data has been saved')
        messages.success(request, 'Data has been updated and saved')
        return redirect('index')

    """Check if error in the Database"""
    if data == 'yesterday' and date_start != day_before.strftime('%Y-%m-%d'):
        messages.error(request, 'Veuillez mettre à jour la base de données avant de récupérer les données du jour dernier')
        return redirect('index')
    
    """Get all data that we are interested in"""
    df = GlobalQuery.objects.filter(hostname__contains='app.beev').values('client_id','date' , 'url', 'brands', 'modeles', 'event_name')

    """Create the dataframe"""
    if data == 'yesterday' or data == 'week' or data == 'month':
        df = df.filter(date__range=[date_start, datetime.today().strftime('%Y-%m-%d')])
        day_before = date_start
    else:
        df = df.filter(date__gte=day_before)
        day_before = day_before.strftime('%Y%m%d')

    df = pd.DataFrame(list(df))

    """Get brands and modeles"""
    brands_dict = df.groupby('brands').count()['client_id'].sort_values(ascending=True).to_dict()
    models_dict = df.groupby('modeles').count()['url'].sort_values(ascending=True).to_dict()
    brands_dict = {k: v for k, v in brands_dict.items() if len(k) > 1}
    models_dict = {k: v for k, v in models_dict.items() if len(k) > 1}
    
    """Get lead to calculate the conversions rate"""
    nb_visitor = df[((df['url'].str.contains('page-produit')) | (df['url'].str.contains('vehic')) | (df['url'].str.contains('configurateur'))) \
                    & (~df['url'].str.contains('borne')) & (~df['url'].str.contains('merci'))
                ].shape[0]
    nb_lead_ev = df[df.event_name == 'onboarding_lead_ev'].shape[0]
    nb_lead_cs = df[df.event_name == 'onboarding_lead_cs'].shape[0]
    
    conversion_ev = nb_lead_ev/nb_visitor * 100
    conversion_cs = nb_lead_cs/nb_visitor * 100

    # Get the conversion numbers
    event_cs = GlobalQuery.objects.filter(
                                                date__range=((datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'), today),
                                                event_name__contains='onboarding_lead_cs'
                                            ).values('date', 'event_name').annotate(Count('client_id'))
    event_cs = pd.DataFrame(list(event_cs))
    event_ev = GlobalQuery.objects.filter(
                                                date__range=((datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'), today),
                                                event_name__contains='onboarding_lead_ev'
                                            ).values('date', 'event_name').annotate(Count('client_id'))
    event_ev = pd.DataFrame(list(event_ev))
    tot = event_cs.merge(event_ev, on='date', how='outer').fillna(0)
    tot['total'] = tot['client_id__count_x'] + tot['client_id__count_y']
    
    
    # Get the map of visitors
    # df_map = GlobalQuery.objects.filter(hostname__contains='app.beev', date__range=[yesterday, date.today()]).values('date',
    #                                                                         'country').annotate(Count('client_id')).order_by('-client_id__count')
    # df_map = pd.DataFrame(list(df_map)).head(5)
    
    """Plot the various graphs"""
    graph_nb_visitor = Dash().plot_gauge(nb_visitor, 'Nombre de visiteurs')
    graph_ev = Dash().plot_gauge(conversion_ev, 'Conversion Rate EV')
    graph_cs = Dash().plot_gauge(conversion_cs, 'Conversion Rate CS')
    graph_event = Dash().get_lead_line(event_ev, event_cs, tot)
    # graph_map = Dash().get_map(df_map)

    
    """How we can't user wordcloud with django we create image and render it in the template"""
    if not os.path.exists('theme/static/img/brands/{}-{}.png'.format(day_before , datetime.today().strftime('%Y%m%d'))):
        car_mask = np.array(Image.open("theme/static/img/car.png"))
        wc = WordCloud(background_color = "white", mask=car_mask, width = 2000, height = 2000, repeat = True).generate_from_frequencies(brands_dict)
        wc.to_image().save("theme/static/img/brands/{}-{}.png".format(day_before, datetime.today().strftime('%Y%m%d')))
    else:
        print('File brands already exists')
    
    if not os.path.exists('theme/static/img/models/{}-{}.png'.format(day_before, datetime.today().strftime('%Y%m%d'))):
        car_mask = np.array(Image.open("theme/static/img/car.png"))
        wc = WordCloud(background_color = "white", mask=car_mask, prefer_horizontal=0.99, width = 2000, height = 2000, repeat = True).generate_from_frequencies(models_dict)
        wc.to_image().save("theme/static/img/models/{}-{}.png".format(day_before, datetime.today().strftime('%Y%m%d')))
    else:
        print('File models already exists')   
    
    """We compare only the 20 best brands and models"""
    n = 20
    context = {
        'day_before': day_before,
        'today': datetime.today().strftime('%Y%m%d'),
        'graph_nb_visitor': graph_nb_visitor,
        'graph_ev': graph_ev,
        'graph_cs': graph_cs,
        'bar_brands': Dash().plot_bar(y=list(brands_dict.keys())[-n:], x=list(brands_dict.values())[-n:]),
        'bar_models': Dash().plot_bar(y=list(models_dict.keys())[-n:], x=list(models_dict.values())[-n:]),
        'total_visitor': nb_visitor,
        'total_lead_ev': nb_lead_ev,
        'total_lead_cs': nb_lead_cs,
        'graph_event': graph_event,
        # 'graph_map': graph_map,
    }
    return render(request, "index.html", context)

def run_script(request):
    """
    Automatically run the script to update the database

    **Context**

    check the last date entered in the database. 
    delete the last date from the database, 
    request the API Bigquery to get the data, 
    save the data in the database

    **Template:**

    :template:`app/index.html`
    """
    # Delete All Data from the database ONLY DEBUG MODE !!!
    # GlobalQuery.objects.all().delete()
    
    # Get last date from the database
    start = GlobalQuery.objects.aggregate(Max('date'))['date__max']
    # Define the date of today
    end = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')
    # Delete the last date from the database and run the script
    if start is not None:
        GlobalQuery.objects.filter(date=start).delete()
        get_data.run(start, end)
        print('Data has been updated')
        save_data.run(start)
        print('Data has been saved')
        messages.success(request, 'Data has been updated and saved')
        return redirect('index')
    else:
        start = datetime.strptime('2022-06-01', '%Y-%m-%d')
        get_data.run(start, end)
        print('Data has been updated')
        save_data.run(start)
        print('Data has been saved')
        messages.success(request, 'Data has been updated and saved')
        return redirect('index')

class AllList(ListView):
    model = GlobalQuery
    template_name = 'all-list.html'
    context_object_name = 'all_list'
    paginate_by = 500
    
    def get_queryset(self):
        result = GlobalQuery.objects.values('client_id', 'date', 'mini', 'maxi', 'total_time', 'all_source', 'event_name').annotate(ccount=Count('url')).order_by('-maxi')
        start = self.request.GET.get('start')
        end = self.request.GET.get('end')
        source = self.request.GET.get('source-dropdown')
        event = self.request.GET.get('event-dropdown')
        
        if start != None and end != None:
            result = result.filter(date__range=[start, end])
        else:
            result = result.filter(date__gte=(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'))
            
        if source != 'all' and source != None:
            result = result.filter(all_source=source)
        
        if event != 'all' and event != None:
            result = result.filter(event_name=event)
        
        return result
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sources'] = GlobalQuery.objects.filter(hostname__contains='app.beev').values('all_source').distinct().order_by('all_source')
        context['events'] = GlobalQuery.objects.filter(hostname__contains='app.beev').values('event_name').distinct().order_by('event_name')
        context['start'] = self.request.GET.get('start')
        context['end'] = self.request.GET.get('end')
        context['source'] = self.request.GET.get('source-dropdown')
        context['event'] = self.request.GET.get('event-dropdown')
        context['total_client'] = self.object_list.count()
        return context

class Client(ListView):
    model = GlobalQuery
    template_name = 'client.html'
    context_object_name = 'client'
    
    def get_queryset(self):
        result = self.model.objects.filter(client_id=self.kwargs['pk'])
        return result
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_page'] = self.object_list.count()
        return context