from django.db import models
from django.contrib.auth.models import User, auth
from allauth.socialaccount.models import SocialApp, SocialToken
import requests
from django.db import connection
import json
from core import settings
import base64


class user_profile(models.Model):
    profile_user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    profile_image = models.ImageField(default='/image/helen.jpg')
    address = models.TextField()
    phone = models.CharField(max_length=50)
    
    def get_facebook_page(token, uid):
        page_fb = requests.get(settings.LINK_API_FB + uid + '/accounts/page_show_list?fields=picture%7Bheight%2Cwidth%2Curl%7D%2Cname%2Caccess_token&access_token=' + token).json()
        return page_fb
    
    def get_header_pinterest(token):
        get_user_header = {
            'Authorization': 'Bearer ' + token
        }
        return get_user_header 
    
    def get_boards_pinterest(token):
        r = requests.get(settings.LINK_API_PINTEREST + 'boards', headers=user_profile.get_header_pinterest(token))
        return r
        

    def get_pinterest_page(token):
        r = requests.get(settings.LINK_API_PINTEREST + 'user_account', headers=user_profile.get_header_pinterest(token))
        return r
    
    def get_twitter_user(token, uid):
        for i in user_profile.get_token_twitter('twitter'):
            abc = [i.secret, i.client_id]
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(bytes(abc[1]+':'+abc[0], "utf-8")).decode(),
            'Content-Type': 'application/x-www-form-urlencoded',
        }  
        response = requests.request("POST", settings.LINK_OAUTH_TWITTER, headers=headers, data='grant_type=client_credentials').json()  
        
        url1 = settings.LINK_API_TWITTER + "users/show.json?user_id=" + uid
        headers1 = {
            'Authorization': 'Bearer '+response['access_token'],
        }
        get_data = requests.request("GET", url1, headers=headers1).json()
        
        u = [get_data['name'], token, get_data['profile_image_url_https'], 'twitter']
        
        return u
    
    def get_header_reddit(token):
        headers = settings.HEADER_REDDIT
        headers = {**headers, **{'Authorization': f'bearer '+token}}
        
        return headers
    
    def get_reddit_user(token):
        headers = user_profile.get_header_reddit(token)
        try:
            reddit1 = requests.get('https://oauth.reddit.com/user/adsmovietnam/about', headers=headers).json()  
            s = reddit1['data']['subreddit']['icon_img']
            s.rfind("?")
            reddit12 = [reddit1['data']['subreddit']['display_name'], token, s[:s.rfind("?")], 'reddit']
        except:
            reddit12 = []   
        return reddit12
    
    
    def get_linkedin_user(token):
        c = requests.get(settings.LINK_API_LINKEDIN + 'me?projection=(picture-url,id,firstName,lastName,profilePicture(displayImage~:playableStreams))&oauth2_access_token='+token).json()
        name = c['firstName']['localized']['en_US'] + ' ' + c['lastName']['localized']['en_US']
        image_url = c["profilePicture"]["displayImage~"]["elements"]
        for i in image_url:
            for o in i['identifiers']:
                if(o['identifier']):
                    image_url_1 = o['identifier']
        f = [name, token, image_url_1, 'linkedin_oauth2']
        return f

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
            if(i[0] == 'reddit'):
                reddit_user = user_profile.get_reddit_user(i[3])
                array_list.append(reddit_user)
            if(i[0] == 'twitter'):
                twitter_user = user_profile.get_twitter_user(i[3], i[1])
                array_list.append(twitter_user)
            if(i[0] == 'linkedin_oauth2'):
                linkedin_user = user_profile.get_linkedin_user(i[3])
                array_list.append(linkedin_user)
                
            if(i[0] == 'pinterest'):
                pinterest_user = user_profile.get_pinterest_page(i[3])
                b = [pinterest_user.json()['username'], i[3], pinterest_user.json()['profile_image'], 'pinterest']
                array_list.append(b)

            if(i[0] == 'facebook'):
                fanpage_fb = user_profile.get_facebook_page(i[3], i[1])
                for i in fanpage_fb['data']:
                    a = [i['name'], i['access_token'], i['picture']['data']['url'], 'facebook']
                    array_list.append(a)
            

        return array_list
    
    

    
    


