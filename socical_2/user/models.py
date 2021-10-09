from django.db import models
from django.contrib.auth.models import User, auth
from allauth.socialaccount.models import SocialApp, SocialToken
import requests
from django.db import connection
import json
from core import settings


class user_profile(models.Model):
    profile_user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    profile_image = models.ImageField(default='/image/helen.jpg')
    address = models.TextField()
    phone = models.CharField(max_length=50)
    
    def get_facebook_page(token, uid):
        page_fb = requests.get(settings.LINK_API_FB + uid + '/accounts/page_show_list?fields=picture%7Bheight%2Cwidth%2Curl%7D%2Cname%2Caccess_token&access_token=' + token).json()
        return page_fb

    

    def get_token_id(account_id):
        get_token = SocialToken.objects.only('token').filter(account_id = account_id)
        return get_token
    
    def get_token_twitter(provider):
        get_token = SocialApp.objects.only('client_id', 'secret').filter(provider = provider)
        return get_token
    
    def get_token_app_accounts_user_logded(user_logged_accounts):
        cursor = connection.cursor()
        cursor.execute("SELECT socialaccount_socialaccount.provider, socialaccount_socialaccount.uid, socialaccount_socialaccount.id, socialaccount_socialtoken.token FROM socialaccount_socialaccount JOIN socialaccount_socialtoken ON socialaccount_socialaccount.id = socialaccount_socialtoken.account_id WHERE user_id =" + str(user_logged_accounts))
        data1 = cursor.fetchall()

        array_list = []
        for i in data1:
            if(i[0] == 'facebook'):
                fanpage_fb = user_profile.get_facebook_page(i[3], i[1])
                
                for i in fanpage_fb['data']:
                    a = [i['name'], i['access_token'], i['picture']['data']['url'], 'facebook']
                    array_list.append(a)


        
        return array_list
    
    

    
    


