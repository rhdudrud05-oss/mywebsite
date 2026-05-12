import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="한국 제조업 위기 대시보드",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main { background-color: #0f172a; }
    .stApp { background-color: #0f172a; }
    h1 { color: #f1f5f9 !important; }
    h2, h3 { color: #cbd5e1 !important; }
    .metric-card {
        background: linear-gradient(135deg, #1e293b, #334155);
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .sql-box {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 12px;
        font-family: monospace;
        font-size: 0.78rem;
        color: #f1f5f9;
        margin-top: 8px;
    }
    .insight-box {
        background: #1e293b;
        border-left: 4px solid #ef4444;
        border-radius: 6px;
        padding: 14px 18px;
        margin-top: 12px;
        color: #f1f5f9;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_conn():
    return sqlite3.connect("manufacturing.db", check_same_thread=False)

conn = get_conn()

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background: linear-gradient(90deg, #1e293b, #0f172a); border-bottom: 2px solid #ef4444;
            padding: 24px 0 16px; margin-bottom: 24px; border-radius: 8px; text-align: center;">
    <h1 style="font-size:2.2rem; margin:0; color:#f1f5f9;">🏭 한국 제조업 위기 대시보드</h1>
    <p style="color:#94a3b8; margin-top:8px; font-size:1rem;">
        광공업생산지수 · 제조업 취업자 · 수출입 무역통계 | 2020 – 2026
    </p>
</div>
""", unsafe_allow_html=True)

# ─── KPI Cards ────────────────────────────────────────────────────────────────
# ★ 하드코딩 날짜 대신 MAX/최신값 자동 탐색으로 변경 (IndexError 방지)
kpi1 = pd.read_sql("""
    SELECT 생산지수 FROM production_index
    WHERE 지역='전국' AND 산업='제조업'
    ORDER BY 연월 DESC LIMIT 1
""", conn).iloc[0, 0]

kpi_latest_month = pd.read_sql("""
    SELECT 연월 FROM production_index
    WHERE 지역='전국' AND 산업='제조업'
    ORDER BY 연월 DESC LIMIT 1
""", conn).iloc[0, 0]

kpi2 = pd.read_sql("""
    SELECT MAX(생산지수) FROM production_index
    WHERE 지역='전국' AND 산업='제조업'
""", conn).iloc[0, 0]

emp_latest = pd.read_sql("""
    SELECT 취업자수 FROM employment
    WHERE 지역='계'
    ORDER BY 반기 DESC LIMIT 1
""", conn).iloc[0, 0]

emp_latest_term = pd.read_sql("""
    SELECT 반기 FROM employment
    WHERE 지역='계'
    ORDER BY 반기 DESC LIMIT 1
""", conn).iloc[0, 0]

emp_peak = pd.read_sql("""
    SELECT MAX(취업자수) FROM employment WHERE 지역='계'
""", conn).iloc[0, 0]

trade_surplus = pd.read_sql("""
    SELECT SUM(수지)/1e9 as total FROM trade WHERE 수지 IS NOT NULL
""", conn).iloc[0, 0]

seoul_2020 = pd.read_sql("""
    SELECT AVG(생산지수) FROM production_index
    WHERE 지역='서울특별시' AND 산업='제조업' AND 연월 LIKE '2020%'
""", conn).iloc[0, 0]
seoul_2025 = pd.read_sql("""
    SELECT AVG(생산지수) FROM production_index
    WHERE 지역='서울특별시' AND 산업='제조업' AND 연월 LIKE '2025%'
""", conn).iloc[0, 0]

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div style="color:#94a3b8; font-size:0.8rem;">전국 제조업 생산지수 ({kpi_latest_month})</div>
        <div style="font-size:2rem; color:#f1f5f9; font-weight:800;">{kpi1:.1f}</div>
        <div style="color:#ef4444; font-size:0.8rem;">▼ 고점({kpi2:.1f}) 대비 하락</div>
    </div>""", unsafe_allow_html=True)
with c2:
    delta_emp = emp_latest - emp_peak
    st.markdown(f"""
    <div class="metric-card">
        <div style="color:#94a3b8; font-size:0.8rem;">제조업 취업자 ({emp_latest_term})</div>
        <div style="font-size:2rem; color:#f1f5f9; font-weight:800;">{emp_latest:,}천명</div>
        <div style="color:#ef4444; font-size:0.8rem;">▼ 고점 대비 {delta_emp:,}천명 감소</div>
    </div>""", unsafe_allow_html=True)
with c3:
    color = "#22c55e" if trade_surplus > 0 else "#ef4444"
    st.markdown(f"""
    <div class="metric-card">
        <div style="color:#94a3b8; font-size:0.8rem;">수출입 총 무역수지 (2021~2026)</div>
        <div style="font-size:2rem; color:{color}; font-weight:800;">{trade_surplus:.1f}B$</div>
        <div style="color:#94a3b8; font-size:0.8rem;">흑자 유지 중 (에너지 수입 부담)</div>
    </div>""", unsafe_allow_html=True)
with c4:
    seoul_chg = (seoul_2025 - seoul_2020) / seoul_2020 * 100
    st.markdown(f"""
    <div class="metric-card">
        <div style="color:#94a3b8; font-size:0.8rem;">서울 제조업 생산지수 변화</div>
        <div style="font-size:2rem; color:#ef4444; font-weight:800;">{seoul_chg:.1f}%</div>
        <div style="color:#ef4444; font-size:0.8rem;">2020 → 2025 평균 비교</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Chart 1 ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📈 차트 1: 전국 제조업 생산지수 추이 (2020–2026)</div>', unsafe_allow_html=True)

df_c1 = pd.read_sql("""
    SELECT 연월, 생산지수
    FROM production_index
    WHERE 지역='전국' AND 산업='제조업'
    ORDER BY 연월
""", conn)

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df_c1['연월'], y=df_c1['생산지수'],
    mode='lines+markers',
    line=dict(color='#3b82f6', width=2.5),
    marker=dict(size=4),
    name='생산지수',
    hovertemplate='%{x}<br>지수: %{y:.1f}<extra></extra>'
))
fig1.add_vrect(x0='2023.01', x1='2023.12',
    fillcolor='#ef4444', opacity=0.08, line_width=0,
    annotation_text='2023 생산 조정기', annotation_position='top left',
    annotation_font_color='#ef4444', annotation_font_size=11)
fig1.add_hline(y=df_c1['생산지수'].mean(), line_dash='dash',
               line_color='#f59e0b', opacity=0.6,
               annotation_text=f"평균 {df_c1['생산지수'].mean():.1f}",
               annotation_font_color='#f59e0b')
fig1.update_layout(
    paper_bgcolor='#1e293b', plot_bgcolor='#1e293b',
    font_color='#cbd5e1', height=360,
    xaxis=dict(showgrid=False, tickangle=-45,
               tickvals=[x for x in df_c1['연월'] if x.endswith('.01') or x.endswith('.07')]),
    yaxis=dict(showgrid=True, gridcolor='#334155', title='생산지수 (2020=100)'),
    margin=dict(l=50, r=20, t=20, b=80)
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("""
<div class="sql-box">
SELECT 연월, 생산지수 FROM production_index<br>
WHERE 지역='전국' AND 산업='제조업' ORDER BY 연월
</div>
<div class="insight-box">
💡 <b>인사이트:</b> 전국 제조업 생산지수는 2021년 말~2022년 초에 약 122까지 올라갔다. 그러나 2023년에 100~103으로 약 15% 떨어졌다. 이는 전 세계 반도체 수요가 급감하고, 코로나 이후 중국 경기가 기대만큼 살아나지 않은 게 주요 원인이었다. 2024년 말부터 빠르게 회복되어 2025년 하반기에는 고점을 넘어섰지만, 월별 등락이 여전히 커서 안정적인 회복이라고 보기는 어렵다. 회복이 특정 달에 집중되고 저점도 반복되는 패턴은 구조적 불안정이 아직 해소되지 않았음을 시사한다.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Chart 2 & 3 ──────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="section-title">🗺️ 차트 2: 지역별 제조업 생산지수 변화 (2020→2025 평균)</div>', unsafe_allow_html=True)
    df_c2 = pd.read_sql("""
        SELECT 지역,
          ROUND(AVG(CASE WHEN 연월 LIKE '2025%' THEN 생산지수 END), 1) as avg_2025,
          ROUND(AVG(CASE WHEN 연월 LIKE '2020%' THEN 생산지수 END), 1) as avg_2020
        FROM production_index
        WHERE 산업='제조업' AND 지역 != '전국'
        GROUP BY 지역
        ORDER BY avg_2025
    """, conn)
    df_c2['색상'] = df_c2['avg_2025'].apply(lambda x: '#22c55e' if x >= 115 else ('#f59e0b' if x >= 100 else '#ef4444'))

    fig2 = go.Figure(go.Bar(
        x=df_c2['avg_2025'], y=df_c2['지역'], orientation='h',
        marker_color=df_c2['색상'],
        text=df_c2['avg_2025'].astype(str), textposition='outside',
        hovertemplate='%{y}<br>2025 평균: %{x:.1f}<extra></extra>'
    ))
    fig2.add_vline(x=100, line_dash='dash', line_color='#f59e0b', opacity=0.8)
    fig2.update_layout(
        paper_bgcolor='#1e293b', plot_bgcolor='#1e293b',
        font_color='#cbd5e1', height=460,
        xaxis=dict(showgrid=True, gridcolor='#334155', title='생산지수 평균'),
        yaxis=dict(showgrid=False),
        margin=dict(l=80, r=60, t=10, b=40)
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("""
    <div class="sql-box">
    SELECT 지역, AVG(CASE WHEN 연월 LIKE '2025%' THEN 생산지수 END) as avg_2025<br>
    FROM production_index WHERE 산업='제조업' AND 지역 != '전국'<br>
    GROUP BY 지역 ORDER BY avg_2025
    </div>
    <div class="insight-box">
    💡 <b>인사이트:</b> 2025년을 기준으로 경기와 인천은 생산지수가 145가 넘는 반면, 서울은 유일하게 100 아래로 떨어졌다. 경기와 인천에는 반도체 및 디스플레이 공장이 집중되어 있는 반면, 서울은 공장이 거의 없는 서비스 중심 도시로 바뀌었기 때문이다. 같은 수도권이지만 제조하는 곳과 서비스를 제공하는 지역이 나뉘어진 형태라고 볼 수 있다.
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="section-title">👷 차트 3: 전국 제조업 취업자 수 추이 (반기별)</div>', unsafe_allow_html=True)
    df_c3 = pd.read_sql("""
        SELECT 반기, 취업자수 FROM employment
        WHERE 지역='계' ORDER BY 반기
    """, conn)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=df_c3['반기'], y=df_c3['취업자수'],
        marker_color=['#ef4444' if v < 4400 else '#3b82f6' for v in df_c3['취업자수']],
        text=df_c3['취업자수'].apply(lambda x: f'{x:,}'),
        textposition='outside',
        hovertemplate='%{x}<br>취업자: %{y:,}천명<extra></extra>'
    ))
    fig3.add_hline(y=4400, line_dash='dot', line_color='#f59e0b',
                   annotation_text='4,400천명 임계선', annotation_font_color='#f59e0b')
    fig3.update_layout(
        paper_bgcolor='#1e293b', plot_bgcolor='#1e293b',
        font_color='#cbd5e1', height=460,
        xaxis=dict(showgrid=False, tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor='#334155', title='취업자 수 (천명)', range=[4200, 4620]),
        margin=dict(l=60, r=20, t=10, b=80)
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("""
    <div class="sql-box">
    SELECT 반기, 취업자수 FROM employment<br>
    WHERE 지역='계' ORDER BY 반기
    </div>
    <div class="insight-box">
    💡 <b>인사이트:</b> 제조업 일자리는 2022년 하반기 약 4,525천 명을 정점으로 2025년 하반기에 4,364천 명까지 161천 명이 줄었다. 같은 기간에 생산지수는 어느 정도 회복되었지만 고용은 따라오지 못한 모습이다. 공장 자동화나 AI의 도입으로 사람 대신 기계가 그 자리를 채우면서, 경기가 좋아져도 일자리는 돌아오지 않는 구조가 됐다.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Chart 4 ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📦 차트 4: 주요 수출입 품목별 무역수지 (2021.03–2026.03 누계, 단위: 백만 달러)</div>', unsafe_allow_html=True)

df_c4 = pd.read_sql("""
    SELECT 품목명, 수출액/1e6 as 수출액_M, 수입액/1e6 as 수입액_M
    FROM trade ORDER BY 수출액 DESC LIMIT 12
""", conn)
df_c4['품목명_short'] = df_c4['품목명'].apply(lambda x: x[:15] + '…' if len(x) > 15 else x)

fig4 = go.Figure()
fig4.add_trace(go.Bar(name='수출액', x=df_c4['품목명_short'], y=df_c4['수출액_M'],
    marker_color='#3b82f6', opacity=0.85,
    hovertemplate='%{x}<br>수출: $%{y:,.0f}M<extra></extra>'))
fig4.add_trace(go.Bar(name='수입액', x=df_c4['품목명_short'], y=df_c4['수입액_M'],
    marker_color='#ef4444', opacity=0.85,
    hovertemplate='%{x}<br>수입: $%{y:,.0f}M<extra></extra>'))
fig4.update_layout(
    barmode='group', paper_bgcolor='#1e293b', plot_bgcolor='#1e293b',
    font_color='#cbd5e1', height=380, legend=dict(bgcolor='#334155'),
    xaxis=dict(showgrid=False, tickangle=-30),
    yaxis=dict(showgrid=True, gridcolor='#334155', title='금액 (백만 달러)'),
    margin=dict(l=60, r=20, t=10, b=120)
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("""
<div class="sql-box">
SELECT 품목명, 수출액/1e6, 수입액/1e6 FROM trade ORDER BY 수출액 DESC LIMIT 12
</div>
<div class="insight-box">
💡 <b>인사이트:</b> 수출은 반도체(전기기기), 자동차, 기계류 세 품목에 집중되어 있고, 수입은 원유, 가스와 같은 에너지가 가장 크다. 반도체 하나가 흔들리면 전체 무역수지도 같이 흔들리는 구조이며 실제로 2023년 반도체 불황 시기에 무역적자가 크게 확대되었다. 특정 품목 의존도가 높다는 것은 외부 충격에 그만큼 약하다는 뜻이다.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Chart 5 ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">⚖️ 차트 5: 품목별 무역수지 — 흑자 vs 적자 (단위: 백만 달러)</div>', unsafe_allow_html=True)

df_surplus = pd.read_sql("SELECT 품목명, 수지/1e6 as 수지_M FROM trade WHERE 수지 > 0 ORDER BY 수지 DESC LIMIT 8", conn)
df_surplus['품목명_short'] = df_surplus['품목명'].apply(lambda x: x[:12] + '…' if len(x) > 12 else x)
df_deficit = pd.read_sql("SELECT 품목명, 수지/1e6 as 수지_M FROM trade WHERE 수지 < 0 ORDER BY 수지 ASC LIMIT 8", conn)
df_deficit['품목명_short'] = df_deficit['품목명'].apply(lambda x: x[:12] + '…' if len(x) > 12 else x)

fig5 = make_subplots(rows=1, cols=2,
    subplot_titles=('🟢 무역수지 흑자 품목 Top 8', '🔴 무역수지 적자 품목 Top 8'))
fig5.add_trace(go.Bar(x=df_surplus['수지_M'], y=df_surplus['품목명_short'],
    orientation='h', marker_color='#22c55e',
    hovertemplate='%{y}<br>흑자: $%{x:,.0f}M<extra></extra>', showlegend=False), row=1, col=1)
fig5.add_trace(go.Bar(x=df_deficit['수지_M'], y=df_deficit['품목명_short'],
    orientation='h', marker_color='#ef4444',
    hovertemplate='%{y}<br>적자: $%{x:,.0f}M<extra></extra>', showlegend=False), row=1, col=2)
fig5.update_layout(
    paper_bgcolor='#1e293b', plot_bgcolor='#1e293b',
    font_color='#cbd5e1', height=360,
    margin=dict(l=20, r=20, t=40, b=20)
)
fig5.update_xaxes(showgrid=True, gridcolor='#334155')
fig5.update_yaxes(showgrid=False)
for ann in fig5['layout']['annotations']:
    ann['font'] = dict(color='#cbd5e1', size=12)
st.plotly_chart(fig5, use_container_width=True)

st.markdown("""
<div class="sql-box">
SELECT 품목명, 수지/1e6 FROM trade WHERE 수지 > 0 ORDER BY 수지 DESC LIMIT 8<br>
SELECT 품목명, 수지/1e6 FROM trade WHERE 수지 < 0 ORDER BY 수지 ASC LIMIT 8
</div>
<div class="insight-box">
💡 <b>인사이트:</b> 전기기기, 자동차, 선박에서 흑자를 내지만, 광물성연료(원유·가스 포함) 수입에서 압도적인 적자가 나고 있다. 제조업에서 아무리 흑자를 내도 에너지 가격이 오르면 금방 상쇄되는 구조로 2022년 러시아-우크라이나 전쟁 때에도 무역적자로 전환됐다. 에너지 자립 없이는 제조업 흑자도 언제든 위협을 받을 수 있다는 게 핵심 위기이다.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<hr style="border-color:#334155; margin:24px 0 16px;">
<div style="text-align:center; color:#64748b; font-size:0.82rem;">
    데이터 출처: 통계청 광공업생산지수 · 시도별 취업자 | K-stat 수출입 무역통계 (2021.03 ~ 2026.03)<br>
    분석 주제: 한국 제조업 위기 — 생산 둔화, 고용 감소, 수출 편중 구조의 복합 위기
</div>
""", unsafe_allow_html=True)
