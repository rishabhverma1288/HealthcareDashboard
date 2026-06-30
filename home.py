
import streamlit as st

pages = {
    "Executive": [
        st.Page("executive.py", title="Executive View"),
    ],
    "Demand": [
        st.Page("demandGeo.py", title="Geography View"),
        st.Page("demandNat.py", title="National View"),
    ],
    "Pull Through": [
        st.Page("pullthrough.py", title="Pull Through View"),
    ]
}

pg = st.navigation(pages)
pg.run()