#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# dataset : https://archive.ics.uci.edu/ml/datasets/Individual+household+electric+power+consumption


# In[1]:


get_ipython().system('spark-submit --version')


# In[2]:


from pyspark.sql import SQLContext
from pyspark import SparkContext, SparkConf
from pyspark.sql import functions as F
from pyspark.sql.functions import udf
from pyspark.sql.types import *
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean


# In[3]:


def get_udf_distance(array1, array2):
    distance, path = fastdtw(array1, array2, dist=euclidean)
    return distance


# In[4]:


conf = SparkConf().setAppName("DTW")
sc   = SparkContext(conf=conf)
sqlContext = SQLContext(sc)


# In[5]:


# Import Data
data   = sc.textFile("household_power_consumption.txt")
header = data.first().split(';')
data   = data.map(lambda x: x.split(';')).filter(lambda x: x!=header)

df = data.toDF(header)

# Use schema
df1 = df.withColumn('Sub_metering_1',df.Sub_metering_1.cast('float'))     .withColumn('Sub_metering_2',df.Sub_metering_2.cast('float'))     .withColumn('Sub_metering_3',df.Sub_metering_3.cast('float'))     .withColumn('Voltage',df.Voltage.cast('float'))

df1.show(5)


# In[6]:


df2 = df1.groupby("Date").agg(F.collect_list("Sub_metering_1").alias('meter1'),F.collect_list("Sub_metering_2").alias('meter2'),F.collect_list("Sub_metering_3").alias('meter3'))

df2.show(5)


# In[10]:


udf_dtw = udf(get_udf_distance , FloatType())
df3 = df2.select('Date', udf_dtw(df2.meter1, df2.meter2).alias('dtw_distance (meter1-meter2)'), udf_dtw(df2.meter2, df2.meter3).alias('dtw_distance (meter2-meter3)'))

df3.show(10)

