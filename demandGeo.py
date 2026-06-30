import streamlit as st
import pandas as pd
from functions import format_number, hcpHco
from charts import bar_chart,line_chart
import plotly.express as px

import json
# def demandGeo
with open("colors.json") as f:

    COLOR_MAPS = json.load(f)


ttp = pd.read_excel("tooltip info.xlsx")
ttp = ttp[ttp["Tab"]=="Geo"]


st.title("Healthcare Dashboard")
st.subheader("Demand - Geography")

st.set_page_config(
    page_title="Demand Dashboard",
    layout="wide"
)

main = pd.read_csv("demand modified.csv")
main_brand = "Cosentyx"

channel_list =  main["channel"].unique().tolist()
payer_list =  main["payer segment"].unique().tolist()

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

    payer = st.multiselect(
        "Payer Segment",
        payer_list,
        default=payer_list
        )

    geo_level = st.selectbox(
        "Geography Level", ("HCO Nation", "HCO Area","HCO Region", "HCO Territory"))

    geo_list = main[geo_level].unique().tolist()
    print(geo_list)
    geo = st.multiselect(
        "Geography",
        
        geo_list,
        default=geo_list,

        accept_new_options=True,

        )


df_filter = main[(main["channel"].isin(channel))
              & (main["payer segment"].isin(payer))
              & (main[geo_level].isin(geo))]

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
        help=ttp[ttp["Metric"] == 1]["Info"][0],
        delta=f"{pct_change:+.2f}% vs Prev. {time_period1}",
        
    )

    
    # st.caption("This is a string that explains something above.")



  

    current = df["claims count"].sum()
    previous = df_previous["claims count"].sum()
    if previous != 0:
        pct_change = ((current - previous) / previous) * 100
    else:
        pct_change = 0
    
    st.metric(
        label="Claims",
        value=format_number(current),
        delta=f"{pct_change:+.2f}% vs Prev. {time_period1}",
        border=True,
        help=ttp[ttp["Metric"] == 2]["Info"][1]
          )

    current_market_share = (
    df["Patient Count"].sum() /
    df_current["Patient Count"].sum())

    previous_market_share = (
    df_previous[df_previous["drug name"] == main_brand]["Patient Count"].sum() /
    df_previous["Patient Count"].sum())
    market_share = round(current_market_share-previous_market_share,2)
    st.metric(
        label="Cosentyx Market Share",
        help=ttp[ttp["Metric"] == 3]["Info"][2],
        value=f"{current_market_share:.1%}",border = True,
        delta=f"{market_share:+.2f}% vs Prev. {time_period1}",)



# Line Chart - MArket Share Trend -------------------------------------------------
if time_period == "CR3M":
    df = df_filter[df_filter["Time Period"].isin(["M1", "M2", "M3"])]
else:
    df = df_filter[df_filter["Time Period"].isin(["M1", "M2", "M3", "M4", "M5", "M6"])]


row = st.container(horizontal=False, border=True,height=545)
with row:

    st.metric(label="Patient Count Trend", value="",help=ttp[ttp["Metric"] == 4]["Info"][3])

    with st.expander("Show Filters"):

        sob = st.multiselect(
            "Source of Business",
            options=df["Source_of_business"].unique(),
            default=df["Source_of_business"].unique()
            )
        lot = st.multiselect(
            "Line of Therapy",
            options=df["Line of therapy"].unique(),
            default=df["Line of therapy"].unique()
            )
        df = df[df["Source_of_business"].isin(sob)]
        df = df[df["Line of therapy"].isin(lot)]
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

# --------------------------------------------------------------------------------------------------



# Second Chart - Payer Segment - LOT  -------------------------------------------------

df = cos_df

df = df[df["Time Period"] == time_period]


df = df.groupby(["payer segment", "Line of therapy"], as_index=False)["Patient Count"].sum()
df1 = df.groupby("payer segment", as_index=False)["Patient Count"].sum()
df1.columns = ["payer segment", "Total Patient Count"]
df = df.merge(df1, on="payer segment")
df["Market Share"] = round(df["Patient Count"] / df["Total Patient Count"]*100, 2)

c1,c2 = st.columns(2)
with c1:
    row = st.container(horizontal=False, border=True,height=500)
    with row:
        st.metric(label="Patient Count by Payer Segment and Line of Therapy", value="",help=ttp[ttp["Metric"] == 5]["Info"][4])
        bar_chart(df,"payer segment","Market Share",
                  "Line of therapy","Payer Segment",
                  "Market Share (%)","LOT",COLOR_MAPS["lot"],"Patient Count",44)
       


# --------------------------------------------------------------------------------------------------


# 3rd Chart - Payer Segment - LOT  -------------------------------------------------

if time_period == "CR3M":
    q = df_filter[df_filter["Time Period"].isin(["M1", "M2", "M3"])]
else:
    q = df_filter[df_filter["Time Period"].isin(["M1", "M2", "M3", "M4", "M5", "M6"])]


dq1 = q[q["drug name"] == main_brand]
dq2 = q[q["switch_from"] == main_brand] 

# ------- Drug ----------
df = dq1.groupby(["switch_from", "period start date"], as_index=False)["Patient Count"].sum()
df_total = df.groupby("period start date",as_index=False)["Patient Count"].sum()
df_total.columns = ["period start date","total patients"]
df = df.merge(df_total,on="period start date")

df["Market Share"] = round(df["Patient Count"]/df["total patients"]*100,2)
df["period start date"] = pd.to_datetime(df["period start date"])
df["Month_Year"] = df["period start date"].dt.strftime("%b'%y")
df = df.sort_values("period start date", ascending=True)

df1_drug = df

# ------- Class ----------

