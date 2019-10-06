#!/usr/bin/env python3
import os
import sys
import json

import requests # pip3 install requests
from configparser import SafeConfigParser, MissingSectionHeaderError # pip3 install ConfigParser


def _create_config(file_name):
    # iniファイルを読みこむ
    # 内部用（get_config_json）　見にくくなるから分けた
    file_path = os.path.abspath(file_name)
    config = SafeConfigParser()

    if os.path.exists(file_path):
        config.read(file_path, encoding='utf8')
    else:
        raise FileNotFoundError

    return config


def get_config_json(filename, sample_json):
    """
    get_config_jsonは、sample_jsonを雛形に、
    configファイルからsample_jsonのキーに対応する値を取ってきて格納する

    Parameters
    -------
    filename : str
        configファイルのパスを格納
    sample_json : dict
        configファイルから値を取り出す雛形

    Returns
    -------
    config_json : dict
        configファイルの値を格納したsample_json
    """
    config = {}
    config_json = {}

    try:
        config = _create_config(filename)
    except FileNotFoundError as e:
        print(f'{filename} が同階層に見つかりませんでした。')
        sys.exit(1)
    except MissingSectionHeaderError as e:
        print(f'{filename} の書式を見直してください。')
        sys.exit(1)

    try:
        # sample_json 内のキーから、configファイル内のキーを検索、値を取ってくる
        config_json = {sec: {param: config[sec][param] for param in sample_json[sec]} \
            for sec in sample_json}
    except KeyError as e:
        print(f'{e} が {filename} 内に見つかりませんでした。')
        sys.exit(1)

    return config_json


class SlackAPI(object):
    """
    SlackAPI は、Slackの webhook_url を
    webhook_url を、ソースファイルとは別の config ファイルに書くために作成

    Attributes
    ----------
    webhook_url : str
        SlackWebAPIのURL
    """

    def __init__(self, inifile_name):
        """
        Parameters
        ----------
        inifile_name : str
            inifile_name は、configファイルのパス
            （configファイルには、叩くSlackWebAPIのURLを記載）
        """
        # 設定ファイル読み込み
        sample_json = {'URL': {'webhook_url': None}}
        config_json = get_config_json(inifile_name, sample_json)
        self.webhook_url = config_json['URL']['webhook_url']

    def print_slack(self, message):
        """
        Slackに出力する
        辞書やリストはそのまま入れるとエラーになるので、strに変換

        Parameters
        -------
        message : str
            message は、Slackに出力したい文字列
        """
        if isinstance(message, dict):
            message = json.dumps(message,indent=4,ensure_ascii=False)
        if isinstance(message, list):
            message = [json.dumps(m,indent=4,ensure_ascii=False) for m in message]
        requests.post(self.webhook_url, data=json.dumps({'text': message}))
