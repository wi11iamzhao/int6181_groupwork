import numpy as np
import time
import datetime
import data_updata_tool
import pyecharts_tool
import utils
from pathlib import Path

def generate_quantile_list(data_list:list)->list:
  quantile_list = []
  for i in range(101):
    p_i = np.percentile(data_list, i)
    quantile_list.append(p_i)
  return quantile_list

def get_quantile_index(quantile_list:list, data:float)->int:
  if data < quantile_list[0]:
    return -1
  for i in range(100):
    if data >= quantile_list[i] and data < quantile_list[i+1]:
      return i
    else:
      continue
  return 100

def get_vix_data() -> dict:
  # TODO:Fix db initialization
  if Path('./hdfdb/daily.hdf5').is_file():
    hdfdb = utils.stock_database.StockDatabase('./hdfdb/daily.hdf5')
    vix_data_old =  hdfdb.load_stock_data('^vix')
    if vix_data_old is not None:
      last_date = vix_data_old['date_list'][-1]
      last_date_str = utils.float_time_to_str(last_date, '%Y-%m-%d')
      vix_data_new = data_updata_tool.load_stock_data_from_yfinance('^VIX', last_date_str)
      vix_data_merged = {
        'open_data_list':vix_data_old['open_data_list'][:-1] + vix_data_new['open_data_list'],
        'close_data_list':vix_data_old['close_data_list'][:-1] + vix_data_new['close_data_list'],
        'low_data_list':vix_data_old['low_data_list'][:-1] + vix_data_new['low_data_list'],
        'high_data_list':vix_data_old['high_data_list'][:-1] + vix_data_new['high_data_list'],
        'volume_data_list':vix_data_old['volume_data_list'][:-1] + vix_data_new['volume_data_list'],
        'date_list':vix_data_old['date_list'][:-1] + vix_data_new['date_list'],
      }
      hdfdb.update_stock_data('^vix', vix_data_merged)
      del hdfdb
      return vix_data_merged
  vix_data = data_updata_tool.load_stock_data_from_yfinance('^VIX','2000-01-01')
  hdfdb = utils.stock_database.StockDatabase('./hdfdb/daily.hdf5')
  hdfdb.update_stock_data('^vix', vix_data)
  del hdfdb
  return vix_data

def draw_echarts(vix_data:dict, output_len:int, charts_name:str):
  quantile_list = generate_quantile_list(vix_data['close_data_list'])
  positive_index_list = []
  negative_index_list = []
  for i in range(output_len):
    data = vix_data['close_data_list'][len(vix_data['date_list']) - output_len + i]
    index = get_quantile_index(quantile_list, data)
    if index > 50:
      positive_index_list.append(index - 50)
      negative_index_list.append(0)
    elif index < 50:
      positive_index_list.append(0)
      negative_index_list.append(index - 50)
    else:
      positive_index_list.append(0)
      negative_index_list.append(0)

  full_candlestick_data_list = utils.get_candlestick_data_list(vix_data)
  candlestick_data_list = full_candlestick_data_list[len(vix_data['date_list']) - output_len:]
  date_str_list = []
  for i in range(output_len):
    date = datetime.datetime.fromtimestamp(vix_data['date_list'][len(vix_data['date_list']) - output_len + i])
    date_str = date.strftime('%Y%m%d')
    date_str_list.append(date_str)

  candlestick_view = pyecharts_tool.init_candlestick_view(
    candlestick_dicts=[{
      'name':'VIX',
      'data':candlestick_data_list,
    }],
    x_axis_items=date_str_list,
    x_axis_indexs=[0,1],
    zoom_range_start=20.0,
    zoom_range_end=80.0,
    line_dicts=None,
    mark_line_items=None,
    title='VIX分位指数',
    sub_title='',
    is_show_legend=False,)
  index_view = pyecharts_tool.init_bar_view(
    x_axis_items=date_str_list,
    bar_data_dicts=[
      {
      'name':'分位指数',
      'color':'red',
      'data':positive_index_list,
      'stack':'stack_1',
      },
      {
      'name':'分位指数',
      'color':'green',
      'data':negative_index_list,
      'stack':'stack_1',
      },
    ],
    stack='stack_1',
    is_percentage=False,
    is_on_zero=True,)
  gird_view = pyecharts_tool.init_gird_view(
    sub_views=[candlestick_view,
              index_view,],
    heights=['45%','10%',],
    top_heights=['5%','55%']
  )
  gird_view.render('./vix_{}.html'.format(time.strftime("%Y-%m-%d", time.localtime())))

def test():
  vix_data = get_vix_data()
  draw_echarts(vix_data, 300, None)

test()