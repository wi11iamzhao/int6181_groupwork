import string
import time
import datetime
import numpy as np

def calculate_moving_average(data_list:list,n:int) -> float:
  ret = np.cumsum(data_list, dtype=float)
  ret[n:] = ret[n:] - ret[:-n]
  return data_list[:n - 1] + list(ret[n - 1:] / n)

def calculate_exponential_weighted_average(data:list, alpha:int, offset=None, dtype=None, order='C', out=None):
    """
    Calculates the exponential moving average over a vector.
    Will fail for large inputs.
    :param data: Input data
    :param alpha: scalar float in range (0,1)
        The alpha parameter for the moving average.
    :param offset: optional
        The offset for the moving average, scalar. Defaults to data[0].
    :param dtype: optional
        Data type used for calculations. Defaults to float64 unless
        data.dtype is float32, then it will use float32.
    :param order: {'C', 'F', 'A'}, optional
        Order to use when flattening the data. Defaults to 'C'.
    :param out: ndarray, or None, optional
        A location into which the result is stored. If provided, it must have
        the same shape as the input. If not provided or `None`,
        a freshly-allocated array is returned.
    """
    data = np.array(data, copy=False)
    if dtype is None:
        if data.dtype == np.float32:
            dtype = np.float32
        else:
            dtype = np.float64
    else:
        dtype = np.dtype(dtype)
    if data.ndim > 1:
        # flatten input
        data = data.reshape(-1, order)

    if out is None:
        out = np.empty_like(data, dtype=dtype)
    else:
        assert out.shape == data.shape
        assert out.dtype == dtype

    if data.size < 1:
        # empty input, return empty array
        return out

    if offset is None:
        offset = data[0]

    alpha = np.array(alpha, copy=False).astype(dtype, copy=False)

    # scaling_factors -> 0 as len(data) gets large
    # this leads to divide-by-zeros below
    scaling_factors = np.power(1. - alpha, np.arange(data.size + 1, dtype=dtype),
                               dtype=dtype)
    # create cumulative sum array
    np.multiply(data, (alpha * scaling_factors[-2]) / scaling_factors[:-1],
                dtype=dtype, out=out)
    np.cumsum(out, dtype=dtype, out=out)

    # cumsums / scaling
    out /= scaling_factors[-2::-1]

    if offset != 0:
        offset = np.array(offset, copy=False).astype(dtype, copy=False)
        # add offsets
        out += offset * scaling_factors[1:]
    return out

def compressed_candlestick_data(
  candlestick_data:list,
  volume_data:list,
  window_size:int,
  ) -> tuple:

  compressed_data = [candlestick_data[0]]
  for i in range(1,len(candlestick_data)):
    compressed_size = window_size
    open_list = []
    close_list = []
    low_list = []
    high_list = []

    if i < window_size:
      compressed_size = i
    for j in range(i-compressed_size,i):
      open_list.append(candlestick_data[j][0])
      close_list.append(candlestick_data[j][1])
      low_list.append(candlestick_data[j][2])
      high_list.append(candlestick_data[j][3])

    compressed_data.append([
      open_list[0],
      close_list[-1],
      min(low_list),
      max(high_list)
    ])

  return compressed_data

def get_candlestick_data_list(data_dict:dict) -> list:
  open_data_list = data_dict['open_data_list']
  close_data_list = data_dict['close_data_list']
  low_data_list = data_dict['low_data_list']
  high_data_list = data_dict['high_data_list']

  candlestick_data_list = []
  for i in range(len(open_data_list)):
    candlestick_data = [
      open_data_list[i],
      close_data_list[i],
      low_data_list[i],
      high_data_list[i],
    ]
    candlestick_data_list.append(candlestick_data)
  return candlestick_data_list

def str_time_to_float(
    time_t:string,
    format='%Y%m%d'
  ) -> float:
  time_t = time.strptime(time_t, format)
  return time.mktime(time_t)

def float_time_to_str(
    time_f:float,
    format='%Y%m%d'
  ) -> string:
  _time_dt = datetime.datetime.fromtimestamp(time_f)
  return _time_dt.strftime(format)

def timestamp_to_str(
  timestamp:float,
  format='%Y-%m-%d'
  ) -> string:
  return datetime.fromtimestamp(timestamp).strftime(format)

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