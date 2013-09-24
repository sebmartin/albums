################################################################################
# Wrapper class around google's Picasa Web Albums Data API
# http://code.google.com/apis/picasaweb/overview.html
#
# Written by: Sebastien Martin, May 2008
################################################################################

from xml.dom import minidom
import os
from urllib import urlopen
import datetime

class Account(object):
    '''A picasa web albums account wrapper class.  This class will request
       information about a google account and parse the XML response.  The 
       relevant information is made easily accessible from member 
       variables and functions.
                 
       A gallery is defined as a group of albums, where each album has one or
       more photos.'''

    def __init__(self, user_id):
        '''Main constructor which takes the URL for an API request then
           retrieves and parses the XML response.'''

        # Member variables
        self.__user_id = user_id
        self.attributes = {}
        self.albums = {}

        # Open an HTTP request
        try:
            fapi = urlopen('http://picasaweb.google.com'+
                           '/data/feed/api/user/'+user_id+'/?kind=album')
        except:
            return

        # Pull info about the gallery
        doc = minidom.parse(fapi)
        self.__parse_gallery(doc.firstChild)

        # Close file handle to the API response
        fapi.close()

    def __parse_gallery(self, node):
        '''Helper method to parse and extract relevant information from the
           root element of a 'get albums' response'''

        for child in node.childNodes:
            childName = child.localName.lower()
            childPrefix = str(child.prefix).lower()

            # Get info from simple child node values
            if childName in ['id', 'title', 'subtitle', 'updated']: 
                if child.firstChild != None:
                    self.attributes[childName] = child.firstChild.nodeValue
                else:
                    self.attributes[childName] = ''

            # Parse the album elements
            elif childName == 'entry':
                # TODO: use the Album class instead
                # ie, Album.build_from_node(child)
                album = Album(self.__user_id, node = child)
                self.albums[album['id']] = album

class Album(dict):
    '''Picasa web album wrapper class.  Objects of this type are instantiated
       from the Account class.'''

    def __init__(self, user_id, node=None, album_id=None):
        '''Class constructor.  This type of object should not be manually
           instantiated.  When an Account object parses the XML response
           it will create an instance of this class for each album in the
           account.
           
           To manually instantiate an object use the static method
           get_album_by_id()''' 

        # Store the params
        self.__user_id = user_id

        # If this object was instantiated from the Album parser, load the
        # album's info from the specified DOM node object
        if node != None:
            album_info = {}
            for child in node.childNodes:
                childName = child.localName.lower()
                childPrefix = str(child.prefix).lower()

                # Get info from simple child node values
                if childName in ('id', 'title', 'timestamp', 'summary'):
                    self[childName] = child.firstChild.nodeValue

                # The thumbnail is buried a bit deeper..
                elif childName == 'group' and childPrefix == 'media':
                    self.__parse_album_media(child)

        elif album_id != None:
            # TODO
            pass

    def __parse_album_media(self, node):
        '''Helper function to parse the media:group elements in an entry (album)
        element.'''

        for child in node.childNodes:
            # Get the thumbnail
            if child.localName.lower() == 'thumbnail' and \
               'url' in child.attributes.keys():
                self['thumbnail'] = \
                    child.attributes['url'].value
                                                 
    def get_photos(self):
        # TODO
# URL example:
# http://picasaweb.google.com/data/feed/api/user/gee.sucka.foo/albumid/5185022091618895361?kind=photo
#                                                ^^^^^^^^^^^^^         ^^^^^^^^^^^^^^^^^^^
        pass
