import streamlit as st

# --- 0. 설정 및 함수 ---
st.set_page_config(page_title="이성적 주거 판단기", layout="centered")

# CSS로 전체적인 폰트나 여백 미세 조정
st.markdown("""
<style>
    .stExpander { border: none !important; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-radius: 10px; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem; }
</style>
""", unsafe_allow_html=True)

def format_currency(value):
    """만원 단위를 억/만원 단위로 변환 + 콤마 포맷팅"""
    val = int(value)
    if val >= 10000:
        uk = val // 10000
        man = val % 10000
        if man > 0:
            return f"{uk}억 {man:,}만원"
        return f"{uk}억원"
    return f"{val:,}만원"

# 카드 HTML 생성 함수 (공백 제거 유지)
def create_card_html(title, total_flow, diff_val, 
                     my_money, deposit, loan, investable, 
                     income_invest, expense_main, expense_loan, 
                     income_capital=0, is_monthly=False, is_jeonse=False, is_best=False):
    
    # 1. 자금 부족 체크
    if investable < 0:
        shortfall = abs(investable)
        return f"""<div style='background-color:#fff5f5; border:1px solid #ffcccc; border-radius:15px; padding:20px; height:100%; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
<h3 style='margin:0; font-size:1.1em; color:#555;'>{title}</h3>
<div style='font-size:2.5em; margin:15px 0;'>🚫</div>
<strong style='color:#e53e3e; font-size:1.0em;'>자금 부족</strong>
<p style='color:#718096; font-size:0.85em; margin-top:10px;'>
<b>{shortfall:,}만원</b> 부족
</p>
</div>"""

    # 2. 디자인 스타일 설정
    border_style = "2px solid #ffd700" if is_best else "1px solid #e2e8f0"
    bg_color = "#ffffff"
    shadow = "0 8px 16px rgba(0,0,0,0.1)" if is_best else "0 4px 6px rgba(0,0,0,0.05)"
    badge_html = "<div style='position:absolute; top:-12px; right:15px; background-color:#ffd700; color:#fff; padding:4px 10px; border-radius:12px; font-size:0.8em; font-weight:bold; box-shadow:0 2px 4px rgba(0,0,0,0.2);'>🏆 BEST</div>" if is_best else ""
    
    # 색상 설정
    color_flow = "#2b6cb0" if total_flow > 0 else "#c53030" # 파랑 / 빨강
    
    # 차이(Delta) 표시 텍스트
    if diff_val == 0:
        diff_html = "<span style='color:#a0aec0; font-size:0.85em'>- (기준)</span>"
    elif diff_val > 0:
        diff_html = f"<span style='color:#2b6cb0; font-size:0.85em; font-weight:bold;'>▲ {diff_val:,} 더 이득</span>"
    else:
        diff_html = f"<span style='color:#c53030; font-size:0.85em; font-weight:bold;'>▼ {abs(diff_val):,} 더 손해</span>"

    # 굴리는 돈 박스
    formula_html = f"""<div style='background-color:#f7fafc; padding:10px; border-radius:8px; margin-bottom:15px; font-size:0.85em; color:#4a5568; text-align:center; border:1px solid #edf2f7;'>
<div style='font-weight:600; margin-bottom:4px; color:#718096;'>💰 굴리는 돈</div>
{int(my_money):,} - ({int(deposit):,} - {int(loan):,})<br>
= <b style='color:#2d3748;'>{int(investable):,} 만원</b>
</div>"""

    # 상세 내역 (Flexbox 활용)
    row_style = "display:flex; justify-content:space-between; margin-bottom:6px; font-size:0.9em;"
    
    details_html = ""
    # 투자수익 (공통)
    details_html += f"<div style='{row_style}'><span style='color:#4299e1;'>+ 투자수익</span> <span style='font-weight:500;'>{int(income_invest):,} 만원</span></div>"
    
    if is_monthly:
        details_html += f"<div style='{row_style}'><span style='color:#f56565;'>- 월세지출</span> <span style='font-weight:500;'>{abs(int(expense_main)):,} 만원</span></div>"
        details_html += f"<div style='{row_style}'><span style='color:#f56565;'>- 대출이자</span> <span style='font-weight:500;'>{abs(int(expense_loan)):,} 만원</span></div>"
        details_html += "<div style='visibility:hidden; height:21px;'>.</div>" 
    elif is_jeonse:
        details_html += f"<div style='{row_style}'><span style='color:#f56565;'>- 대출이자</span> <span style='font-weight:500;'>{abs(int(expense_loan)):,} 만원</span></div>"
        details_html += "<div style='display:flex; justify-content:space-between; color:#cbd5e0; margin-bottom:6px; font-size:0.9em;'><span>- 월세지출</span> <span>0 만원</span></div>"
        details_html += "<div style='visibility:hidden; height:21px;'>.</div>" 
    else: 
        details_html += f"<div style='{row_style}'><span style='color:#4299e1;'>+ 집값상승</span> <span style='font-weight:500;'>{int(income_capital):,} 만원</span></div>"
        details_html += f"<div style='{row_style}'><span style='color:#f56565;'>- 대출원리금</span> <span style='font-weight:500;'>{abs(int(expense_loan)):,} 만원</span></div>"
        details_html += "<div style='visibility:hidden; height:21px;'>.</div>" 

    # 최종 HTML 조립
    html = f"""<div style='position:relative; background-color:{bg_color}; border:{border_style}; border-radius:16px; padding:20px; height:100%; display:flex; flex-direction:column; box-shadow:{shadow}; transition: transform 0.2s;'>
{badge_html}
<h3 style='margin-top:5px; text-align:center; font-size:1.1em; color:#4a5568; font-weight:600;'>{title}</h3>
<div style='text-align:center; margin-bottom:5px;'>
<span style='font-size:1.8em; font-weight:800; color:{color_flow}; letter-spacing:-0.5px;'>{int(total_flow):,}</span>
<span style='font-size:1.0em; color:{color_flow};'>만원</span>
</div>
<div style='text-align:center; margin-bottom:20px; height:20px;'>
{diff_html}
</div>
{formula_html}
<div style='border-top:1px solid #edf2f7; padding-top:15px; flex-grow:1;'>
{details_html}
</div>
</div>"""
    return html


