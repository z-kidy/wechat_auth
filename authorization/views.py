# -*- coding: utf-8 -*-
import hashlib
import time 

from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
WEIXIN_TOKEN = 'lvxingjiakidy'
 

@api_view(['GET', 'POST'])
def index(request):
    if request.method == "GET":
        signature = request.GET.get("signature", None)
        timestamp = request.GET.get("timestamp", None)
        nonce = request.GET.get("nonce", None)
        echostr = request.GET.get("echostr", None)
        token = WEIXIN_TOKEN
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = "%s%s%s" % tuple(tmp_list)
        tmp_str = hashlib.sha1(tmp_str).hexdigest()
        if tmp_str == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse("weixin  index")

    if request.method == 'POST':
        data = request.data
        ToUserName = data.get('ToUserName', '')
        FromUserName = data.get('FromUserName', '')
        MsgType = data.get('MsgType', '')
        Content = data.get('Content', '')
        return Response(
                    {  'toUserName': FromUserName,
                       'fromUserName': ToUserName,
                       'createTime': time.time(),
                       'msgType': MsgType,
                       'content': Content,
                    },
            content_type='application/xml'
        )

    

