import typing
import math
import pandas as pd
from copy import copy
from pyecharts.charts import Page
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Grid, Kline
from pyecharts.commons.utils import JsCode

def safe_index(df):
    data = None
    if str(df.index.dtype) == 'datetime64[ns]':
        data = df.index.to_series().dt.strftime("%Y-%m-%d").tolist()
    else:
        data = [str(x) for x in df.index.tolist()]
    return data

def safe_last_value(df, col, value=None):
    if col in df.columns:
        return df[col].iloc[-1]
    return value


def get_pos_top_height_kline(plot_list: typing.List[typing.Any]):
    plot_list = [plot for plot in plot_list if plot]
    plot_index = [i + 1 for i in range(len(plot_list))]
    sub_graph_count = len(plot_index)
    border = 5
    if sub_graph_count == 0:
        pos_top_list = [5, 90]
        height_list = [78, 10]
    elif sub_graph_count == 1:
        pos_top_list = [5, 65]
        height_list = [50, 20]
    else:
        pos_top_list = [5]
        height_list = [45]
        # top_height = 5
        # kline_height = 45
        kline_label_height = 5 
        # timebar_height = 11
        # 100 = top_height + kline_height + subcharts + timebar_height
        split_count = int( (39 - border*sub_graph_count - kline_label_height - 5) / sub_graph_count) 
        for i in range(sub_graph_count):
            label_height = 0
            if i == 0:
                label_height = 5
            pos_top_list.append(pos_top_list[-1] + height_list[-1] + border + label_height)
            height_list.append(split_count)
    # print(pos_top_list, height_list)
    return pos_top_list, height_list

def get_pos_top_height(plot_list: typing.List[typing.Any]):
    plot_list = [plot for plot in plot_list if plot]
    plot_index = [i for i in range(len(plot_list))]
    sub_graph_count = len(plot_index)
    border = 5
    # if sub_graph_count == 0 or sub_graph_count == 1:
    #     pos_top_list = [5, 90]
    #     height_list = [85, 15]
    # else:
    #     pos_top_list = [5]
    #     height_list = [20]
    label = 5
    split_height = int( (100 - (sub_graph_count+1)*border - label) / sub_graph_count )
    pos_top_list = [border]
    height_list = [split_height]
    for i in range(sub_graph_count-1):
        label = 5 if i == 0 else 0
        pos_top_list.append(pos_top_list[-1] + height_list[-1] + border + label)
        height_list.append(split_height)
    return pos_top_list, height_list


def filter_bar_plot(bar_plot_list: typing.List[Bar]) -> typing.List[Bar]:
    return [bar_plot for bar_plot in bar_plot_list if bar_plot]




def plot_add_yaxis(
    chart,
    data: pd.DataFrame,
    label: str,
    xindex: int,
    yindex = 0,
    showPoint: bool = False,
    side: str = 'left',
    point = None,
    gap: str = None,
    extendAxis: bool=False,
    extendLabel: str=None
):

    isLine = isinstance(chart, Line)
    ydata = data.tolist()
    if isLine:
        # Line
        chart.add_yaxis(
            series_name=label,
            y_axis=ydata,
            xaxis_index=xindex,
            yaxis_index=yindex,
            # y數值
            label_opts=opts.LabelOpts(is_show=showPoint),
            # markpoint_opts=opts.MarkPointOpts(
            #     data=[
            #         opts.MarkPointItem(type_="max", name="最大值"),
            #         opts.MarkPointItem(type_="min", name="最小值")
            #     ]
            # )
        )
        return

    # Bar
    chart.add_yaxis(
        series_name=label,
        y_axis=ydata,
        xaxis_index=xindex,
        yaxis_index=yindex,
        # y數值
        label_opts=opts.LabelOpts(is_show=showPoint),
        gap=gap,
        # markpoint_opts=opts.MarkPointOpts(
        #     data=[
        #         opts.MarkPointItem(type_="max", name="最大值"),
        #         opts.MarkPointItem(type_="min", name="最小值")
        #     ]
        # )
    )

    if extendAxis:
        extSide = 'right' if side == 'left' else 'left'
        chart.extend_axis(
            yaxis=opts.AxisOpts(
                name=extendLabel,
                type_="value",
                position=extSide,
            )
        )
    # return chart

