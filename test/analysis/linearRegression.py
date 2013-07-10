'''
Created on Jul 8, 2013

@author: soultoru
'''
from test.db.mongo import Database
import pandas
import statsmodels.api as sm

class LinearRegression(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.name=="LinearRegression"
        
    
    def getLinearRegression(self):
        sm.GLM().fit()
        
if __name__ == "__main__" :
    print "#################################"
    data = sm.datasets.scotland.load()
    print data
    data.exog = sm.add_constant(data.exog)
    print data.exog
    gamma_model = sm.GLM(data.endog, data.exog,family=sm.families.Gamma())
    gamma_results = gamma_model.fit()
    print gamma_results.params
    print gamma_results.scale
    print gamma_results.deviance
    print gamma_results.pearson_chi2
    print gamma_results.llf
    print "#################################"