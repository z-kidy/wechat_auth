# -*- coding: utf-8 -*-
import hashlib
import time
import urllib
import json
import logging

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wechat_auth.settings import appID, appsecret, Token

logger = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
def index(request):
    """
    微信简单通信，
    GET用于验证签名信息，
    加密/校验流程如下：
    1. 将token、timestamp、nonce三个参数进行字典序排序
    2. 将三个参数字符串拼接成一个字符串进行sha1加密
    3. 开发者获得加密后的字符串可与signature对比，标识该请求来源于微信
    POST实现一个简单的回复信息
    """
    if request.method == "GET":
        signature = request.GET.get("signature", None)
        timestamp = request.GET.get("timestamp", None)
        nonce = request.GET.get("nonce", None)
        echostr = request.GET.get("echostr", None)
        tmp_list = [Token, timestamp, nonce]
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
                      {'toUserName': fromUserName,
                       'fromUserName': toUserName,
                       'createTime': int(time.time()),   # 格式规定time是int类型
                       'msgType': msgType,
                       'content': content,
                       },
                      )


def web_auth(request):
    """
    网页提示是否授权

    """
    if request.method == 'GET':
        return render(request, 'web_auth.html')
    if request.method == 'POST':
        flag = int(request.POST.get('flag', 0))   # flag 表示是否同意授权 1/0
        if flag:
            data = urllib.urlencode({
                'appid': appID,
                'redirect_uri': 'http://' + request.get_host() + reverse('get_code'),
                'response_type': 'code',
                'scope': 'snsapi_userinfo',
                'state': 'STATE',
            })
            redirect_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?' + \
                data + '#wechat_redirect'
            return redirect(redirect_url)         # 同意授权则跳转到获取code
        else:
            return redirect(reverse('web_auth'))

@api_view(['GET'])
def get_code(request):
    """
    用户授予权限，获取code，通过code获取access_toekn, 再通过access_token获取用户信息
    """
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
                logger.exception(u'调用微信api失败[%s]！', reson)
                return Response({
                    'result': 0,
                    'error': u'调用微信api失败'
                    })

            response_dic = json.loads(response.read())          # 解析json
            errcode = response_dic.get('errcode', None)         # 调用失败
            if errcode:
                # raise 错误原因
                logger.exception(
                    u'调用微信api失败[%d:%s]！', errcode, response_dic.get('errmsg', ''))
                return Response({
                    'result': 0,
                    'error': u'调用微信api失败'
                })

            access_token = response_dic.get('access_token', '')
            openid = response_dic.get('openid', '')

            # 第四步：拉取用户信息(需scope为 snsapi_userinfo), 使用到access_token, openid
            info_url = 'https://api.weixin.qq.com/sns/userinfo'
            try:
                info_response = urllib.urlopen(url=info_url,
                                               data=urllib.urlencode({
                                                   'access_token': access_token,
                                                   'openid': openid,
                                                   # 默认使用中文吧
                                                   'lang': 'zh_CN'
                                               })
                                               )
            except Exception, reson:
                logger.exception(u'调用微信api失败[%s]！', reson)
                return Response({
                    'result': 0,
                    'error': u'调用微信api失败'
                    })

            info_dic = json.loads(info_response.read())          # 解析json
            errcode = info_dic.get('errcode', None)              # 调用失败
            if errcode:
                # raise 错误原因
                logger.exception(
                    u'调用微信api失败[%d:%s]！', errcode, response_dic.get('errmsg', ''))
                return Response({
                    'result': 0,
                    'error': u'调用微信api失败'
                })

            nickname = info_dic.get('nickname', '')              # 昵称
            sex = info_dic.get('sex', 0)                         # 性别
            province = info_dic.get('province', '')              # 省
            country = info_dic.get('country', '')                # 国家
            city = info_dic.get('city', '')                      # 城市
            headimgurl = info_dic.get('headimgurl', '')          # 头像url

            return render(request, 'user_info.html',
                          {
                              'nickname': nickname,
                              'sex': sex,
                              'province': province,
                              'country': country,
                              'city': city,
                              'headimgurl': headimgurl,
                          },
                          )
