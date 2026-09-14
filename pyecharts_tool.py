import string
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Kline, Line, Bar, Grid
from pyecharts.globals import ThemeType

def init_candlestick_view(
  candlestick_dicts:list,
  x_axis_items:list,
  x_axis_indexs:list,
  zoom_range_start:float,
  zoom_range_end:float,
  line_dicts:list,
  mark_line_items:list,
  title="",
  sub_title="",
  is_show_legend=False,):

  kline_view = Kline()
  kline_view.add_xaxis(xaxis_data=x_axis_items)

  if mark_line_items is None:
    for candlestick_dict in candlestick_dicts:
      kline_view.add_yaxis(
        series_name=candlestick_dict['name'],
        y_axis=candlestick_dict['data'],
        itemstyle_opts=opts.ItemStyleOpts(
        color="#ef232a",
        color0="#14b143",
        border_color="#ef232a",
        border_color0="#14b143",
        opacity=candlestick_dict['opacity'] if 'opacity' in candlestick_dict else 0.8,),)
  else:
    candlestick_dict = candlestick_dicts[0]
    kline_view.add_yaxis(
      series_name=candlestick_dict['name'],
      y_axis=candlestick_dict['data'],
      itemstyle_opts=opts.ItemStyleOpts(
      color="#ef232a",
      color0="#14b143",
      border_color="#ef232a",
      border_color0="#14b143",
      opacity=candlestick_dict['opacity'] if 'opacity' in candlestick_dict else 0.8,),
      markline_opts=opts.MarkLineOpts(
      label_opts=opts.LabelOpts(
          position="middle", color="blue", font_size=15
      ),
      data=mark_line_items[0],
      symbol=["circle", "none"],),)
  kline_view.set_global_opts(
    title_opts=opts.TitleOpts(
      title=title,
      subtitle=sub_title, 
      pos_left="0"),
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
    tooltip_opts=opts.TooltipOpts(
      trigger="axis",
      axis_pointer_type="cross",
      background_color="rgba(245, 245, 245, 0.8)",
      border_width=1,
      border_color="#ccc",
      textstyle_opts=opts.TextStyleOpts(color="#000"),
    ),
    datazoom_opts=[
      opts.DataZoomOpts(
          is_show=False,
          type_="inside",
          xaxis_index=x_axis_indexs,
          range_start=zoom_range_start,
          range_end=zoom_range_end,
      ),
      opts.DataZoomOpts(
          is_show=True,
          xaxis_index=x_axis_indexs,
          type_="slider",
          pos_top="96.5%",
          range_start=zoom_range_start,
          range_end=zoom_range_end,
      ),
    ] if x_axis_indexs is not None else None,
    yaxis_opts=opts.AxisOpts(
      is_scale=True,
      # splitarea_opts=opts.SplitAreaOpts(
      #     is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
      # ),
    ),
    visualmap_opts=opts.VisualMapOpts(
      is_show=False,
      dimension=2,
      series_index=5,
      is_piecewise=True,
      pieces=[
          {"value": 1, "color": "#00da3c"},
          {"value": -1, "color": "#ec0000"},
      ],
    ),
    axispointer_opts=opts.AxisPointerOpts(
      is_show=True,
      link=[{"xAxisIndex": "all"}],
      label=opts.LabelOpts(background_color="#777"),
    ),
    legend_opts=opts.LegendOpts(is_show=is_show_legend),
  )
  if line_dicts is None:
    return kline_view
  
  line_view = (
    Line()
    .add_xaxis(xaxis_data=x_axis_items)
    .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"),)
  )
  for line_dict in line_dicts:
    line_view.add_yaxis(
      series_name=line_dict['name'],
      y_axis=line_dict['data'],
      is_smooth=False,
      is_hover_animation=False,
      linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
      label_opts=opts.LabelOpts(is_show=False),
      itemstyle_opts=opts.ItemStyleOpts(
        color=line_dict['color'],
        opacity=0.1)
    )
  overlapped_kline_view = kline_view.overlap(line_view)
  return overlapped_kline_view
    
def init_bar_view(
  x_axis_items:list,
  bar_data_dicts:list,
  stack='stack_0',
  line_dicts=None,
  is_on_zero=False,
  is_percentage=False):
  
  bar_view = Bar()
  bar_view.add_xaxis(xaxis_data=x_axis_items)

  for bar_data_dict in bar_data_dicts:
    bar_view.add_yaxis(
      series_name=bar_data_dict['name'],
      y_axis=bar_data_dict['data'],
      stack=bar_data_dict['stack'] if 'stack' in bar_data_dict else stack,
      itemstyle_opts=opts.ItemStyleOpts(
        color=bar_data_dict['color'], 
        opacity=bar_data_dict['opacity'] if 'opacity' in bar_data_dict else 0.8),
      label_opts=opts.LabelOpts(
        is_show=False,
        formatter='{c} %'if is_percentage is True else None
        ),
    )
  bar_view.set_global_opts(
    xaxis_opts=opts.AxisOpts(
      type_="category",
      is_scale=True,
      split_number=20,
      boundary_gap=False,
      axisline_opts=opts.AxisLineOpts(is_on_zero=False),
      axistick_opts=opts.AxisTickOpts(is_show=False),
      splitline_opts=opts.SplitLineOpts(is_show=False),
      axislabel_opts=opts.LabelOpts(is_show=False),
      min_="dataMin",
      max_="dataMax",
    ),
    yaxis_opts=opts.AxisOpts(
      split_number=4,
      axisline_opts=opts.AxisLineOpts(is_on_zero=is_on_zero),
      axistick_opts=opts.AxisTickOpts(is_show=False),
      splitline_opts=opts.SplitLineOpts(is_show=False),
      axislabel_opts=opts.LabelOpts(formatter='{value} %'if is_percentage is True else None),
    ),
    legend_opts=opts.LegendOpts(is_show=False),
  )
  if line_dicts is None:
    return bar_view

  line_view = (
    Line()
    .add_xaxis(xaxis_data=x_axis_items)
    .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"),)
  )  
  for line_dict in line_dicts:
    line_view.add_yaxis(
      series_name=line_dict['name'],
      y_axis=line_dict['data'],
      is_smooth=True,
      is_hover_animation=False,
      linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
      label_opts=opts.LabelOpts(is_show=False),
    )
  overlapped_bar_view = bar_view.overlap(line_view)
  return overlapped_bar_view

def init_gird_view(
  sub_views:list,
  heights:list,
  top_heights:list,
  width='2560px',
  height='1440px',):

  grid_view = Grid(
    init_opts=opts.InitOpts(
      width=width,
      height=height,
      animation_opts=opts.AnimationOpts(animation=False),
    )
  )

  for i in range(len(sub_views)):
    grid_view.add(
      sub_views[i],
      grid_opts=opts.GridOpts(
        pos_left="5%", 
        pos_right="5%", 
        pos_top=top_heights[i],
        height=heights[i],)
    )
  
  return grid_view

def get_kline_green_and_red_color():
  return JsCode(
    """
      function(params) {
          var colorList;
          if (data.datas[params.dataIndex][1]>data.datas[params.dataIndex][0]) {
              colorList = '#ef232a';
          } else {
              colorList = '#14b143';
          }
          return colorList;
      }
    """)

def get_bar_green_and_red_color():
  return JsCode(
    """
      function(params) {
          var colorList;
          if (params.data >= 0) {
            colorList = '#ef232a';
          } else {
            colorList = '#14b143';
          }
          return colorList;
      }
    """)
