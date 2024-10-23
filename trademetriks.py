import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Setting Page config
st.set_page_config(page_title="Trademetriks", layout="wide")


# Linking CSS
with open('./style/style.css') as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html = True)

# Title
st.markdown('<p class="title">Trademetriks</p>', unsafe_allow_html = True)

# Functions for data extraction or conversion
# Functions for extracting and converting data
def extract_symbol(sym):
    return sym[4:]

def split_date(dates):
    return dates.split(" ")[0]

def convert_date(dates):
    return datetime.datetime.timestamp(dates)

def extract_instrument(inst):
    return "Equity" if inst[-2:] == "EQ" else "Options"

def convert_side(side):
    return "Buy" if side==1 else "Sell"

def get_day_number(day):
    week   = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',  'Friday', 'Saturday', 'Sunday']
    return week[day]

def get_month_name(month_num):
    month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    return month[month_num-1]


# Data Munging
df = pd.read_csv("./data/trades_data_latest.csv", index_col=0) 
trades_df = df[["tradePrice", "productType", "tradedQty", "symbol", "orderDateTime","tradeValue","side", "orderType"]]
trades_df['intraCheck'] = trades_df['tradedQty']*trades_df['side']
trades_df['netTrade'] = trades_df['tradeValue'] * trades_df['side']*-1
trades_df["symbol_extracted"] = trades_df["symbol"].apply(extract_symbol)
trades_df["datetime"] = pd.to_datetime(trades_df["orderDateTime"], dayfirst=True)
trades_df['date_converted'] = pd.to_datetime(trades_df["orderDateTime"], dayfirst=True).dt.date
trades_df["month"] = pd.to_datetime(trades_df["orderDateTime"], dayfirst=True).dt.month
trades_df["instrumentType"] = trades_df["symbol"].apply(extract_instrument)
trades_df["tradeType"] = trades_df["side"].apply(convert_side)



# Groupwise Aggregation
trades_agg_df = trades_df[["symbol_extracted","date_converted","intraCheck","netTrade"]].groupby(["date_converted","symbol_extracted"]).sum()
trades_agg_df = trades_agg_df[trades_agg_df["intraCheck"]==0].reset_index()[["symbol_extracted", "netTrade"]].groupby("symbol_extracted").sum()
gross_p_and_l = trades_agg_df['netTrade'].sum().round(2)


