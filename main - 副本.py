import argparse
import time
import datetime
import vix
import spx
import pyecharts_tool
from logger import Logger
from utils import utils


def _sync_data(vix_data:dict, spx_data:dict):
  length = min(vix.get_vix_data_length(vix_data), spx.get_spx_data_length(spx_data))
  offset = 0
  for i in range(length):
    delta_time = abs(vix_data['date_list'][i] - spx_data['date_list'][i])
    if delta_time >= 3605:
      time_str_a = utils.float_time_to_str(vix_data['date_list'][i], '%Y-%m-%d %H:%M:%S')
      time_str_b = utils.float_time_to_str(spx_data['date_list'][i], '%Y-%m-%d %H:%M:%S')
      print('_sync_data:{}and{}'.format(time_str_a, time_str_b))

def draw_charts(vix_data:dict, output_len:int, output_path:str):
  precentile_list = utils.generate_percentile_list(vix_data['close_data_list'])
  positive_index_list = []
  negative_index_list = []
  for i in range(output_len):
    data = vix_data['close_data_list'][len(vix_data['date_list']) - output_len + i]
    index = utils.get_precentile_index(precentile_list, data)
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
  gird_view.render(output_path + 'result_{}.html'.format(time.strftime("%Y-%m-%d", time.localtime())))