st.title("🏠 이성적 주거 판단기")
st.markdown("##### **투자/자산 상승분**과 **주거 비용**을 합산하여 **연간 총 경제적 이익**을 시뮬레이션합니다.")


# --- 1. 입력 섹션 ---
with st.expander("📝 자산 및 매물 정보 입력 (클릭해서 펼치기)", expanded=True):
    
    st.markdown("#### 1. 내 자산 및 금리")
    col_asset1, col_asset2 = st.columns(2)
    with col_asset1:
        my_money = st.number_input("내 가용 현금 (만원)", value=10000, step=1000, format="%d")
        st.caption(f"💰 {format_currency(my_money)}")
    with col_asset2:
        loan_rate_pct = st.number_input("대출 금리 (%)", value=4.0, step=0.1, format="%.1f")
        loan_rate = loan_rate_pct / 100

    col_rate1, col_rate2 = st.columns(2)
    with col_rate1:
        stock_return_pct = st.number_input("투자 기대 수익률 (%)", value=4.0, step=0.1, format="%.1f")
        stock_return = stock_return_pct / 100
    with col_rate2:
        house_growth_pct = st.number_input("집값 기대 상승률 (%)", value=4.0, step=0.1, format="%.1f")
        house_growth = house_growth_pct / 100
        
    st.divider()
    
    st.markdown("#### 2. 매물 정보")
    
    tab_m, tab_j, tab_b = st.tabs(["월세", "전세", "매매"])
    
    with tab_m:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            monthly_deposit = st.number_input("월세 보증금 (만원)", value=5000, step=500, format="%d")
            monthly_loan = st.number_input("월세 보증금 대출 (만원)", value=0, step=500, format="%d")
        with col_m2:
            monthly_rent = st.number_input("월세 (만원)", value=100, step=5, format="%d")
            
    with tab_j:
        col_j1, col_j2 = st.columns(2)
        with col_j1:
            jeonse_deposit = st.number_input("전세 보증금 (만원)", value=30000, step=1000, format="%d")
        with col_j2:
            jeonse_loan = st.number_input("전세 자금 대출 (만원)", value=20000, step=1000, format="%d")
            
    with tab_b:
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            buying_price = st.number_input("매매 가격 (만원)", value=50000, step=1000, format="%d")
        with col_b2:
            buying_loan = st.number_input("매매 담보 대출 (만원)", value=40000, step=1000, format="%d")


