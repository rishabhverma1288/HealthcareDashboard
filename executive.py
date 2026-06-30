import streamlit as st
import pandas as pd
from functions import format_number, hcpHco,patient_type
from charts import bar_chart,line_chart,normal_bar_chart,normal_bar_chart_2
import plotly.express as px

import json
# def demandGeo
with open("colors.json") as f:

    COLOR_MAPS = json.load(f)





st.title("Healthcare Dashboard")
st.subheader("Executive View")

st.set_page_config(
    page_title="Executive View",
    layout="wide"
)

main = pd.read_csv("demand modified.csv")

main["Patient Type"] = main.apply(
    lambda row: patient_type(
        row["Line of therapy"],
        row["Source_of_business"]
    ),
    axis=1
)

main_brand = "Cosentyx"

channel_list =  main["channel"].unique().tolist()


with st.sidebar:

    time_period = st.selectbox(
        "Time Period",
        ("R3M", "R6M"),
    )
    time_period = "C" + time_period
    time_period1 = time_period[1:]
   

    
    


df_filter = main
            # (cos_df[geo_level] == geo)
            # & (cos_df["Time Period"] == time_period) 
df = df_filter

df_current = df[df["Time Period"] == time_period]
prev_time_period = "P" + time_period[1:]
print(prev_time_period)
df_previous = df[(df["Time Period"] == prev_time_period)
                   & (df["drug name"] == main_brand)]



cos_df = df_current[df_current["drug name"] == main_brand]             


df = cos_df


row = st.container(horizontal=False,border=True)
with row:
    row = st.container(horizontal=True)
    with row:

        current = df["Patient Count"].sum()
        previous = df_previous["Patient Count"].sum()
        if previous != 0:
            pct_change = ((current - previous) / previous) * 100
        else:
            pct_change = 0

        st.metric(
            label="Patients",
            value=format_number(current),
            
            border=True,
            delta=f"{pct_change:+.2f}% vs Prev. {time_period1}",
            
        )

        current = df[df["Patient Type"]=="1L New Patients"]["Patient Count"].sum()
        previous = df_previous[df_previous["Patient Type"]=="1L New Patients"]["Patient Count"].sum()
        if previous != 0:
            pct_change = ((current - previous) / previous) * 100
        else:
            pct_change = 0

        st.metric(
            label="1L New Patients",
            value=format_number(current),
            
            border=True,
           
            delta=f"{pct_change:+.2f}% vs Prev. {time_period1}",
            
        )

        current = df[df["Patient Type"]=="1L Continue Patients"]["Patient Count"].sum()
        previous = df_previous[df_previous["Patient Type"]=="1L Continue Patients"]["Patient Count"].sum()
        if previous != 0:
            pct_change = ((current - previous) / previous) * 100
        else:
            pct_change = 0

        st.metric(
            label="1L Continue Patients",
            value=format_number(current),
            
            border=True,
           
            delta=f"{pct_change:+.2f}% vs Prev. {time_period1}",
            
        )

        current = df[df["Patient Type"]=="2L+ New Patients"]["Patient Count"].sum()
        previous = df_previous[df_previous["Patient Type"]=="2L+ New Patients"]["Patient Count"].sum()
        if previous != 0:
            pct_change = ((current - previous) / previous) * 100
        else:
            pct_change = 0

        st.metric(
            label="2L+ New Patients",
            value=format_number(current),
            
            border=True,
           
            delta=f"{pct_change:+.2f}% vs Prev. {time_period1}",
            
        )

        current = df[df["Patient Type"]=="2L+ Continue Patients"]["Patient Count"].sum()
        previous = df_previous[df_previous["Patient Type"]=="2L+ Continue Patients"]["Patient Count"].sum()
        if previous != 0:
            pct_change = ((current - previous) / previous) * 100
        else:
            pct_change = 0

        st.metric(
            label="2L+ Continue Patients",
            value=format_number(current),
            
            border=True,
            
            delta=f"{pct_change:+.2f}% vs Prev. {time_period1}",
            
        )


    if time_period == "CR3M":
        df1 = df_filter[df_filter["Time Period"].isin(["M1", "M2", "M3"])]
    else:
        df1 = df_filter[df_filter["Time Period"].isin(["M1", "M2", "M3", "M4", "M5", "M6"])]

    df1 = df1[df1["drug name"] == main_brand]  
    df1 = df1.groupby(["Patient Type","period start date"])["Patient Count"].sum().reset_index()
    df1_total = df1.groupby(["period start date"])["Patient Count"].sum().reset_index()
    df1_total.columns = ["period start date","total"]
    df1 = df1.merge(df1_total,on="period start date")
    df1["Market Share"] =  round(df1["Patient Count"]/df1["total"]*100,2)
    df1["period start date"] = pd.to_datetime(df1["period start date"])
    df1["Month_Year"] = df1["period start date"].dt.strftime("%b'%y")


    bar_chart(df1,"Month_Year","Market Share","Patient Type",
                            "Months","Market Share (%)","Patient Type",COLOR_MAPS["patienttype"],"Patient Count",51)




main = pd.read_csv("PT modified.csv")



if time_period == "CR3M":
    df_current = main[main["Time Period"].isin(["M1", "M2", "M3"])]
else:
    df_current = main[main["Time Period"].isin(["M1", "M2", "M3", "M4", "M5", "M6"])]




cos_df = df_current[df_current["drug name"] == main_brand]  
df = cos_df
df["Approved claims"] = df["paid claims count"]+df["reverse claim count"]
df = df.groupby(["period start date"])[["claims count","Approved claims","rejected claim count"]].sum().reset_index()
df["Approval Rate"] = round(df["Approved claims"]/df["claims count"]*100,2)
df["Denial Rate"] = round(df["rejected claim count"]/df["claims count"]*100,2)

df = df[["period start date","Approval Rate","Denial Rate"]]
df_unpivot = df.melt(
    id_vars="period start date",
    var_name="Metric",
    value_name="Value"
)
df_unpivot["period start date"] = pd.to_datetime(df_unpivot["period start date"])
df_unpivot["Month_Year"] = df_unpivot["period start date"].dt.strftime("%b'%y")


row = st.container(horizontal=True)
with row:
    row = st.container(horizontal=False,border=True)
    with row:
        st.metric("Cosentyx Approved/Denial Rate","")
        line_chart(df_unpivot,"Month_Year","Value","Metric","Months","Claim Rate","Rates",COLOR_MAPS["claimsRate"],4)


    cos_df = df_current[df_current["drug name"] == main_brand]  
    df = cos_df  
  
    df = df.groupby(["reject reason"])[["rejected claim count"]].sum().reset_index() 
    df["Type"] = "Denied Claims" 
    df = df.sort_values("rejected claim count",ascending=False)
    row = st.container(horizontal=False,border=True)
    with row:
        st.metric("Cosentyx Denied Claims","")
        normal_bar_chart_2(df,"reject reason","rejected claim count","Months","Denied Claims","#BBC9E5",5)
