import os
from dotenv import load_dotenv

from pyweixin import WeiXin

load_dotenv()

MP_APP_ID = os.getenv('MP_APP_ID')
MP_APP_SECRET = os.getenv('MP_APP_SECRET')
THUMB_MEDIA_ID = os.getenv('THUMB_MEDIA_ID')

if __name__ == '__main__':
    # 获取access_token
    result = WeiXin.get_access_token(appid=MP_APP_ID, secret=MP_APP_SECRET)
    access_token = result.get('access_token')

    # 创建草稿
    draft = WeiXin.create_draft(
        access_token=access_token,
        title='文章标题',
        digest='文章摘要',
        content='<p>文章内容</p>',
        author='',
        thumb_media_id=THUMB_MEDIA_ID,
    )
    print(draft)