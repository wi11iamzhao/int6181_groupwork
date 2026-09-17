import argparse
import time
import datetime
import msg
import pyecharts_tool
import data_cleaning_tool
import data_update_tool
import moving_average as ma
from logger import Logger
from utils import utils

def draw_charts(vix_data:dict, spx_data:dict, spx_ma_list:list[float], output_len:int, output_path:str):
  vix_precentile_list = utils.generate_percentile_list(vix_data['close_data_list'])
  vix_positive_index_list = []
  vix_negative_index_list = []
  for i in range(output_len):
    data = vix_data['close_data_list'][len(vix_data['date_list']) - output_len + i]
    index = utils.get_precentile_index(vix_precentile_list, data)
    if index > 50:
      vix_positive_index_list.append(index - 50)
      vix_negative_index_list.append(0)
    elif index < 50:
      vix_positive_index_list.append(0)
      vix_negative_index_list.append(index - 50)
    else:
      vix_positive_index_list.append(0)
      vix_negative_index_list.append(0)

  # full_vix_candlestick_data_list = utils.get_candlestick_data_list(vix_data)
  # vix_candlestick_data_list = full_vix_candlestick_data_list[len(vix_data['date_list']) - output_len:]
  full_spx_candlestick_data_list = utils.get_candlestick_data_list(spx_data)
  spx_candlestick_data_list = full_spx_candlestick_data_list[len(spx_data['date_list']) - output_len:]
  date_str_list = []
  for i in range(output_len):
    date = datetime.datetime.fromtimestamp(vix_data['date_list'][len(vix_data['date_list']) - output_len + i])
    date_str = date.strftime('%Y%m%d')
    date_str_list.append(date_str)

  spx_ma_delta_list = []
  for i in range(len(spx_data['close_data_list'])):
    delta = spx_data['close_data_list'][i] - spx_ma_list[i]
    spx_ma_delta_list.append(delta)

  spx_precentile_list = utils.generate_percentile_list(spx_ma_delta_list)
  spx_positive_index_list = []
  spx_negative_index_list = []
  for i in range(output_len):
    data = spx_ma_delta_list[i]
    index = utils.get_precentile_index(spx_precentile_list, data)
    if index > 50:
      spx_positive_index_list.append(index - 50)
      spx_negative_index_list.append(0)
    elif index < 50:
      spx_positive_index_list.append(0)
      spx_negative_index_list.append(index - 50)
    else:
      vix_positive_index_list.append(0)
      spx_negative_index_list.append(0)

  spx_candlestick_view = pyecharts_tool.init_candlestick_view(
    candlestick_dicts=[{
      'name':'SP500 Index',
      'data':spx_candlestick_data_list,
    }],
    x_axis_items=date_str_list,
    x_axis_indexs=[0,1,2],
    zoom_range_start=20.0,
    zoom_range_end=80.0,
    line_dicts=[{
        'name':'MA250',
        'data':spx_ma_list[len(spx_ma_list) - output_len:],
        'color':'#ff0000'}],
    mark_line_items=None,
    title='SP500 Index',
    sub_title='',
    is_show_legend=False,)
  spx_percentile_bar_view = pyecharts_tool.init_bar_view(
    x_axis_items=date_str_list,
    bar_data_dicts=[
      {
      'name':'SPX-MA250百分位指数',
      'color':'red',
      'data':spx_positive_index_list,
      'stack':'stack_1',
      },
      {
      'name':'SPX-MA250百分位指数',
      'color':'green',
      'data':spx_negative_index_list,
      'stack':'stack_1',
      }],
    stack='stack_1',
    is_percentage=False,
    is_on_zero=True,)
  vix_percentile_bar_view = pyecharts_tool.init_bar_view(
      x_axis_items=date_str_list,
      bar_data_dicts=[
        {
        'name':'VIX百分位指数',
        'color':'red',
        'data':vix_positive_index_list,
        'stack':'stack_2',
        },
        {
        'name':'VIX百分位指数',
        'color':'green',
        'data':vix_negative_index_list,
        'stack':'stack_2',
        }],
      line_dicts=[{
      'name':'VIX',
      'data':vix_data['close_data_list'][len(vix_data['close_data_list']) - output_len:],
      'color':'#151B54'}],
      stack='stack_2',
      is_percentage=False,
      is_on_zero=True,)
  gird_view = pyecharts_tool.init_gird_view(
    sub_views=[spx_candlestick_view,
              spx_percentile_bar_view,
              vix_percentile_bar_view],
    heights=['40%', '10%', '10%',],
    top_heights=['5%', '50%', '65%']
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

  vix_data = None
  spx_data = None

  if args.update is True:
    if args.offline is True:
      logger.error('You cannot update local date in offline mode.Exit!')
      return None
    
  # VIX
  vix_data_local = data_update_tool.load_data_from_local_file('^VIX')
  vix_data_datetime = None
  if vix_data_local is not None:
    vix_data_datetime = data_update_tool.get_data_datetime(vix_data_local)
    length = data_update_tool.get_data_length(vix_data_local)
    datetime_str = data_update_tool.get_data_datetime_str(vix_data_local)
    delta_time = datetime.datetime.now().timestamp() - vix_data_datetime.timestamp()
    logger.info(msg.MSG_INFO_LOAD_LOCAL_VIX_DATA_SUCCESSED.format(length, datetime_str))

  else:
    delta_time = 1073741824
    logger.info(msg.MSG_INFO_NO_LOCAL_VIX_DATA)
  if args.offline is not True:
    if delta_time < 3600 * 24:
      logger.info(msg.MSG_INFO_LOCAL_VIX_DATA_VAILD)
      vix_data = vix_data_local
    else:
      logger.info(msg.MSG_INFO_LOCAL_VIX_DATA_INVAILD)
      time_strat = time.perf_counter()
      vix_data_new = data_update_tool.get_data_from_yfinance('^VIX', vix_data_datetime)
      time_end = time.perf_counter()
      if vix_data_new is None:
        logger.error('Failed to download VIX data from Yahoo Finance.Please check your network connection.Exit!')
        return
      time_delta = time_end - time_strat
      vix_data_length = data_update_tool.get_data_length(vix_data_new)
      timestamp_str = data_update_tool.get_data_datetime_str(vix_data_new)
      logger.info(msg.MSG_INFO_GET_VIX_DATA_YFINANCE_SUCCESSED.format(time_delta, vix_data_length, timestamp_str))
      vix_data = data_update_tool.merge_data(vix_data_local, vix_data_new)

  # SPX
  spx_data_local = data_update_tool.load_data_from_local_file('^SPX')
  spx_data_datetime = None
  if spx_data_local is not None:
    spx_data_datetime = data_update_tool.get_data_datetime(spx_data_local)
    length = data_update_tool.get_data_length(spx_data_local)
    datetime_str = data_update_tool.get_data_datetime_str(spx_data_local)
    delta_time = datetime.datetime.now().timestamp() - spx_data_datetime.timestamp()
    logger.info(msg.MSG_INFO_LOAD_LOCAL_SPX_DATA_SUCCESSED.format(length, datetime_str))
  else:
    delta_time = 1073741824
    logger.info(msg.MSG_INFO_NO_LOCAL_SPX_DATA)
  if args.offline is not True:
    if delta_time < 3600 * 24:
      logger.info(msg.MSG_INFO_LOCAL_SPX_DATA_VAILD)
      spx_data = spx_data_local
    else:
      logger.info(msg.MSG_INFO_LOCAL_SPX_DATA_INVAILD)
      time_strat = time.perf_counter()
      spx_data_new = data_update_tool.get_data_from_yfinance('^SPX', spx_data_datetime)
      time_end = time.perf_counter()
      if spx_data_new is None:
        logger.error('Failed to download SPX data from Yahoo Finance.Please check your network connection.Exit!')
        return
      time_delta = time_end - time_strat
      spx_data_length = data_update_tool.get_data_length(spx_data_new)
      timestamp_str = data_update_tool.get_data_datetime_str(spx_data_new)
      logger.info(msg.MSG_INFO_GET_SPX_DATA_YFINANCE_SUCCESSED.format(time_delta, spx_data_length, timestamp_str))
      spx_data = data_update_tool.merge_data(spx_data_local, spx_data_new)

    # Check data
    if vix_data is None or spx_data is None:
      logger.error(msg.MEG_ERROR_DATA_ERROR)
      return
    
  # Clean data
  vix_data_length = data_update_tool.get_data_length(vix_data)
  spx_data_length = data_update_tool.get_data_length(spx_data)
  if vix_data_length == 0 or spx_data_length == 0:
    logger.error(msg.MSG_ERROR_DATA_CONFLICT)
    return
  vix_data, spx_data = data_cleaning_tool.delete_invalid_items(vix_data, spx_data)
  vix_data_length = data_update_tool.get_data_length(vix_data)
  spx_data_length = data_update_tool.get_data_length(spx_data)
  if vix_data_length == 0 or spx_data_length == 0 or vix_data_length != spx_data_length:
    logger.error(msg.MSG_ERROR_DATA_CONFLICT)
    return
    
  if args.offline is not True:
    result_vix = data_update_tool.update_local_data('^VIX', vix_data)
    result_spx = data_update_tool.update_local_data('^SPX', spx_data)
    if result_vix is not None and result_spx is not None and result_vix == result_spx:
      logger.info(msg.MSG_INFO_UPDATE_LOCAL_DATA_SUCCESSED.format(result_vix))
    else:
      logger.error(msg.MSG_ERROR_UPDATE_LOCAL_DATA_FAILED)

  if args.update is True:
    return
  spx_ma250_list = ma.get_moving_average_data_list(spx_data, 250)
  draw_charts(vix_data, spx_data, spx_ma250_list, 720, './output/')
  logger.info('Output result to ./output/result_{}.html'.format(time.strftime("%Y-%m-%d", time.localtime())))

if __name__ == '__main__':
  main()
  
