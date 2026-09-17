import numpy as np
import time
import datetime
import data_update_tool
import pyecharts_tool
import utils
from pathlib import Path

def get_vix_data_from_yfinance(start_time=None) -> dict:
  start_time_str = '2000-01-01'
  if start_time is not None:
    start_time_str = start_time.strftime('%Y-%m-%d')
  vix_data = data_update_tool.load_stock_data_from_yfinance('^VIX', start_time_str)
  return vix_data

def load_vix_data_from_local_file() -> dict:
  if Path('./hdfdb/daily.hdf5').is_file():
    hdfdb = utils.stock_database.StockDatabase('./hdfdb/daily.hdf5')
    vix_data = hdfdb.load_stock_data('^VIX')
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
  hdfdb.update_stock_data('^VIX', vix_data_merged)
  del hdfdb
  return vix_data_merged

def get_vix_data_datetime(vix_data:dict) -> datetime.datetime:
  last_date = vix_data['date_list'][-1]
  return datetime.datetime.fromtimestamp(last_date)

def get_vix_data_datetime_str(vix_data:dict) -> str:
  timestamp = get_vix_data_datetime(vix_data)
  return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def get_vix_data_length(vix_data:dict) -> int:
  return len(vix_data['date_list'])
