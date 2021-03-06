#!/usr/bin/env python

import pymysql
import pandas as pd
import sys, json

sys.path.append('../utils')
from aes_crypto import AESCipher
from utils import md5_unique

# equity basics path
eq_path='/home/lzhenn/array/lzhenn/findata/equity/instrument/180805/'



def mainfunc():
    pd_cre=pd.read_csv('../../credential/credential.csv', index_col='item')
    code =pd_cre.loc['mysql','cred']
    
    crypto_obj=AESCipher('Always Love You')
    passwd=crypto_obj.decrypt(code)
    
    connection = pymysql.connect(host='localhost',
                             user='lzhenn',
                             password=passwd,
                             db='mercuriusdb',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    ii=0 
    while ii<144:
        fn='instrument_%03d.json' % ii
        print(fn)
        json_str=open(eq_path+'/'+fn).read()
        json_str=json_str.replace('\\\\\\','xxx')
        json_str=json_str.replace('\\','')
        json_str=json_str.replace('xxx','\\')
        json_str=json_str.strip('"')
        data=json.loads(json_str)
        datalist=data['results'] 
        for item in datalist:
            with connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `eq_symbol_id_name` (`name`, `symbol`, `bbid`, `rhid`,`mcid`,`simple_name`, `country`, `type`, `list_date`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "+\
                      "on duplicate key update `name`=`name`;"
                cursor.execute(sql, (str(item['name']),str(item['symbol']),str(item['bloomberg_unique']),str(item['id']),str(md5_unique(item['bloomberg_unique']+item['symbol'])),str(item['simple_name']),item['country'],item['type'],item['list_date']))
        ii=ii+1
    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()
    connection.close()

if __name__=='__main__':
    mainfunc()
