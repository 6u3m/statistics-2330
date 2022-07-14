from datetime import datetime
import pandas as pd


pd.options.display.float_format = '{:.2f}'.format

def statistics_pepb(df, bardf):    
    for idx, row in df.iterrows():
        dps = '現金股利'
        eps = '每股盈餘_TTM'
        book = '淨值'
        month = 1

        s = datetime(row.start.year, row.start.month, row.start.day)
        e = datetime(row.end.year, row.end.month, row.end.day)

        mark = (
            (bardf.datetime >= s) &
            (bardf.datetime <= e )
        )
        n = bardf[mark]
        count = n.shape[0]
        if count == 0:
            continue

        # 股價變化
        _o = n.open.iloc[0]
        _h = n.high.max()
        _l = n.low.min()
        _c = n.close.iloc[-1]

        # 本益比淨值比
        _pe = n.close/row[eps]
        _pe_max = n.high/row[eps]
        _pe_min = n.low/row[eps]
        _pb = n.close/row[book]
        _pb_max = n.high/row[book]
        _pb_min = n.low/row[book]
        _pe = _pe[_pe>0]

        sel = df.start == s
        df.loc[sel, '本益比平均數'] = _pe.mean()
        df.loc[sel, '本益比最大值'] = _pe_max.max()
        df.loc[sel, '本益比最小值'] = _pe_min.min()
        df.loc[sel, '淨值比平均數'] = _pb.mean()
        df.loc[sel, '淨值比最大值'] = _pb_max.max()
        df.loc[sel, '淨值比最小值'] = _pb_min.min()
        df.loc[sel, 'open'] = _o
        df.loc[sel, 'high'] = _h
        df.loc[sel, 'low'] = _l
        df.loc[sel, 'close'] = _c



bardf = pd.read_csv("bars.csv")
bardf['datetime'] = pd.to_datetime(bardf['datetime']) # 轉換成日期格式
bardf.index = bardf['datetime']                       #

findf = pd.read_csv("quarter.csv")
findf.index = findf['quarter']
findf.start = pd.to_datetime(findf.start)
findf.end = pd.to_datetime(findf.end)
findf['每股盈餘_TTM'] = findf['每股盈餘'].rolling(window=4).sum()


statistics_pepb(findf, bardf)

#
print(findf[['本益比最小值', '本益比平均數', '淨值比平均數', 'high', 'low']])

# 儲存數據
findf.to_csv('demo2.csv')



