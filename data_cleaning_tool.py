
def delete_invalid_items(vix_data:dict, spx_data:dict) -> tuple[dict, dict]:
  vix_date_list = vix_data['date_list']
  spx_date_list = spx_data['date_list']
  vix_data_copy = {
    'open_data_list':vix_data['open_data_list'].copy(),
    'close_data_list':vix_data['close_data_list'].copy(),
    'low_data_list':vix_data['low_data_list'].copy(),
    'high_data_list':vix_data['high_data_list'].copy(),
    'volume_data_list':vix_data['volume_data_list'].copy(),
    'date_list':vix_data['date_list'].copy()}
  spx_data_copy = {
      'open_data_list':spx_data['open_data_list'].copy(),
      'close_data_list':spx_data['close_data_list'].copy(),
      'low_data_list':spx_data['low_data_list'].copy(),
      'high_data_list':spx_data['high_data_list'].copy(),
      'volume_data_list':spx_data['volume_data_list'].copy(),
      'date_list':spx_data['date_list'].copy()}
  vix_date_approximation_list = []
  spx_date_approximation_list = []

  for date in vix_date_list:
    vix_date_approximation_list.append(int(date / (3600 * 24)))
  for date in spx_date_list:
    spx_date_approximation_list.append(int(date / (3600 * 24)))

  for i in range(len(vix_date_approximation_list)):
    index = vix_date_approximation_list[i]
    if index not in spx_date_approximation_list:
      # delete item from vix_data
      del vix_data_copy['open_data_list'][i]
      del vix_data_copy['close_data_list'][i]
      del vix_data_copy['low_data_list'][i]
      del vix_data_copy['high_data_list'][i]
      del vix_data_copy['volume_data_list'][i]
      del vix_data_copy['date_list'][i]

  for i in range(len(spx_date_approximation_list)):
    index = spx_date_approximation_list[i]
    if index not in vix_date_approximation_list:
        # delete item from spx_data
        del spx_data_copy['open_data_list'][i]
        del spx_data_copy['close_data_list'][i]
        del spx_data_copy['low_data_list'][i]
        del spx_data_copy['high_data_list'][i]
        del spx_data_copy['volume_data_list'][i]
        del spx_data_copy['date_list'][i]
  return vix_data_copy, spx_data_copy