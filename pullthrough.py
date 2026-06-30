import streamlit as st
import pandas as pd
from functions import format_number, hcpHco
from charts import bar_chart,line_chart,bar_bar,normal_bar_chart
import plotly.express as px

import json
# def demandGeo
with open("colors.json") as f:

    COLOR_MAPS = json.load(f)


ttp = pd.read_excel("tooltip info.xlsx")
ttp = ttp[ttp["Tab"]=="pt"].reset_index()


st.title("Healthcare Dashboard")
st.subheader("Pull Through")

st.set_page_config(
    page_title="Pullthrogh Dashboard",
    layout="wide"
)

main = pd.read_csv("PT modified.csv")
main_brand = "Cosentyx"

channel_list =  main["Channel"].unique().tolist()
payer_list =  main["Payer Segment"].unique().tolist()

payers =  main["Payer Name"].unique().tolist()
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

    payer_names = st.multiselect(
        "Payers",
        payers,
        default=payers
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


df_filter = main[(main["Channel"].isin(channel))
              & (main["Payer Segment"].isin(payer))
              & (main[geo_level].isin(geo))
              & (main["Payer Name"].isin(payer_names))]



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
    row1 = st.container(horizontal=False,border=True)
    with row1:
        met = df["claims count"].sum()
        paid = df["paid claims count"].sum()
        reverse = df["reverse claim count"].sum()
        rejected = df["rejected claim count"].sum()

        st.metric(label="Submission Approval - Claims",
                value=format_number(paid+reverse),
                
                help=ttp[ttp["Metric"] == 1]["Info"][0])
        
        
        r = round((paid+reverse)/met*100,2)
        st.metric(label="Submission Approval - Rate",
                value=f"{r}%",
                
                help=ttp[ttp["Metric"] == 1]["Info"][0])
    
    row1 = st.container(horizontal=False,border=True)
    with row1:
        r = round((paid)/met*100,2)
        st.metric(label="Submission Paid Claim Rate",
                value=f"{r}%",
                
                help=ttp[ttp["Metric"] == 2]["Info"][1])
        

        r = round((reverse)/met*100,2)
        st.metric(label="Submission Reverse Claim Rate",
                value=f"{r}%",
                
                help=ttp[ttp["Metric"] == 2]["Info"][1])
        
    row1 = st.container(horizontal=False,border=True)
    with row1:
        r = rejected
        st.metric(label="Submission Denial - Claims",
                value=f"{format_number(r)}",
                
                help=ttp[ttp["Metric"] == 3]["Info"][2])
        

        r = round((rejected)/met*100,2)
        st.metric(label="Submission Denial - Rate",
                value=f"{r}%",
                
                help=ttp[ttp["Metric"] == 3]["Info"][2])
        
df = cos_df
df = df.groupby(["Payer Segment"]).agg({"claims count":"sum",
                                        "paid claims count":"sum",
                                        "reverse claim count":"sum",
                                        "rejected claim count":"sum"}).reset_index()
df["Approved claims"] = df["paid claims count"]+df["reverse claim count"]
df = df.sort_values("claims count",ascending = False)

row = st.container(horizontal = True)

with row:
    row1 = st.container(border=True,height=600)
    with row1:
        st.metric("Claims by Payer Segment","",help=ttp[ttp["Metric"] == 4]["Info"][3])
        selected = st.selectbox("Claims Type",("Approved Claims",
                                            "Paid Claims",
                                            "Reverse Claims",
                                            "Rejected Claims"))
        
        if selected == "Approved Claims":
            d = list(df["Approved claims"])
        elif selected == "Paid Claims":
            d = list(df["paid claims count"])
        elif selected == "Reverse Claims":
            d = list(df["reverse claim count"])
        else:
            d = list(df["rejected claim count"])

        x = list(df["Payer Segment"])
        total = list(df["claims count"])


        bar_bar(x,d,total,selected,43)
    row1 = st.container(border=True,height=600)
    with row1:
        df = cos_df
        st.metric("Claims/Patients by Payer Segment","",help=ttp[ttp["Metric"] == 5]["Info"][4])
        df = df.groupby(["Line of therapy","Payer Segment"])[["Patient Count","claims count"]].sum().reset_index()
        selected = st.selectbox("Claims/Patients",("Claims","Patients"))
        
        if selected == "Claims":
            normal_bar_chart(df,"Payer Segment","claims count","Line of therapy",
                  "Payer Segment","# Claims","Line of therapy",COLOR_MAPS["lot"],99)
        else:
            normal_bar_chart(df,"Payer Segment","Patient Count","Line of therapy",
                  "Payer Segment","# Patients","Line of therapy",COLOR_MAPS["lot"],99)
            




if time_period == "CR3M":
    df1 = df_filter[df_filter["Time Period"].isin(["M1", "M2", "M3"])]
else:
    df1 = df_filter[df_filter["Time Period"].isin(["M1", "M2", "M3", "M4", "M5", "M6"])]



brands =  df1["drug name"].unique().tolist()
row = st.container(border=True)
with row:
    cl = st.expander("Show Filters")
    with cl:
        brand = st.multiselect(
                "Brand",
                brands,
                default=brands
                )
    
    df1 = df1[(df1["drug name"].isin(brand))]


    row = st.container(horizontal = True)
    with row:
        row1 = st.container(border=True,height=600)
        with row1:
            st.metric("Claims by Payer Segment","",help=ttp[ttp["Metric"] == 6]["Info"][5])
            selected = st.selectbox("Claims Type",("Approved Claims",
                                                "Paid Claims",
                                                "Reverse Claims",
                                                "Rejected Claims"),key=4)
            df = df1
            df["Approved claims"] = df["paid claims count"]+df["reverse claim count"]
            
            if selected == "Approved Claims":
                d = "Approved claims"
            elif selected == "Paid Claims":
                d = "paid claims count"
            elif selected == "Reverse Claims":
                d = "reverse claim count"
            else:
                d = "rejected claim count"
            

            df = df.groupby(["drug name","period start date"])[["claims count",d]].sum().reset_index()
            dd = f"{d} Rate"
            df[dd] = round(df[d]/df["claims count"]*100)
            df["period start date"] = pd.to_datetime(df["period start date"])
            df["Month_Year"] = df["period start date"].dt.strftime("%b'%y")
            line_chart(df,"Month_Year",dd,"drug name",
                    "Months",selected,"Brand",COLOR_MAPS["brands"],88)
        row1 = st.container(border=True,height=600)
        with row1:
            st.metric("Claims/Patients by Payer Segment","",help=ttp[ttp["Metric"] == 7]["Info"][6])
            df = df1
            df = df.groupby(["reject reason","period start date"])["reverse claim count"].sum().reset_index()
            df_total = df.groupby(["period start date"])[["reverse claim count"]].sum().reset_index()
            df_total.columns = ["period start date","total"]
            df = df.merge(df_total,on="period start date")
            df["market share"] = round(df["reverse claim count"]/df["total"]*100,2)
            df["period start date"] = pd.to_datetime(df["period start date"])
            df["Month_Year"] = df["period start date"].dt.strftime("%b'%y")

            selected = st.selectbox("Claims Type",("Share",
                                                "Rejected Claims"),key=5)
            print(df["reject reason"])
            
            if selected == "Share":
                bar_chart(df,"Month_Year","market share","reject reason",
                        "Months","Market Share (%)","Denial Reason",COLOR_MAPS["rejectReasons"],"reverse claim count",51)
            else:
                normal_bar_chart(df,"Month_Year","reverse claim count","reject reason",
                        "Months","Rejected Claims","Denial Reason",COLOR_MAPS["rejectReasons"],51)








    def format_k(value):
        if pd.isna(value):
            return ""
        if value >= 1000:
            return f"{value / 1000:.2f}K"
        return f"{value:,.0f}"


    def format_percent(value):
        if pd.isna(value):
            return ""
        return f"{value:.1f}%"


    st.metric(label=f"Summary Tab - {time_period1}",value="",help=ttp[ttp["Metric"] == 8]["Info"][7])

    table_df = df1.copy()
    table_df["Approved claims"] = (
        table_df["paid claims count"] + table_df["reverse claim count"]
    )

    base_columns = ["Payer Name", "Payer Segment", "Channel"]

    summary_table = (
        table_df.groupby(base_columns, as_index=False)[["claims count", "Patient Count"]]
        .sum()
        .rename(
            columns={
                "Payer Name": "Payer",
                "claims count": "# Claims",
                "Patient Count": "# Patients",
            }
        )
    )

    brand_table = (
        table_df.groupby(base_columns + ["drug name"], as_index=False)[
            ["claims count", "Patient Count", "Approved claims", "rejected claim count"]
        ]
        .sum()
    )
    brand_table["Approval Rate"] = (
        brand_table["Approved claims"] / brand_table["claims count"] * 100
    )
    brand_table["Denial Rate"] = (
        brand_table["rejected claim count"] / brand_table["claims count"] * 100
    )

    brand_table = brand_table.rename(
        columns={
            "Payer Name": "Payer",
            "drug name": "Drug Name",
            "Patient Count": "# Patients",
        }
    )

    brand_pivot = brand_table.pivot_table(
        index=["Payer", "Payer Segment", "Channel"],
        columns="Drug Name",
        values=["# Patients", "Approval Rate", "Denial Rate"],
        aggfunc="sum",
    )
    brand_pivot = brand_pivot.swaplevel(0, 1, axis=1).sort_index(axis=1, level=0)
    brand_pivot = brand_pivot.reindex(
        ["# Patients", "Approval Rate", "Denial Rate"],
        axis=1,
        level=1,
    )

    summary_table = summary_table.set_index(["Payer", "Payer Segment", "Channel"])
    display_table = pd.concat([summary_table, brand_pivot], axis=1).reset_index()
    display_table = display_table.sort_values("# Patients", ascending=False)

    display_table.columns = pd.MultiIndex.from_tuples(
        [
            column if isinstance(column, tuple) else ("", column)
            for column in display_table.columns
        ]
    )

    formatters = {
        ("", "# Claims"): format_k,
        ("", "# Patients"): format_k,
    }

    for column in display_table.columns:
        if isinstance(column, tuple) and column[0]:
            if column[1] == "# Patients":
                formatters[column] = lambda value: "" if pd.isna(value) else f"{value:,.0f}"
            elif column[1] in ["Approval Rate", "Denial Rate"]:
                formatters[column] = format_percent

    st.dataframe(
        display_table.style.format(formatters),
        use_container_width=True,
        hide_index=True,
    )
