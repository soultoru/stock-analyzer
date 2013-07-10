# coding:utf-8
'''
Created on Jul 9, 2013

@author: soultoru
'''
from test.db.mongo import Database
from datetime import datetime,timedelta
from pymongo import ASCENDING,DESCENDING
import re

class Data(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
    def getData(self,collection):
        keys = collection.find_one().keys()
        keys.remove(u"_id")
        data = []
        for cur in collection.find().sort([(u"code",ASCENDING), (u"date",DESCENDING)]):
#            cur[u"date"] = datetime.strptime(cur[u"date"],u"%Y/%m/%d")
            del cur[u"_id"]
            cur.update({'day_low_price':min([cur[u'morning_low_price'],cur[u'afternoon_low_price']])})
            cur.update({'day_high_price':min([cur[u'morning_high_price'],cur[u'afternoon_high_price']])})
            cur.update({'day_transaction':sum([cur[u'morning_transaction'],cur[u'afternoon_transaction']])})
            sorted(cur)
            data.append(cur)
        tmp_data = []
        i=1
        while i < len(data) -3 :
            if data[i][u"code"] == data[i+3][u"code"]: 
                tmp_r = {}
                tmp_r.update({u"0_"+key:data[i][key] for key in data[i].keys()})
                tmp_r.update({u"1_"+key:data[i+1][key] for key in data[i+1].keys()})
                tmp_r.update({u"2_"+key:data[i+2][key] for key in data[i+2].keys()})
                tmp_r.update({u"3_"+key:data[i+3][key] for key in data[i+3].keys()})
                tmp_data.append(tmp_r)
            i=i+1
        print len(tmp_data)
        
    def getData2(self,collection):
        #項目一覧の取得
        tmp_data = collection.find_one()
        keys = tmp_data.keys()
        #価格に関係するkeyのみを抽出
        prices_keys = [key for key in keys if (None != re.search("price", key))]
        print prices_keys
        #価格を比較
        prices_ratio_keys = [key1 + u"/" + key2
              for key1 in prices_keys for key2 in prices_keys
              if tmp_data[key1] != None and tmp_data[key2] != None and prices_keys.index(key1) > prices_keys.index(key2)]
        data_keys = keys + prices_ratio_keys
        tmp1 = []
        tmp1.append(data_keys)
        for data in collection.find():
            prices_ratio = {key:float(data[key.split(u'/')[0]])/float(data[key.split(u'/')[1]])-1 
                            for key in prices_ratio_keys
                            if data[key.split(u'/')[0]] != None and data[key.split(u'/')[1]] != None
                            and prices_keys.index(key.split(u'/')[0]) > prices_keys.index(key.split(u'/')[1])}
            tmp2 = {}
            tmp2.update(data)
            tmp2.update(prices_ratio)
            tmp3 = [tmp2[key] for key in data_keys if key in tmp2]
            tmp1.append(tmp3) 
        return tmp1
    def convertToListFromDictionary(self,data):
        data
        pass
    
if __name__ == "__main__" :
    db = Database()
    conn = db.getConnectionNoAuth(u"127.0.0.1")
    coll = db.getCollection(conn, u"slice", u"prices")
    array = Data().getData(coll)
    conn.close()
