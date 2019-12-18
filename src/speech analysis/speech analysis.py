#!/usr/bin/env python
# coding: utf-8

# In[1]:


# dataset : https://archive.ics.uci.edu/ml/datasets/Individual+household+electric+power+consumption


# In[2]:


get_ipython().system('spark-submit --version')


# In[3]:


from pyspark.sql import SQLContext
from pyspark import SparkContext, SparkConf
from pyspark.sql import functions as F
from pyspark.sql.functions import udf
from pyspark.sql.types import *
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from pyspark.sql import Row
from pyspark.sql.functions import lit


# In[48]:


import boto3
import numpy as np
import os


# In[5]:


s3 = boto3.client('s3')


# In[6]:


response = s3.list_objects(Bucket='sagemaker-tired')


# In[7]:


conf = SparkConf().setAppName("DTW")
sc   = SparkContext(conf=conf)
sqlContext = SQLContext(sc)


# In[8]:


def get_udf_distance(array1, array2):
    distance, path = fastdtw(array1, array2, dist=euclidean)
    return distance


# In[144]:


data = []

for content in response.get('Contents'):
    if content.get('Key').split('/')[0] == 'sleep_npy_file' and content.get('Key')[-1] != '/':
        print(content.get('Key')) 
        s3.download_file('sagemaker-tired', content.get('Key'), './raw_npy/' + content.get('Key').split('/')[1])
        np_data = np.load('./raw_npy/' + content.get('Key').split('/')[1])
        #print(np_data)
        np_data = list(np.ravel(np_data))#, order='C')
        mfcc_feat = list(map(float, np_data)) 
        data.append(mfcc_feat)
        
        
R = Row('ID', 'mfcc')

df = sqlContext.createDataFrame([R(i, x) for i, x in enumerate(data)]) 
df.cache()
df.show()


# In[66]:


udf_dtw = udf(get_udf_distance , FloatType())


# In[145]:


data_compare = []
wav_list = os.listdir('./compare_npy')
for file_name in wav_list:
    np_data = np.load('./compare_npy/' + file_name)
    np_data = list(np.ravel(np_data))#, order='C')
    mfcc_feat = list(map(float, np_data)) 
    data_compare.append(mfcc_feat)
    
R2 = Row('ID2', 'compare_mfcc')


# In[114]:


from pyspark.sql.functions import broadcast


# In[146]:


corr_list = []

for data_ in data_compare:    
    arr = sqlContext.createDataFrame([R2(i, data_) for i in range(len(data))]) 
    #arr.show()
    
    df = df.join(broadcast(arr), df.ID == arr.ID2)
    #df.show()


    dtw_df = df.select('ID', udf_dtw(df.mfcc, df.compare_mfcc).alias('result'))
    dtw_df.orderBy('result')#.show()

    value = dtw_df.collect()[0]
    #print(value[1])

    compare_mfcc = df.where(df.ID == value[0]).collect()
    #df.show()
    #print(type(compare_mfcc))
    corr_ = np.corrcoef(data_,compare_mfcc[0][1])[0][1]
    print("corr : ", corr_)
    corr_list.append(corr_)
    df = df.drop("compare_mfcc")


# In[147]:


from pylab import plot, show, ylim

#y = [50.0, 52.0, 60.0, 60.0, 59.0, 73.0, 74.0, 77.0, 69.0, 63.0, 61.0, 56.0]

ylim(-1, 1)
plot(corr_list)
show()


# In[12]:


'''
R2 = Row('ID', 'compare_mfcc')

arr = sqlContext.createDataFrame([R2(i, data[0]) for i in range(len(data))]) 
arr.show()

df = df.join(arr, ["ID"])
df.show()

for name, dtype in df.dtypes:
    print(name, dtype)
    
dtw_df = df.select('ID', udf_dtw(df.mfcc, df.compare_mfcc).alias('result'))
dtw_df.orderBy('result').show()
'''

