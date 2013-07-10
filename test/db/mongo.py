# coding:utf-8
'''
Created on Jul 8, 2013

@author: soultoru
'''


from pymongo import Connection

class Database(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.name = 'Database'
    @classmethod
    def getConnection(self,host,database,user,password):
        return Connection(u"mongodb://"+user+u":"+password+u"@"+host+u"/"+database)
    @classmethod
    def getConnectionNoAuth(self,host):
        return Connection(host)

    def getCollection(self,connection,database,collection):
        return connection[database][collection]

    def find(self,collection):
        cursor = collection.find({})
        array = list()
        for data in cursor:
            array.append(data)
        return array

    def close(self,conn):
        conn.close()
        
