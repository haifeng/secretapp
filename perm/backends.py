from django.contrib.auth.models import User
from django.conf import settings
from facebook import Facebook

from socialauth.models import FacebookUserProfile, AuthMeta
from socialauth.lib.facebook import get_user_info, get_facebook_signature

from tools import clear_permissions
from datetime import datetime
import random

FACEBOOK_API_KEY = getattr(settings, 'FACEBOOK_API_KEY', '')
FACEBOOK_SECRET_KEY = getattr(settings, 'FACEBOOK_SECRET_KEY', '')
FACEBOOK_URL = getattr(settings, 'FACEBOOK_URL', 'http://api.facebook.com/restserver.php')

def get_fb_data(facebook, fb_user):
    fb_data = None
    try_count = 0
    max_count = 3
    while not fb_data and try_count < max_count:
        try:
            fb_data = facebook.users.getInfo([fb_user], ['uid', 'email', 'about_me', 'first_name', 'last_name', 'pic_big', 'pic', 'pic_square', 'current_location', 'profile_url'])
            break
        except Exception, e:
            try_count += 1
            print e
    if not fb_data:
        return None

    return fb_data[0]

class ClaimFacebookBackend:
    def authenticate(self, request):
        """
        Started at 
            http://github.com/uswaretech/Django-Socialauth/blob/master/socialauth/auth_backends.py
        
        Made massive improvements with error handling.
        """
        facebook =  Facebook(settings.FACEBOOK_API_KEY, settings.FACEBOOK_SECRET_KEY)
        check = facebook.check_session(request)
        clear_permissions(request) # for internal perms
        try:
            fb_user = facebook.users.getLoggedInUser()
            fb_data = get_fb_data(facebook, fb_user)
            
            profile = FacebookUserProfile.objects.get(facebook_uid = unicode(fb_user))            
        except FacebookUserProfile.DoesNotExist:
            username = 'FB:%s' % fb_data['uid']
            fb_user,new_user = User.objects.get_or_create(username = username)
            fb_user.is_active = True
            fb_user.first_name = fb_data['first_name']
            fb_user.last_name = fb_data['last_name']
            fb_user.email = fb_data['email']
            fb_user.save()
            
            try:
                profile = FacebookUserProfile(facebook_uid= unicode(fb_data['uid']), user=fb_user)
                profile.save()
                auth_meta = AuthMeta(user=user, provider='Facebook').save()
            except:
                pass
        except Exception, e:
            return None
            #print unicode(e)
        
        user = profile.user
        
        if user.is_active:
            if fb_data:        
                user.email = fb_data['email']
                user.save()
                profile.profile_image_url = fb_data['pic']
                profile.profile_image_url_big = fb_data['pic_big']
                profile.profile_image_url_small = fb_data['pic_square']
                profile.location = unicode(fb_data['current_location'])
                profile.about_me = unicode(fb_data['about_me'])[:100]
                profile.url = unicode(fb_data['profile_url'])
                profile.save()        
            return user
        else:
            return None

    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
