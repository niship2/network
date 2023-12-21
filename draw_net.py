import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import networkx as nx


def set_shape(label, applicant_label_list):
    if label in applicant_label_list:
        return "square"
    else:
        return "circle"


def set_color(label, applicant_label_list):
    if label in applicant_label_list:
        return "pink"
    else:
        return "green"


def draw_net(
    G,
    applicant_label_list,
    NODE_SIZE=10,
    EDGE_WIDTH=0.2,
    k=0.15,
    scale=1000,
    label_flag=False,
):
    pos = nx.spring_layout(
        G,
        iterations=20,
        scale=scale,
        k=k,
        weight="size",
        seed=1,
    )

    draw_df = (
        pd.DataFrame.from_dict(pos, orient="index", columns=["x", "y"])
        .reset_index()
        .reset_index()
        .rename(columns={"level_0": "id", "index": "label"})
    )
    draw_df["shape"] = draw_df["label"].apply(
        lambda x: set_shape(x, applicant_label_list)
    )
    draw_df["color"] = draw_df["label"].apply(
        lambda x: set_color(x, applicant_label_list)
    )

    nodejson = draw_df.to_dict(orient="records")

    # G2でidとlabelを対応させる。
    G2 = nx.convert_node_labels_to_integers(
        G, first_label=0, ordering="default", label_attribute="nodelabel"
    )
    edge_x = []
    edge_y = []
    for edge in G2.edges():
        # print(nodejson[edge[0]]["x"])
        x0 = nodejson[edge[0]]["x"]
        y0 = nodejson[edge[0]]["y"]
        x1 = nodejson[edge[1]]["x"]
        y1 = nodejson[edge[1]]["y"]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    fig = go.Figure(
        data=[
            go.Scattergl(
                x=edge_x,
                y=edge_y,
                mode="lines",
                text=draw_df["label"].tolist(),
            ),
        ]
    )

    fig.add_scatter(
        x=draw_df["x"],
        y=draw_df["y"],
        mode="markers+text" if label_flag else "markers",
        text=draw_df["label"],
        hoverinfo="text",
    )

    fig.update_traces(
        line={"width": EDGE_WIDTH, "color": "grey"},
    )

    fig.update_traces(
        marker=dict(
            size=NODE_SIZE, symbol=draw_df["shape"], color=draw_df["color"], angle=0
        ),
        selector=dict(mode="markers"),
    )

    # fig.update_layout(dragmode='drawrect')
    fig.update_layout(xaxis=dict(showgrid=False, showticklabels=False))  # 軸のグリッドを表示
    fig.update_layout(yaxis=dict(showgrid=False, showticklabels=False))  # 軸のグリッドを表示
    fig.update_layout(title="出願人と分野のネットワーク図\n<sub>■は出願人、〇は分野</sub>")

    return fig
