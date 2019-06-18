import json, time, datetime, os
from django.http import HttpResponse, StreamingHttpResponse
from ics import Calendar, Event
from django.conf import settings
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from .utils import FileManager, Conf
from django.utils.encoding import escape_uri_path

YOUR_CLIENT_ID = Conf.get_str('FoursquareAPP', 'CLIENT_ID')
YOUR_CLIENT_SECRET = Conf.get_str('FoursquareAPP', 'CLIENT_SECRET')
YOUR_REGISTERED_REDIRECT_URI = Conf.get_str('FoursquareAPP', 'REGISTERED_REDIRECT_URI')


try:
    # 实例化调度器
    scheduler = BackgroundScheduler()
    # 调度器使用DjangoJobStore()
    scheduler.add_jobstore(DjangoJobStore(), "default")


    # 每日凌晨执行
    @register_job(scheduler, 'cron', month='*', day='*', hour='0', minute='0', second='0', id='create_history_checkins')
    def create_history_checkins():
        # 添加完整COOKIE，否则需要登录验证
        cs = {
            ### ********* ###
        }
        step_1 = 'https://foursquare.com/oauth2/authenticate?client_id=%s&client_secret=%s&response_type=code&redirect_uri=%s' % (
            YOUR_CLIENT_ID, YOUR_CLIENT_SECRET, YOUR_REGISTERED_REDIRECT_URI)

        #resp =redirect(step_1)
        resp = requests.get(step_1, cookies=cs)
        
    # 监控任务
    register_events(scheduler)
    # 调度器开始
    scheduler.start()
except Exception as e:
    print(e)
    # 报错则调度器停止执行
    scheduler.shutdown()

def index(request):
    code = request.GET.get('code')

    step_3 = 'https://foursquare.com/oauth2/access_token?client_id=%s&client_secret=%s&grant_type=authorization_code&redirect_uri=%s&code=%s'%(YOUR_CLIENT_ID,YOUR_CLIENT_SECRET, YOUR_REGISTERED_REDIRECT_URI,code)
    resp = requests.get(url=step_3)
    token = json.loads(resp.content)

    nowTime=datetime.datetime.now().strftime('%Y%m%d')#现在
    
    # 今天日期
    today = datetime.date.today()

    # 昨天时间
    yesterday = today - datetime.timedelta(days=1)
    
    # 明天时间
    tomorrow = today + datetime.timedelta(days=1)
    
    #yesterday_start_time = int(time.mktime(time.strptime(str(yesterday), '%Y-%m-%d')))
    # 2009-06-01 00:00:00
    yesterday_start_time = 1243785600
    today_end_time = (int(time.mktime(time.strptime(str(tomorrow), '%Y-%m-%d'))))
    offset = 0
    
    c = Calendar()
    while True:
        url = 'https://api.foursquare.com/v2/users/self/checkins?oauth_token=%s&v=%s&beforeTimestamp=%s&afterTimestamp=%s&limit=250&&offset=%s'%(token['access_token'], nowTime, today_end_time, yesterday_start_time, offset)
        resp = requests.get(url=url)
        data = json.loads(resp.text)
    
        if len(data['response']['checkins']['items']) == 0:
            break
   
        for item in data['response']['checkins']['items']:
            try:
                e = Event()
                e.name = item['venue']['name']
                e.uid = item['id']
                e.begin = item['createdAt'] + item['timeZoneOffset']
                e.location = '%s'%'-'.join([s for s in item['venue']['location']['formattedAddress']])
                e.status = 'CONFIRMED'
                c.events.add(e)
                print(item['venue']['location']['formattedAddress'])
            except:
                continue
        offset += 250
    file_path = os.path.join(settings.MEDIA_ROOT, 'HistoryCheckins', 'HistoryCheckins.ics')

    [dir_name, file_name] = os.path.split(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(c)


    return HttpResponse(json.dumps({"success": True}))

    
def history_checkins(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'HistoryCheckins', 'HistoryCheckins.ics')
    file_name = 'HistoryCheckins.ics'
    response = StreamingHttpResponse(FileManager.file_iterator(file_path))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(file_name))

    return response
