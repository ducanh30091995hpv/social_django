from allauth import socialaccount
from allauth.account.utils import user_field
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.utils.translation import gettext as _
from .models import user_profile, share_link, share_link_page, create_share_link

from var_dump import var_dump
from django.core.files.storage import FileSystemStorage
from core import settings
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
import requests
import base64
import os, binascii
from user.models import share_link, share_link_page, create_share_link
from django.http import HttpResponse
from django.http import HttpResponseRedirect

# Create your views here.


def register(request):
    dang_ky = _("Đăng Ký")
    dang_nhap = _("Đăng Nhập")
    text_1 = _("Bạn đã có tài khoản?")
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            obj = User.objects.get(username=username, email=email)
            err_user_email = _("Tên tài khoản hoặc email đã tồn tại")
            return render(request, "register.html", {"err_user_email": err_user_email, "dang_ky": dang_ky, "dang_nhap": dang_nhap, "text_1": text_1})
        except User.DoesNotExist:
            obj = User.objects.create_user(username=username, email=email, password=password)
            obj.save()
            return render(request, "register.html", {"dang_ky": dang_ky, "dang_nhap": dang_nhap, "text_1": text_1})
    else:
        return render(request, "register.html", {"dang_ky": dang_ky, "dang_nhap": dang_nhap, "text_1": text_1})


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("home")
        else:
            return redirect("user-register")
    else:
        return redirect("user-register")


def logout(request):
    auth.logout(request)
    return redirect("home")


def profile_user(request):

    user_logged = request.user
    user_1 = User.objects.get(id=user_logged.id)
    user_2 = user_profile.objects.get(profile_user=user_logged.id)

    social = settings.SOCIAL_ARR

    account_provider = SocialAccount.objects.values("provider").filter(user_id=user_logged.id)

    return render(request, "main_profile.html", {"user_1": user_1, "user_2": user_2, "social": social, "account_provider": account_provider})


def chanel(request):
    user_logged = request.user
    user_1 = User.objects.get(id=user_logged.id)
    user_2 = user_profile.objects.get(profile_user=user_logged.id)
    social = settings.SOCIAL_ARR
    account_provider = SocialAccount.objects.values("provider").filter(user_id=user_logged.id)
    account_provider1 = SocialAccount.objects.values("id", "provider", "uid").filter(user_id=user_logged.id)
    for i in account_provider1:
        if i["provider"] == "facebook":
            for k in user_profile.get_token_id(i["id"]):
                page_fb = requests.get("https://graph.facebook.com/v12.0/" + i["uid"] + "/accounts/page_show_list?fields=picture{height,width,url},name,access_token,category,link&access_token=" + k.token).json()

        if i["provider"] == "linkedin_oauth2":
            for k in user_profile.get_token_id(i["id"]):
                abc = requests.get("https://api.linkedin.com/v2/me?projection=(picture-url,id,firstName,lastName,profilePicture(displayImage~:playableStreams))&oauth2_access_token=" + k.token).json()

        if i["provider"] == "twitter":
            token_client_id_twitter = ""
            token_secret_id_twitter = ""
            for a in user_profile.get_token_twitter(i["provider"]):
                token_client_id_twitter = a.client_id
                token_secret_id_twitter = a.secret
            for k in user_profile.get_token_id(i["id"]):
                url = "https://api.twitter.com/oauth2/token"
                payload = "grant_type=client_credentials"
                headers = {
                    "Authorization": "Basic " + base64.b64encode(bytes(token_client_id_twitter + ":" + token_secret_id_twitter, "utf-8")).decode(),
                    "Content-Type": "application/x-www-form-urlencoded",
                }

                response = requests.request("POST", url, headers=headers, data=payload)

                url1 = "https://api.twitter.com/1.1/users/show.json?user_id=" + i["uid"]
                payload1 = {}
                headers1 = {
                    "Authorization": "Bearer " + response.json()["access_token"],
                }
                response1 = requests.request("GET", url1, headers=headers1, data=payload1)
                twitter1 = response1.json()

        if i["provider"] == "reddit":
            for k in user_profile.get_token_id(i["id"]):
                headers = {"User-Agent": "MyAPI/0.0.1"}
                headers = {**headers, **{"Authorization": f"bearer " + k.token}}
                try:
                    reddit1 = requests.get("https://oauth.reddit.com/user/adsmovietnam/about", headers=headers).json()
                    s = reddit1["data"]["subreddit"]["icon_img"]
                    s.rfind("?")
                    reddit1 = {
                        "title": reddit1["data"]["subreddit"]["title"],
                        "image": s[: s.rfind("?")],
                        "desscription": reddit1["data"]["subreddit"]["public_description"],
                        "name": reddit1["data"]["subreddit"]["display_name_prefixed"],
                        "url": "https://www.reddit.com" + reddit1["data"]["subreddit"]["url"],
                    }

                except ValueError:  # includes simplejson.decoder.JSONDecodeError
                    reddit1 = {
                        "error": "Lỗi Thời Gian Connect Reddit! Xin Vui Lòng Connect Lại Reddit",
                    }
        if i["provider"] == "pinterest":
            for k in user_profile.get_token_id(i["id"]):
                get_user_header = {"Authorization": "Bearer " + k.token}
                try:
                    r = requests.get("https://api.pinterest.com/v5/user_account", headers=get_user_header)
                    pinterest_user = {"name": r.json()["username"], "image": r.json()["profile_image"], "url": "https://www.pinterest.com/" + r.json()["username"], "type": r.json()["account_type"]}
                except ValueError:  # includes simplejson.decoder.JSONDecodeError
                    pinterest_user = {
                        "error": "Lỗi Thời Gian Connect Pinterest! Xin Vui Lòng Connect Lại Pinterest",
                    }

    return render(
        request, "main_chanel.html", {"user_1": user_1, "user_2": user_2, "social": social, "account_provider": account_provider, "page_fb": page_fb, "abc": abc, "twitter1": twitter1, "reddit1": reddit1, "pinterest_user": pinterest_user}
    )


