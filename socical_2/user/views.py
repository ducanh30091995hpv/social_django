

from allauth import socialaccount
from allauth.account.utils import user_field
from django.contrib.auth import authenticate
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.utils.translation import gettext as _
from .models import user_profile
import json
from var_dump import var_dump
from django.core.files.storage import FileSystemStorage
from core import settings
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
import requests
import base64
from core import settings
from werkzeug.utils import secure_filename
from user.models import user_Post




# Create your views here.


def register(request):
    dang_ky = _('Đăng Ký')
    dang_nhap = _('Đăng Nhập')
    text_1 = _('Bạn đã có tài khoản?')
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        try:
            obj = User.objects.get(username=username, email=email)
            err_user_email = _('Tên tài khoản hoặc email đã tồn tại')
            return render(request, 'register.html', {'err_user_email': err_user_email, 'dang_ky': dang_ky, 'dang_nhap':dang_nhap, 'text_1': text_1})
        except User.DoesNotExist:
            obj = User.objects.create_user(username=username, email=email, password=password)
            obj.save()
            return render(request, 'register.html',{'dang_ky': dang_ky, 'dang_nhap': dang_nhap, 'text_1': text_1})
    else:
        return render(request, 'register.html', {'dang_ky': dang_ky, 'dang_nhap': dang_nhap, 'text_1': text_1})
    
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            return redirect('user-register')
    else:
        return redirect('user-register')

def logout(request):
    auth.logout(request)
    return redirect('home')

def profile_user(request):
    
    user_logged = request.user
    user_1 = User.objects.get(id = user_logged.id)
    user_2 = user_profile.objects.get(profile_user = user_logged.id)
    
    social = settings.SOCIAL_ARR
    
    account_provider = SocialAccount.objects.values('provider').filter(user_id = user_logged.id)

    return render(request, 'main_profile.html', {'user_1': user_1, 'user_2': user_2, 'social': social, 'account_provider': account_provider})

def chanel(request):
    user_logged = request.user
    user_1 = User.objects.get(id = user_logged.id)
    user_2 = user_profile.objects.get(profile_user = user_logged.id)
    social = settings.SOCIAL_ARR
    account_provider = SocialAccount.objects.values('provider').filter(user_id = user_logged.id)
    account_provider1 = SocialAccount.objects.values('id', 'provider', 'uid').filter(user_id = user_logged.id)
    for i in account_provider1:
        if(i['provider'] == 'facebook'):
            for k in user_profile.get_token_id(i['id']):
                page_fb = requests.get('https://graph.facebook.com/v12.0/'+i['uid']+'/accounts/page_show_list?fields=picture{height,width,url},name,access_token,category,link&access_token='+k.token).json()

        if(i['provider'] == 'linkedin_oauth2'):
            for k in user_profile.get_token_id(i['id']):
                abc = requests.get('https://api.linkedin.com/v2/me?projection=(picture-url,id,firstName,lastName,profilePicture(displayImage~:playableStreams))&oauth2_access_token='+k.token).json()
                
        if(i['provider'] == 'twitter'):
            token_client_id_twitter = ''
            token_secret_id_twitter = ''
            for a in user_profile.get_token_twitter(i['provider']):
                token_client_id_twitter = a.client_id
                token_secret_id_twitter = a.secret
            for k in user_profile.get_token_id(i['id']):

                url1 = "https://api.twitter.com/1.1/users/show.json?user_id="+i['uid']

                payload1={}
                headers1 = {
                'Authorization': 'Bearer '+ user_profile.get_bear_token_twitter(token_client_id_twitter, token_secret_id_twitter),
                }
                response1 = requests.request("GET", url1, headers=headers1, data=payload1)
                twitter1 = response1.json()
                
        if(i['provider'] == 'reddit'):
            for k in user_profile.get_token_id(i['id']):
                headers = {'User-Agent': 'MyAPI/0.0.1'}
                headers = {**headers, **{'Authorization': f'bearer '+k.token}}
                try:
                    reddit1 = requests.get('https://oauth.reddit.com/user/adsmovietnam/about', headers=headers).json()
                    s = reddit1['data']['subreddit']['icon_img']
                    s.rfind("?")
                    reddit1 = {
                        'title': reddit1['data']['subreddit']['title'],
                        'image': s[:s.rfind("?")],
                        'desscription': reddit1['data']['subreddit']['public_description'],
                        'name': reddit1['data']['subreddit']['display_name_prefixed'],
                        'url': 'https://www.reddit.com'+reddit1['data']['subreddit']['url'],
                    }
                   
                except ValueError:  # includes simplejson.decoder.JSONDecodeError
                    reddit1 = {
                        'error': 'Lỗi Thời Gian Connect Reddit! Xin Vui Lòng Connect Lại Reddit',
                    }
        if(i['provider'] == 'pinterest'):
            for k in user_profile.get_token_id(i['id']):
                get_user_header = {
                    'Authorization': 'Bearer ' + k.token
                } 
                try:
                    r = requests.get('https://api.pinterest.com/v5/user_account', headers=get_user_header)
                    pinterest_user = {
                        'name': r.json()['username'],
                        'image': r.json()['profile_image'],
                        'url': 'https://www.pinterest.com/'+r.json()['username'],
                        'type': r.json()['account_type']
                    }
                except ValueError:  # includes simplejson.decoder.JSONDecodeError
                    pinterest_user = {
                        'error': 'Lỗi Thời Gian Connect Pinterest! Xin Vui Lòng Connect Lại Pinterest',
                    }
    

              
    return render(request, 'main_chanel.html', {'user_1': user_1, 'user_2': user_2, 'social': social, 'account_provider': account_provider, 'page_fb': page_fb, 'abc': abc, 'twitter1': twitter1, 'reddit1': reddit1, 'pinterest_user': pinterest_user})

