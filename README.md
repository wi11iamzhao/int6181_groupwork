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
直接运行，输出echart  
```bash
python main.py
```
离线模式，无需从yahoo finance更新数据，适用于无法访问该服务的网络环境  
```bash
python main.py --offline
```
仅更新本地数据，不输出任何结果  
```bash
python main.py --update
```
获取帮助  
```bash
python main.py --help
```
## TODO
### 已计划
- [X] 修复h5py无法正常存储数据的问题
- [X] 增强命令行交互
- [X] 增加一个新的因子(SP500-MA250)
- [ ] 完善细节
- [ ] 实现运行后直接调用系统浏览器加载输出
### 待定
- [ ] 编写安装脚本`setup.py`
- [ ] 制作精美的README说明
- [ ] 增加测试用例



