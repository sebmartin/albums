from django.shortcuts import render_to_response
from albums.models import Album, Media
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from datetime import date, datetime, timedelta
import calendar

def home(request):
    params = { 'albums' : Album.objects.filter(visible = True).order_by('-edit_time') }
    return render_to_response('home.html', params)

def thumbnail_view(request, media, page_num = 1, params = {}):
    paginator = Paginator(media, 12)
    try:
        page_num = int(page_num)
        if page_num <= 0:
            raise ValueError()
    except:
        page_num = 1

    params.update({
        'media_list' : paginator.page(page_num).object_list,
        'paginator' : paginator,
        'page' : paginator.page(page_num)
    })

    return render_to_response('album.html', params)

def album(request, album_id, page_num):
    try:
        media = Media.objects.filter(album__id = album_id)
        media = media.order_by('-create_time')
        params = {
            'album' : Album.objects.get(id = album_id),
            'albums' : Album.objects.filter(visible = True).order_by('-edit_time'),
        }
        params['breadcrumb'] = ' &raquo; %s' % params['album'].title
    except Album.DoesNotExist:
        raise Http404
    return thumbnail_view(request, media, page_num, params)

def month(request, year, month, page_num):
    try:
        year = int(year)
        month = int(month)
        first_day = date(year, month, 1)
        last_day = \
            first_day + timedelta(days = calendar.monthrange(year, month)[1])
    except:
        raise Http404

    media = Media.objects.filter(create_time__range = (first_day, last_day))
    media = media.order_by('-create_time')
    params = {
        'breadcrumb': ' &raquo; %s' % datetime.strftime(first_day, '%B %Y')
    }
    return thumbnail_view(request, media, page_num, params)