def gen_graphic_opts():
    graphic_opts=[
        opts.GraphicGroup(
            graphic_item=opts.GraphicItem(
                rotation=JsCode("Math.PI / 4"),
                bounding="raw",
                right=110,
                bottom=110,
                z=100,
            ),
            children=[
                opts.GraphicRect(
                    graphic_item=opts.GraphicItem(
                        left="center", top="center", z=100
                    ),
                    graphic_shape_opts=opts.GraphicShapeOpts(width=400, height=50),
                    graphic_basicstyle_opts=opts.GraphicBasicStyleOpts(
                        fill="rgba(0,0,0,0.3)"
                    ),
                ),
                opts.GraphicText(
                    graphic_item=opts.GraphicItem(
                        left="center", top="center", z=100
                    ),
                    graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                        text="pyecharts bar chart",
                        font="bold 26px Microsoft YaHei",
                        graphic_basicstyle_opts=opts.GraphicBasicStyleOpts(
                            fill="#fff"
                        ),
                    ),
                ),
            ],
        )
    ]
    return graphic_opts

def make_points(point, ylist):
    if point is None:
        return None
    point_data = []
    num = 0
    idx_list = safe_index(point)
    # data_list = point.tolist()
    for p in point.tolist():
        # print([idx_list[num], ylist[num]], p)
        v = opts.MarkPointItem(
                name="", 
                coord=[
                    idx_list[num], 
                    round(ylist[num]*1.025 if p > 0 else ylist[num]*0.85 ,0) 
                ], 
                value=round(p,1)
            )
        point_data.append(v)
        num+=1
    # print(point_data)
    markpoint_opts=opts.MarkPointOpts(data=point_data)
    return markpoint_opts

def gen_bar(
    data: pd.DataFrame,
    label: str,
    xindex: int,
    yindex = 0,
    showPoint: bool = False,
    side: str = 'left',
    extendAxis: bool = False,
    extendLabel: str = '',
    point = None,
    gap: str = None,
    zoom: bool = False
):
    xdata = safe_index(data)
    ydata = data.tolist()

    datazoomOpts = None
    if zoom:
        datazoomOpts = [opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")]


    bar = Bar()
    bar.add_xaxis(xaxis_data=xdata)
    bar.add_yaxis(
        series_name=label,
        y_axis=ydata,
        xaxis_index=xindex,
        yaxis_index=yindex,
        # y數值
        label_opts=opts.LabelOpts(is_show=showPoint),
        gap=gap,
        # markpoint_opts=opts.MarkPointOpts(
        #     data=[
        #         opts.MarkPointItem(type_="max", name="最大值"),
        #         opts.MarkPointItem(type_="min", name="最小值")
        #     ]
        # )
    )
    bar.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            type_="category",
            grid_index=xindex,
            # axislabel_opts=opts.LabelOpts(is_show=showPoint),
            # axislabel_opts=opts.LabelOpts(is_show=True),
            axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="shadow"),
        ),
        # yaxis_opts=opts.AxisOpts(position=side),
        yaxis_opts=opts.AxisOpts(
        #     # is_scale=True,
            name=label,
            position=side,
        #     # name_gap=0,
        #     # Y軸值            
        #     # axisline_opts=opts.AxisLineOpts(is_show=False),
        #     # axistick_opts=opts.AxisTickOpts(is_show=False),
        #     # 橫向分割-區域線
            splitline_opts=opts.SplitLineOpts(is_show=True),
        #     # 橫向分割-區域黑白區間顯示
        #     # splitarea_opts=opts.SplitAreaOpts(
        #     #     is_show=True, 
        #     #     areastyle_opts=opts.AreaStyleOpts(opacity=0.8)
        #     # ),
        ),
        # legend_opts=opts.LegendOpts(is_show=False),
        datazoom_opts=datazoomOpts,
        graphic_opts=gen_graphic_opts()

    )

    if extendAxis:
        extSide = 'right' if side == 'left' else 'left'
        bar.extend_axis(
            yaxis=opts.AxisOpts(
                name=extendLabel,
                type_="value",
                position=extSide,
            )
        )

    return bar

