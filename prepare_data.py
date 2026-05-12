"""
데이터 전처리 및 SQLite DB 구축 스크립트
실행: python prepare_data.py
"""

import pandas as pd
import sqlite3
import os

DB_PATH = "manufacturing.db"

def build_db():
    # ── 1. 광공업생산지수 ─────────────────────────────────────────────────────
    df1 = pd.read_csv(
        "data/시도_산업별_광공업생산지수.csv",
        encoding="cp949",
        header=0
    )
    df1 = df1.iloc[1:].reset_index(drop=True)  # 단위행 제거
    id_cols = ["시도별", "산업별"]
    value_cols = [c for c in df1.columns if c not in id_cols]
    df1_long = df1.melt(id_vars=id_cols, value_vars=value_cols,
                         var_name="연월", value_name="생산지수")
    df1_long["연월"] = df1_long["연월"].str.replace(" p)", "", regex=False).str.strip()
    df1_long["생산지수"] = pd.to_numeric(df1_long["생산지수"], errors="coerce")
    df1_long = df1_long.dropna(subset=["생산지수"])
    df1_long.rename(columns={"시도별": "지역", "산업별": "산업"}, inplace=True)

    # ── 2. 취업자 ────────────────────────────────────────────────────────────
    df2 = pd.read_csv(
        "data/시도_산업별_취업자.csv",
        encoding="cp949",
        header=0
    )
    df2 = df2.iloc[1:].reset_index(drop=True)
    id_cols2 = ["행정구역별", "산업별"]
    value_cols2 = [c for c in df2.columns if c not in id_cols2]
    df2_long = df2.melt(id_vars=id_cols2, value_vars=value_cols2,
                         var_name="반기", value_name="취업자수")
    df2_long["취업자수"] = pd.to_numeric(df2_long["취업자수"], errors="coerce")
    df2_long = df2_long.dropna(subset=["취업자수"])
    df2_long.rename(columns={"행정구역별": "지역", "산업별": "산업"}, inplace=True)

    # ── 3. 수출입 무역통계 ───────────────────────────────────────────────────
    df3 = pd.read_excel(
        "data/품목_수출입_총괄.xls",
        engine="xlrd"
    )
    df3_clean = df3.iloc[3:].copy()
    df3_clean.columns = ["순번", "코드", "품목명", "수출액", "수출평균증감률",
                          "수출중량", "수입액", "수입평균증감률", "수입중량", "수지"]
    df3_clean = df3_clean[df3_clean["코드"].notna()].copy()
    df3_clean["품목명"] = df3_clean["품목명"].str.replace(r"\s+", " ", regex=True).str.strip()
    for col in ["수출액", "수입액", "수지", "수출평균증감률", "수입평균증감률"]:
        df3_clean[col] = pd.to_numeric(df3_clean[col], errors="coerce")
    df3_clean = df3_clean[df3_clean["순번"].notna()].dropna(subset=["수출액"])

    # ── DB 저장 ──────────────────────────────────────────────────────────────
    conn = sqlite3.connect(DB_PATH)
    df1_long.to_sql("production_index", conn, if_exists="replace", index=False)
    df2_long.to_sql("employment", conn, if_exists="replace", index=False)
    df3_clean.to_sql("trade", conn, if_exists="replace", index=False)
    conn.close()

    print(f"DB 구축 완료: {DB_PATH}")
    print(f"  - production_index: {len(df1_long)}행")
    print(f"  - employment:       {len(df2_long)}행")
    print(f"  - trade:            {len(df3_clean)}행")

if __name__ == "__main__":
    build_db()
