## Usage

### 爬蟲

#### 環境設置

- windows 10
- 微信桌面版
- 按鍵精靈2014
- notepad++
- python3.6

#### Python

1. setting.conf 設定資料庫資訊，URL_DIR 設定為按鍵精靈 Folder 的路徑
2. Mail 服務需開啟 google 服務並取得金藥
3. 使用 python weixin_crawler.py 即可

#### 按鍵精靈

1. 登入微信，並且將所有公眾號文章首頁加入收藏
2. 進入 notepad++ > 設定 > 快速鍵設定，將 "貼上 HTML 內容" 設為 CTRL + R
3. 開啟按鍵精靈，並將 url_crawler/Crawl_URL.Q 匯入
4. 設定參數(座標顏色可用按鍵精靈內的"抓抓"來調整)
  - Foloder - 抓出的 HTML file 儲存的地方
  - Foloder2 - 其餘程式所需資料
  - init_X, init_Y - 可以隨意設
  - Bar_X, Bar_Y1, Bar_Y2, Line_X - 點入公眾號文章列表時，最右邊的滾輪 的 X 座標及最上面的Y座標(Y1)最下面的Y座標(Y2)，Line_X 只要在下圖紅框範圍內即可。
  - ScreenShot_X1, ScreenShotX2 - 我們須紀錄每個文章標題圖片，因此需要標記文章標題位置 (X座標)，大概挑選一個長度即可 (如下圖所示，盡量不要挑太長，留白空間會增加)。
  
	![](https://i.imgur.com/ZgqUZqg.png)

  - Account_X, Account_Y1, Account_Y2, Account_BarX, Account_BarY - 收藏頁面的列表 X 座標(下圖紅框範圍內即可)，Y1, Y2 則需要頁面的最高及最低點。 BarX 就是右方滾輪的 X 座標，BarY 為滾輪滾到最底的座標大約會跟 Y2 接近，而 Y1 也會跟滾輪滾到最頂的Y座標接近。

    ![](https://i.imgur.com/3NDGPTY.png)
	
  - Refresh_X, Refresh_Y - 文章列表頁面的重新整理按鈕座標
  - Account_Width - 大約計算即可，計算兩個連結之間的距離，用連結中某個字母的 pixel Y 座標對應計算。
  - Account_Bar_Color, Bar_Color, Bar_Color2 - Account_Bar_Color 收藏頁面的 Bar 顏色(hover 在 Bar 上會變色要注意，紀錄變色前的)，Bar_Color, Bar_Color2 在文章列表頁面的 Bar 顏色，同樣紀錄變色前的，但有時會有不同顏色所以需要紀錄 Bar_Color2。
  - LinkColor - 連結顏色
  - Line_Color, Line_Color2 - 文章分隔線顏色
  - PageWidth - 文章分隔線之間的寬度

5. 點開微信收藏畫面，並停留在收藏最底端，按 F10 即可開始執行按鍵精靈
6. 若使用虛擬機，則須將 url_crawler/Go.bat 中的路徑更改為 F10.vbs 所在路徑，並使用 Win10 排程工作排定時間，並停留在微信收藏頁面，等待時間到程式就會自動執行。

### 分析

#### 文章相似度及情緒分析

1. 設定 statistics.py 中參數
  - GET_KEYWORDS - 可以決定是否要產生關鍵字相關檔案
  - wanted_word - 使用之關鍵字
  - export_dirs - 輸出資料夾
  - start - 開始計算日期
  - end - 結束計算日期

2. 輸入 python statistics.py 即開始執行

##### 輸出文件

輸出文件有

- <date>_statistics.csv - 每天的總文章 pairs, 相似度大於 0.3 的比例與總數。
- <date>_sentiment.csv - 每篇文章的情緒分布。
- <date>_statistics.png - 所有文章 pairs 在相似度上的分布。

#### 文章數量統計

1. 設定 download_data.py, plots.py 的時間區間
2. python download_data.py
3. python plots.py

##### 輸出文件

- count.csv - 時間區間內的公眾號 official, license, forprofit, total, censor(被刪除文章) 數量
- week_count.png - 每周文章總數折線圖
- week_count_rate.png - 每周文章 官方/全部, 有許可證/全部, 商業號/全部 比例折線圖
- week_count_rate2.png - 每周文章 官方/非官方, 有許可證/無許可證, 商業號/非商業號 比例折線圖
