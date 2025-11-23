# -*- coding: utf8
# Author: twinsant@gmail.com
from pyweixin import WeiXin


def test_gen_signature():
    params = {
        'token': 'token',
        'timestamp': 'timestamp',
        'nonce': 'nonce',
    }
    gen_signature = WeiXin.gen_signature(params)
    assert gen_signature == '6db4861c77e0633e0105672fcd41c9fc2766e26e'


def test_on_connect_validate():
    weixin = WeiXin.on_connect(
        token='token',
        timestamp='timestamp',
        nonce='nonce',
        signature='6db4861c77e0633e0105672fcd41c9fc2766e26e',
        echostr='echostr'
    )
    assert weixin.validate() is True


def test_on_connect_validate_false():
    weixin = WeiXin.on_connect(
        token='token',
        timestamp='timestamp',
        nonce='nonce_false',
        signature='6db4861c77e0633e0105672fcd41c9fc2766e26e',
        echostr='echostr'
    )
    assert weixin.validate() is False


def test_on_message_text():
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
    
    assert 'ToUserName' in j
    assert j['ToUserName'] == 'toUser'
    assert 'FromUserName' in j
    assert j['FromUserName'] == 'fromUser'
    assert 'CreateTime' in j
    assert j['CreateTime'] == 1348831860
    assert 'MsgType' in j
    assert j['MsgType'] == 'text'
    assert 'Content' in j
    assert j['Content'] == 'this is a test'
    assert 'MsgId' in j
    assert j['MsgId'] == '1234567890123456'


def test_on_message_image():
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
    
    assert 'ToUserName' in j
    assert j['ToUserName'] == 'toUser'
    assert 'FromUserName' in j
    assert j['FromUserName'] == 'fromUser'
    assert 'CreateTime' in j
    assert j['CreateTime'] == 1348831860
    assert 'MsgType' in j
    assert j['MsgType'] == 'image'
    assert 'PicUrl' in j
    assert j['PicUrl'] == 'this is a url'
    assert 'MsgId' in j
    assert j['MsgId'] == '1234567890123456'


def test_on_message_location():
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
    
    assert 'ToUserName' in j
    assert j['ToUserName'] == 'toUser'
    assert 'FromUserName' in j
    assert j['FromUserName'] == 'fromUser'
    assert 'CreateTime' in j
    assert j['CreateTime'] == 1351776360
    assert 'MsgType' in j
    assert j['MsgType'] == 'location'
    assert 'Location_X' in j
    assert j['Location_X'] == '23.134521'
    assert 'Location_Y' in j
    assert j['Location_Y'] == '113.358803'
    assert 'Scale' in j
    assert j['Scale'] == '20'
    assert 'Label' in j
    assert j['Label'] == u'位置信息'
    assert 'MsgId' in j
    assert j['MsgId'] == '1234567890123456'


def test_on_message_link():
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
    
    assert 'ToUserName' in j
    assert j['ToUserName'] == 'toUser'
    assert 'FromUserName' in j
    assert j['FromUserName'] == 'fromUser'
    assert 'CreateTime' in j
    assert j['CreateTime'] == 1351776360
    assert 'MsgType' in j
    assert j['MsgType'] == 'link'
    assert 'Title' in j
    assert j['Title'] == u'公众平台官网链接'
    assert 'Description' in j
    assert j['Description'] == u'公众平台官网链接'
    assert 'Url' in j
    assert j['Url'] == 'url'
    assert 'MsgId' in j
    assert j['MsgId'] == '1234567890123456'


def test_to_xml_text():
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
    
    expected = xml.replace('\n', '').replace(' ', '').strip()
    actual = weixin.to_xml(
        to_user_name=to_user_name,
        from_user_name=from_user_name,
        create_time=create_time,
        msg_type=msg_type,
        content=content,
        func_flag=func_flag
    )
    assert expected == actual
