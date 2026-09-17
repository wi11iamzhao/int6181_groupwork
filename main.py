import argparse
import time
import datetime
import vix
import pyecharts_tool
from logger import Logger
from utils import utils

def draw_charts(vix_data:dict, output_len:int, output_path:str):
  precentile_list = vix.generate_percentile_list(vix_data['close_data_list'])
  positive_index_list = []
  negative_index_list = []
  for i in range(output_len):
    data = vix_data['close_data_list'][len(vix_data['date_list']) - output_len + i]
    index = vix.get_precentile_index(precentile_list, data)
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
  # args.update = True
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
      logger.info('No local vix data exist.Just try to create it.')
      vix_data = vix.get_vix_data_from_yfinance()
      if vix_data is None:
        logger.error('Failed to download VIX data from Yahoo Finance.Please check your network connection.Exit!')
        return
      update_result = vix.update_local_vix_data(None, vix_data)
      if update_result is None:
        logger.error('Failed to update local VIX data.!Please check the disk and permissions.Exit!')
      else:
        timestamp_str = vix.get_vix_data_timestamp_str(vix_data)
        logger.info('Local VIX data updated successfully.')
      return
    else:
      local_data_last_date = vix.get_vix_data_timestamp(vix_data_local)
      timestamp_str = vix.get_vix_data_timestamp_str(vix_data_local)
      delta_time = datetime.datetime.now().timestamp() - local_data_last_date.timestamp()
      if delta_time < 3600 * 24:
        logger.info('Local VIX data is valid,timestamp:{}.Exit!'.format(timestamp_str))
        return
      logger.info('Local VIX data may be invalid,timestamp:{}.Try to download vix data from yahoo fianance'.format(timestamp_str))
      vix_data = vix.get_vix_data_from_yfinance(local_data_last_date)
      if vix_data is None:
        logger.error('Failed to download VIX data from Yahoo Finance.Please check your network connection.Exit!')
        return
      update_result = vix.update_local_vix_data(None, vix_data)
      if update_result is None:
        logger.error('Failed to update local VIX data.!Please check the disk and permissions.Exit!')
      return
    return
  
  # Normal Mode
  vix_data_local = vix.load_vix_data_from_local_file()
  if args.offline is False:
    if vix_data_local is None:
      logger.info('No local vix data exist.Just try to create it.')
      vix_data_new = vix.get_vix_data_from_yfinance()
      if vix_data_new is None:
        logger.error('Failed to download VIX data from Yahoo Finance.Please check your network connection.Exit!')
        return
      vix_data = vix.update_local_vix_data(None, vix_data_new)
      if vix_data is None:
        logger.warning('Failed to update local VIX data.!Please check the disk and permissions.Attempting to download the full VIX data now.')
        vix_data = vix.get_vix_data_from_yfinance()
        if vix_data is None:
          logger.error('Failed to download VIX data from Yahoo Finance.Please check your network connection.Exit!')
          return
    else:
      local_data_last_date = vix.get_vix_data_timestamp(vix_data_local)
      timestamp_str = vix.get_vix_data_timestamp_str(vix_data_local)
      delta_time = datetime.datetime.now().timestamp() - local_data_last_date.timestamp().timestamp()
      if delta_time < 3600 * 24:
        logger.info('Local VIX data is valid,no update is required.,timestamp:{}.'.format(timestamp_str))
        vix_data = vix_data_local
      else:
        logger.info('Local VIX data may be invalid,timestamp:{}.Try to download vix data from yahoo fianance'.format(timestamp_str))
        vix_data_new = vix.get_vix_data_from_yfinance(local_data_last_date)
        if vix_data_new is None:
          logger.error('Failed to download VIX data from Yahoo Finance.Please check your network connection.Exit!')
          return
        vix_data = vix.update_local_vix_data(vix_data_local, vix_data_new)
        if vix_data is None:
          logger.warning('Failed to update local VIX data.!Please check the disk and permissions.Attempting to download the full VIX data now.')
          vix_data = vix.get_vix_data_from_yfinance()
          if vix_data is None:
            logger.error('Failed to download VIX data from Yahoo Finance.Please check your network connection.Exit!')
            return
  else:
    # Offline Mode
    if vix_data_local is None:
      logger.error('Local VIX data is missing.offline mode execution failed.Exit')
      return
    local_data_last_date = vix.get_vix_data_timestamp(vix_data_local)
    timestamp_str = vix.get_vix_data_timestamp_str(vix_data_local)
    delta_time = datetime.datetime.now().timestamp() - local_data_last_date.timestamp().timestamp()
    if delta_time < 3600 * 24:
      logger.info('Local VIX data is valid,timestamp:{}.'.format(timestamp_str))
    else:
      logger.info('Local VIX data may be invalid,timestamp:{}.It will not update in offline mode.', timestamp_str)
    vix_data = vix_data_local

  # Check VIX data
  if vix_data is None:
    logger.error('Internal error! VIX data is None. Exit!')
  draw_charts(vix_data, 720, 'all')
  logger.info('Output result to ./output/result_all.html')
if __name__ == '__main__':
  main()
  
