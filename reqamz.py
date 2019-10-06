#!/usr/bin/env python3
from mymodule import get_config_json as get_conf
import base64
import hashlib
import hmac
import datetime
from urllib import parse

import requests # pip3 install requests


class MWSRequest(object):

    inifile_name = './config/amazon.ini'

    # Amazon規定の日付形式にフォーマット
    def _datetime_encode(self, dt):
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


    # URLを作成
    def recreate_url(self):
        # params -> クエリストリング
        query_string = '&'.join(f"{n}={parse.quote(v, safe='')}"
                                for n, v in sorted(self.params.items()))
        # 署名を作成
        canonical = f'{self.HTTP_ACTION}\n{self.DOMAIN}\n/{self.ENDPOINT}\n{query_string}'
        h = hmac.new(
            self.CREDENTIAL['SECRET_KEY'].encode('utf-8'),
            canonical.encode('utf-8'),
            hashlib.sha256)
        signature = parse.quote(base64.b64encode(h.digest()), safe='')

        self.url = f'https://{self.DOMAIN}/{self.ENDPOINT}?{query_string}&Signature={signature}'


    # コンストラクタ
    def __init__(self, API_PARAM, add_params = None):
        # 大文字は固定値
        self.API_PARAM = API_PARAM # 何のAPI使うか(商品検索APIなど)/バージョン etc...
        self.ENDPOINT = f"{API_PARAM['SECTION']}/{self.API_PARAM['VERSION']}"
        self.HTTP_ACTION = 'POST'
        self.DOMAIN = 'mws.amazonservices.jp'

        # Amazonの情報を読み込み
        sample_json = {
            'CREDENTIAL': {
                'SELLER_ID'    : None,
                'AUTH_TOKEN'   : None,
                'ACCESS_KEY_ID': None,
                'SECRET_KEY'   : None
            }
        }
        # get_conf:　iniファイル名とJSONの雛形から
        #               iniファイルの中身が入ったJSONを作成
        self.CREDENTIAL = get_conf(self.inifile_name, sample_json)['CREDENTIAL']

        timestamp = self._datetime_encode(datetime.datetime.utcnow())
        # 基本のパラメータ
        self.params = {
            'AWSAccessKeyId': self.CREDENTIAL['ACCESS_KEY_ID'],
            'Action': self.API_PARAM['ACTION'],
            'SellerId': self.CREDENTIAL['SELLER_ID'],
            'MWSAuthToken': self.CREDENTIAL['AUTH_TOKEN'],
            'SignatureVersion': '2',
            'Timestamp': timestamp,
            'Version': self.API_PARAM['VERSION'],
            'SignatureMethod': 'HmacSHA256',
            'MarketplaceId': self.API_PARAM['MARKETPLACE_ID'],
        }

        if add_params is not None:
            self.update_param_json(add_params)

        self.recreate_url()


    # MWSにリクエスト
    def request_mws(self):
        return requests.post(self.url)


    # URLを返す/ URL変更なしで取得だけしたい時
    def get_url(self):
        return self.url


    # paramsに追加
    def update_param_json(self, JSON):
        self.params.update(JSON)
        self.recreate_url()


    # 最終更新からどれだけたった？
    # 未完成！！
    def get_lastupdate(self):
        last_update_after = _datetime_encode(
            datetime.datetime.utcnow() - datetime.timedelta(days=1))