def update_user(request):
    user_logged = request.user

    if request.method == "POST":

        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        username = request.POST["username"]
        address = request.POST["address"]

        if request.FILES.getlist("fielduploader[]"):
            image = request.FILES.getlist("fielduploader[]")
            user_profile.objects.update(profile_image=image[0])
            fss = FileSystemStorage()
            fss.save(image[0].name, image[0])

        var_dump(first_name + last_name + email + phone + username + address)
        if first_name:
            User.objects.filter(id=user_logged.id).update(first_name=first_name)
        if last_name:
            User.objects.filter(id=user_logged.id).update(last_name=last_name)
        if email:
            User.objects.filter(id=user_logged.id).update(email=email)
        if username:
            User.objects.filter(id=user_logged.id).update(username=username)
        if phone:
            user_profile.objects.filter(profile_user=user_logged.id).update(phone=phone)
        if address:
            user_profile.objects.filter(profile_user=user_logged.id).update(address=address)

        return redirect("/user/profile/")

    else:

        return redirect("/user/profile/")


def post_bai(request):
    user_logged = request.user
    user_1 = User.objects.get(id=user_logged.id)
    user_2 = user_profile.objects.get(profile_user=user_logged.id)
    social = settings.SOCIAL_ARR
    account_provider = SocialAccount.objects.values("provider").filter(user_id=user_logged.id)

    data123 = user_profile.get_token_app_accounts_user_logded(user_logged.id)

    return render(request, "main_post.html", {"user_1": user_1, "user_2": user_2, "social": social, "account_provider": account_provider, "data123": data123})


def create_index_user(request):
    share_link1 = share_link.objects.all()
    return render(request, "create_index.html", {"share_link1": share_link1})


def create_share_user(request):

    if request.method == "POST":
        name = request.POST["share_name"]
        code = (binascii.b2a_hex(os.urandom(30))).decode()
        address = request.POST["address"]
        phone = request.POST["phone"]
        code_invite = (binascii.b2a_hex(os.urandom(10))).decode()
        by_invite = request.POST["by_invite"]
        try:
            obj = share_link.objects.get(code=code)
            err_share_user_id = _("Code đã tồn tại")
            return render(request, "create.html", {"err_share_user_id": err_share_user_id})
        except share_link.DoesNotExist:
            obj = share_link.objects.create(name=name, code=code, address=address, phone=phone, code_invite=code_invite, by_invite=by_invite)
            obj.save()
            return redirect("create-index-user")
    else:
        return render(request, "create.html")


