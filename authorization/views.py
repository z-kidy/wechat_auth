# -*- coding: utf-8 -*-
import hashlib
import time 
import urllib
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
WEIXIN_TOKEN = 'lvxingjiakidy'
 
from wechat_auth.settings import appID, appsecret 

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
        toUserName = data.get('ToUserName', '')
        fromUserName = data.get('FromUserName', '')
        msgType = data.get('MsgType', '')
        content = data.get('Content', '')

        return render(request, 'reply.xml',
                    {  'toUserName': fromUserName,
                       'fromUserName': toUserName,
                       'createTime': int(time.time()),
                       'msgType': msgType,
                       'content': content,
                    },
            content_type='application/xml'
        )

@api_view(['GET'])
def get_code(request):
    if request.method == 'GET':
        code = request.GET.get('code', '')
        if code:
            # 第二步：通过code换取网页授权access_token
            try:
                response = urllib.urlopen(url='https://api.weixin.qq.com/sns/oauth2/access_token',
                    data=urllib.urlencode({
                    'appid': appID,
                    'secret': appsecret,
                    'code': code,
                    'grant_type': 'authorization_code',
                    })
                )
            except Exception, reson:
                print reson

            response_dic = json.loads(response.read())                 # 解析json
            errcode = response_dic.get('errcode', None)         # 调用失败
            if errcode:
                raise Warning(response_dic.get('errmsg', ''))   # raise 错误原因
            
            print response_dic
            
            access_token = response_dic.get('access_token', '')
            expires_in = response_dic.get('expires_in', '')
            refresh_token = response_dic.get('refresh_token', '')
            openid = response_dic.get('openid', '')
            scope = response_dic.get('scope', '')


            # 第四步：拉取用户信息(需scope为 snsapi_userinfo)
            info_url = 'https://api.weixin.qq.com/sns/userinfo'
            try:
                info_response = urllib.urlopen(url=info_url,
                    data=urllib.urlencode({
                    'access_token': access_token,
                    'openid': openid,
                    'lang':'zh_CN'       # 默认使用中文吧                        
                    })
                )
            except Exception, reson:
                print reson

            info_dic = json.loads(info_response.read())                 # 解析json
            errcode = info_dic.get('errcode', None)              # 调用失败
            if errcode:
                raise Warning(response_dic.get('errmsg', ''))   # raise 错误原因

            nickname = info_dic.get('nickname', '')
            sex = info_dic.get('sex', '')
            province = info_dic.get('province', '')
            city = info_dic.get('city', '')
            country = info_dic.get('country', '')
            city = info_dic.get('city', '')
            headimgurl = info_dic.get('headimgurl', '')

            print info_dic

        return HttpResponse('ok')
