import yfinance
import datetime
import numpy as np
import datetime
import utils
from pathlib import Path

def get_history_data_yfinance(code:str, start_time_str='2000-01-01') -> dict:
  try:
    stock_ticker = yfinance.Ticker(code)
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    stock_data = stock_ticker.history(start=start_time_str, end=today_str)
    if stock_data is None:
      return None
    stock_data.reset_index(inplace=True)
    open_data_list = stock_data['Open'].to_list()
    close_data_list = stock_data['Close'].to_list()
    low_data_list = stock_data['Low'].to_list()
    high_data_list = stock_data['High'].to_list()
    volume_data_list = stock_data['Volume'].to_list()
    _date_list = stock_data['Date'].to_list()
    date_list = []
    for date in _date_list:
       date_list.append(date.timestamp())
    result_dict = {
      'open_data_list':open_data_list,
      'close_data_list':close_data_list,
      'low_data_list':low_data_list,
      'high_data_list':high_data_list,
      'volume_data_list':volume_data_list,
      'date_list':date_list,
    }
    return result_dict
  except Exception as e:
      return None

def get_data_from_yfinance(code:str, start_time=None) -> dict:
  start_time_str = '2000-01-01'
  if start_time is not None:
    start_time_str = start_time.strftime('%Y-%m-%d')
  data = get_history_data_yfinance(code, start_time_str)
  return data

def load_data_from_local_file(code:str) -> dict:
  if Path('./hdfdb/daily.hdf5').is_file():
    hdfdb = utils.stock_database.StockDatabase('./hdfdb/daily.hdf5')
    data = hdfdb.load_stock_data(code)
    del hdfdb
    return data
  else:
    return None

def merge_data(data_old:dict, data_new:dict) -> dict:
  
  if data_old is not None: 
    if data_old['date_list'][-1] != data_new['date_list'][0]:
      return None
    data_merged = {
      'open_data_list':data_old['open_data_list'][:-1] + data_new['open_data_list'],
      'close_data_list':data_old['close_data_list'][:-1] + data_new['close_data_list'],
      'low_data_list':data_old['low_data_list'][:-1] + data_new['low_data_list'],
      'high_data_list':data_old['high_data_list'][:-1] + data_new['high_data_list'],
      'volume_data_list':data_old['volume_data_list'][:-1] + data_new['volume_data_list'],
      'date_list':data_old['date_list'][:-1] + data_new['date_list'],
    }
  else:
    data_merged = {
      'open_data_list':data_new['open_data_list'].copy(),
      'close_data_list':data_new['close_data_list'].copy(),
      'low_data_list':data_new['low_data_list'].copy(),
      'high_data_list':data_new['high_data_list'].copy(),
      'volume_data_list':data_new['volume_data_list'].copy(),
      'date_list':data_new['date_list'].copy()
    }
  return data_merged
  
    
def update_local_data(code:str, data:dict) -> int:
  hdfdb = utils.stock_database.StockDatabase('./hdfdb/daily.hdf5')
  result = hdfdb.update_stock_data(code, data)
  del hdfdb
  return result

def get_data_datetime(data:dict) -> datetime.datetime:
  last_date = data['date_list'][-1]
  return datetime.datetime.fromtimestamp(last_date)

def get_data_datetime_str(data:dict) -> str:
  timestamp = get_data_datetime(data)
  return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def get_data_length(data:dict) -> int:
  return len(data['date_list'])
