import numpy as np
import time
import datetime
import data_update_tool
import pyecharts_tool
import utils
from pathlib import Path

def generate_percentile_list(data_list:list) -> list:
  precentile_list = []
  for i in range(101):
    p_i = np.percentile(data_list, i)
    precentile_list.append(p_i)
  return precentile_list

def get_precentile_index(precentile_list:list, data:float) -> int:
  if data < precentile_list[0]:
    return -1
  for i in range(100):
    if data >= precentile_list[i] and data < precentile_list[i+1]:
      return i
    else:
      continue
  return 100

def get_vix_data_from_yfinance(start_time=None) -> dict:
  start_time_str = '2000-01-01'
  if start_time is not None:
    start_time_str = start_time.strftime('%Y-%m-%d')
  vix_data = data_update_tool.load_stock_data_from_yfinance('^VIX', start_time_str)
  return vix_data

def load_vix_data_from_local_file() -> dict:
  if Path('./hdfdb/daily.hdf5').is_file():
    hdfdb = utils.stock_database.StockDatabase('./hdfdb/daily.hdf5')
    vix_data =  hdfdb.load_stock_data('^vix')
    del hdfdb
    return vix_data
  else:
    return None

def update_local_vix_data(vix_data_local:dict, vix_data_new:dict) -> dict:
  if vix_data_local is not None:
    vix_data_merged = {
      'open_data_list':vix_data_local['open_data_list'][:-1] + vix_data_new['open_data_list'],
      'close_data_list':vix_data_local['close_data_list'][:-1] + vix_data_new['close_data_list'],
      'low_data_list':vix_data_local['low_data_list'][:-1] + vix_data_new['low_data_list'],
      'high_data_list':vix_data_local['high_data_list'][:-1] + vix_data_new['high_data_list'],
      'volume_data_list':vix_data_local['volume_data_list'][:-1] + vix_data_new['volume_data_list'],
      'date_list':vix_data_local['date_list'][:-1] + vix_data_new['date_list'],
    }
  else:
    vix_data_merged = vix_data_new
  hdfdb = utils.stock_database.StockDatabase('./hdfdb/daily.hdf5')
  hdfdb.update_stock_data('^vix', vix_data_merged)
  del hdfdb
  return vix_data_merged

def get_vix_data_timestamp(vix_data:dict) -> datetime.datetime:
  last_date = vix_data['date_list'][-1]
  timestamp = datetime.datetime.fromtimestamp(last_date)
  return timestamp

def get_vix_data_timestamp_str(vix_data:dict) -> str:
  timestamp = get_vix_data_timestamp(vix_data)
  return timestamp.strftime('%Y-%m-%d %H:%M:%S')
  
def test_and_draw_echarts(vix_data:dict, output_len:int):
  precentile_list = generate_percentile_list(vix_data['close_data_list'])
  positive_index_list = []
  negative_index_list = []
  for i in range(output_len):
    data = vix_data['close_data_list'][len(vix_data['date_list']) - output_len + i]
    index = get_precentile_index(precentile_list, data)
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