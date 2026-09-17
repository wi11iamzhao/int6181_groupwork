import utils

def get_moving_average_data_list(data:dict, n:int) -> list[float]:
  # This function requires optimization for parallel computing.
  # Otherwise, calculating all the moving averages would consume a considerable amount of time.
  close_data = data['close_data_list']
  return utils.calculate_moving_average(close_data, n)
  # moving_average_list = []
  # for i in range(1, n):
  #   moving_average = utils.calculate_moving_average(close_data, i)
  #   moving_average_list.append(moving_average)
  # data_length = len(close_data)
  # if data_length < n:
  #   return moving_average_list
  # for i in range(i,data_length):
  #   moving_average = utils.calculate_moving_average(close_data, n)
  #   moving_average_list.append(moving_average)
  # return moving_average_list