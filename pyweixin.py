# -*- coding: utf8
# Author: twinsant@gmail.com
import hashlib
import xml.etree.ElementTree as ET

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
                value = long(child.text)
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
        for k in sorted(kwargs.iterkeys(), cmp):
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
        # 不需要判断echostr，因为每个POST请求不会发echostr，只有第一次Get请求会发echostr
        # echostr = self.echostr

        if self.is_not_none(params):
            _signature = self._signature(params)
            if _signature == signature:
                return True
        return False

    def is_not_none(self, params):
        for k, v in params.items():
            if v is None:
                return False
        return True

    def _signature(self, params):
        '''http://docs.python.org/2/library/hashlib.html
        '''
        a = sorted([v for k, v in params.items()])
        s = ''.join(a)
        return hashlib.sha1(s).hexdigest()

import unittest
class WeiXinTestCase(unittest.TestCase):
    def test_on_connect_validate(self):
        weixin = WeiXin.on_connect(token='token',
            timestamp='timestamp',
            nonce='nonce',
            signature='6db4861c77e0633e0105672fcd41c9fc2766e26e',
            echostr='echostr')
        self.assertEqual(weixin.validate(), True)

    def test_on_connect_validate_false(self):
        weixin = WeiXin.on_connect(token='token',
            timestamp='timestamp',
            nonce='nonce_false',
            signature='6db4861c77e0633e0105672fcd41c9fc2766e26e',
            echostr='echostr')
        self.assertEqual(weixin.validate(), False)

    def test_on_message_text(self):
        body = '''
        <xml>
            <ToUserName><![CDATA[toUser]]></ToUserName>
            <FromUserName><![CDATA[fromUser]]></FromUserName> 
            <CreateTime>1348831860</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[this is a test]]></Content>
            <MsgId>1234567890123456</MsgId>
       </xml>
        '''
        weixin = WeiXin.on_message(body)
        j = weixin.to_json()
        def assertParam(name, value):
            self.assertEqual(name in j, True)
            self.assertEqual(j[name], value)
        assertParam('ToUserName', 'toUser')
        assertParam('FromUserName', 'fromUser')
        assertParam('CreateTime', 1348831860)
        assertParam('MsgType', 'text')
        assertParam('Content', 'this is a test')
        assertParam('MsgId', '1234567890123456')

    def test_on_message_image(self):
        body = '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[image]]></MsgType>
        <PicUrl><![CDATA[this is a url]]></PicUrl>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        weixin = WeiXin.on_message(body)
        j = weixin.to_json()
        def assertParam(name, value):
            self.assertEqual(name in j, True)
            self.assertEqual(j[name], value)
        assertParam('ToUserName', 'toUser')
        assertParam('FromUserName', 'fromUser')
        assertParam('CreateTime', 1348831860)
        assertParam('MsgType', 'image')
        assertParam('PicUrl', 'this is a url')
        assertParam('MsgId', '1234567890123456')

    def test_on_message_location(self):
        body = '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1351776360</CreateTime>
        <MsgType><![CDATA[location]]></MsgType>
        <Location_X>23.134521</Location_X>
        <Location_Y>113.358803</Location_Y>
        <Scale>20</Scale>
        <Label><![CDATA[位置信息]]></Label>
        <MsgId>1234567890123456</MsgId>
        </xml> 
        '''
        weixin = WeiXin.on_message(body)
        j = weixin.to_json()
        def assertParam(name, value):
            self.assertEqual(name in j, True)
            self.assertEqual(j[name], value)
        assertParam('ToUserName', 'toUser')
        assertParam('FromUserName', 'fromUser')
        assertParam('CreateTime', 1351776360)
        assertParam('MsgType', 'location')
        assertParam('Location_X', '23.134521')
        assertParam('Location_Y', '113.358803')
        assertParam('Scale', '20')
        assertParam('Label', u'位置信息')
        assertParam('MsgId', '1234567890123456')

    def test_on_message_link(self):
        body = '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1351776360</CreateTime>
        <MsgType><![CDATA[link]]></MsgType>
        <Title><![CDATA[公众平台官网链接]]></Title>
        <Description><![CDATA[公众平台官网链接]]></Description>
        <Url><![CDATA[url]]></Url>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        weixin = WeiXin.on_message(body)
        j = weixin.to_json()
        def assertParam(name, value):
            self.assertEqual(name in j, True)
            self.assertEqual(j[name], value)
        assertParam('ToUserName', 'toUser')
        assertParam('FromUserName', 'fromUser')
        assertParam('CreateTime', 1351776360)
        assertParam('MsgType', 'link')
        assertParam('Title', u'公众平台官网链接')
        assertParam('Description', u'公众平台官网链接')
        assertParam('Url', 'url')
        assertParam('MsgId', '1234567890123456')

    def test_to_xml_text(self):
        xml = '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>12345678</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[content]]></Content>
        <FuncFlag>0</FuncFlag>
        </xml>
        '''
        weixin = WeiXin()
        to_user_name = 'toUser'
        from_user_name = 'fromUser'
        create_time = 12345678
        msg_type = 'text'
        content = 'content'
        func_flag = 0
        self.assertEqual(xml.replace('\n', '').replace(' ', '').strip(), weixin.to_xml(to_user_name=to_user_name,
            from_user_name=from_user_name,
            create_time=create_time,
            msg_type=msg_type,
            content=content,
            func_flag=func_flag))

if __name__ == '__main__':
    unittest.main()
