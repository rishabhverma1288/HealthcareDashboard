import pandas as pd
import plotly.express as px
import streamlit as st


def format_number(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return f"{num:,.0f}"
    


# with mid4:
#     st.metric(label="Source of Business",value="")
#     pie_df = (
#         df.groupby("Source_of_business", as_index=False)
#         ["Patient Count"].sum()
#     )
#     fig = px.pie(
#         pie_df,
#         values="Patient Count",
#         names="Source_of_business",
#     )
#     fig.update_layout(
#     margin=dict(t=0, b=0, l=0, r=0),
#     height=250
#     )

#     st.plotly_chart(fig, use_container_width=True,

#     config={"displayModeBar": False})




def hcpHco(df,cat,df_all):
    if cat =="HCP":
        dq = df.groupby(["HCP Segment","period start date"],as_index=False)["Patient Count"].sum()
        r = "HCP Segment"
        col = "hcp"
        df_table = df.groupby(
            ["HCP Name", "HCP Segment", "HCO Name", "New Prescriber Flag"],
            as_index=False
        ).agg({
            "claims count": "sum",
            "Patient Count": "sum",
            
        })
        df_table.columns = ["HCP Name", "HCP Segment", "HCO Name", "New Prescriber Flag","# Claims","# Patients"]
        df_table = df_table.sort_values("# Claims",ascending=False)
        filters = ["HCP Name", "HCP Segment", "HCO Name", "New Prescriber Flag"]

    else:
        dq = df.groupby(["HCO Segment","period start date"],as_index=False)["Patient Count"].sum()
        r = "HCO Segment"
        col = "hco"
        df_table = df.groupby(
            ["HCO Name", "HCO Segment",  "New Prescriber Flag"],
            as_index=False
        ).agg({
            "claims count": "sum",
            "Patient Count": "sum",
            
        })
        
        df_table.columns = ["HCO Name", "HCO Segment",  "New Prescriber Flag","# Claims","# Patients"]
        df_table = df_table.sort_values("# Claims",ascending=False)
        filters = ["HCO Name", "HCO Segment",  "New Prescriber Flag"]
    
    dq_total = dq.groupby(["period start date"],as_index=False)["Patient Count"].sum()
    dq_total.columns = ["period start date","total patients"]
    dq2 = dq
    dq = dq.merge(dq_total,on="period start date")
    dq["Market Share"] = round(dq["Patient Count"]/dq["total patients"]*100,2)
    dq["period start date"] = pd.to_datetime(dq["period start date"])
    dq["Month_Year"] = dq["period start date"].dt.strftime("%b'%y")
    dq = dq.sort_values("period start date", ascending=True)


    
    dq_total = df_all.groupby(["period start date"],as_index=False)["Patient Count"].sum()
    dq_total.columns = ["period start date","total patients"]
    dq2 = dq2.merge(dq_total,on="period start date")
    dq2["Market Share"] = round(dq2["Patient Count"]/dq2["total patients"]*100,2)
    dq2["period start date"] = pd.to_datetime(dq2["period start date"])
    dq2["Month_Year"] = dq2["period start date"].dt.strftime("%b'%y")
    dq2 = dq2.sort_values("period start date", ascending=True)

    return dq,dq2,r,col,df_table,filters

def patient_type(line_of_therapy, source_of_business):
    if line_of_therapy == "1L" and source_of_business == "New":
        return "1L New Patients"
    elif line_of_therapy == "1L" and source_of_business != "New":
        return "1L Continue Patients"
    elif line_of_therapy != "1L" and source_of_business == "New":
        return "2L+ New Patients"
    else:
        return "2L+ Continue Patients"