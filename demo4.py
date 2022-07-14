from datetime import datetime
import pandas as pd
import numpy as np
import plotting


offline = False

pd.options.display.float_format = '{:.2f}'.format


def zigzag_6u3m(s, pct=10.0, cols=['O','H','L','C']):
    ut = 1 + pct / 100
    dt = 1 - pct / 100

    O = cols[0]
    H = cols[1]
    L = cols[2]
    C = cols[3]

    dp = s.index[0]
    lp = s[C][dp]
    hp = None
    tr = None

    # zzd, zzp = [pd], [lp]
    zzd, zzp = [], []

    # changeH, changeL
    # Lpoint, Hpoint
    for ix, ch, cl in zip(s.index, s[H], s[L]):
        # No initial trend
        if tr is None:
            if ch > lp:
                tr = 1
                lp, hp = cl, ch
                zzd.append(dp)
                zzp.append(lp)
            elif cl < lp:
                tr = -1
                lp, hp = cl, ch
                zzd.append(pd)
                zzp.append(hp)
            else:
                tr = 1
                lp, hp = cl, ch
                zzd.append(dp)
                zzp.append(lp)
        # Trend is up
        elif tr == 1:
            # New H
            if ch > hp:
                dp, lp, hp = ix, cl, ch
            # Reversal
            elif cl < lp and (hp-cl)/hp > pct/100:
                zzd.append(dp)
                zzp.append(hp)

                tr, dp, lp, hp = -1, ix, cl, ch
        # Trend is down
        else:
            # New L
            if cl < lp:
                dp, lp, hp = ix, cl, ch
            # Reversal
            elif ch > hp and (ch-lp)/lp > pct/100:
                zzd.append(dp)
                zzp.append(lp)

                tr, dp, lp, hp = 1, ix, cl, ch

    # Extrapolate the current trend
    if zzd[-1] != s.index[-1]:
        zzd.append(s.index[-1])

        if tr is None:
            zzp.append(s[C][zzd[-1]])
        elif tr == 1:
            zzp.append(s[H][zzd[-1]])
        else:
            zzp.append(s[L][zzd[-1]])


    return pd.Series(zzp, index=zzd)

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



def statisitics_period(statdf, bardf, period="1W"):
    ## 1W週/1M月/1Q季統計
    s = statdf.datetime.iloc[0]
    e = statdf.datetime.iloc[-1]

    tdf = pd.date_range(f'{s.year}-{s.month}-1',f'{e.year}-{e.month}-1', freq=period)
    o = pd.DataFrame()
    for dt in tdf.tolist():
        if period == '1W':
            s = datetime(dt.year, dt.month, dt.day) - timedelta(days=6)
            e = datetime(dt.year, dt.month, dt.day)
        elif period == '1M':
            s = datetime(dt.year, dt.month, 1)
            e = datetime(dt.year, dt.month, dt.day)
        elif period == '1Q':
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

        # 統計數據結果
        sel = (statdf.start >= s) & (statdf.start <= e)
        statdf.loc[sel, '本益比平均數'] = _pe.mean()
        statdf.loc[sel, '本益比最大值'] = _pe_max.max()
        statdf.loc[sel, '本益比最小值'] = _pe_min.min()
        statdf.loc[sel, '淨值比平均數'] = _pb.mean()
        statdf.loc[sel, '淨值比最大值'] = _pb_max.max()
        statdf.loc[sel, '淨值比最小值'] = _pb_min.min()

    return statdf

def get_period(bar, period="1W"):
    # bar => 轉換 => 每月統計數據
    # period = 1W週/1M月/1Q季統計
    bar = bar.sort_index()
    s = bar.datetime.iloc[0]
    e = bar.datetime.iloc[-1]

    year = e.year
    month = e.month+1
    if e.month+1>12:
        year+=1
        month=1
    e = datetime(year, month, 1)


    drs = pd.date_range(f'{s.year}-{s.month}-1',f'{e.year}-{e.month}-{e.day}', freq=period)
    o = pd.DataFrame()
    for dt in drs.tolist():
        if period == '1W':
            s = datetime(dt.year, dt.month, dt.day) - timedelta(days=6)
            e = datetime(dt.year, dt.month, dt.day)
        elif period == '1M':
            s = datetime(dt.year, dt.month, 1)
            e = datetime(dt.year, dt.month, dt.day)
        mark = (bar.datetime >= s) & (bar.datetime <= e )
        n = bar[mark]
        if n.shape[0] == 0:
            continue 
        data = {
            'datetime': s,
            'start': s,
            'end': e,
            'price': n.close.mean(),
            'open': n.open.iloc[0],
            'high': n.high.max(),
            'low': n.low.min(),
            'close': n.close.iloc[-1],
            'volume': n.volume.sum(),
            '每股盈餘_TTM': n['每股盈餘_TTM'].iloc[-1]
        }
        t = pd.DataFrame([data])
        o = o.append(t)

    o.index = o.start
    return o


bardf = pd.read_csv("bars.csv")
bardf['datetime'] = pd.to_datetime(bardf['datetime']) # 轉換成日期格式
bardf.index = bardf['datetime']                       #

qdf = pd.read_csv("quarter.csv")
qdf.index = qdf['quarter']
qdf['datetime'] = pd.to_datetime(qdf['datetime'])
qdf['start'] = pd.to_datetime(qdf.start)
qdf['end'] = pd.to_datetime(qdf.end)
qdf['每股盈餘_TTM'] = qdf['每股盈餘'].rolling(window=4).sum()

# 1.
statistics_bar(bardf, qdf)
# 2.
barmdf = get_period(bardf, period='1M')
# 3.
barmdf = statisitics_period(barmdf, bardf, period='1Q')
# 儲存數據
barmdf.to_csv('demo4.csv')

# 圖表
df = barmdf
charts = []
cols=['open','high','low','close']
s = zigzag_6u3m(df, cols=cols)
s.name = 'value'
c = pd.DataFrame(s)
c['chart'] = 'line'
c['label'] = 'ZigZag'
c['point'] = c.value.pct_change()*100
c['isOverlap'] = True
c['overlap'] = 'main'
charts.append(c)

s = round(df['本益比最大值']*df['每股盈餘_TTM'],1)
s.name = 'value'
c = pd.DataFrame(s)
c['chart'] = 'line'
c['label'] = 'Max'
c['isOverlap'] = True
c['overlap'] = 'main'
c['showPoint'] = False
charts.append(c)

s = round(df['本益比最小值']*df['每股盈餘_TTM'],1)
s.name = 'value'
c = pd.DataFrame(s)
c['chart'] = 'line'
c['label'] = 'Min'
c['isOverlap'] = True
c['overlap'] = 'main'
c['showPoint'] = False
charts.append(c)

s = round(df['每股盈餘_TTM'],2)
s.name = 'value'
c = pd.DataFrame(s)
c['chart'] = 'bar'
c['label'] = 'EPS TTM'
c['isOverlap'] = False
c['overlap'] = ''
c['showPoint'] = False
c['side'] = 'left'
c['extendAxis'] = True
charts.append(c)

chart = plotting.plots(df, charts)

chart.render('demo4.html')
content = open('demo4.html', 'r').read()
content = content.replace('Awesome-pyecharts', '自己統計台積電的金融數據demo4')
if offline:
    content = content.replace('https://assets.pyecharts.org/assets/echarts.min.js', './echarts.min.js')
with open('demo4.html', 'w') as f:
    f.write(content)
    f.close()
