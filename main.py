#!/usr/bin/env python3
import reqamz
from wrapmongo import MongoAccess

def main():
    # MWSRequest初期化用パラメータ
    API_PARAM = {
        'ACTION'  : 'GetMatchingProduct',
        'SECTION' : 'Products',
        'VERSION' : '2011-10-01',
        'MARKETPLACE_ID' : 'A1VC38T7YXB528'
    }
    # ASINリストをDBから取得（10個）
    asin_list = ['B004EH30DY', 'B00SP9KG34', '4473032655']
    mongo = MongoAccess()
    mongo.find()
    add_JSON = {}
    count = 1
    for asin in asin_list:
        add_JSON[f'ASINList.ASIN.{count}'] = asin
        count+=1
    mws_request = reqamz.MWSRequest(API_PARAM, add_JSON)
    response = mws_request.request_mws()
    print(response.content.decode())


if __name__ == '__main__':
    main()
