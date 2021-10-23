from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from dateutil import parser
from bs4 import BeautifulSoup
from core import settings
import os

class UserConfig(AppConfig):
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'
    
    def job_cache():
        os.system('py manage.py clear_cache')
    
    def job():
        from user.models import user_Post
        array_id_post = []
        abc = user_Post.objects.filter(activated = 0)

        for i in abc:
            datetime_object = i.date_up + ' ' + i.time_up
            time_cover = parser.parse(datetime_object)
            text_body = BeautifulSoup(i.text_body, "html.parser")
            if(time_cover == datetime.now().replace(second=0, microsecond=0) and i.id_app_post == ''):
                array_app = str(i.array_app).split('|')
                dem_token = len(array_app)
                for o in range(0,dem_token):
                    if(o%2==0):
                        id_post = user_Post.post_link(array_app[o], text_body.get_text(), i.link, i.tag, array_app[1+o], i.title)
                        array_id_post.append(id_post)  
                    else:
                        print('không khớp')        
                user_Post.objects.filter(id = i.id).update(id_app_post = settings.cover_list_to_string(array_id_post))  
                user_Post.objects.filter(id = i.id).update(activated = 1)                 
                print('thanh cong')
            else:
                print('con ccccc')

    def job3():
        import requests
        import json
        url = settings.LINK_API_LINKEDIN + "shares"
        payload = json.dumps({
            "content": {
                "contentEntities": [
                {
                    "entityLocation": "https://adsmo.vn/",
                    "thumbnails": [
                    {
                        "resolvedUrl": ""
                    }
                    ]
                }
                ],
                "title": "Test Share with Contentaaaaaaaaaaaaabbbbbb"
            },
            "distribution": {
                "linkedInDistributionTarget": {}
            },
            "owner": "urn:li:person:kIzh7UUR-4",
            "subject": "Test Share Subjectaaaaaaaaaaaabbbbbb",
            "text": {
                "text": "Test Share!aaaaaaaaaaaaaaaaaabbbbb"
            }
        })
        headers = {
            'Authorization': 'Bearer AQVCKNNSvBy0BszHl2AdnUbH8tlTfn-a_R_jn41L_SE8jHZdyGYJ4FqnmtDnXM161ZtbcWcaIJjafjeVlAItqnVfa_upXJ8VzifyT9FRn9e0rzUD1ALdu_S8AUn_Woxa0E-EUwMNHNzTtuG5ILIHj5xg42rjCsRi12aheQoytK8avRiIk60qrR3amNR28XRrEgXrqlraWm-fTdjFms2NIsbLxafxYqqsrO28OcAWDhTNzsXm5ujO5g4PHaMn2hWU9T-5srA38mgFTtZHTe-nSUV5jxjBfPx7os25MbztI-hWTGiLLxsW90c2eANrA18kcOhTnEEQ4UbFIhBByf8JL7wo7p95AA',
            'Content-Type': 'application/json',
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.json()['activity'])
        
    def ready(self):
        scheduler = BackgroundScheduler()
        scheduler.add_job(UserConfig.job_cache, 'interval', seconds=5)
        #scheduler.add_job(UserConfig.job3, 'interval', seconds=59)
        scheduler.add_job(UserConfig.job, 'interval', seconds=10, jitter=120)
        scheduler.start()


