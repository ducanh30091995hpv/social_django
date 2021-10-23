from django.db import models
from django.contrib.auth.models import User, auth
from allauth.socialaccount.models import SocialApp, SocialToken, SocialAccount
import requests
from django.db import connection
import json
from core import settings
import base64
from time import gmtime, strftime
from bs4 import BeautifulSoup
from django.contrib.sites.models import Site
import os
from requests_oauthlib import OAuth1
import urllib.parse


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
            reddit1 = requests.get(settings.LINK_API_REDDIT + 'user/adsmovietnam/about', headers=headers).json()  
            s = reddit1['data']['subreddit']['icon_img']
            s.rfind("?")
            reddit12 = [reddit1['data']['subreddit']['display_name'], token, s[:s.rfind("?")], 'reddit']
        except:
            reddit12 = []   
        return reddit12
    
    
    def get_linkedin_user(token):
        c = requests.get(settings.LINK_API_LINKEDIN + 'me?projection=(id,firstName,lastName,profilePicture(displayImage~:playableStreams))&oauth2_access_token='+token).json()
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
    
    def get_id_twitter(provider):
        get_token = SocialAccount.objects.only('id').filter(provider = provider)
        return get_token
    
    def get_twitter_oauth1_token_secret(id):
        id = SocialToken.objects.only('token', 'token_secret').filter(account_id = id)
        return id
    
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
    
    def get_bear_token_twitter(token_client_id_twitter, token_secret_id_twitter):
        payload='grant_type=client_credentials'
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(bytes(token_client_id_twitter+':'+token_secret_id_twitter, "utf-8")).decode(),
            'Content-Type': 'application/x-www-form-urlencoded',
        }
                
        response = requests.request("POST", settings.LINK_OAUTH_TWITTER, headers=headers, data=payload)
        if(response.json()['access_token']):
            return response.json()['access_token']
        else:
            return 'Lỗi'
    
    def get_uid_linkedin_oauth2(provider):
        uid = ''
        abc = SocialAccount.objects.only('uid').filter(provider = provider)
        for i in abc:
            uid = str(i.uid)
        return uid
        

class user_Post(models.Model):
    user_id = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    array_app = models.TextField(null=True)
    array_img = models.TextField(null=True, default='')
    tag = models.TextField(null=True, default='')
    link = models.TextField(null=True)
    date_up = models.CharField(null=True, max_length=255, default='')
    time_up = models.CharField(null=True, max_length=255, default='')
    text_body = models.TextField(null=True)
    title = models.CharField(null=True, max_length=255)
    create_at = models.DateTimeField(auto_now=strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    activated = models.BooleanField(default=False)
    id_app_post = models.TextField(null=True, default='')
    
    def tag_facebook(tag):
        tag = str(tag).split(',')
        dem_tag = len(tag)
        for i in range(0,dem_tag):
            tag[i] = '%23'+tag[i]
        tag = ' '.join(tag)
        return '\n'+tag
    
    def post_link(provider, textbody, link, tag, token, title):
        
        if(provider == 'facebook'):
            abc = requests.post(settings.LINK_API_FB + 'me/feed?message=' + str(textbody).replace('#', '%23') + user_Post.tag_facebook(tag) + '&link='+link+'&access_token=' + token).json()
            if(abc['id']):
                return abc['id'] 
            else:
                return 'Lỗi'
        if(provider == 'twitter'):
            token_client_id_twitter = ''
            token_secret_id_twitter = ''
            id_twitter = 0
            token_client_id_twitter1 = ''
            token_secret_id_twitter2 = ''
            
            for a in user_profile.get_token_twitter('twitter'):
                token_client_id_twitter = a.client_id
                token_secret_id_twitter = a.secret
            for i in user_profile.get_id_twitter('twitter'):
                id_twitter = i.id
            for i in user_profile.get_twitter_oauth1_token_secret(id_twitter):
                token_client_id_twitter1 = i.token
                token_secret_id_twitter2 = i.token_secret
            
            url = settings.LINK_API_TWITTER + 'statuses/update.json?status=' + urllib.parse.quote_plus(textbody) + user_Post.tag_facebook(tag)
            auth = OAuth1(token_client_id_twitter, token_secret_id_twitter, token_client_id_twitter1, token_secret_id_twitter2)
            abc = requests.post(url, auth=auth).json()
            if(abc['id_str']):
                return abc['id_str']
            else:
                return 'Looix'
                
            #print(token_client_id_twitter + '|' + token_secret_id_twitter + '|' + token_client_id_twitter1 + '|' + token_secret_id_twitter2)
            
        if(provider == 'linkedin_oauth2'):
            url = settings.LINK_API_LINKEDIN + "shares"
            payload = json.dumps({
                "content": {
                    "contentEntities": [
                    {
                        "entityLocation": link,
                        "thumbnails": [
                        {
                            "resolvedUrl": ""
                        }
                        ]
                    }
                    ],
                    "title": title
                },
                "distribution": {
                    "linkedInDistributionTarget": {}
                },
                "owner": "urn:li:person:" + user_profile.get_uid_linkedin_oauth2(provider),
                "subject": title,
                "text": {
                    "text": textbody + str(user_Post.tag_facebook(tag)).replace('%23', '#')
                }
            })
            headers = {
                'Authorization': 'Bearer ' +  token,
                'Content-Type': 'application/json',
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            if(response.json()['activity']):
                return response.json()['activity']
            else:
                return 'Lỗi'
                
        
        


        
    
        
    
    
    

    
    


