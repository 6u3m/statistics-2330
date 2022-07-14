from datetime import datetime
import pandas as pd
import numpy as np
import math

offline = False


def statistics_bar(bardf, findf , statistics_type=1):
    """
    bar + 財務報表 => 計算本益比 => 將資料寫入 bar
    每天盈餘本益比統計
    2. 每季3,6,9,12月 
    統計區間一
    統計週期: 2022Q1 
    資料日期: 2022-01-01 ~ 2022-03-31
    統計區間二
    統計週期: 2022Q1 
    資料日期: 2022-04-01 ~ 2022-06-31
    2022Q1 前四期eps總和算出 2022Q2 下季的本益比，
    產生的數據會有較大的不準確性，當公司獲利成長轉衰退
    時，等於用較高的eps來算出衰退時候的數據。

    1. 年度
    統計週期: 2021 
    資料日期: 2021-01-01 ~ 2021-12-31
    用 2021 EPS 計算 2021 本益比
    計算出來的數據不連貫, 跨年的時候數據變化過大
    """
    for idx, row in findf.iterrows():
        dps = '現金股利'
        eps = '每股盈餘_TTM'
        book = '淨值'

        if np.isnan(row[eps]):
            continue

        # 
        year = row.datetime.year
        month = row.datetime.month
        # day= 10
        quarter = 3
        sdt = datetime(year, month, 1)
        if month+quarter > 12:
            month = 1
            year=year+1
        else:
            month+=quarter
        edt = datetime(year, month, 1)
        if statistics_type == 2:
            sdt = datetime(year, month, 1)
            if month+quarter > 12:
                month = 1
                year = year+1
            else:
                month+=quarter            
            edt = datetime(year, month, 1)

        mark = (
            (bardf['datetime'] >= sdt) &
            (bardf['datetime'] < edt )
        )
        n = bardf[mark]
        count = n.shape[0]
        if count == 0:
            continue

        # _yield = n.close/row[dps]
        _pe = n.close/row[eps]
        _pe_max = n.high/row[eps]
        _pe_min = n.low/row[eps]
        _pb = n.close/row[book]
        _pb_max = n.high/row[book]
        _pb_min = n.low/row[book]
        _pe = _pe[_pe>0]

        # bardf.loc[_yield.index, '殖利率'] = _yield
        bardf.loc[_pb.index, '淨值比'] = _pb
        bardf.loc[_pb.index, '淨值比最大值'] = _pb_max
        bardf.loc[_pb.index, '淨值比最小值'] = _pb_min
        bardf.loc[_pb.index, '淨值'] = row[book]
        bardf.loc[n.index, '每股盈餘_TTM'] = row[eps]
        if _pe.shape[0] == 0:
            bardf.loc[n.index, '本益比'] = np.nan
            bardf.loc[n.index, '本益比最大值'] = np.nan
            bardf.loc[n.index, '本益比最小值'] = np.nan
        else:
            bardf.loc[_pe.index, '本益比'] = _pe
            bardf.loc[_pe.index, '本益比最大值'] = _pe_max
            bardf.loc[_pe.index, '本益比最小值'] = _pe_min


bardf = pd.read_csv("bars.csv")
bardf['datetime'] = pd.to_datetime(bardf['datetime']) # 轉換成日期格式
bardf.index = bardf['datetime']

qdf = pd.read_csv("quarter.csv")
qdf.index = qdf['quarter']
qdf['datetime'] = pd.to_datetime(qdf['datetime'])
qdf['start'] = pd.to_datetime(qdf.start)
qdf['end'] = pd.to_datetime(qdf.end)
qdf['每股盈餘_TTM'] = qdf['每股盈餘'].rolling(window=4).sum()


statistics_bar(bardf, qdf)


bardf['PE'] = [ math.floor(v) if str(v) != 'nan' else 'nan' for v in bardf['本益比'].tolist()]
operations = {'PE':'count'}
t = bardf.groupby('PE').agg(operations)
t.columns = ['days']
t = t.drop('nan', axis=0)
t = t.reset_index()
print(t)