from datetime import datetime
import pandas as pd


bardf = pd.read_csv("bars.csv")
bardf['datetime'] = pd.to_datetime(bardf['datetime']) # 轉換成日期格式
bardf.index = bardf['datetime']                       #

findf = pd.read_csv("quarter.csv")
findf.index = findf['quarter']
findf.start = pd.to_datetime(findf.start)
findf.end = pd.to_datetime(findf.end)
findf['每股盈餘_TTM'] = findf['每股盈餘'].rolling(window=4).sum()


fin = findf.iloc[-1] # 取出最新一季報表
s = datetime(fin.start.year, fin.start.month, fin.start.day)
e = datetime(fin.end.year, fin.end.month, fin.end.day)
mark = (
    (bardf.datetime >= s) &
    (bardf.datetime <= e )
)
n = bardf[mark]
pe = n['open']/fin['每股盈餘_TTM']
pe_max = n['high']/fin['每股盈餘_TTM']
pe_min = n['low']/fin['每股盈餘_TTM']
pb = n['open']/fin['淨值']
pb_max = n['high']/fin['淨值']
pb_min = n['low']/fin['淨值']


print("季別", fin.quarter , "統計交易日", n.shape[0], s.strftime("%Y%m%d"), "~", e.strftime("%Y%m%d"))
print("本益比平均數", pe.mean(), "本益比最大值", pe_max.max(), "本益比最小值", pe_min.min())
print("淨值比平均數", pb.mean(), "淨值比最大值", pb_max.max(), "淨值比最小值", pb_min.min())

