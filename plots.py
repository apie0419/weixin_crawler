import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties
from datetime import date, timedelta


plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
plt.rcParams['axes.unicode_minus'] = False

start = date(2018, 10, 28)
end = date(2019, 10, 6)

def get_count_csv(df):
    censor = df.loc[:, ["account", "censor"]]
    group_censor = censor.groupby("account", as_index = False)
    sum_censor = group_censor.sum()

    sum_total = pd.DataFrame({"Total": df.groupby("account", as_index = False).size()}).reset_index()

    attributes = df.loc[:, ["account", "forprofit", "license", "official"]].drop_duplicates().reset_index(drop=True)
    ans = attributes.merge(sum_censor, on = "account")
    ans = ans.merge(sum_total, on = "account")
    ans.to_csv("count.csv", encoding = "utf-8")


def get_week_count_plot(df, start, end):
    now = start
    dt = list()
    res = list()
    while True:
        if now == end:
            break
        df2 = df.loc[(df["date"] >= pd.Timestamp(now)) & (df["date"] < pd.Timestamp(now + timedelta(weeks = 1)))]
        res.append(df2.shape[0])
        dt.append(str(now))
        now += timedelta(weeks = 1)


    index = pd.date_range(start = str(start), end = str(end - timedelta(days = 7)), freq = "W")
    index = [pd.to_datetime(date, format='%d-%m-%Y').date() for date in index]
        
    results = pd.DataFrame({
            "文章總數": res
        }, index = index)
    
    ax = results.plot(figsize=(18, 9), marker=".")
    ax.margins(1, 0.5)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.SU, interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.label.set_size(15)
    ax.yaxis.label.set_size(15)
    
    ax.set_xlabel("週次")
    ax.set_ylabel("文章總數")
    
    # plt.gcf().autofmt_xdate()
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.2)
    plt.savefig("week_count.png")

def get_week_countrate_plot(df, start, end):
    dt = list()
    official_list = list()
    forprofit_list = list()
    license_list = list()
    now = start
    while True:
        if now == end:
            break
        all_df = df.loc[(df["date"] >= pd.Timestamp(now)) & (df["date"] < pd.Timestamp(now + timedelta(weeks = 1)))]
        total = all_df.shape[0]
        official = all_df.loc[df["official"] == 1].shape[0]
        forprofit = all_df.loc[df["forprofit"] == 1].shape[0]
        license = all_df.loc[df["license"] == 1].shape[0]
        
        
        
        official_list.append(official/total)
        forprofit_list.append(forprofit/total)
        license_list.append(license/total)
        dt.append(str(now))
        now += timedelta(weeks = 1)
    
    index = pd.date_range(start = str(start), end = str(end - timedelta(days = 7)), freq = "W")
    index = [pd.to_datetime(date, format='%d-%m-%Y').date() for date in index]
    results = pd.DataFrame({
            "商業號/全部": forprofit_list,
            "官方/全部": official_list,
            "有許可證/全部": license_list
        }, index = index)
    
    
    ax = results.plot(figsize=(18, 9), marker = ".")
    ax.margins(1, 0.5)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.SU, interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.label.set_size(15)
    ax.yaxis.label.set_size(15)
    plt.xticks(rotation=90)
    # plt.gcf().autofmt_xdate()
    ax.set_xlabel("週次")
    ax.set_ylabel("比例")
    plt.subplots_adjust(bottom=0.2)
    plt.savefig("week_count_rate.png")

def get_week_ratio_plot(df, start, end):
    dt = list()
    official_list = list()
    forprofit_list = list()
    license_list = list()
    now = start
    while True:
        if now == end:
            break
        all_df = df.loc[(df["date"] >= pd.Timestamp(now)) & (df["date"] < pd.Timestamp(now + timedelta(weeks = 1)))]
        total = all_df.shape[0]
        official = all_df.loc[df["official"] == 1].shape[0]
        forprofit = all_df.loc[df["forprofit"] == 1].shape[0]
        license = all_df.loc[df["license"] == 1].shape[0]
        
        official_list.append(official/(total - official))
        forprofit_list.append(forprofit/(total - forprofit))
        license_list.append(license/(total - license))
        dt.append(str(now))
        now += timedelta(weeks = 1)
    
    index = pd.date_range(start = str(start), end = str(end - timedelta(days = 7)), freq = "W")
    index = [pd.to_datetime(date, format='%d-%m-%Y').date() for date in index]
    results = pd.DataFrame({
            "商業號/非商業號": forprofit_list,
            "官方/非官方": official_list,
            "有許可證/無許可證": license_list
        }, index = index)
    
    
    ax = results.plot(figsize=(18, 9), marker = ".")
    ax.margins(1, 0.5)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.SU, interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.label.set_size(15)
    ax.yaxis.label.set_size(15)
    plt.xticks(rotation=90)
    # plt.gcf().autofmt_xdate()
    ax.set_xlabel("週次")
    ax.set_ylabel("比例")
    plt.subplots_adjust(bottom=0.2)
    plt.savefig("week_count_rate2.png")



if __name__ == '__main__':
    df = pd.read_csv("Data.csv", encoding = "utf-8", index_col = 0)
    df["date"] = pd.to_datetime(df["date"])

    get_count_csv(df)
    get_week_countrate_plot(df, start, end)
    get_week_count_plot(df, start, end)
    get_week_ratio_plot(df, start, end)
