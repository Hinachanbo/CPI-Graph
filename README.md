# CPI Graph maker
**Date:** 2025/9/4
## 実装概要
以下のサイトのCPIの推移をグラフ化します。更新ランプの適正CPIを散布図で同時に表示します。
前回からの差分のみをスクレイピングするようになっています。
https://cpi.makecir.com/

![グラフ](screenshot.png)

## 使用した技術
- python
- HTMLの処理：requests, BeautifulSoup
- データフレーム：pandas
- グラフ描写：matplotlib.pyplot, seaborn
