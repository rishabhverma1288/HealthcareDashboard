import streamlit as st
import pandas as pd
from functions import format_number
from charts import bar_chart,line_chart, bar_chart_horizontal
import plotly.express as px

import json

with open("colors.json") as f:

    COLOR_MAPS = json.load(f)



ttp = pd.read_excel("tooltip info.xlsx")
ttp = ttp[ttp["Tab"]=="nat"].reset_index()

st.title("Healthcare Dashboard")
st.subheader("Demand - National")

st.set_page_config(
    page_title="Demand Dashboard",
    layout="wide"
)

main = pd.read_csv("demand modified.csv")
main_brand = "Cosentyx"
channel_list =  main["channel"].unique().tolist()
lot_list =  main["Line of therapy"].unique().tolist()

with st.sidebar:

    time_period = st.selectbox(
        "Time Period",
        ("R3M", "R6M"),
    )
    time_period = "C" + time_period
    time_period1 = time_period[1:]
    channel = st.multiselect(
        "Channel",
        channel_list,
        default=channel_list
    )

    lot = st.multiselect(
        "Line of Therapy",
        lot_list,
        default=lot_list
        )

   


df_filter = main[(main["channel"].isin(channel))
              & (main["Line of therapy"].isin(lot))]

            # (cos_df[geo_level] == geo)
            # & (cos_df["Time Period"] == time_period) 
df = df_filter

df_current = df[df["Time Period"] == time_period]
prev_time_period = "P" + time_period[1:]
print(prev_time_period)
df_previous = df[(df["Time Period"] == prev_time_period)
                   & (df["drug name"] == main_brand)]


df_current_s = df[(df["Time Period"] == time_period)
                   & (df["switch_from"] == main_brand)]
df_previous_s = df[(df["Time Period"] == prev_time_period)
                   & (df["switch_from"] == main_brand)]

cos_df = df_current[df_current["drug name"] == main_brand]             


df = cos_df

row = st.container(horizontal=True)


with row:
    
    # st.caption("This is a string that explains something above.")
    current_market_share = (
    df["Patient Count"].sum() /
    df_current["Patient Count"].sum())

    previous_market_share = (
    df_previous[df_previous["drug name"] == main_brand]["Patient Count"].sum() /
    df_previous["Patient Count"].sum())
    market_share = round(current_market_share-previous_market_share,2)
    st.metric(
        label="Cosentyx Market Share",
        help=ttp[ttp["Metric"] == 1]["Info"][0],
        value=f"{current_market_share:.1%}",border = True,
        delta=f"{market_share:+.2f}%",)
    
    current = df[df["Source_of_business"]=="New"]["Patient Count"].sum()
    previous = df_previous[df_previous["Source_of_business"]=="New"]["Patient Count"].sum()
    if previous != 0:
        pct_change = ((current - previous) / previous) * 100
    else:
        pct_change = 0

    st.metric(
        label="New Patients",
        value=format_number(current),
        delta=f"{pct_change:+.2f}% vs Prev. {time_period1}",
        border=True,
        help=ttp[ttp["Metric"] == 2]["Info"][1]
    )

    current = df[df["Source_of_business"]=="Switch"]["Patient Count"].sum()
    previous = df_previous[df_previous["Source_of_business"]=="Switch"]["Patient Count"].sum()
    if previous != 0:
        pct_change = ((current - previous) / previous) * 100
    else:
        pct_change = 0
    st.metric(
        label="Switch to Cosentyx",
        value=format_number(current),
        
        border=True,
        help=ttp[ttp["Metric"] == 3]["Info"][2],
        delta=f"{pct_change:+.2f}% vs Prev. {time_period1}",
        
    )

    current = df_current_s[df_current_s["Source_of_business"]=="Switch"]["Patient Count"].sum()
    previous = df_previous_s[df_previous_s["Source_of_business"]=="Switch"]["Patient Count"].sum()
    if previous != 0:
        pct_change = ((current - previous) / previous) * 100
    else:
        pct_change = 0
    st.metric(
        label="Switch From Cosentyx",
        value=format_number(current),
        
        border=True,
        help=ttp[ttp["Metric"] == 4]["Info"][3],
        delta=f"{pct_change:+.2f}% vs Prev. {time_period1}",
        
    )


# Line Chart ----------------

if time_period == "CR3M":
    df = df_filter[df_filter["Time Period"].isin(["M1", "M2", "M3"])]
else:
    df = df_filter[df_filter["Time Period"].isin(["M1", "M2", "M3", "M4", "M5", "M6"])]


