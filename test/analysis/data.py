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
    #目標日から過去何日分をデータとして利用するか
    data_day = 3
    #1日で取得したデータの比較候補
    compare_list_in_a_day =[
                            #午前の価格比較
                            "morning_close_price/morning_open_price",
                            "morning_high_price/morning_open_price",
                            "morning_low_price/morning_open_price",
                            "morning_high_price/morning_close_price",
                            "morning_low_price/morning_close_price",
                            "morning_high_price/morning_low_price",
                            #午後の価格比較
                            "afternoon_close_price/afternoon_open_price",
                            "afternoon_high_price/afternoon_open_price",
                            "afternoon_low_price/afternoon_open_price",
                            "afternoon_high_price/afternoon_close_price",
                            "afternoon_low_price/afternoon_close_price",
                            "afternoon_high_price/afternoon_low_price",
                            #一日の価格比較
                            "afternoon_close_price/morning_open_price",
                            "day_high_price/morning_open_price",
                            "day_low_price/morning_open_price",
                            "day_high_price/afternoon_close_price",
                            "day_low_price/afternoon_close_price",
                            "day_high_price/day_low_price"]
    #平均との比較候補
    compare_list_average = [
                            #平均トランザクションとの比較
                            "morning_transaction/average_morning_transaction",
                            "afternoon_transaction/average_afternoon_transaction",
                            "day_transaction/average_day_transaction"]
    #過去日との比較候補
    compare_list_past = [
                            #日跨ぎの価格比較
                         "afternoon_close_price/afternoon_close_price",
                         "morning_open_price/morning_open_price",
                         "morning_open_price/afternoon_close_price",
                            #日跨ぎのトランザクション比較
                         "morning_transaction/morning_transaction",
                         "afternoon_transaction/afternoon_transaction",
                         "day_transaction/day_transaction"
                         ]
    def __init__(self):
        '''
        Constructor
        '''
    def getData(self,collection):
        #データの取得
        data = []
        for cur in collection.find().sort([(u"code",ASCENDING), (u"date",DESCENDING)]):
            del cur[u"_id"]
            #一日分のトランザクションを算出"
            cur.update({'day_low_price':min([cur[u'morning_low_price'],cur[u'afternoon_low_price']])})
            cur.update({'day_high_price':min([cur[u'morning_high_price'],cur[u'afternoon_high_price']])})
            cur.update({'day_transaction':sum([cur[u'morning_transaction'],cur[u'afternoon_transaction']])})
            sorted(cur)
            data.append(cur)
        #ある1日、ある銘柄でのデータの比較
        for r in data:
            for l in self.compare_list_in_a_day:
                tmp1 = r[l.split(u'/')[0]]
                tmp2 = r[l.split(u'/')[1]]
                if tmp1 != None and tmp2 != None:
                    tmp3 = float(tmp1)/float(tmp2)
                else:
                    tmp3 = None
                r.update({l:tmp3})
        #codeごとの平均トランザクション
        codes=list(set([r[u"code"]for r in data]))
        average_transactions={}
        for code in codes:
            tmp_transaction = {}
            day = [r[u"day_transaction"] for r in data if r[u"code"] == code]
            tmp_transaction.update({u"average_day_transaction":sum(day)/len(day)})
            morning = [r[u"morning_transaction"] for r in data if r[u"code"] == code]
            tmp_transaction.update({u"average_morning_transaction":sum(morning)/len(morning)})
            afternoon = [r[u"afternoon_transaction"] for r in data if r[u"code"] == code]
            tmp_transaction.update({u"average_afternoon_transaction":sum(afternoon)/len(afternoon)})
            average_transactions.update({code:tmp_transaction})
        for r in data:
            r.update(average_transactions[r[u"code"]])
        
        #codeごとに平均とある1日のトランザクションを比較
        for r in data:
            for l in self.compare_list_average:
                tmp1 = r[l.split(u'/')[0]]
                tmp2 = r[l.split(u'/')[1]]
                if tmp1 != None and tmp2 != None:
                    tmp3 = float(tmp1)/float(tmp2)
                else:
                    tmp3 = None
                r.update({l:tmp3})
                
        #目標日から過去数日を同じレコードにまとめる
        composition_data = []
        i = 0
        while i < len(data) - self.data_day :
            if data[i][u"code"] == data[i+self.data_day][u"code"]: 
                tmp_r = {u"code":data[i][u"code"],u"date":data[i][u"date"]}
                for j in range(0,self.data_day):
                    tmp_r.update({str(j)+u"_("+key+u")":data[i+j][key] for key in data[i+j].keys() if key != u"code" and key != u"date"})
                composition_data.append(tmp_r)
            i=i+1
        #ある銘柄過去日との比較
        for r in composition_data:
            for l in self.compare_list_past:
                for i in range(1,self.data_day-1):
                    str1 = str(i) + u"_(" + l.split(u'/')[0] + u")"
                    str2 = str(i+1)  + u"_(" + l.split(u'/')[1] + u")"
                    tmp1 = r[str1]
                    tmp2 = r[str2]
                    if tmp1 != None and tmp2 != None and tmp2 != 0:
                        tmp3 = float(tmp1)/float(tmp2)
                    else:
                        tmp3 = None
                    r.update({str1 + "/" + str2:tmp3})
        #code,dateと比率になっていないものはすべて削除
        return [ { s:r[s] for s in r.keys() if s==u"date" or s==u"code" or re.match(r'.*/.*',s)} for r in composition_data]
    def convertToListFromDictionary(self,data):
        data
        pass
    
if __name__ == "__main__" :
    db = Database()
    conn = db.getConnectionNoAuth(u"127.0.0.1")
    coll = db.getCollection(conn, u"slice", u"prices")
    array = Data().getData(coll)
    print array[0][u"code"]
    conn.close()
