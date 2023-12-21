import streamlit as st
import pandas as pd
import networkx as nx

# import xlsxwriter


from streamlit.logger import get_logger
from draw_net import draw_net

LOGGER = get_logger(__name__)


color_discrete_map = {
    "pink": "pink",
    "darksalmon": "darksalmon",
}


def run():
    st.set_page_config(page_title="Hello", page_icon=":smiley:", layout="wide")

    st.sidebar.write("分析対象ファイルをアップロードしてください。")
    # st.sidebar.warning("アップロードファイルはサーバには保存されないので注意")

    # ファイルアップロードウィジェット
    uploaded_file = st.sidebar.file_uploader("ファイルを選択", type=["csv", "xlsx"])

    df = pd.DataFrame()

    # ファイルがアップロードされたら、その内容を読み込む
    if uploaded_file is not None:
        # ファイルの拡張子によって読み込み方法を分岐
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, encoding="cp932")
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)

    tab1, tab2 = st.tabs(["データ処理", "描画"])
    with tab1:
        with st.expander("読み込んだデータ(一部)"):
            # データフレームを表示
            st.dataframe(df.head(10))

        sep_list = [",", "|"]
        with st.expander("出願人列と分類列指定", expanded=True):
            all_col = df.columns.tolist()
            applicant_col = st.selectbox("出願人の列を選択", all_col)
            sep1 = st.selectbox("共同出願人の場合の区切り", sep_list)

            clas_col = st.selectbox("特許分類の列を選択", all_col)
            sep2 = st.selectbox("複数の特許分類の区切り", sep_list)

        left_df = df[applicant_col].str.split(sep1, expand=True).stack().reset_index()
        right_df = df[clas_col].str.split(sep2, expand=True).stack().reset_index()

        # 同じindex同士合体
        decomp_df = pd.merge(left_df, right_df, on="level_0")
        decomp_df = decomp_df[["0_x", "0_y"]].rename(
            columns={"0_x": applicant_col, "0_y": clas_col}
        )

        with st.expander("出願人列と分類列を分解", expanded=True):
            agg_df = decomp_df.groupby(
                [applicant_col, clas_col], as_index=False, dropna=False
            ).size()
            st.dataframe(agg_df.sort_values(by="size", ascending=False))

    with tab2:
        st.write("ネットワーク図")
        init_appl_list = df[applicant_col].value_counts().index.tolist()

        # 描画パラメータ
        with st.expander("描画パラメータ"):
            draw_param_col1, draw_param_col2, draw_param_col3 = st.columns(3)
            with draw_param_col1:
                NODE_SIZE = st.slider("円の大きさ", 5, 100, 10)
                EDGE_WIDTH = st.slider("線の太さ", 0.1, 5.0, 0.2)
            with draw_param_col2:
                k = st.slider("ばね定数", 0.01, 3.0, 0.15)
                scale = 1000  # st.slider("スケール", 1, 1000, 500)
                edge_size_range = st.slider("共起回数：閾値以上に限定", 1, 100, 2)

            with draw_param_col3:
                label_flag = False  # st.checkbox("ラベル表示")
                select_list_range = st.slider(
                    "出願人指定(出願件数順)", 1, len(init_appl_list), (1, 10)
                )

            select_appl_list = init_appl_list[
                select_list_range[0] : select_list_range[1]
            ]

        agg_df2 = agg_df[agg_df[applicant_col].isin(select_appl_list)][
            agg_df["size"] >= edge_size_range
        ]
        applicant_label_list = agg_df2["出願人・権利者名"].tolist()
        clas_label_list = agg_df2["IPC"].tolist()

        G = nx.from_pandas_edgelist(agg_df2, target=applicant_col, source=clas_col)

        fig = draw_net(
            G, applicant_label_list, NODE_SIZE, EDGE_WIDTH, k, scale, label_flag
        )

        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    run()
