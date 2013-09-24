
from django.core.management import setup_environ
from albums import settings
from datetime import datetime
setup_environ(settings)

# Script to sync the local database with the picasa web album
from albums.models import TempAlbum, TempAlbumThumbnail, \
                          TempMedia, TempMediaThumbnail, \
                          Album, AlbumThumbnail, \
                          Media, MediaThumbnail

import gdata.photos.service
gd_client = gdata.photos.service.PhotosService()
gd_client.email = '<youraddress>@gmail.com'
gd_client.password = '<password>'
gd_client.source = "Seb's online album"
gd_client.ProgrammaticLogin()
thumb_sizes = [32, 48, 64, 72, 144, 160, 200, 288, 320, 400, 512, 
               576, 640, 720, 800, 912, 1024, 1152, 1280, 1440, 1600]

###
# Helper functions
def format_date(dt):
    dt = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.000Z')
    diff = datetime.utcnow() - datetime.now()
    return dt + diff

def googlify_image_size(size):
    for s in thumb_sizes:
        if s >= size:
            return s                                            
    return thumb_size[-1]
###

# Delete temp tables
TempAlbum.objects.all().delete()
TempAlbumThumbnail.objects.all().delete()
TempMedia.objects.all().delete()
TempMediaThumbnail.objects.all().delete()

# Request the main feed for the gallery, which lists all albums
print "Fetching albums..."
thumbsize = settings.ALBUM_THUMB_SIZE
gthumbsize = googlify_image_size(thumbsize)
thumbratio = (float(thumbsize) / (float(gthumbsize)))
album_feed = gd_client.GetFeed('/data/feed/api/user/%s' \
                               '?kind=album&thumbsize=%d' \
                               % ('seb.d.martin', gthumbsize))
for album_info in album_feed.entry:
    # Fetch album details
    print " o %s" % album_info.title.text
    album = TempAlbum(
            id = album_info.gphoto_id.text,
            title = album_info.title.text,
            description = album_info.summary.text or '',
            create_time = datetime.fromtimestamp(
                int(album_info.timestamp.text[:-3])),
            edit_time = format_date(album_info.updated.text),
            )
    album.visible = not album.title.lower().startswith('test_')
    album.save()

    # Fetch album thumbnails
    thumb_count = 0
    for thumb_info in album_info.media.thumbnail:
        thumbnail = TempAlbumThumbnail(
                album = album,
                url = thumb_info.url,
                width = int(thumb_info.width) * thumbratio,
                height = int(thumb_info.height) * thumbratio
            )
        thumbnail.save()
        thumb_count += 1
    print "    o cached %d thumbnail(s) for the album" % thumb_count

    # Fetch photos
    thumbsize = settings.PHOTO_THUMB_SIZE
    gthumbsize = googlify_image_size(thumbsize)
    thumbratio = (float(thumbsize) / (float(gthumbsize)))
    image_size = 640
    photo_feed = gd_client.GetFeed('/data/feed/api/user/%s/albumid/%s' \
                                   '?kind=photo&thumbsize=%d&imgmax=%d' \
                                   % ('seb.d.martin', album.id, gthumbsize, 
                                       image_size))
    for media_info in photo_feed.entry:
        print "    o media: %s" % media_info.media.title.text
        # Get the create time from the EXIF if available (date pic was taken)
        create_time = media_info.timestamp.text
        if hasattr(media_info.exif, 'time') and \
           media_info.exif.time.text != '':
            create_time = media_info.exif.time.text
        media = TempMedia(
                id = media_info.gphoto_id.text,
                album = album,
                url = media_info.content.src,
                width = int(media_info.width.text),
                height = int(media_info.height.text),
                description = media_info.media.description.text or '',
                mime = media_info.content.type,
                file_name = media_info.media.title.text,
                create_time = datetime.fromtimestamp(
                    int(create_time[:-3])),
                edit_time = format_date(media_info.updated.text)
            )
        # See if this is a video
        for content in media_info.media.content:
            if content.medium == 'video':
                media.url = content.url
                media.mime = content.type

        media.save()

        # Fetch media thumbnail(s)
        for thumb_info in media_info.media.thumbnail:
            thumbnail = TempMediaThumbnail(
                    media = media,
                    url = thumb_info.url,
                    width = int(thumb_info.width) * thumbratio,
                    height = int(thumb_info.height) * thumbratio
                )
            thumbnail.save()


# Update live tables
def merge_from_temp(table, delete_temp=False):
    from django.db import connection
    cursor = connection.cursor()

    # SQL bits that will be used a few times..
    join_clause = '%(table)s AS t1 %%s JOIN temp_%(table)s AS t2 ' \
                  'ON t1.id = t2.id' % {'table' : table._meta.db_table}

    # update existing records
    field_names = []
    for field in table._meta.fields:
        if field.rel == None:
            field_names.append(field.name)
        else:
            field_names.append('%s_%s' % (field.name, field.rel.field_name))
    set_clause = ', '.join(['t1.%(f)s = t2.%(f)s' % {'f' : f} 
                            for f in field_names])
    cursor.execute('UPDATE %s SET %s' % (join_clause % 'INNER', set_clause))
    cursor.execute('DELETE t1.* FROM %s WHERE t2.id IS NULL' \
            % (join_clause % 'LEFT'))
    cursor.execute('INSERT INTO %s SELECT t2.* FROM %s WHERE t1.id is NULL' \
            % (table._meta.db_table, join_clause % 'RIGHT'))
    if delete_temp == True:
        cursor.execute("DELETE FROM temp_%s" % table._meta.db_table)

merge_from_temp(Album, delete_temp = True)
merge_from_temp(AlbumThumbnail, delete_temp = True)
merge_from_temp(Media, delete_temp = True)
merge_from_temp(MediaThumbnail, delete_temp = True)