def update_user(request):
    user_logged = request.user

    if (request.method == 'POST'):
        
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        username = request.POST['username']
        address = request.POST['address']
        
        
        if (request.FILES.getlist('fielduploader[]')):
            image = request.FILES.getlist('fielduploader[]')
            user_profile.objects.update(profile_image = image[0])
            fss = FileSystemStorage()
            fss.save(image[0].name, image[0])
        
        if (first_name):
            User.objects.filter(id = user_logged.id).update(first_name = first_name)
        if (last_name):
            User.objects.filter(id = user_logged.id).update(last_name = last_name)
        if (email):
            User.objects.filter(id = user_logged.id).update(email = email)
        if (username):
            User.objects.filter(id = user_logged.id).update(username = username)
        if (phone):
            user_profile.objects.filter(profile_user = user_logged.id).update(phone = phone)
        if (address):
            user_profile.objects.filter(profile_user = user_logged.id).update(address = address)
        
        return redirect('/user/profile/')
    
    else:
        
        return redirect('/user/profile/')
    
    
def post_bai(request):
    user_logged = request.user
    user_1 = User.objects.get(id = user_logged.id)
    user_2 = user_profile.objects.get(profile_user = user_logged.id)
    social = settings.SOCIAL_ARR
    account_provider = SocialAccount.objects.values('provider').filter(user_id = user_logged.id)
    
    data123 = user_profile.get_token_app_accounts_user_logded(user_logged.id)

    return render(request, 'main_post.html', {'user_1': user_1, 'user_2': user_2, 'social': social, 'account_provider': account_provider, 'data123': data123})



def check_post(request):
    user_logged = request.user
    if(request.method == "POST"):
        mang_app = []
        mang_file = []
        tag_a = request.POST['tags']
        links = request.POST['links']
        date1 = settings.cover_datetime(request.POST['date1'])
        hour1 = request.POST['hour1']
        text1 = request.POST['text1']
        title123 = request.POST['title123']
        files = request.FILES.getlist('files[]')
        
        column1RelArray = json.loads(request.POST['column1RelArray'])
        for n in range(0, column1RelArray['length']):
            mang_app.append(column1RelArray[str(n)])
            
        if(files):
            for i in files:
                fss = FileSystemStorage()
                name = fss.save(i.name, i)
                mang_file.append(fss.url(name)) 
        
        user_Post.objects.create(array_app = settings.cover_list_to_string(mang_app), array_img = settings.cover_list_to_string(mang_file), tag = tag_a, link = links, date_up = date1, time_up = hour1, text_body = text1, title = title123, user_id_id = user_logged.id)
        
        return HttpResponse('Thành công!')            
    else: 
        return HttpResponse('Lỗi!')
    

def check_post1(request):
    user_logged = request.user
    if(request.method == "POST"):
        mang_app = []
        mang_file = []
        tag_a = request.POST['tags']
        links = request.POST['links']

        text1 = request.POST['text1']
        title123 = request.POST['title123']
        files = request.FILES.getlist('files[]')
        
        column1RelArray = json.loads(request.POST['column1RelArray'])
        for n in range(0, column1RelArray['length']):
            mang_app.append(column1RelArray[str(n)])
            
        if(files):
            for i in files:
                fss = FileSystemStorage()
                name = fss.save(i.name, i)
                mang_file.append(fss.url(name)) 
            
        user_Post.objects.create(array_app = settings.cover_list_to_string(mang_app), array_img = settings.cover_list_to_string(mang_file), tag = tag_a, link = links, text_body = text1, title = title123, user_id_id = user_logged.id)
        
        return HttpResponse('Thành công')            
    else: 
        return HttpResponse('Lỗi!')
    

        
def manage_post_user(request):
    user_logged = request.user
    user_1 = User.objects.get(id = user_logged.id)
    user_2 = user_profile.objects.get(profile_user = user_logged.id)
    social = settings.SOCIAL_ARR
    account_provider = SocialAccount.objects.values('provider').filter(user_id = user_logged.id)
    dem = range(0,6)
    dem2 = range(0,7)
    data123 = user_profile.get_token_app_accounts_user_logded(user_logged.id)
    
    return render(request, 'check_post.html', {'user_1': user_1, 'user_2': user_2, 'social': social, 'account_provider': account_provider, 'dem': dem, 'dem2': dem2, 'data123': data123})




   
    



