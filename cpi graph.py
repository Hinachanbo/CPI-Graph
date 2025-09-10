import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import time
from datetime import datetime

# ----------------------------
# 設定
# ----------------------------
BASE_URL = "https://cpi.makecir.com/users/view/9615"  # ユーザページ
CSV_FILE = "history.csv"

lamp_order = ["FULLCOMBO","EXHARD","HARD","CLEAR","EASY"]
lamp_colors = {
    "FULLCOMBO": "#FF9966", "EXHARD": "#FFFF99", "HARD": "#FF6666", 
    "CLEAR": "#99CCFF", "EASY": "#99FF99"
}

# ----------------------------
# 既存データを読み込み
# ----------------------------
if os.path.exists(CSV_FILE):
    df_existing = pd.read_csv(CSV_FILE, parse_dates=["Date"])
    last_date = df_existing["Date"].max()
else:
    df_existing = pd.DataFrame()
    last_date = None

# ----------------------------
# 更新履歴ページのスクレイピング
# ----------------------------
res = requests.get(BASE_URL)
soup = BeautifulSoup(res.text, "html.parser")

# 履歴テーブルの行を取得
table = soup.find("table", id="histories-table")
rows = table.find("tbody").find_all("tr")

data = []
dates = []
cpis = []


for row in rows:
    cols = row.find_all("td")
    date_str = cols[0].text.strip()
    date = pd.to_datetime(date_str)
    cpi = float(cols[1].text.strip())
    if(not(not len(data) == 0 and dates[-1] == date)):
        dates.append(date)
        cpis.append(cpi)
    
    # 既に持っている日付ならスキップ
    if last_date is not None and date <= last_date:
        continue

    print(date)
    
    
    detail_link = "https://cpi.makecir.com" + cols[3].find("a")["href"]
    
    # 詳細ページのスクレイピング
    detail_res = requests.get(detail_link)
    detail_soup = BeautifulSoup(detail_res.text, "html.parser")
    lamp_table = detail_soup.find("table", id="lamp-changes")
    if lamp_table:
        for lamp_row in lamp_table.find("tbody").find_all("tr"):
            cols2 = lamp_row.find_all("td")
            title = cols2[0].text.strip()
            lamp_pc = cols2[2].find("div", class_="pc-dsp").text.strip()
            cpi_val = cols2[3].text.strip()
            cpi_val = float(cpi_val) if cpi_val not in ("-","") else None
            data.append({
                "Date": date,
                "Title": title,
                "Lamp": lamp_pc,
                "LampColor": lamp_colors.get(lamp_pc, "#000000"),
                "CPI": cpi_val
            })
    print("finish")
    time.sleep(10) 

# ----------------------------
# DataFrame 作成・結合
# ----------------------------
df_new = pd.DataFrame(data)
if not df_new.empty:
    df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset=["Date","Title","Lamp"])
else:
    df_combined = df_existing.copy()

# CSV に保存
df_combined.to_csv(CSV_FILE, index=False)

# ----------------------------
# グラフ描画
# ----------------------------
def daily_graph():
    fig, ax = plt.subplots(figsize=(12,6))

    # 背景色
    fig.patch.set_facecolor("lightgray")
    ax.set_facecolor("lightgray")

    # グリッドを一番奥
    ax.grid(True, zorder=0)

    # lamp_order の順番で zorder を振る
    for i, lamp in enumerate(reversed(lamp_order), start=1):
        df_lamp = df_combined[df_combined["Lamp"] == lamp]
        if not df_lamp.empty:
            ax.scatter(
                df_lamp["Date"], df_lamp["CPI"],
                marker=".", color=lamp_colors.get(lamp),
                label=lamp, zorder=i
            )

    # 折れ線を一番最前面に描画
    ax.plot(dates, cpis, marker='.', color='black', label='CPI', zorder=len(lamp_order)+1)

    ax.set_xlabel("Date")
    ax.set_ylabel("CPI")
    ax.set_title("CPI Graph")
    plt.xticks(rotation=45)
    ax.legend()
    plt.tight_layout()
    plt.savefig("cpi_graph.png", dpi=300)



daily_graph()