def gen_line(
    data: pd.DataFrame,
    label: str,
    xindex: int,
    yindex: int = 0,
    point: pd.DataFrame = None,
    showPoint: bool = False,
    side: str = 'left',
    extendAxis: bool = False,
    extendLabel: str = '',
    isOverlap: bool = False,
    zoom: bool = False
) -> Line:

    xdata = safe_index(data)
    ydata = data.tolist()
    markpoints = make_points(point, ydata)

    datazoomOpts = None
    if zoom:
        datazoomOpts = [opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")]

    line = Line(
        init_opts=opts.InitOpts(
            animation_opts=opts.AnimationOpts(animation=False),
        )
    )
    line.add_xaxis(xaxis_data=xdata)
    line.add_yaxis(
        series_name=label,
        y_axis=ydata,
        # is_smooth=True,
        # is_symbol_show=False,
        # is_hover_animation=False,
        linestyle_opts=opts.LineStyleOpts(width=2, opacity=1),
        label_opts=opts.LabelOpts(is_show=showPoint),
        xaxis_index=xindex,
        yaxis_index=yindex,
        markpoint_opts=markpoints,
        # markpoint_opts=opts.MarkPointOpts(
        #     data=[
        #         opts.MarkPointItem(type_="max", name="最大值"),
        #         opts.MarkPointItem(type_="min", name="最小值")
        #     ]
        # )
    )
    line.set_global_opts(        
        xaxis_opts=opts.AxisOpts(
            type_="category",
            # grid_index=[0,1],
            axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="shadow"),
        ),
        yaxis_opts=opts.AxisOpts(
            is_scale=True,
            splitarea_opts=opts.SplitAreaOpts(
                is_show=True, 
                areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
            position=side,
            ## formatter
            # axislabel_opts=opts.LabelOpts(formatter="{value} /月"),
            # min_=JsCode(min_function),
            # max_=JsCode(max_function),
            # min_="dataMin",
            # max_="dataMax"
        ),
        # yaxis_opts=opts.AxisOpts(position="left"),
        # legend_opts=opts.LegendOpts(is_show=False),
        # legend_opts=opts.LegendOpts(pos_bottom="5%")
        datazoom_opts = datazoomOpts
    )

    if extendAxis:
        extSide = 'left' if side == 'right' else 'left'
        line.extend_axis(
            yaxis=opts.AxisOpts(
                name=extendLabel,
                type_="value",
                position=extSide,
            )
        )



    return line

def gen_table(title, headers, rows):
    table = Table()
    table.add(headers, rows)
    table.set_global_opts(
        title_opts=ComponentTitleOpts(
            title=title, 
            # subtitle="我是副标题支持换行哦"
        )
    )
    return table

def gen_kline_plot(
    stock_data: pd.DataFrame,
    chart_data: [],
):
    xaxis_index = [i for i in range(len(chart_data)+1)] 
    # xaxis_data = stock_data.index.to_series().dt.strftime("%Y-%m-%d").tolist()
    xaxis_data = safe_index(stock_data)
    min_value = stock_data.low.min()
    max_value = stock_data.high.max()
    ndigits = 0
    if min_value < 10:
       ndigits = 2

    rangeStart = int((len(xaxis_data)-30)/len(xaxis_data)*100)
    # print(rangeStart)
    
    # [open, close, low, high]
    kline_data = [
        list(kline_dict.values())
        for kline_dict in stock_data[["open", "close", "low", "high"]].to_dict(
            "records"
        )
    ]

    
    kline = Kline(
        init_opts=opts.InitOpts(
            animation_opts=opts.AnimationOpts(animation=False),
        )
    )
    kline.add_xaxis(
        xaxis_data=xaxis_data
    )
    kline.add_yaxis(
        series_name="",
        y_axis=kline_data,
        itemstyle_opts=opts.ItemStyleOpts(color="#ec0000", color0="#00da3c"),
    )
    kline.set_global_opts(
        legend_opts=opts.LegendOpts(is_show=True, pos_left="center"),
        datazoom_opts=[
            # 滑鼠可以控制放大縮小
            opts.DataZoomOpts(
                is_show=False,
                type_="inside",
                xaxis_index=xaxis_index,
                range_start=rangeStart,
                range_end=100,
            ),
            opts.DataZoomOpts(
                is_show=True,
                xaxis_index=xaxis_index,
                type_="slider",
                pos_top="90%",
                range_start=rangeStart,
                range_end=100,
            ),
        ],
        yaxis_opts=opts.AxisOpts(
            is_scale=True,
            splitarea_opts=opts.SplitAreaOpts(
                is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
            # min_=round(min_value*0.95, ndigits),
            # max_=round(max_value*1.05, ndigits),
            # min_="dataMin",
            # max_="dataMax",
            # min_=JsCode(min_function),
            # max_=JsCode(max_function),
        ),
        xaxis_opts=opts.AxisOpts(
            type_="category",
            is_scale=True,
            boundary_gap=False,
            axisline_opts=opts.AxisLineOpts(is_on_zero=False),
            splitline_opts=opts.SplitLineOpts(is_show=False),
            split_number=20,
            min_="dataMin",
            max_="dataMax",
        ),
        # 右上角工具箱
        tooltip_opts=opts.TooltipOpts(
            trigger="axis",
            axis_pointer_type="cross",
            background_color="rgba(245, 245, 245, 0.8)",
            border_width=1,
            border_color="#ccc",
            textstyle_opts=opts.TextStyleOpts(color="#000"),
        ),
        # 視覺指針
        # visualmap_opts=opts.VisualMapOpts(
        #     is_show=False,
        #     dimension=2,
        #     series_index=series_index,
        #     is_piecewise=True,
        #     pieces=[
        #         {"value": 1, "color": "#ec0000"},
        #         {"value": -1, "color": "#00da3c"},
        #     ],
        # ),
        # 跨多個x軸
        axispointer_opts=opts.AxisPointerOpts(
            is_show=True,
            link=[{"xAxisIndex": "all"}],
            label=opts.LabelOpts(background_color="#777"),
        ),
        # 右上角brush筆畫工具
        brush_opts=opts.BrushOpts(
            x_axis_index="all",
            brush_link="all",
            out_of_brush={"colorAlpha": 0.1},
            brush_type="lineX",
        ),
    )
    return kline

def gen_grid(
    plot_list: typing.List[Bar],
    width: str,
    height: str,
    filename: str=None,
    zoom: bool=False,
    extendAxis: bool=False
) -> Grid:
    datazoomOpts = None
    if zoom:
        xaxis_index = [i for i in range(len(plot_list))] 
        datazoomOpts = [
            opts.DataZoomOpts(
                xaxis_index=xaxis_index,
            ), 
            opts.DataZoomOpts(
                xaxis_index=xaxis_index,
                type_="inside")
        ]
    # if extendAxis:
    index = 0
    topPlot = plot_list[0]
    topPlot.set_global_opts(
        # 跨多個x軸（顯示x軸）
        axispointer_opts=opts.AxisPointerOpts(
            is_show=True,
            link=[{"xAxisIndex": "all"}],
            label=opts.LabelOpts(background_color="#777"),
        ),
        legend_opts=opts.LegendOpts(pos_top="0%"),
        datazoom_opts=datazoomOpts,        
    )
    # for plot in plot_list:
    #     plot.set_global_opts(
    #         # 跨多個x軸（顯示x軸）
    #         axispointer_opts=opts.AxisPointerOpts(
    #             is_show=True,
    #             link=[{"xAxisIndex": "all"}],
    #             label=opts.LabelOpts(background_color="#777"),
    #         ),
    #         legend_opts=opts.LegendOpts(pos_top="0%"),
    #         datazoom_opts=datazoomOpts
    #     )

    grid_chart = Grid(
        init_opts=opts.InitOpts(
            width=width,
            height=height,
            animation_opts=opts.AnimationOpts(animation=False),
        )
    )
    pos_top_list, height_list = get_pos_top_height(plot_list=plot_list)

    for plot in plot_list:
        if topPlot != plot:
            plot.set_global_opts(
                legend_opts=opts.LegendOpts(pos_top=f"{pos_top_list[index]-5}%")
            )
        grid_chart.add(
            plot,
            grid_opts=opts.GridOpts(
                pos_left="10%",
                pos_right="8%",
                pos_top=f"{pos_top_list[index]}%",
                height=f"{height_list[index]}%",
            ),
            # 1. 使用時, 在多個subchart時, 會導致全部集中在一起
            # 2. extendAxis 兩個以上的 yaxis, 一定要開啟才會正常顯示
            is_control_axis_index=True if extendAxis else False
        )
        index += 1

    return grid_chart

def plot_kline_charts(
    overlap_kline_line: Kline,
    plot_list: typing.List[Bar],
    width: str,
    height: str,
    filename: str=None,
) -> Grid:
    index = 0
    grid_chart = Grid(
        init_opts=opts.InitOpts(
            width=width,
            height=height,
            animation_opts=opts.AnimationOpts(animation=False),
        )
    )
    pos_top_list, height_list = get_pos_top_height_kline(plot_list=plot_list)
    grid_chart.add(
        overlap_kline_line,
        grid_opts=opts.GridOpts(
            pos_left="10%",
            pos_right="8%",
            pos_top=f"{pos_top_list[index]}%",
            height=f"{height_list[index]}%",
        ),        
        # is_control_axis_index=True
    )
    index += 1
    bar_plot_list = filter_bar_plot(plot_list)
    for sub_plot in bar_plot_list:
        if index == 1:
            sub_plot.set_global_opts(
                legend_opts=opts.LegendOpts(pos_top=f"{pos_top_list[index]-5}%"),
            )
        grid_chart.add(
            sub_plot,
            grid_opts=opts.GridOpts(
                pos_left="10%",
                pos_right="8%",
                pos_top=f"{pos_top_list[index]}%",
                height=f"{height_list[index]}%",
            ),
            # 
        )
        index += 1
    # grid_chart.render(filename)
    return grid_chart



def plots(barDf, chartDfs):
    subcharts = []
    chart_map = {}
    overlap_charts = []
    normal_data_map = {}
    overlap_data_map = {}
    # 1. tidy all charts
    for df in chartDfs:
        chartType = df.chart.iloc[-1]
        label = df.label.iloc[-1] 
        isOverlap = df.isOverlap.iloc[-1]
        side = 'left'
        showPoint = False        
        if 'side' in df.columns:
            side = df.side.iloc[-1]
        if 'showPoint' in df.columns:
            showPoint = df.showPoint.iloc[-1]
        if isOverlap:
            overlap = 'main'
            if 'overlap' in df.columns:
                overlap = df.overlap.iloc[-1]
                datas = overlap_data_map.setdefault( overlap, [])
                datas.append(df)
        else:
            normal_data_map[label] = df
    
    # settings for chart
    xidx = 0
    yidx = 0

    # 2. overlap to kline
    datas = overlap_data_map.get('main', [])    
    for subdf in datas:
        # xidx = yidx
        subChartType = subdf.chart.iloc[-1]
        subLabel = subdf.label.iloc[-1] 
        subSide = 'left'
        subShowPoint = False
        subPoint = None
        if 'point' in subdf.columns:
            subPoint = subdf.point
        if 'side' in subdf.columns:
            subSide = subdf.side.iloc[-1]
        if 'showPoint' in subdf.columns:
            subShowPoint = subdf.showPoint.iloc[-1]
        if subChartType == 'line':
            chart = gen_line(
                subdf.value, subLabel, xidx, 
                showPoint=showPoint, point=subPoint, side=side)
        else:
            chart = gen_bar(
                df.value, label, xidx, 
                showPoint=showPoint, point=subPoint, side=side)
        overlap_charts.append(chart) 
        xidx +=1

    # 3. subchart
    for label, df in normal_data_map.items():
        xidx = 0
        yidx = 0
        chartType = df.chart.iloc[-1]
        label = df.label.iloc[-1] 
        side = 'left'
        point = None
        isOverlap = df.isOverlap.iloc[-1]
        showPoint = False
        extendAxis = False
        if 'point' in df.columns:
            point = df.point
        if 'side' in df.columns:
            side = df.side.iloc[-1]
        if 'showPoint' in df.columns:
            showPoint = df.showPoint.iloc[-1]
        if 'extendAxis' in df.columns:
            extendAxis = df.extendAxis.iloc[-1]
        
        if chartType == 'line':
            chart = gen_line(
                df.value, label, xidx, 
                showPoint=showPoint, point=point, side=side, extendAxis=extendAxis)
        else:
            chart = gen_bar(
                df.value, label, xidx, 
                showPoint=showPoint, point=point, side=side, extendAxis=extendAxis)
        datas = overlap_data_map.get(label, [])
        for subdf in datas:
            # yidx =xidx+1
            yidx +=1
            subChartType = subdf.chart.iloc[-1]
            subLabel = subdf.label.iloc[-1] 
            subSide = 'left'
            subPoint = None
            subShowPoint = False
            if 'side' in subdf.columns:
                subSide = subdf.side.iloc[-1]
            if 'showPoint' in subdf.columns:
                subShowPoint = subdf.showPoint.iloc[-1]
            if 'point' in subdf.columns:
                subPoint = subdf.point

            subchart = gen_line(
                subdf.value, 
                subLabel, 
                xidx, 
                point=subPoint, 
                showPoint=subShowPoint, 
                yindex=yidx, 
                side=subSide, 
                isOverlap=True)
            chart.overlap(subchart)
        subcharts.append(chart)
        xidx +=1

    kchart = gen_kline_plot(barDf, subcharts)
    for chart in overlap_charts:
        kchart.overlap(chart)
    high = 600
    if len(subcharts) > 3:
        high = len(subcharts)*200
    return plot_kline_charts(kchart, subcharts, '100%', f'{high}px')