# --- 2. 계산 로직 ---

# A. [월세 계산]
real_my_money_monthly = monthly_deposit - monthly_loan
surplus_cash_monthly = my_money - real_my_money_monthly

income_invest_monthly = surplus_cash_monthly * stock_return 
expense_rent_yearly = -(monthly_rent * 12)                  
expense_loan_monthly = -(monthly_loan * loan_rate)          

total_flow_monthly = income_invest_monthly + expense_rent_yearly + expense_loan_monthly


# B. [전세 계산]
real_my_money_jeonse = jeonse_deposit - jeonse_loan
surplus_cash_jeonse = my_money - real_my_money_jeonse

income_invest_jeonse = surplus_cash_jeonse * stock_return   
expense_loan_jeonse = -(jeonse_loan * loan_rate)            

total_flow_jeonse = income_invest_jeonse + expense_loan_jeonse


# C. [매매 계산]
real_my_money_buying = buying_price - buying_loan
surplus_cash_buying = my_money - real_my_money_buying

income_invest_buying = surplus_cash_buying * stock_return   
income_capital_gain = buying_price * house_growth           

# 원리금 균등 상환 계산 (30년)
if buying_loan > 0 and loan_rate > 0:
    rate_monthly = loan_rate / 12
    n_months = 30 * 12
    monthly_payment = buying_loan * (rate_monthly * (1 + rate_monthly)**n_months) / ((1 + rate_monthly)**n_months - 1)
    yearly_payment = monthly_payment * 12
elif buying_loan > 0 and loan_rate == 0:
    yearly_payment = buying_loan / 30
else:
    yearly_payment = 0

expense_loan_buying = -(yearly_payment) 

total_flow_buying = income_invest_buying + expense_loan_buying + income_capital_gain


# --- 3. 승자 결정 ---
valid_options = {}
if surplus_cash_monthly >= 0: valid_options["monthly"] = total_flow_monthly
if surplus_cash_jeonse >= 0: valid_options["jeonse"] = total_flow_jeonse
if surplus_cash_buying >= 0: valid_options["buying"] = total_flow_buying

best_option_key = None
if valid_options:
    best_option_key = max(valid_options, key=valid_options.get)


# --- 4. 결과 출력 ---
st.divider()

st.subheader("📊 연간 총 경제적 이익 비교")
st.caption("※ 경제적 이익 = 실제 현금 유출입(비용) + 자산 가치 변동분(집값/투자평가익)")

# 비교 기준값 (월세 기준)
base_flow = total_flow_monthly if surplus_cash_monthly >= 0 else 0

col1, col2, col3 = st.columns(3)

with col1:
    html = create_card_html(
        title="월세",
        total_flow=total_flow_monthly,
        diff_val=0, 
        my_money=my_money,
        deposit=monthly_deposit,
        loan=monthly_loan,
        investable=surplus_cash_monthly,
        income_invest=income_invest_monthly,
        expense_main=expense_rent_yearly,
        expense_loan=expense_loan_monthly,
        is_monthly=True,
        is_best=(best_option_key == "monthly")
    )
    st.markdown(html, unsafe_allow_html=True)

with col2:
    diff = int(total_flow_jeonse - base_flow) if surplus_cash_jeonse >= 0 else 0
    html = create_card_html(
        title="전세",
        total_flow=total_flow_jeonse,
        diff_val=diff,
        my_money=my_money,
        deposit=jeonse_deposit,
        loan=jeonse_loan,
        investable=surplus_cash_jeonse,
        income_invest=income_invest_jeonse,
        expense_main=0,
        expense_loan=expense_loan_jeonse,
        is_jeonse=True,
        is_best=(best_option_key == "jeonse")
    )
    st.markdown(html, unsafe_allow_html=True)

with col3:
    diff = int(total_flow_buying - base_flow) if surplus_cash_buying >= 0 else 0
    html = create_card_html(
        title="매매",
        total_flow=total_flow_buying,
        diff_val=diff,
        my_money=my_money,
        deposit=buying_price,
        loan=buying_loan,
        investable=surplus_cash_buying,
        income_invest=income_invest_buying,
        expense_main=0,
        expense_loan=expense_loan_buying,
        income_capital=income_capital_gain,
        is_best=(best_option_key == "buying")
    )
    st.markdown(html, unsafe_allow_html=True)