def edit_share_user(request, id):
    data_share_link = share_link.objects.get(id=id)
    return render(request, "edit_share.html", {"data_share_link": data_share_link})


def update_share_user(request, id):

    data_share_link = share_link.objects.get(id=id)
    if request.method == "POST":
        name = request.POST["share_name"]
        address = request.POST["address"]
        phone = request.POST["phone"]
        by_invite = request.POST["by_invite"]
        share_link.objects.filter(id=id).update(name=name, address=address, phone=phone, by_invite=by_invite)
        return redirect("create-index-user")
    else:
        return render(request, "edit_share.html", {"data_share_link": data_share_link})


def delete_share_user(request, id):

    data_share_link = share_link.objects.get(id=id)
    data_share_link.delete()
    return redirect("create-index-user")


def delete_short_ly(request, id):

    data_share_link = create_share_link.objects.get(id=id)
    data_share_link.delete()
    # obj = data_share_link.update(name=name, code=code, address=address, phone=phone)
    # obj.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


# def copy_short_ly(request):

#     data_share_link = create_share_link.objects.get(id=id)
#     data_share_link.delete()
#     # obj = data_share_link.update(name=name, code=code, address=address, phone=phone)
#     # obj.save()
#     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def short_link(request):
    return render(request, "short_link.html")


def short_ly(request, slug):
    data_share_link = create_share_link.objects.get(link_share=slug)
    link_rd = data_share_link.page_link
    code_user = data_share_link.code_user
    return render(request, "short_ly.html", {"link_rd": link_rd, "slug": slug, "code_user": code_user})


def count_view(request):
    if request.method == "POST":
        code = request.POST["code_user"]
        page_link = request.POST["page_link"]
        data_link = share_link.objects.get(code=code)
        if data_link:
            share_link_data = share_link_page.objects.get(code=code)
            try:
                share_link_page.objects.filter(code=code).update(count_view_site=share_link_data.count_view_site + 1)
                return render(request, "real_link.html")
            except share_link_page.DoesNotExist:
                obj = share_link_page.objects.create(page_link=page_link, code=code, user_id=1, count_view_site=1)
                obj.save()
                return render(request, "real_link.html")
        else:
            return render(request, "real_link.html")
    else:
        return render(request, "real_link.html")

def real_link(request):
    return render(request, "real_link.html")


def create_short_link(request, id):
    data_share_link = share_link.objects.get(id=id)
    data_share_link_data = create_share_link.objects.filter(code_user=data_share_link.code)
    stt_code = 0
    return render(request, "create_short_link.html", {"data_share_link": data_share_link, "data_share_link_data": data_share_link_data, "stt_code": stt_code})

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def eva_short_link(request):
    if request.method == "POST":
        code_user = request.POST["code_user"]
        page_link = request.POST["link_create"]
        link_share = (binascii.b2a_hex(os.urandom(5))).decode()
        obj_data_link = create_share_link.objects.filter(code_user=code_user, page_link=page_link)
        link_result = "https://127.0.0.1:8000/en/user/short.ly/" + link_share
        if obj_data_link.exists():
            err_share_code = _("Code đã tồn tại")
            return HttpResponse(err_share_code)
        else:
            obj = create_share_link.objects.create(page_link=page_link, code_user=code_user, link_share=link_share, count_view_site = 1)
            obj.save()
            return HttpResponse(link_result)
    else:
        return render(request, "real_link.html")

def count_view_short_ly(request):
    if request.method == "POST":
        link_share = request.POST["slug"]
        data_link = create_share_link.objects.get(link_share=link_share)
        if data_link:
            create_share_link.objects.filter(link_share=link_share).update(count_view_site=data_link.count_view_site + 1)
            return HttpResponse(data_link.page_link)
        else:
            return render(request, "real_link.html")
    else:
        return render(request, "real_link.html")