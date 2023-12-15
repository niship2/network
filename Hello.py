# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import pandas as pd
#import xlsxwriter


from streamlit.logger import get_logger

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
        
    )

    st.title("競合・競合先探索アプリ！")
    st.write("サイドバーから分析対象ファイルをアップロードしてください。")


    # ファイルアップロードウィジェット
    uploaded_file = st.sidebar.file_uploader("ファイルを選択", type=["csv", "xlsx"])

    # ファイルがアップロードされたら、その内容を読み込む
    if uploaded_file is not None:
        # ファイルの拡張子によって読み込み方法を分岐
        if uploaded_file.name.endswith(".csv"):
          df = pd.read_csv(uploaded_file,encoding="cp932")
        elif uploaded_file.name.endswith(".xlsx"):
          df = pd.read_excel(uploaded_file)
      
    if df is not None:
        with st.expander("読み込んだデータ"):
        # データフレームを表示
            st.dataframe(df)            
            
    sep_list = [",","|"]
    with st.sidebar.form("my_form"):
        all_col = df.columns.tolist()
        applicant_col = st.selectbox("出願人の列を選択",all_col)
        sep1 = st.selectbox("共同出願人の場合の区切り",sep_list)

        #all_col.remove(applicant_col)

        clas_col = st.selectbox("特許分類の列を選択",all_col)
        sep2 = st.selectbox("複数の特許分類の区切り",sep_list)


        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")

    if submitted:
        left_df = df[applicant_col].str.split(sep1,expand=True).stack().reset_index()
        right_df = df[clas_col].str.split(sep2,expand=True).stack().reset_index()

        #同じindex同士合体
        decomp_df = pd.merge(left_df,right_df,on="level_0")
        decomp_df = decomp_df[["0_x","0_y"]].rename(columns={"0_x":applicant_col,"0_y":clas_col})
            

        with st.expander("出願人列と分類列を分解"):
            agg_df = decomp_df.groupby([applicant_col,clas_col],as_index=False,dropna=False).size()
            st.dataframe(agg_df.sort_values(by="size",ascending=False))


if __name__ == "__main__":
    run()