df = dq1.groupby(["switch_from_class", "period start date"], as_index=False)["Patient Count"].sum()
df_total = df.groupby("period start date",as_index=False)["Patient Count"].sum()
df_total.columns = ["period start date","total patients"]
df = df.merge(df_total,on="period start date")

df["Market Share"] = round(df["Patient Count"]/df["total patients"]*100,2)
df["period start date"] = pd.to_datetime(df["period start date"])
df["Month_Year"] = df["period start date"].dt.strftime("%b'%y")
df = df.sort_values("period start date", ascending=True)
df1_class = df
# ------- Drug ----------

df2 = dq2.groupby(["drug name","period start date"], as_index=False)["Patient Count"].sum()

df_total = df2.groupby("period start date",as_index=False)["Patient Count"].sum()
df_total.columns = ["period start date","total patients"]
df2 = df2.merge(df_total,on="period start date")
df2["Market Share"] = round(df2["Patient Count"]/df2["total patients"]*100,2)
df2["period start date"] = pd.to_datetime(df2["period start date"])
df2["Month_Year"] = df2["period start date"].dt.strftime("%b'%y")
df2 = df2.sort_values("period start date", ascending=True)
df2_drug = df2
# ------- Class ----------
df2 = dq2.groupby(["class","period start date"], as_index=False)["Patient Count"].sum()

df_total = df2.groupby("period start date",as_index=False)["Patient Count"].sum()
df_total.columns = ["period start date","total patients"]
df2 = df2.merge(df_total,on="period start date")
df2["Market Share"] = round(df2["Patient Count"]/df2["total patients"]*100,2)
df2["period start date"] = pd.to_datetime(df2["period start date"])
df2["Month_Year"] = df2["period start date"].dt.strftime("%b'%y")
df2 = df2.sort_values("period start date", ascending=True)
df2_class = df2



with c2:
    row = st.container(horizontal=False, border=True,height=500)

    with row:
        c1,c2 = st.columns([3,7])
        with c2:
            with st.expander("Show Filters"):
                
                
                q = st.selectbox("Switch To/From",("Switch To","Switch From"))
                brand_class_switch = st.selectbox("Brand/Class",("Brand","Class"))


                if q == "Switch To" and brand_class_switch == "Brand":
                    p ="Switch To Cosentyx"
                    df_chart = df1_drug
                    col = "switch_from"
                    col_rename = "Switch From"

                elif q == "Switch From" and brand_class_switch == "Brand":
                    p = "Switch From Cosentyx" 
                    df_chart = df2_drug
                    col = "drug name"
                    col_rename = "Switch To"

                elif q == "Switch To" and brand_class_switch == "Class":
                    p ="Switch To Cosentyx"
                    df_chart = df1_class
                    col = "switch_from_class"
                    col_rename = "Switch From"

                elif q == "Switch From" and brand_class_switch == "Class":
                    p = "Switch From Cosentyx" 
                    df_chart = df2_class
                    col = "class"
                    col_rename = "Switch To"


              
                
                

                if brand_class_switch == "Brand" and q == "Switch To":
                    list_ = df_chart["switch_from"].unique().tolist()
                elif brand_class_switch == "Brand" and q == "Switch From":
                    list_ = df_chart["drug name"].unique().tolist()
                elif brand_class_switch == "Class" and q == "Switch To":
                    list_ = df_chart["switch_from_class"].unique().tolist()
                elif brand_class_switch == "Class" and q == "Switch From":
                    list_ = df_chart["class"].unique().tolist()

                
                channel = st.multiselect(
                        brand_class_switch,
                        list_,
                        default=list_
                    )
                
                

        with c1:      
            st.metric(label=p, value="",help=ttp[ttp["Metric"] == 6]["Info"][5])

        
        # chart(df1,x_x,y_y,colour,x_rename,y_rename,color_name,key)
        
        
        bar_chart(df_chart,"Month_Year","Market Share",col,"Months","Market Share (%)",col_rename,COLOR_MAPS["brands"],"Patient Count",1)


# __---___---___-__-___--__HCP/HCO------_______-______------__----


row = st.container(horizontal=False, border=True)
with row:
    if time_period == "CR3M":
        df = df_filter[df_filter["Time Period"].isin(["M1", "M2", "M3"])]
    else:
        df = df_filter[df_filter["Time Period"].isin(["M1", "M2", "M3", "M4", "M5", "M6"])]

    df_cos = df[df["drug name"] == main_brand]
    c1,c2 = st.columns([1,9])
    with c1:
        hcp_hco = st.selectbox("HCP/HCO",("HCP","HCO"))
    df_chart,df_chart2,type,col,df_table,filters = hcpHco(df_cos,hcp_hco,df)

    pp = type.split(" ")[0]


    c1,c2 = st.columns(2)
    with c1:
        row = st.container(horizontal=False, border=True,height=500)
        with row:
            st.metric(label=f"{main_brand} {pp} Patient Distribution", value="",help=ttp[ttp["Metric"] == 7]["Info"][6])
            bar_chart(df_chart,"Month_Year","Market Share",type,"Months","#Patients",type,COLOR_MAPS[col],"Patient Count",55)
    with c2:
        row = st.container(horizontal=False, border=True,height=500)
        with row:
            st.metric(label=f"{main_brand} {pp} Patient Share", value="",help=ttp[ttp["Metric"] == 8]["Info"][7])
            line_chart(df_chart2,"Month_Year","Market Share",type,"Months","Market Share (%)",type,COLOR_MAPS[col],555)

 
    st.metric(label="Summary Tab", value="",help=ttp[ttp["Metric"] == 9]["Info"][8])
    with st.expander("Show Table Filters"):
        for x in filters:
            q=  main[x].unique().tolist()
            d = st.multiselect(
                x,
                q,
                default=q
            )
    df_table
            
