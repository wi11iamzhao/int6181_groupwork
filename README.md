# INT6181-P01 Python GroupWork
## 项目介绍
通过yfinance从雅虎金融获取数据后用pyecharts展示当前美股市场的恐慌/乐观情况
## 指标
### VIX
VIX指数（Volatility Index）是芝加哥期权交易所（CBOE）编制的市场波动率指数，用来衡量市场对标普500指数未来30天波动程度的预期，常被称为“恐慌指数”。  
通过当前VIX指数在历史数据的分位区间，可以衡量市场的恐慌/乐观程度。
## 安装依赖项
```bash
pip install yfinance pyecharts h5py
```
## Highlights
- 使用yfinance获取金融数据
- 使用h5py缓存大量数据
- 使用pyecharts生成网页图表展示数据
## 运行
尚未完全完工，目前运行vix.py会在目录下输出一个当日的运行结果，文件名为`vix_日期_.html`
## TODO
### 已计划
- [X]修复h5py无法正常存储数据的问题
- [ ]增加命令行接口
- [ ]完善细节
### 待定
- [ ]增加一个新的因子
- [ ]增加测试用例
- [ ]完善README
- [ ]实现运行后直接调用系统浏览器加载输出

