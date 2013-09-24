from django.db import models

# Abstract models
class _AThumbnail(models.Model):
    url = models.URLField(verify_exists = False, max_length = 512)
    width = models.SmallIntegerField()
    height = models.SmallIntegerField()

    class Meta:
        abstract = True
        ordering = ['width', 'height']

class _AAlbum(models.Model):
    id = models.CharField(max_length = 32, primary_key = True)
    title = models.CharField(max_length = 128)
    description = models.CharField(max_length = 128, blank = True)
    visible = models.BooleanField()
    create_time = models.DateTimeField()
    edit_time = models.DateTimeField()

    class Meta:
        abstract = True

class _AMedia(models.Model):
    id = models.CharField(max_length = 32, primary_key = True)
    url = models.URLField(verify_exists = False, max_length = 512)
    width = models.SmallIntegerField()
    height = models.SmallIntegerField()
    description = models.CharField(max_length = 128)
    mime = models.CharField(max_length = 64)
    file_name = models.CharField(max_length = 128)
    create_time = models.DateTimeField()
    edit_time = models.DateTimeField()

    class Meta:
        abstract = True

    def video_total_width(self):
        return self.width + 100

    def video_total_height(self):
        return self.height + 100

# Production models
class Album(_AAlbum):
    pass

class AlbumThumbnail(_AThumbnail):
    album = models.ForeignKey(Album)

class Media(_AMedia):
    album = models.ForeignKey(Album)

class MediaThumbnail(_AThumbnail):
    media = models.ForeignKey(Media)

# Temp models
# -- these models are exactly the same as the production models, except they
#    are used to merge the data from picasa web services with existing data
#    without disturbing the live site.
class TempAlbum(_AAlbum):
    class Meta:
        db_table = 'temp_albums_album'

class TempAlbumThumbnail(_AThumbnail):
    album = models.ForeignKey(TempAlbum)
    class Meta:
        db_table = 'temp_albums_albumthumbnail'

class TempMedia(_AMedia):
    album = models.ForeignKey(TempAlbum)
    class Meta:
        db_table = 'temp_albums_media'
class TempMediaThumbnail(_AThumbnail):
    media = models.ForeignKey(TempMedia)
    class Meta:
        db_table = 'temp_albums_mediathumbnail'
