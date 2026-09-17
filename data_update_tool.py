import yfinance
import datetime

def load_stock_data_from_yfinance(code:str, start_time_str='2000-01-01') -> dict:
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