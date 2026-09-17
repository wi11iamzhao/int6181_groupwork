import numpy as np
import datetime
import data_update_tool
import utils
from pathlib import Path

def get_spx_data_from_yfinance(start_time=None) -> dict:
  start_time_str = '2000-01-01'
  if start_time is not None:
    start_time_str = start_time.strftime('%Y-%m-%d')
  spx_data = data_update_tool.load_stock_data_from_yfinance('^SPX', start_time_str)
  return spx_data

def load_spx_data_from_local_file() -> dict:
  if Path('./hdfdb/daily.hdf5').is_file():
    hdfdb = utils.stock_database.StockDatabase('./hdfdb/daily.hdf5')
    spx_data = hdfdb.load_stock_data('^SPX')
    del hdfdb
    return spx_data
  else:
    return None

def update_local_spx_data(spx_data_local:dict, spx_data_new:dict) -> dict:
  if spx_data_local is not None:
    spx_data_merged = {
      'open_data_list':spx_data_local['open_data_list'][:-1] + spx_data_new['open_data_list'],
      'close_data_list':spx_data_local['close_data_list'][:-1] + spx_data_new['close_data_list'],
      'low_data_list':spx_data_local['low_data_list'][:-1] + spx_data_new['low_data_list'],
      'high_data_list':spx_data_local['high_data_list'][:-1] + spx_data_new['high_data_list'],
      'volume_data_list':spx_data_local['volume_data_list'][:-1] + spx_data_new['volume_data_list'],
      'date_list':spx_data_local['date_list'][:-1] + spx_data_new['date_list'],
    }
  else:
    spx_data_merged = spx_data_new
  hdfdb = utils.stock_database.StockDatabase('./hdfdb/daily.hdf5')
  hdfdb.update_stock_data('^SPX', spx_data_merged)
  del hdfdb
  return spx_data_merged

def get_spx_data_datetime(spx_data:dict) -> datetime.datetime:
  last_date = spx_data['date_list'][-1]
  return datetime.datetime.fromtimestamp(last_date)


def get_spx_data_datetime_str(spx_data:dict) -> str:
  timestamp = get_spx_data_datetime(spx_data)
  return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def get_spx_data_length(spx_data:dict) -> int:
  return len(spx_data['date_list'])

def get_moving_average_data_list(spx_data:dict, n:int) -> list[float]:
  # This function requires optimization for parallel computing.
  # Otherwise, calculating all the moving averages would consume a considerable amount of time.
  close_data = spx_data['close_data_list']
  moving_average_list = []
  for i in range(n):
    moving_average = utils.calculate_moving_average(close_data, i)
    moving_average_list.append(moving_average)
  data_length = len(close_data)
  if data_length < n:
    return moving_average_list
  for i in range(i,data_length):
    moving_average = utils.calculate_moving_average(close_data, n)
    moving_average_list.append(moving_average)
  return moving_average_list