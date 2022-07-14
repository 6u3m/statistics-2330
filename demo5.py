from datetime import datetime
import pandas as pd
import numpy as np

offline = False

pd.options.display.float_format = '{:.2f}'.format


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


def statisitics_pepb2(statdf, bardf, type="1W"):
    ## 1W週/1M月/1Q季統計
    s = statdf.datetime.iloc[0]
    e = statdf.datetime.iloc[-1]

    tdf = pd.date_range(f'{s.year}-{s.month}-1',f'{e.year}-{e.month}-1', freq=type)
    o = pd.DataFrame()
    for dt in tdf.tolist():
        if type == '1W':
            s = datetime(dt.year, dt.month, dt.day) - timedelta(days=6)
            e = datetime(dt.year, dt.month, dt.day)
        elif type == '1M':
            s = datetime(dt.year, dt.month, 1)
            e = datetime(dt.year, dt.month, dt.day)
        elif type == '1Q':
            s = datetime(dt.year, dt.month-2, 1)
            e = datetime(dt.year, dt.month, dt.day)
        mark = (statdf.datetime >= s) & (statdf.datetime <= e)
        n = statdf[mark]
        if n.shape[0] == 0:
            continue

        mark = (bardf.datetime >= s) & (bardf.datetime <= e)
        _bardf = bardf[mark] 
        if _bardf.shape[0] == 0:
            continue

        barrow = _bardf.iloc[-1]


        # 本益比淨值比
        _pe = _bardf.close/barrow['每股盈餘_TTM']
        _pe_max = _bardf.high/barrow['每股盈餘_TTM']
        _pe_min = _bardf.low/barrow['每股盈餘_TTM']
        _pb = _bardf.close/barrow['淨值']
        _pb_max = _bardf.high/barrow['淨值']
        _pb_min = _bardf.low/barrow['淨值']
        _pe = _pe[_pe>0]

        print(s, e, _pe_min.min(), _pe.mean())

        sel = (statdf.start >= s) & (statdf.start <= e)
        statdf.loc[sel, '本益比平均數'] = _pe.mean()
        statdf.loc[sel, '本益比最大值'] = _pe_max.max()
        statdf.loc[sel, '本益比最小值'] = _pe_min.min()
        statdf.loc[sel, '淨值比平均數'] = _pb.mean()
        statdf.loc[sel, '淨值比最大值'] = _pb_max.max()
        statdf.loc[sel, '淨值比最小值'] = _pb_min.min()

    return statdf

# demo5.py
bardf = pd.read_csv("bars.csv")
bardf['datetime'] = pd.to_datetime(bardf['datetime']) # 轉換成日期格式
bardf.index = bardf['datetime']  

qdf = pd.read_csv("quarter.csv")
qdf.index = qdf['quarter']
qdf['datetime'] = pd.to_datetime(qdf['datetime'])
qdf['start'] = pd.to_datetime(qdf.start)
qdf['end'] = pd.to_datetime(qdf.end)
qdf['Q'] = [(str(x))[4:6] for x in qdf.quarter.tolist()]
qdf['每股盈餘_TTM'] = qdf['每股盈餘'].rolling(window=4).sum()



#
statistics_bar(bardf, qdf)
qdf = statisitics_pepb2(qdf, bardf, type='1Q')


qdf['每股盈餘_AVG_3YEAR'] = (qdf['每股盈餘_TTM'] + qdf['每股盈餘_TTM'].shift(4*1) + qdf['每股盈餘_TTM'].shift(4*2)) / 3
qdf['每股盈餘_AVG_5YEAR'] = (
	  (
    qdf['每股盈餘_TTM'] + 
    qdf['每股盈餘_TTM'].shift(4*1) + 
    qdf['每股盈餘_TTM'].shift(4*2) +
    qdf['每股盈餘_TTM'].shift(4*3) +
    qdf['每股盈餘_TTM'].shift(4*4) 
    ) / 5
)


sel = [
    '每股盈餘_AVG_3YEAR','每股盈餘_AVG_5YEAR','每股盈餘_TTM','每股盈餘_TTM_YoY', 
    '本益比最小值', '本益比平均數_TTM', '本益比平均數_TTM_YoY'
]
display_cols = ['EPS:AVG 3YEAR','5YEAR','__TTM','__YoY','PE:最小值','AVG TTM','__YoY']
#
# 每季YoY數據
#
qdf['每股盈餘_TTM_YoY'] = qdf['每股盈餘_TTM'].pct_change()
qdf['本益比平均數_TTM'] = qdf['本益比平均數'].rolling(window=4).mean()
qdf['本益比平均數_TTM_YoY'] = qdf['本益比平均數_TTM'].pct_change()

n = qdf[sel]
n['每股盈餘_TTM_YoY'] = n['每股盈餘_TTM_YoY']*100
n['本益比平均數_TTM_YoY'] = n['本益比平均數_TTM_YoY']*100
n.columns = display_cols
count = n.shape[0]
print(n[count-21:count])



#
# 前12月YoY數據
#
qdf['每股盈餘_TTM_YoY'] = (qdf['每股盈餘_TTM']-qdf['每股盈餘_TTM'].shift(4))/qdf['每股盈餘_TTM'].shift(4)
qdf['本益比平均數_TTM'] = qdf['本益比平均數'].rolling(window=4).mean()
qdf['本益比平均數_TTM_YoY'] = (qdf['本益比平均數_TTM']-qdf['本益比平均數_TTM'].shift(4))/qdf['本益比平均數_TTM'].shift(4)

mark = (qdf.Q == qdf.Q.iloc[-1])
n = qdf[mark][sel]
n['每股盈餘_TTM_YoY'] = n['每股盈餘_TTM_YoY']*100
n['本益比平均數_TTM_YoY'] = n['本益比平均數_TTM_YoY']*100
n.columns = display_cols
count = n.shape[0]
print(n[count-6:count])