#Average Stocks traded and Average Amount Traded
stocks_traded_df = trades_df[["symbol_extracted","date_converted","intraCheck","netTrade"]].groupby(["date_converted","symbol_extracted"]).sum()
stocks_traded_df = stocks_traded_df[stocks_traded_df["intraCheck"]==0].reset_index()[["date_converted","symbol_extracted", "netTrade"]].groupby("date_converted").agg({"symbol_extracted":"count","netTrade":"sum"}).reset_index()
avg_stocks_traded =  (stocks_traded_df["symbol_extracted"].sum()// stocks_traded_df.shape[0])
amount_traded_df = trades_df[["symbol_extracted","date_converted","intraCheck","tradeValue"]].groupby(["date_converted","symbol_extracted"]).sum()
amount_traded_df = amount_traded_df[amount_traded_df['intraCheck']==0].reset_index()[["date_converted","tradeValue"]].groupby("date_converted").sum().reset_index()
avg_amount_traded = int(amount_traded_df["tradeValue"].mean().round(0))


# Datewise Aggregation
trades_net_df = trades_df[["intraCheck","netTrade","date_converted","symbol_extracted"]].groupby(["date_converted","symbol_extracted"]).sum()
trades_net_df = trades_net_df[trades_net_df["intraCheck"]==0]
cum_df = trades_net_df.reset_index()[["date_converted","netTrade"]].groupby("date_converted").sum()
cum_df = cum_df.reset_index()
cum_df["cumulative_value"] = cum_df["netTrade"].cumsum()
cum_df["day"] = pd.to_datetime(cum_df["date_converted"], dayfirst=True).dt.weekday
wins_count = cum_df[cum_df["netTrade"]>=0]['netTrade'].count()
loss_count = cum_df[cum_df["netTrade"]<0]['netTrade'].count()
win_rate = round(wins_count/ (wins_count+loss_count),2)
pl_ratio = round(cum_df[cum_df["netTrade"]>=0]['netTrade'].sum() / (-1*cum_df[cum_df["netTrade"]<0]['netTrade']).sum(),2)

#Daywise Aggregation
daywise_agg_df = cum_df[["day","netTrade"]].groupby("day").sum().reset_index()
daywise_agg_df["day_of_week"] = daywise_agg_df["day"].apply(get_day_number)
daywise_agg_df = daywise_agg_df.sort_values("day")


# Monthwise Aggregation
trades_month_stock_df = trades_df[["intraCheck","netTrade","month","symbol_extracted","date_converted"]].groupby(["date_converted","symbol_extracted","month"]).sum()
trades_month_stock_df = trades_month_stock_df[trades_month_stock_df["intraCheck"]==0]
trades_month_agg_df = trades_month_stock_df.reset_index()[['month', 'netTrade']].groupby('month').sum().round(2).reset_index()
trades_month_agg_df["monthName"] = trades_month_agg_df["month"].apply(get_month_name)
month_p_and_l = trades_month_agg_df[trades_month_agg_df["month"]==datetime.datetime.now().date().month]["netTrade"].reset_index().loc[0,"netTrade"]

# Last Day Profit
last_profit = trades_net_df.reset_index()[["date_converted", "netTrade"]].groupby("date_converted").sum().sort_values("date_converted",ascending=False).reset_index().iloc[0,1].round(2)
last_data_update = trades_net_df.reset_index()[["date_converted", "netTrade"]].groupby("date_converted").sum().sort_values("date_converted",ascending=False).reset_index().iloc[0,0]

#recent trades
recent_trades_df = trades_df[["orderDateTime","date_converted","symbol_extracted","tradeType","productType","tradePrice","tradedQty","tradeValue"]].sort_values("orderDateTime", ascending=False).reset_index()
recent_trades_df = recent_trades_df[recent_trades_df["date_converted"]==last_data_update][["orderDateTime","symbol_extracted","tradeType","productType","tradePrice","tradedQty","tradeValue"]]


# Instrument Wise Data
#to be commented
trades_inst_df = trades_df[["intraCheck","netTrade","instrumentType","symbol_extracted","date_converted"]].groupby(["date_converted","instrumentType","symbol_extracted"]).sum()
trades_inst_df = trades_inst_df[trades_inst_df["intraCheck"]==0].reset_index()[["instrumentType","netTrade"]].groupby("instrumentType").sum()


# banner with div tags
st.markdown(
    f"""<div class = "banner">
            <div class="kpi" style="background-color:#FF9500">
                <p>{"Gross Profit" if gross_p_and_l >=0 else "Gross Loss"}</p>
                <p class="value">{gross_p_and_l} Rs</p>
            </div>
            <div class="kpi" style="background-color:#00C3FF">
                <p>{"Today Profit" if last_profit>=0 else "Today Loss"}</p>
                <p class="value">{last_profit} Rs</p>
            </div>
            <div class="kpi" style="background-color:#B86C6C">
                <p>{"Month Profit" if month_p_and_l>=0 else "Month Loss"}</p>
                <p class="value">{month_p_and_l} Rs</p>
            </div>
            <div class="kpi" style="background-color:#FF9696">
                <p>Win rate</p>
                <p class="value">{win_rate}</p>
            </div>
            <div class="kpi" style="background-color:#9BDE43">  
                <p>P/L ratio</p>
                <p class="value">{pl_ratio}</p>
            </div>
            <div class="kpi" style="background-color:#FF78E0">
                <p>Avg stocks traded daily<p>
                <p class="value">{avg_stocks_traded}</p>
            </div>
            <div class="kpi" style="background-color:#969AFF">
                <p>Avg amount traded daily</p>
                <p class="value">{avg_amount_traded} Rs</p>
            </div>
    </div>""",unsafe_allow_html=True)


# Chart Layout1 with streamlit chart elements
#st.markdown(
#    """<div class="chart_1">
#        <div class="chart_element">Cumulative P/L graph</div>
#        <div class="chart_element">Date Wise P/L Graph</div>
#        <div class="chart_element">Day wise P/L</div>
#    </div>""", unsafe_allow_html=True
#)
# Done with Streamlit columns only


col1_ch1, col2_ch1, col3_ch1 = st.columns(3, gap="medium")
with col1_ch1:
    with st.container():
        st.markdown('<p class="kpi">Cumulative Profit or Loss</p>', unsafe_allow_html = True)
        st.line_chart(cum_df,x="date_converted",y="cumulative_value",color=["#FF6666"],height=290, x_label="Date",y_label="Amount")
    
with col2_ch1:
    with st.container():
        st.markdown('<p class="kpi">Date wise Profit or loss</p>', unsafe_allow_html = True)
        plot_df = trades_net_df.reset_index()[["date_converted","netTrade"]].groupby("date_converted").sum()
        st.bar_chart(plot_df,color="netTrade",height=290)

with col3_ch1:
    with st.container():
        st.markdown('<p class="kpi">Week Day wise Profit or Loss</p>', unsafe_allow_html = True)
        st.bar_chart(daywise_agg_df, x="day_of_week", y="netTrade", x_label="Day of Week",y_label="Net Trade", horizontal=True,                      height=290,color="netTrade")
        


# Chart Layout2
#st.markdown(
#    """<div class="chart_2">
#        <div class="chart_element">Top Traded stocks</div>
#        <div class="chart_element">Monthwise P/L</div>
#        <div class="chart_element">Recenty Trades</div>
#    </div>""", unsafe_allow_html=True
#)

col1_ch2, col2_ch2, col3_ch2 = st.columns([0.24,0.24,0.42], gap="medium")
with col1_ch2:
    with st.container():
        st.markdown('<p class="kpi">Monthwise Profit Loss</p>', unsafe_allow_html = True)
        st.bar_chart(trades_month_agg_df,x="monthName",y="netTrade",use_container_width=True, height=275,x_label="Month", y_label="Amount")
        

with col2_ch2:
    with st.container():
        st.markdown('<p class="kpi">Stockwise Performance</p>', unsafe_allow_html = True)
        st.dataframe(trades_agg_df.reset_index(), use_container_width=True,hide_index=True, height=275)

with col3_ch2:
    with st.container():
        st.markdown('<p class="kpi">Recent Trades</p>', unsafe_allow_html = True)
        st.dataframe(recent_trades_df, use_container_width=True,hide_index=True, height=275)

st.markdown(
    f"""<div class="developer">
            <div class="developer_item">Last Updated Data on {last_data_update} </div>
            <div class="developer_item">Developed by Naveen Kumar</div> 
            </div>""",unsafe_allow_html=True
)