import string
import datetime
import h5py
import numpy as np
from .hdf5database import HDF5Database

class StockDatabase(HDF5Database):
  def __init__(self, file_path:string) -> None:
    super(StockDatabase, self).__init__(file_path)
    self.read_event.wait()
    self.write_event.clear()
    with h5py.File(self.database_file, 'a') as db:
      if 'stock' not in db.keys():
        db.create_group('stock')
    self.write_event.set()

  def update_stock_data(self, stock_code:string, data_dict:dict) -> int:
    self.read_event.wait()
    self.write_event.clear()
    try:
      with h5py.File(self.database_file, 'a') as db:
        if stock_code not in db['stock'].keys():
          group = db['stock'].create_group(stock_code)
          sub_group_raw = group.create_group('raw')
          sub_group_relative = group.create_group('relative')

          group.create_dataset('date', data=np.array(data_dict['date_list'], dtype=np.float64), dtype='float64', maxshape=(None,), chunks=True)
          sub_group_raw.create_dataset('open', data=np.array(data_dict['open_data_list'], dtype=np.float64), dtype='float64', maxshape=(None,), chunks=True)
          sub_group_raw.create_dataset('close', data=np.array(data_dict['close_data_list'], dtype=np.float64), dtype='float64', maxshape=(None,), chunks=True)
          sub_group_raw.create_dataset('low', data=np.array(data_dict['low_data_list'], dtype=np.float64), dtype='float64', maxshape=(None,), chunks=True)
          sub_group_raw.create_dataset('high', data=np.array(data_dict['high_data_list'], dtype=np.float64), dtype='float64', maxshape=(None,), chunks=True)
          sub_group_raw.create_dataset('volume', data=np.array(data_dict['volume_data_list'], dtype=np.float64), dtype='float64', maxshape=(None,), chunks=True)
          if 'amount_data_list' in data_dict.keys():
            sub_group_raw.create_dataset('amount', data=np.array(data_dict['amount_data_list'], dtype=np.float64), dtype='float64', maxshape=(None,), chunks=True)
          db.attrs['update_time'] = datetime.datetime.utcnow().timestamp()
          return len(data_dict['date_list'])

        _trade_date = db['/stock/'+ stock_code + '/date']
        _open_data = db['/stock/'+ stock_code + '/raw/open']
        _close_data = db['/stock/'+ stock_code + '/raw/close']
        _low_data = db['/stock/'+ stock_code + '/raw/low']
        _high_data = db['/stock/'+ stock_code + '/raw/high']
        _volume_data = db['/stock/'+ stock_code + '/raw/volume']
        if 'amount_data_list' in data_dict.keys():
          _amount_data = db['/stock/'+ stock_code + '/raw/amount']

        _trade_date_list = _trade_date[:].tolist()
        _open_data_list = _open_data[:].tolist()
        _close_data_list = _close_data[:].tolist()
        _low_data_list = _low_data[:].tolist()
        _high_data_list = _high_data[:].tolist()
        _volume_data_list = _volume_data[:].tolist()
        if 'amount_data_list' in data_dict.keys():
          _amount_data_list = _amount_data[:].tolist()

        trade_date_list = data_dict['date_list']
        open_data_list = data_dict['open_data_list']
        close_data_list = data_dict['close_data_list']
        low_data_list = data_dict['low_data_list']
        high_data_list = data_dict['high_data_list']
        volume_data_list = data_dict['volume_data_list']
        if 'amount_data_list' in data_dict.keys():
          amount_data_list = data_dict['amount_data_list']
        
        _open_data_dict = dict(zip([date for date in _trade_date_list],[open_date for open_date in _open_data_list]))
        _close_data_dict = dict(zip([date for date in _trade_date_list],[close_data for close_data in _close_data_list]))
        _low_data_dict = dict(zip([date for date in _trade_date_list],[low_data for low_data in _low_data_list]))
        _high_data_dict = dict(zip([date for date in _trade_date_list],[high_data for high_data in _high_data_list]))
        _volume_data_dict = dict(zip([date for date in _trade_date_list],[volume_data for volume_data in _volume_data_list]))
        if 'amount_data_list' in data_dict.keys():
          _amount_data_dict = dict(zip([date for date in _trade_date_list],[amount_data for amount_data in _amount_data_list]))

        open_data_dict = dict(zip([date for date in trade_date_list],[open_date for open_date in open_data_list]))
        close_data_dict = dict(zip([date for date in trade_date_list],[close_data for close_data in close_data_list]))
        low_data_dict = dict(zip([date for date in trade_date_list],[low_data for low_data in low_data_list]))
        high_data_dict = dict(zip([date for date in trade_date_list],[high_data for high_data in high_data_list]))
        volume_data_dict = dict(zip([date for date in trade_date_list],[volume_data for volume_data in volume_data_list]))
        if 'amount_data_list' in data_dict.keys():
          amount_data_dict = dict(zip([date for date in trade_date_list],[amount_data for amount_data in amount_data_list]))

        _open_data_dict.update(open_data_dict)
        _close_data_dict.update(close_data_dict)
        _low_data_dict.update(low_data_dict)
        _high_data_dict.update(high_data_dict)
        _volume_data_dict.update(volume_data_dict)
        if 'amount_data_list' in data_dict.keys():
          _amount_data_dict.update(amount_data_dict)

        trade_date_list = list(_open_data_dict.keys())
        open_data_list = list(_open_data_dict.values())
        close_data_list = list(_close_data_dict.values())
        low_data_list = list(_low_data_dict.values())
        high_data_list = list(_high_data_dict.values())
        volume_data_list = list(_volume_data_dict.values())
        if 'amount_data_list' in data_dict.keys():
          amount_data_list = list(_amount_data_dict.values())

        _trade_date.resize(len(trade_date_list),axis=0)
        _open_data.resize(len(open_data_list),axis=0)
        _close_data.resize(len(close_data_list),axis=0)
        _low_data.resize(len(low_data_list),axis=0)
        _high_data.resize(len(high_data_list),axis=0)
        _volume_data.resize(len(volume_data_list),axis=0)
        if 'amount_data_list' in data_dict.keys():
          _amount_data.resize(len(amount_data_list),axis=0)

        _trade_date[:] = np.array(trade_date_list, dtype=np.float64)
        _open_data[:] = np.array(open_data_list, dtype=np.float64) 
        _close_data[:] = np.array(close_data_list, dtype=np.float64)
        _low_data[:] = np.array(low_data_list, dtype=np.float64)
        _high_data[:] = np.array(high_data_list, dtype=np.float64)
        _volume_data[:] = np.array(volume_data_list, dtype=np.float64)
        if 'amount_data_list' in data_dict.keys():
          _amount_data[:] = np.array(amount_data_list, dtype=np.float64)
        db.attrs['update_time'] = datetime.datetime.utcnow().timestamp()
        return len(trade_date_list)
    except Exception as e:
      return None
    finally:
      self.write_event.set()

  def load_stock_data(self, stock_code:string) -> dict:
    self.write_event.wait()
    self.read_event.clear()
    try:
      with h5py.File(self.database_file, 'r') as db:
        if stock_code not in db['stock'].keys():
          return None

        _trade_date = db['/stock/'+ stock_code + '/date']
        _open_data = db['/stock/'+ stock_code + '/raw/open']
        _close_data = db['/stock/'+ stock_code + '/raw/close']
        _low_data = db['/stock/'+ stock_code + '/raw/low']
        _high_data = db['/stock/'+ stock_code + '/raw/high']
        _volume_data = db['/stock/'+ stock_code + '/raw/volume']
        _amount_data = db['/stock/'+ stock_code + '/raw/amount']

        _trade_date_list = _trade_date[:].tolist()
        _open_data_list = _open_data[:].tolist()
        _close_data_list = _close_data[:].tolist()
        _low_data_list = _low_data[:].tolist()
        _high_data_list = _high_data[:].tolist()
        _volume_data_list = _volume_data[:].tolist()
        _amount_data_list = _amount_data[:].tolist()

        # candlestick_data_list = []
        # for i in range(len(_trade_date_list)):
        #   candlestick_data = [
        #     _open_data_list[i],
        #     _close_data_list[i],
        #     _low_data_list[i],
        #     _high_data_list[i]]
        #   candlestick_data_list.append(candlestick_data)

        result_dict = {
          # 'candlestick_data_list':candlestick_data_list,
          'open_data_list':_open_data_list,
          'close_data_list':_close_data_list,
          'low_data_list':_low_data_list,
          'high_data_list':_high_data_list,
          'volume_data_list':_volume_data_list,
          'amount_data_list':_amount_data_list,
          'date_list':_trade_date_list,
        }
        return result_dict
    except Exception as e:
      return None
    finally:
      self.read_event.set()