def main():
  main_logger = Logger('./log/' + time.strftime("%Y-%m-%d", time.localtime()) + '.log')
  logger = main_logger.logger
  parser = argparse.ArgumentParser()
  parser.add_argument('-u', 
                      '--update',
                      dest='update',
                      action='store_true',
                      required=False, 
                      help='Just update loacl data, Do not echo any result.')
  parser.add_argument('-o',
                      '--offline',
                      dest='offline',
                      action='store_true',
                      required=False,
                      help='Offline Mode, Only use local data.')
  parser.add_argument('-s',
                      '--silent',
                      dest='silent',
                      action='store_true',
                      required=False,
                      help='Silent Mode,Do not use the system browser to display the results.')
  args = parser.parse_args()
  # args hacker for quick test
  args.update = True
  # args.offline = True
  # args.silent = True

  logger.info('Runing Investor Sentiment')
  logger.info('args:' + str(vars(args)))
  # VIX Precentile
  # Update Only Mode
  if args.update is True:
    if args.offline is True:
      logger.error('You cannot update local date in offline mode.Exit!')
      return None
    logger.info('Load VIX data from local file')
    vix_data_local = vix.load_vix_data_from_local_file()
    if vix_data_local is None:
      logger.info('No local VIX data exist.Just try to create it.')
      time_strat = time.perf_counter()
      vix_data = vix.get_vix_data_from_yfinance()
      time_end = time.perf_counter()
      if vix_data is None:
        logger.error('Failed to download VIX data from Yahoo Finance.Please check your network connection.Exit!')
        return
      time_delta = time_end - time_strat
      vix_data_length = vix.get_vix_data_length(vix_data)
      timestamp_str = vix.get_vix_data_timestamp_str(vix_data)
      logger.info('Download VIX data from Yahoo Finance Successed.time={:.3f}s,length={},timestamp={}'.format(time_delta, vix_data_length, timestamp_str))
      update_result = vix.update_local_vix_data(None, vix_data)
      if update_result is None:
        logger.error('Failed to update local VIX data.!Please check the disk and permissions.Exit!')
        return
      vix_data_length = vix.get_vix_data_length(update_result)
      timestamp_str = vix.get_vix_data_timestamp_str(update_result)
      logger.info('Local VIX data update successfull.length={},timestamp={}'.format(vix_data_length, timestamp_str))
    else:
      local_data_last_date = vix.get_vix_data_timestamp(vix_data_local)
      timestamp_str = vix.get_vix_data_timestamp_str(vix_data_local)
      delta_time = datetime.datetime.now().timestamp() - local_data_last_date.timestamp()
      if delta_time < 3600 * 24:
        logger.info('Local VIX data is valid,timestamp:{}.Exit!'.format(timestamp_str))
        return
      logger.info('Local VIX data may be invalid,timestamp:{}.Try to download VIX data from yahoo fianance'.format(timestamp_str))
      time_strat = time.perf_counter()
      vix_data = vix.get_vix_data_from_yfinance(local_data_last_date)
      time_end = time.perf_counter()
      if vix_data is None:
        logger.error('Failed to download VIX data from Yahoo Finance.Please check your network connection.Exit!')
        return
      time_delta = time_end - time_strat
      vix_data_length = vix.get_vix_data_length(vix_data)
      timestamp_str = vix.get_vix_data_timestamp_str(vix_data)
      logger.info('Download VIX data from Yahoo Finance Successed.time={:.3f}s,length={},timestamp={}'.format(time_delta, vix_data_length, timestamp_str))
      update_result = vix.update_local_vix_data(vix_data_local, vix_data)
      if update_result is None:
        logger.error('Failed to update local VIX data.!Please check the disk and permissions.Exit!')
        return
      vix_data_length = vix.get_vix_data_length(update_result)
      timestamp_str = vix.get_vix_data_timestamp_str(update_result)
      logger.info('Local VIX data update successfull.length={},timestamp={}'.format(vix_data_length, timestamp_str))
        
    logger.info('Load SPX data from local file')
    spx_data_local = spx.load_spx_data_from_local_file()
    if spx_data_local is None:
      logger.info('No local SPX data exist.Just try to create it.')
      time_strat = time.perf_counter()
      spx_data = spx.get_spx_data_from_yfinance()
      time_end = time.perf_counter()
      if spx_data is None:
        logger.error('Failed to download SPX data from Yahoo Finance.Please check your network connection.Exit!')
        return
      time_delta = time_end - time_strat
      spx_data_length = spx.get_spx_data_length(spx_data)
      timestamp_str = spx.get_spx_data_timestamp_str(spx_data)
      logger.info('Download SPX data from Yahoo Finance Successed.time={:.3f}s,length={},timestamp={}'.format(time_delta, spx_data_length, timestamp_str))
      update_result = spx.update_local_spx_data(None, spx_data)
      if update_result is None:
        logger.error('Failed to update local SPX data.!Please check the disk and permissions.Exit!')
        return
      spx_data_length = spx.get_spx_data_length(update_result)
      timestamp_str = spx.get_spx_data_timestamp_str(update_result)
      logger.info('Local SPX data update successfull.length={},timestamp={}'.format(spx_data_length, timestamp_str))
    else:
      local_data_last_date = spx.get_spx_data_timestamp(spx_data_local)
      timestamp_str = spx.get_spx_data_timestamp_str(spx_data_local)
      delta_time = datetime.datetime.now().timestamp() - local_data_last_date.timestamp()
      if delta_time < 3600 * 24:
        logger.info('Local SPX data is valid,timestamp:{}.Exit!'.format(timestamp_str))
        return
      logger.info('Local SPX data may be invalid,timestamp:{}.Try to download SPX data from yahoo fianance'.format(timestamp_str))
      time_strat = time.perf_counter()
      spx_data = spx.get_spx_data_from_yfinance(local_data_last_date)
      time_end = time.perf_counter()
      if spx_data is None:
        logger.error('Failed to download SPX data from Yahoo Finance.Please check your network connection.Exit!')
        return
      time_delta = time_end - time_strat
      spx_data_length = spx.get_spx_data_length(spx_data)
      timestamp_str = spx.get_spx_data_timestamp_str(spx_data)
      logger.info('Download SPX data from Yahoo Finance Successed.time={:.3f}s,length={},timestamp={}'.format(time_delta, spx_data_length, timestamp_str))
      update_result = spx.update_local_spx_data(spx_data_local, spx_data)
      if update_result is None:
        logger.error('Failed to update local SPX data.!Please check the disk and permissions.Exit!')
        return
      spx_data_length = spx.get_spx_data_length(update_result)
      timestamp_str = spx.get_spx_data_timestamp_str(update_result)
      logger.info('Local SPX data update successfull.length={},timestamp={}'.format(spx_data_length, timestamp_str))
    _sync_data(vix_data, spx_data)
    return
  
  # Normal Mode
  vix_data_local = vix.load_vix_data_from_local_file()
  if args.offline is False:
    if vix_data_local is None:
      logger.info('No local VIX data exist.Just try to create it.')
      time_strat = time.perf_counter()
      vix_data_new = vix.get_vix_data_from_yfinance()
      time_end = time.perf_counter()
      if vix_data_new is None:
        logger.error('Failed to download VIX data from Yahoo Finance.Please check your network connection.Exit!')
        return
      time_delta = time_end - time_strat
      vix_data_length = vix.get_vix_data_length(vix_data_new)
      timestamp_str = vix.get_vix_data_timestamp_str(vix_data_new)
      logger.info('Download VIX data from Yahoo Finance Successed.time={:.3f}s,length={},timestamp={}'.format(time_delta, vix_data_length, timestamp_str))
      vix_data = vix.update_local_vix_data(None, vix_data_new)
      if vix_data is None:
        logger.warning('Failed to update local VIX data.!Please check the disk and permissions.Attempting to download the full VIX data now.')
        time_strat = time.perf_counter()
        vix_data_new = vix.get_vix_data_from_yfinance()
        time_end = time.perf_counter()
        if vix_data is None:
          logger.error('Failed to download VIX data from Yahoo Finance.Please check your network connection.Exit!')
          return
        time_delta = time_end - time_strat
        vix_data_length = vix.get_vix_data_length(vix_data)
        timestamp_str = vix.get_vix_data_timestamp_str(vix_data)
        logger.info('Download VIX data from Yahoo Finance Successed.time={:.3f}s,length={},timestamp={}'.format(time_delta, vix_data_length, timestamp_str))
      else:
        vix_data_length = vix.get_vix_data_length(vix_data)
        timestamp_str = vix.get_vix_data_timestamp_str(vix_data)
        logger.info('Local VIX data update successfull.length={},timestamp={}'.format(vix_data_length, timestamp_str))
    else:
      local_data_last_date = vix.get_vix_data_timestamp(vix_data_local)
      timestamp_str = vix.get_vix_data_timestamp_str(vix_data_local)
      delta_time = datetime.datetime.now().timestamp() - local_data_last_date.timestamp()
      if delta_time < 3600 * 24:
        logger.info('Local VIX data is valid,no update is required.timestamp:{}.'.format(timestamp_str))
        vix_data = vix_data_local
      else:
        logger.info('Local VIX data may be invalid,timestamp:{}.Try to download VIX data from yahoo fianance'.format(timestamp_str))
        time_strat = time.perf_counter()
        vix_data_new = vix.get_vix_data_from_yfinance()
        time_end = time.perf_counter()
        time_delta = time_end - time_strat
        vix_data_length = vix.get_vix_data_length(vix_data_new)
        timestamp_str = vix.get_vix_data_timestamp_str(vix_data_new)
        logger.info('Download VIX data from Yahoo Finance Successed.time={:.3f}s,length={},timestamp={}'.format(time_delta, vix_data_length, timestamp_str))
        if vix_data_new is None:
          logger.error('Failed to download VIX data from Yahoo Finance.Please check your network connection.Exit!')
          return
        vix_data = vix.update_local_vix_data(vix_data_local, vix_data_new)
        if vix_data is None:
          logger.warning('Failed to update local VIX data.!Please check the disk and permissions.Attempting to download the full VIX data now.')
          time_strat = time.perf_counter()
          vix_data = vix.get_vix_data_from_yfinance()
          time_end = time.perf_counter()
          if vix_data is None:
            logger.error('Failed to download VIX data from Yahoo Finance.Please check your network connection.Exit!')
            return
          time_delta = time_end - time_strat
          vix_data_length = vix.get_vix_data_length(vix_data)
          timestamp_str = vix.get_vix_data_timestamp_str(vix_data)
          logger.info('Download VIX data from Yahoo Finance Successed.time={:.3f}s,length={},timestamp={}'.format(time_delta, vix_data_length, timestamp_str))
        else:
          vix_data_length = vix.get_vix_data_length(vix_data)
          timestamp_str = vix.get_vix_data_timestamp_str(vix_data)
          logger.info('Local VIX data update successfull.length={},timestamp={}'.format(vix_data_length, timestamp_str))
  else:
    # Offline Mode
    if vix_data_local is None:
      logger.error('Local VIX data is missing.offline mode execution failed.Exit')
      return
    local_data_last_date = vix.get_vix_data_timestamp(vix_data_local)
    timestamp_str = vix.get_vix_data_timestamp_str(vix_data_local)
    delta_time = datetime.datetime.now().timestamp() - local_data_last_date.timestamp()
    if delta_time < 3600 * 24:
      logger.info('Local VIX data is valid,timestamp:{}.'.format(timestamp_str))
    else:
      logger.info('Local VIX data may be invalid,timestamp:{}.It will not update in offline mode.', timestamp_str)
    vix_data = vix_data_local

  # Check VIX data
  if vix_data is None:
    logger.error('Internal error! vix_data is None. Exit!')
  draw_charts(vix_data, 720, './output/')
  logger.info('Output result to ./output/result_{}.html'.format(time.strftime("%Y-%m-%d", time.localtime())))

if __name__ == '__main__':
  main()
  
