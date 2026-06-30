import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.express as px
import streamlit as st
import textwrap


def apply_axis_format(fig):
    fig.update_layout(template="simple_white")
    fig.update_xaxes(
        showline=True,
        linecolor="black",
        linewidth=1,
        mirror=False,
        showgrid=False,
        zeroline=False,
    )
    fig.update_yaxes(
        showline=True,
        linecolor="black",
        linewidth=1,
        mirror=False,
        showgrid=False,
        zeroline=False,
    )


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
    hovertemplate = (
        f"<b>{x_title or x}</b>=%{{x}}<br>"
        f"<b>{y_title or y}</b>=%{{y}}"
    )
    if color:
        hovertemplate = f"<b>{color_title or color}</b>=%{{fullData.name}}<br>" + hovertemplate
    fig.update_traces(hovertemplate=hovertemplate + "<extra></extra>")

    fig.update_layout(
        xaxis_title=x_title or x,
        yaxis_title=y_title or y,
        uniformtext_minsize=11,
        uniformtext_mode="hide",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.32,
            xanchor="center",
            x=0.5,
            title="",
        ),
        margin=dict(l=60, r=30, t=30, b=120),
        height=400,
    )
    apply_axis_format(fig)

    if render:
        st.plotly_chart(
            fig,
            use_container_width=True,
            key=key,
        )

    return fig



def bar_chart(df1, x_x, y_y, colour, x_rename, y_rename, color_name,colouring,above_labels, key):

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
        textfont=dict(size=13, color="white"),
        hovertemplate=(
            f"<b>{color_name}</b>=%{{fullData.name}}<br>"
            f"<b>{x_rename}</b>=%{{x}}<br>"
            f"<b>{y_rename}</b>=%{{y:.1f}}%<extra></extra>"
        )
    )   

    # Total patients above each bar
    totals = (
        df1.groupby(x_x)[above_labels]
        .sum()
        .reset_index()
    )

    for _, row in totals.iterrows():

        total = row[above_labels]

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
        y=-0.3,
        xanchor="center",
        x=0.5,
        title=""
    ),
    margin=dict(l=30, r=30, t=20, b=110),
    height=400
    )
    apply_axis_format(fig)

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=key
    )



