import pymysql
from datetime import datetime, timedelta

def getdate(now,i):
    try:
        # 连接到 MySQL 数据库
        cnx = pymysql.connect(host='127.0.0.1', user='root', password='password', database='triaxial')
        cursor = cnx.cursor()
    except pymysql.Error:
        return None
    # 计算最近三秒的时间范围
    three_seconds_ago = now - timedelta(seconds=30)

    # 查询最近三秒内的数据
    query = "SELECT * FROM data_table WHERE time >= %s"
    values = (three_seconds_ago,)
    cursor.execute(query, values)

    #data_dict = {}
    ls_time=[]
    ls_data=[]
    now = datetime.timestamp(datetime.strptime(str(now), '%Y-%m-%d %H:%M:%S.%f')) * 1000
    for result in cursor.fetchall():
        timestamp = result[1]
        timestamp = datetime.timestamp(datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S.%f')) * 1000
        timestamp = now - timestamp
        # if id not in data_dict:
        #     data_dict[id] = {'data_list': [], 'timestamp_list': []}
        # data_dict[id]['data_list'].append(value)
        # data_dict[id]['timestamp_list'].append(timestamp)
        ls_time.append(timestamp)
        ls_data.append(result[i])

    # 关闭数据库连接
    cursor.close()
    cnx.close()

    return ls_data,ls_time


# now = datetime.now()
# data,time = getdate(now,2)
# print(data,time)

# # 获取采集器id为'001'的设备数据和采集时间列表
# data_list = data_dict.get('001', {}).get('data_list', [])
# timestamp_list = data_dict.get('001', {}).get('timestamp_list', [])
# 获取 data_dict 中所有采集器id
# id_list = list(data_dict.keys())