row = st.container(horizontal=False, border=True,height=525)
with row:

    st.metric(label="Patient Count Trend", value="",help=ttp[ttp["Metric"] == 5]["Info"][4])

    with st.expander("Show Filters"):

        sob = st.multiselect(
            "Source of Business",
            options=df["Source_of_business"].unique(),
            default=df["Source_of_business"].unique()
            )

        df = df[df["Source_of_business"].isin(sob)]
        q = (
        df.groupby(["period start date", "drug name","class"], as_index=False)
        ["Patient Count"]
        .sum()
        )
        q_join = q.groupby("period start date", as_index=False)["Patient Count"].sum()
        q_join.columns = ["period start date", "Total Sum"]
        q = q.merge(q_join, on="period start date")
        q["Market Share"] = round(q["Patient Count"] / q["Total Sum"]*100 , 2)
        q["period start date"] = pd.to_datetime(q["period start date"])
        q["Month_Year"] = q["period start date"].dt.strftime("%b'%y")

        brnd = st.multiselect(
            "Brand",
            options=q["drug name"].unique(),
            default=q["drug name"].unique()
            )
        clss = st.multiselect(
            "Class",
            options=q["class"].unique(),
            default=q["class"].unique()
            )
        q = q[q["drug name"].isin(brnd)]
        q = q[q["class"].isin(clss)]

        

  
    line_chart(q,"Month_Year","Market Share","drug name","Months","Market Share (%)","Brand",COLOR_MAPS["brands"],56)       

# LOT bar chart and switch

if time_period == "CR3M":
    df = df_filter[df_filter["Time Period"].isin(["M1", "M2", "M3"])]
else:
    df = df_filter[df_filter["Time Period"].isin(["M1", "M2", "M3", "M4", "M5", "M6"])]
drugs =  df["drug name"].unique().tolist()

row = st.container( border=True,height=1100)
with row:   
    c1,c2,c3 = st.columns([9,5,5])
    with c2:
        selected_brand = st.selectbox(
            "Brand",
            drugs,
        )
    with c3:
        switch = st.selectbox(
            "Switch To/From",
            ("Switch To","Switch From"),
        )
    with c1:
        st.metric(f"{selected_brand} Patient Share and Patients {switch} {selected_brand} - {time_period1}","",help=ttp[ttp["Metric"] == 6]["Info"][5])
    ldf = df[df["drug name"] == selected_brand]
    ldf = ldf.groupby(["drug name","Line of therapy"], as_index=False)["Patient Count"].sum()
    ldf_total = ldf.groupby(["drug name"], as_index=False)["Patient Count"].sum()
    ldf_total.columns = ["drug name","total patients"]
    ldf = ldf.merge(ldf_total,on="drug name")
    ldf["Market Share"] = round(ldf["Patient Count"]/ldf["total patients"]*100,2)


    col1, col2 = st.columns([3,5])
    with col1:

        bar_chart(ldf,"drug name","Market Share","Line of therapy","Brand","Market Share (%)","LOT",COLOR_MAPS["lot"],"Patient Count",66)


    with col2:
        df = df[df["Source_of_business"]=="Switch"]
        if switch=="Switch To":
            rdf = df[df["drug name"] == selected_brand]
            rdf = rdf.groupby(["period start date","switch_from"], as_index=False)["Patient Count"].sum()
            rdf_total = rdf.groupby(["period start date"], as_index=False)["Patient Count"].sum()
            rdf_total.columns = ["period start date","total patients"]
            rdf = rdf.merge(rdf_total,on="period start date")
            rdf["Market Share"] = round(rdf["Patient Count"]/rdf["total patients"]*100,2)
            rdf["period start date"] = pd.to_datetime(rdf["period start date"])
            rdf["Month_Year"] = rdf["period start date"].dt.strftime("%b'%y")
            rdf = rdf.sort_values("period start date", ascending=True)
            bar_chart(rdf,"Month_Year","Market Share","switch_from","Months","Market Share (%)","Switch From",COLOR_MAPS["brands"],"Patient Count",77)
            
        else:
            rdf = df[df["switch_from"] == selected_brand]
            rdf = rdf.groupby(["period start date","drug name"], as_index=False)["Patient Count"].sum()
            rdf_total = rdf.groupby(["period start date"], as_index=False)["Patient Count"].sum()
            rdf_total.columns = ["period start date","total patients"]
            rdf = rdf.merge(rdf_total,on="period start date")
            rdf["Market Share"] = round(rdf["Patient Count"]/rdf["total patients"]*100,2)
            rdf["period start date"] = pd.to_datetime(rdf["period start date"])
            rdf["Month_Year"] = rdf["period start date"].dt.strftime("%b'%y")
            rdf = rdf.sort_values("period start date", ascending=True)
            bar_chart(rdf,"Month_Year","Market Share","drug name","Months","Market Share (%)","Switch To",COLOR_MAPS["brands"],"Patient Count",77)
        rdf = df
    rdf = rdf.groupby(["drug name","switch_from"], as_index=False)["Patient Count"].sum()
    rdf_total = rdf.groupby(["drug name"], as_index=False)["Patient Count"].sum()
    rdf_total.columns = ["drug name","total patients"]
    rdf = rdf.merge(rdf_total,on="drug name")
    rdf["Market Share"] = round(rdf["Patient Count"]/rdf["total patients"]*100,2)
    st.write("")
    st.metric(f"Switches by Brand - {time_period1}",value="",help=ttp[ttp["Metric"] == 7]["Info"][6])
    bar_chart_horizontal(rdf,"drug name","Market Share","switch_from","Brand","Market Share (%)","Switch From",COLOR_MAPS["brands"],88)