def line_chart(df,x_x,y_y,colour,x_rename,y_rename,col_rename,colouring,key):
    def format_percent(value):
        return f"{value:.1f}%"

    def add_endpoint_labels(fig):
        endpoint_candidates = {"start": [], "end": []}

        for trace in fig.data:
            points = [
                (x, y)
                for x, y in zip(trace.x, trace.y)
                if pd.notna(x) and pd.notna(y)
            ]

            if not points:
                continue

            start_x, start_y = points[0]
            end_x, end_y = points[-1]

            endpoint_candidates["start"].append(
                {
                    "x": start_x,
                    "y": start_y,
                    "text": format_percent(start_y),
                    "color": trace.line.color,
                    "xshift": -30,
                    "xanchor": "right",
                }
            )
            endpoint_candidates["end"].append(
                {
                    "x": end_x,
                    "y": end_y,
                    "text": format_percent(end_y),
                    "color": trace.line.color,
                    "xshift": 30,
                    "xanchor": "left",
                }
            )

        values = pd.to_numeric(df[y_y], errors="coerce").dropna()
        y_range = values.max() - values.min() if not values.empty else 0
        min_gap = max(y_range * 0.08, 0.6)

        for candidates in endpoint_candidates.values():
            shown_y_values = []

            for item in sorted(candidates, key=lambda label: label["y"]):
                if any(abs(item["y"] - shown_y) < min_gap for shown_y in shown_y_values):
                    continue

                shown_y_values.append(item["y"])
                fig.add_annotation(
                    x=item["x"],
                    y=item["y"],
                    text=item["text"],
                    showarrow=False,
                    xshift=item["xshift"],
                    xanchor=item["xanchor"],
                    yanchor="middle",
                    font=dict(
                        size=11,
                        color=item["color"],
                    ),
                )
    
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

        line=dict(width=3),

        hovertemplate=(
            f"<b>{col_rename}</b>=%{{fullData.name}}<br>"
            f"<b>{x_rename}</b>=%{{x}}<br>"
            f"<b>{y_rename}</b>=%{{y:.1f}}%<extra></extra>"
        )

    )
    add_endpoint_labels(fig)
    fig.update_layout(
        legend=dict(
            orientation="h",      # Horizontal legend
            yanchor="top",
            y=-0.28,              # Keep clear of x-axis title
            xanchor="center",
            x=0.5,
            title=""
        ),
        xaxis_title_standoff=8,
        margin=dict(l=30, r=30, t=0, b=95),
        height=400
    )
    apply_axis_format(fig)

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
        textfont=dict(size=13, color="white"),
        hovertemplate=(
            f"<b>{color_name}</b>=%{{fullData.name}}<br>"
            f"<b>{x_rename}</b>=%{{y}}<br>"
            f"<b>{y_rename}</b>=%{{x:.1f}}%<extra></extra>"
        )
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
            y=-0.3,
            xanchor="center",
            x=0.5,
            title=""
        ),
        margin=dict(l=80, r=40, t=20, b=110),
        height=400
    )
    apply_axis_format(fig)

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
    inner_labels = [f"{value/1000:.1f}K" for value in inner]

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
            text=inner_labels,
            textposition="outside",        # <-- Above blue bars
            textfont=dict(
                size=12,
                color="black"
            ),
            customdata=x_x,
            hovertemplate="%{customdata} - %{text}<extra></extra>",
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
            b=0
        )
    )
    apply_axis_format(fig)

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
    if df1.empty:
        st.info("No data available for the selected filters.")
        return

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
            size=12,
            color="white",
        ),
        hovertemplate=(
            f"<b>{color_name}</b>=%{{fullData.name}}<br>"
            f"<b>{x_rename}</b>=%{{x}}<br>"
            f"<b>{y_rename}</b>=%{{text}}<extra></extra>"
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
    label_gap = ymax * 0.06 if ymax else 1
    
    for _, row in totals.iterrows():
        total_label = format_k(row[y_y])
        fig.add_annotation(
            x=row[x_x],
            
            y=row[y_y] + label_gap,
            text=f"<b>{total_label}</b>",
            
            showarrow=False,
            font=dict(
                size=12,
                color="black",
            ),
        )

    # ----------------------------
    # Wrap long x-axis labels
    # ----------------------------
    wrapped = {
        x: "<br>".join(textwrap.wrap(str(x), width=16))
        for x in df1[x_x].unique()
    }

    fig.update_xaxes(
        tickvals=list(wrapped.keys()),
        ticktext=list(wrapped.values()),
        tickangle=0,
        categoryorder="array",
        categoryarray=[
            "Commercial",
            "Regional Health Plan",
            "PBM",
            "Medicaid Managed Care",
            "Government",
            "Medicare/Medicaid",
            "Integrated Delivery Network (IDN)",
        ],
    )

    # ----------------------------
    # Layout
    # ----------------------------
    fig.update_layout(
        autosize=True,
        height=400,
        uniformtext_minsize=11,
        uniformtext_mode="hide",
        xaxis_title=x_rename,
        yaxis_title=y_rename,
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.38,
            yanchor="top",
            title="",
        ),
        margin=dict(
            l=60,
            r=20,
            t=20,
            b=0,
        ),
    )
    fig.update_yaxes(range=[0, ymax + (label_gap * 2)])
    apply_axis_format(fig)

    # ----------------------------
    # Display
    # ----------------------------
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "responsive": True,
            "displayModeBar": False,
        },
        key=key,
    )




def normal_bar_chart_2(
    df1,
    x_x,
    y_y,
    x_rename,
    y_rename,
    color,
    key,
):
    df1 = df1.copy()
    if df1.empty:
        st.info("No data available for the selected filters.")
        return

    def format_number(value):
        if pd.isna(value):
            return ""
        return f"{value:,.0f}"

    df1["Label"] = df1[y_y].apply(format_number)

    fig = px.bar(
        df1,
        x=x_x,
        y=y_y,
        labels={
            x_x: x_rename,
            y_y: y_rename,
        },
    )

    fig.update_traces(
        marker_color=color,
        hovertemplate=(
            f"<b>{x_rename}</b>=%{{x}}<br>"
            f"<b>{y_rename}</b>=%{{y:,.0f}}<extra></extra>"
        ),
    )

    ymax = df1[y_y].max()
    label_gap = ymax * 0.06 if ymax else 1

    for _, row in df1.iterrows():
        fig.add_annotation(
            x=row[x_x],
            y=row[y_y] + label_gap,
            text=f"<b>{row['Label']}</b>",
            showarrow=False,
            font=dict(size=12, color="black"),
        )

    wrapped = {
        x: "<br>".join(textwrap.wrap(str(x), width=16))
        for x in df1[x_x].unique()
    }

    fig.update_xaxes(
        tickvals=list(wrapped.keys()),
        ticktext=list(wrapped.values()),
        tickangle=0,
    )

    fig.update_layout(
        autosize=True,
        height=400,
        uniformtext_minsize=11,
        uniformtext_mode="hide",
        xaxis_title=x_rename,
        yaxis_title=y_rename,
        showlegend=False,
        margin=dict(
            l=60,
            r=20,
            t=20,
            b=0,
        ),
    )
    fig.update_yaxes(range=[0, ymax + (label_gap * 2)])
    apply_axis_format(fig)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "responsive": True,
            "displayModeBar": False,
        },
        key=key,
    )
