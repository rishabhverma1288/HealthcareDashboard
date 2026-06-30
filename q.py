import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.express as px
import streamlit as st
import textwrap


def create_bar_chart(
    df,
    x,
    y,
    color=None,
    x_title=None,
    y_title=None,
    color_title=None,
    color_map=None,
    text=None,
    key=None,
    render=True,
):
    labels = {
        x: x_title or x,
        y: y_title or y,
    }

    if color:
        labels[color] = color_title or color

    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        text=text or y,
        labels=labels,
        color_discrete_map=color_map,
    )

    fig.update_traces(
        texttemplate="%{text}",
        textposition="outside",
        textfont=dict(size=12, color="black"),
        cliponaxis=False,
    )

    fig.update_layout(
        xaxis_title=x_title or x,
        yaxis_title=y_title or y,
        uniformtext_minsize=11,
        uniformtext_mode="hide",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            title="",
        ),
        margin=dict(l=60, r=30, t=30, b=80),
        height=400,
    )

    if render:
        st.plotly_chart(
            fig,
            use_container_width=True,
            key=key,
        )

    return fig



def bar_chart(df1, x_x, y_y, colour, x_rename, y_rename, color_name,colouring, key):

    fig = px.bar(
        df1,
        x=x_x,
        y=y_y,
        color=colour,
        text=y_y,
        labels={
            x_x: x_rename,
            y_y: y_rename,
            colour: color_name
        },
        color_discrete_map=colouring
    )

    # Percentage labels inside stacks
    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(size=13, color="white")
    )   

    # Total patients above each bar
    totals = (
        df1.groupby(x_x)["Patient Count"]
        .sum()
        .reset_index()
    )

    for _, row in totals.iterrows():

        total = row["Patient Count"]

        if total >= 1000:
            label = f"{total/1000:.1f}K"
        else:
            label = f"{total:,.0f}"

        fig.add_annotation(
            x=row[x_x],
            y=103,  # slightly above 100%
            text=f"{label}",
            showarrow=False,
            font=dict(size=13, color="black")
        )

    fig.update_layout(
    uniformtext_minsize=12,
    uniformtext_mode="hide",   # or False
    yaxis=dict(range=[0, 110]),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.15,
        xanchor="center",
        x=0.5,
        title=""
    ),
    margin=dict(l=80, r=40, t=20, b=0),
    height=400
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=key
    )



def line_chart(df,x_x,y_y,colour,x_rename,y_rename,col_rename,colouring,key):
    
    fig = px.line(
        df,
        x=x_x,
        y=y_y,
        color=colour,
        markers=True,
        labels={
                x_x:x_rename,
                y_y:y_rename,
                colour:col_rename
            },
        color_discrete_map=colouring
    )
    
       
    fig.update_traces(

        mode="lines",

        line=dict(width=3)

    )
    fig.update_layout(
        legend=dict(
            orientation="h",      # Horizontal legend
            yanchor="middle",
            y=-0.2,               # Move below chart
            xanchor="center",
            x=0.5,
            title=""
        ),
        margin=dict(l=80, r=60, t=0, b=0),
        height=400
    )

    # Remove horizontal gridlines
    # fig.update_yaxes(showgrid=False)

    # Optional: remove vertical gridlines too
    # fig.update_xaxes(showgrid=False)

    st.plotly_chart(
    fig,
    use_container_width=True,
    key=key
    )



def bar_chart_horizontal(df1, x_x, y_y, colour, x_rename, y_rename, color_name, colouring, key):

    fig = px.bar(
        df1,
        x=y_y,                # Numeric
        y=x_x,                # Category
        color=colour,
        orientation="h",      # <-- IMPORTANT
        text=y_y,
        labels={
            x_x: x_rename,
            y_y: y_rename,
            colour: color_name
        },
        color_discrete_map=colouring
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(size=13, color="white")
    )

    fig.update_layout(
        barmode="stack",
        xaxis=dict(
            range=[0, 100],
            title=y_rename
        ),
        yaxis=dict(
            title=x_rename
        ),
        uniformtext_minsize=12,
        uniformtext_mode="hide",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            title=""
        ),
        margin=dict(l=80, r=40, t=20, b=0),
        height=400
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=key
    )





import plotly.graph_objects as go
import textwrap
import plotly.graph_objects as go
import streamlit as st

def bar_bar(x_x, inner, outer, y_title, key):

    # Wrap x-axis labels (15 characters per line)
    wrapped_x = [
        "<br>".join(textwrap.wrap(str(label), width=15))
        for label in x_x
    ]

    fig = go.Figure()

    # Background bars
    fig.add_trace(
        go.Bar(
            x=wrapped_x,
            y=outer,
            marker_color="#b8aca6",
            width=0.55,
            hoverinfo="skip",
            showlegend=False
        )
    )

    # Foreground bars
    fig.add_trace(
        go.Bar(
            x=wrapped_x,
            y=inner,
            marker_color="#4b80b0",
            width=0.35,
            text=[f"{x/1000:.1f}K" for x in inner],
            textposition="outside",        # <-- Above blue bars
            textfont=dict(
                size=12,
                color="black"
            ),
            cliponaxis=False,              # Prevent label clipping
            showlegend=False
        )
    )

    # Labels on top of gray bars
    for x, y in zip(wrapped_x, outer):
        fig.add_annotation(
            x=x,
            y=y,
            text=f"<b>{y/1000:.1f}K</b>",
            showarrow=False,
            yshift=12,
            font=dict(size=12, color="black")
        )

    fig.update_layout(
        barmode="overlay",
        template="simple_white",
        height=400,

        yaxis_title=y_title,

        xaxis=dict(
            tickangle=0,          # Wrapped labels don't need rotation
            automargin=True
        ),

        yaxis=dict(
            automargin=True
        ),

        margin=dict(
            l=60,
            r=20,
            t=20,
            b=80
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=key
    )




def normal_bar_chart(
    df1,
    x_x,
    y_y,
    colour,
    x_rename,
    y_rename,
    color_name,
    colouring,
    key,
):

    df1 = df1.copy()

    # ----------------------------
    # Format numbers
    # ----------------------------
    def format_k(x):
        if x >= 1_000_000:
            return f"{x/1_000_000:.1f}M"
        elif x >= 1000:
            return f"{x/1000:.1f}K"
        return f"{x:.0f}"

    # Labels inside bars
    df1["Label"] = df1[y_y].apply(format_k)

    fig = px.bar(
        df1,
        x=x_x,
        y=y_y,
        color=colour,
        text="Label",
        labels={
            x_x: x_rename,
            y_y: y_rename,
            colour: color_name,
        },
        color_discrete_map=colouring,
    )

    # ----------------------------
    # Labels inside bars
    # ----------------------------
    fig.update_traces(
        texttemplate="%{text}",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(
            size=13,
            color="white",
        ),
    )

    # ----------------------------
    # Total label above each bar
    # ----------------------------
    totals = (
        df1.groupby(x_x, as_index=False)[y_y]
        .sum()
    )

    ymax = totals[y_y].max()

    for _, row in totals.iterrows():

        fig.add_annotation(
            x=row[x_x],
            y=row[y_y] + ymax * 0.02,
            text=format_k(row[y_y]),
            showarrow=False,
            font=dict(
                size=14,
                color="black",
            ),
        )

