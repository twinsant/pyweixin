# -*- coding: utf8
# Author: twinsant@gmail.com
import hashlib
import json
import xml.etree.ElementTree as ET
from functools import cmp_to_key

import requests

class WeiXin(object):
    def __init__(self, token=None, timestamp=None, nonce=None, signature=None, echostr=None, xml_body=None):
        self.token = token
        self.timestamp = timestamp
        self.nonce = nonce
        self.signature = signature
        self.echostr = echostr

        self.xml_body = xml_body

    @classmethod
    def on_connect(self, token=None, timestamp=None, nonce=None, signature=None, echostr=None):
        obj = WeiXin(token=token,
            timestamp=timestamp,
            nonce=nonce,
            signature=signature,
            echostr=echostr)
        return obj

    @classmethod
    def on_message(self, xml_body):
        obj = WeiXin(xml_body=xml_body)
        return obj

    def to_json(self):
        '''http://docs.python.org/2/library/xml.etree.elementtree.html#xml.etree.ElementTree.XML
        '''
        j = {}
        root = ET.fromstring(self.xml_body)
        for child in root:
            if child.tag == 'CreateTime':
                value = int(child.text)
            else:
                value = child.text
            j[child.tag] = value
        return j

    def _to_tag(self, k):
        return ''.join([w.capitalize() for w in k.split('_')])

    def _cdata(self, data):
        '''http://stackoverflow.com/questions/174890/how-to-output-cdata-using-elementtree
        '''
        if type(data) is str:
            return '<![CDATA[%s]]>' % data.replace(']]>', ']]]]><![CDATA[>')
        return data

    def to_xml(self, **kwargs):
        xml = '<xml>'
        def cmp(x, y):
            ''' WeiXin need ordered elements?
            '''
            orderd = ['to_user_name', 'from_user_name', 'create_time', 'msg_type', 'content', 'func_flag']
            try:
                ix = orderd.index(x)
            except ValueError:
                return 1
            try:
                iy = orderd.index(y)
            except ValueError:
                return -1
            return ix - iy
        for k in sorted(kwargs.keys(), key=cmp_to_key(cmp)):
            v = kwargs[k]
            tag = self._to_tag(k)
            xml += '<%s>%s</%s>' % (tag, self._cdata(v), tag)
        xml += '</xml>'
        return xml

    def validate(self):
        params = {}
        params['token'] = self.token
        params['timestamp'] = self.timestamp
        params['nonce'] = self.nonce

        signature = self.signature

        if self.is_not_none(params):
            gen_signature = self.gen_signature(params)
            if gen_signature == signature:
                return True
        return False

    def is_not_none(self, params):
        for k, v in params.items():
            if v is None:
                return False
        return True

    @classmethod
    def gen_signature(self, params):
        '''http://docs.python.org/2/library/hashlib.html
        '''
        a = sorted([v for k, v in params.items()])
        s = ''.join(a)
        return hashlib.sha1(s.encode('utf-8')).hexdigest()

    @staticmethod
    def get_access_token(appid, secret):
        """获取微信公众号 access_token
        
        接口文档: https://developers.weixin.qq.com/doc/subscription/api/base/api_getaccesstoken.html
        
        Args:
            appid: 微信公众号的 AppID
            secret: 微信公众号的 AppSecret
        
        Returns:
            dict: 包含 access_token 和 expires_in 的字典
                  成功: {"access_token": "ACCESS_TOKEN", "expires_in": 7200}
                  失败: {"errcode": 错误码, "errmsg": "错误信息"}
        """
        if not appid or not secret:
            return {"errcode": -1, "errmsg": "appid 或 secret 未配置"}
        
        url = 'https://api.weixin.qq.com/cgi-bin/token'
        params = {
            'grant_type': 'client_credential',
            'appid': appid,
            'secret': secret
        }
        
        response = requests.get(url, params=params)
        return response.json()

    @staticmethod
    def create_draft(access_token, title, digest, content, 
                    content_source_url='', thumb_media_id=None, author=''):
        """创建微信公众号草稿
        
        接口文档: https://developers.weixin.qq.com/doc/subscription/api/draft/draft_add.html
        
        Args:
            access_token: 微信公众号 access_token
            title: 文章标题
            digest: 文章摘要
            content: 文章内容(HTML格式)
            content_source_url: 原文链接(可选)
            thumb_media_id: 封面图片的media_id(可选)
            author: 文章作者(可选)
        
        Returns:
            dict: 微信API返回的结果
                  成功: {"media_id": "MEDIA_ID"}
                  失败: {"errcode": 错误码, "errmsg": "错误信息"}
        """
        url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}'
        
        article = {
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "content_source_url": content_source_url,
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }
        
        if thumb_media_id:
            article['thumb_media_id'] = thumb_media_id
        else:
            raise ValueError("thumb_media_id 不能为空")
        
        data = {"articles": [article]}
        data_to_send = json.dumps(data, ensure_ascii=False)
        
        response = requests.post(url, data=data_to_send, 
                                headers={'Content-Type': 'application/json'})
        return response.json()