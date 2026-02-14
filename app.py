import streamlit as st

# --- 0. 설정 및 함수 ---
st.set_page_config(page_title="이성적 주거 판단기", layout="centered")

# CSS로 스타일 조정
st.markdown("""
<style>
    .stExpander { border: none !important; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-radius: 10px; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem; }
    .metric-label { font-size: 0.9em; color: #718096; margin-bottom: 2px; }
    .metric-value { font-size: 1.4em; font-weight: 800; }
    .detail-row { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 0.9em; }
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

# 카드 HTML 생성 함수
def create_card_html(title, net_cash_flow, net_asset_change, 
                     my_money, deposit, loan, investable, 
                     income_invest, income_capital, 
                     expense_rent, expense_loan_cash, expense_loan_cost,
                     is_best_asset=False):
    
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

    # 2. 디자인 설정
    border_style = "2px solid #ffd700" if is_best_asset else "1px solid #e2e8f0"
    shadow = "0 8px 16px rgba(0,0,0,0.1)" if is_best_asset else "0 4px 6px rgba(0,0,0,0.05)"
    badge_html = "<div style='position:absolute; top:-12px; right:15px; background-color:#ffd700; color:#fff; padding:4px 10px; border-radius:12px; font-size:0.8em; font-weight:bold; box-shadow:0 2px 4px rgba(0,0,0,0.2);'>🏆 자산 1위</div>" if is_best_asset else ""
    
    # 색상 설정
    color_asset = "#2b6cb0" if net_asset_change > 0 else "#c53030"
    color_cash = "#2b6cb0" if net_cash_flow > 0 else "#c53030"

    # 굴리는 돈 박스
    formula_html = f"""<div style='background-color:#f7fafc; padding:10px; border-radius:8px; margin-bottom:15px; font-size:0.85em; color:#4a5568; text-align:center; border:1px solid #edf2f7;'>
<div style='font-weight:600; margin-bottom:4px; color:#718096;'>💰 굴리는 돈</div>
{int(my_money):,} - ({int(deposit):,} - {int(loan):,})<br>
= <b style='color:#2d3748;'>{int(investable):,} 만원</b>
</div>"""

    # 상세 내역 HTML 작성
    details_html = ""
    
    # (1) 자산 증가 요인 (파란색)
    if income_invest > 0:
        details_html += f"<div class='detail-row'><span style='color:#4299e1;'>+ 투자수익</span> <span style='font-weight:500;'>{int(income_invest):,} 만원</span></div>"
    if income_capital > 0:
        details_html += f"<div class='detail-row'><span style='color:#4299e1;'>+ 집값상승</span> <span style='font-weight:500;'>{int(income_capital):,} 만원</span></div>"
    
    # (2) 현금 유출/비용 요인 (빨간색)
    if expense_rent > 0:
        details_html += f"<div class='detail-row'><span style='color:#f56565;'>- 월세지출</span> <span style='font-weight:500;'>{int(expense_rent):,} 만원</span></div>"
    
    # 대출 관련 표시
    # 매매의 경우: 현금유출(원리금)과 비용(이자)가 다름
    # 여기서는 '현금흐름' 위주로 보여줄지, '비용' 위주로 보여줄지 결정해야 함
    # 헷갈리지 않게 '대출지출'로 통일하되, 매매는 (원리금)이라고 명시
    if expense_loan_cash > 0:
        label = "대출원리금" if (expense_loan_cash != expense_loan_cost) else "대출이자"
        details_html += f"<div class='detail-row'><span style='color:#f56565;'>- {label}</span> <span style='font-weight:500;'>{int(expense_loan_cash):,} 만원</span></div>"

    # 줄 맞춤용 빈 div (내용이 너무 적을 때 높이 확보)
    if (income_invest == 0 and income_capital == 0 and expense_rent == 0 and expense_loan_cash == 0):
        details_html += "<div style='height:20px;'></div>"

    # 최종 HTML 조립
    html = f"""<div style='position:relative; background-color:#fff; border:{border_style}; border-radius:16px; padding:20px; height:100%; display:flex; flex-direction:column; box-shadow:{shadow}; transition: transform 0.2s;'>
{badge_html}
<h3 style='margin-top:5px; text-align:center; font-size:1.1em; color:#4a5568; font-weight:600;'>{title}</h3>

<div style='text-align:center; margin-bottom:15px; border-bottom:1px solid #eee; padding-bottom:10px;'>
    <div class='metric-label'>📈 연간 총 자산 변동</div>
    <div class='metric-value' style='color:{color_asset};'>{int(net_asset_change):,} 만원</div>
</div>

<div style='text-align:center; margin-bottom:15px;'>
    <div class='metric-label'>💸 연간 순현금흐름</div>
    <div class='metric-value' style='color:{color_cash}; font-size:1.2em;'>{int(net_cash_flow):,} 만원</div>
    <div style='font-size:0.75em; color:#a0aec0;'>(투자수익 제외)</div>
</div>

{formula_html}

<div style='border-top:1px solid #edf2f7; padding-top:15px; flex-grow:1;'>
{details_html}
</div>
</div>"""
    return html


st.title("🏠 이성적 주거 판단기")
st.markdown("##### **순현금흐름(생활비)**과 **총 자산 변동(재산)**을 동시에 비교합니다.")


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
expense_rent_yearly = monthly_rent * 12
expense_loan_monthly_cash = monthly_loan * loan_rate # 이자만 납부 가정

# 순현금흐름 (지출만)
net_cash_flow_monthly = -(expense_rent_yearly + expense_loan_monthly_cash)

# 총 자산 변동 (투자수익 포함, 비용 차감)
net_asset_change_monthly = income_invest_monthly - expense_rent_yearly - expense_loan_monthly_cash


# B. [전세 계산]
real_my_money_jeonse = jeonse_deposit - jeonse_loan
surplus_cash_jeonse = my_money - real_my_money_jeonse

income_invest_jeonse = surplus_cash_jeonse * stock_return   
expense_loan_jeonse_cash = jeonse_loan * loan_rate # 이자만 납부

# 순현금흐름
net_cash_flow_jeonse = -(expense_loan_jeonse_cash)

# 총 자산 변동
net_asset_change_jeonse = income_invest_jeonse - expense_loan_jeonse_cash


# C. [매매 계산]
real_my_money_buying = buying_price - buying_loan
surplus_cash_buying = my_money - real_my_money_buying

income_invest_buying = surplus_cash_buying * stock_return   
income_capital_gain = buying_price * house_growth           

# 1. 대출 원리금 (현금 유출)
if buying_loan > 0 and loan_rate > 0:
    rate_monthly = loan_rate / 12
    n_months = 30 * 12
    monthly_payment = buying_loan * (rate_monthly * (1 + rate_monthly)**n_months) / ((1 + rate_monthly)**n_months - 1)
    yearly_payment_total = monthly_payment * 12
elif buying_loan > 0 and loan_rate == 0:
    yearly_payment_total = buying_loan / 30
else:
    yearly_payment_total = 0

# 2. 대출 이자비용 (자산 차감용)
yearly_interest_only = buying_loan * loan_rate

# 순현금흐름 (투자수익 제외, 원리금 전액 차감)
net_cash_flow_buying = -(yearly_payment_total)

# 총 자산 변동 (투자수익 포함, 집값상승 포함, 이자만 비용으로 차감)
# 원금 상환분은 내 자산(대출 감소=순자산 증가)이므로 비용 아님
net_asset_change_buying = income_invest_buying + income_capital_gain - yearly_interest_only


# --- 3. 승자 결정 (자산 변동 기준) ---
valid_options = {}
if surplus_cash_monthly >= 0: valid_options["monthly"] = net_asset_change_monthly
if surplus_cash_jeonse >= 0: valid_options["jeonse"] = net_asset_change_jeonse
if surplus_cash_buying >= 0: valid_options["buying"] = net_asset_change_buying

best_asset_key = None
if valid_options:
    best_asset_key = max(valid_options, key=valid_options.get)


# --- 4. 결과 출력 ---
st.divider()

st.subheader("📊 비교 분석 결과")
st.caption("※ **순현금흐름**: 실제 통장 잔고 변화 (마이너스면 생활비에서 지출)")
st.caption("※ **총 자산 변동**: 부동산/주식 가치 상승을 포함한 내 재산의 변화")

col1, col2, col3 = st.columns(3)

with col1:
    html = create_card_html(
        title="월세",
        net_cash_flow=net_cash_flow_monthly,
        net_asset_change=net_asset_change_monthly,
        my_money=my_money,
        deposit=monthly_deposit,
        loan=monthly_loan,
        investable=surplus_cash_monthly,
        income_invest=income_invest_monthly,
        income_capital=0,
        expense_rent=expense_rent_yearly,
        expense_loan_cash=expense_loan_monthly_cash,
        expense_loan_cost=expense_loan_monthly_cash,
        is_best_asset=(best_asset_key == "monthly")
    )
    st.markdown(html, unsafe_allow_html=True)

with col2:
    html = create_card_html(
        title="전세",
        net_cash_flow=net_cash_flow_jeonse,
        net_asset_change=net_asset_change_jeonse,
        my_money=my_money,
        deposit=jeonse_deposit,
        loan=jeonse_loan,
        investable=surplus_cash_jeonse,
        income_invest=income_invest_jeonse,
        income_capital=0,
        expense_rent=0,
        expense_loan_cash=expense_loan_jeonse_cash,
        expense_loan_cost=expense_loan_jeonse_cash,
        is_best_asset=(best_asset_key == "jeonse")
    )
    st.markdown(html, unsafe_allow_html=True)

with col3:
    html = create_card_html(
        title="매매",
        net_cash_flow=net_cash_flow_buying,
        net_asset_change=net_asset_change_buying,
        my_money=my_money,
        deposit=buying_price,
        loan=buying_loan,
        investable=surplus_cash_buying,
        income_invest=income_invest_buying,
        income_capital=income_capital_gain,
        expense_rent=0,
        expense_loan_cash=yearly_payment_total,        # 현금유출 (원리금)
        expense_loan_cost=yearly_interest_only,        # 자산비용 (이자)
        is_best_asset=(best_asset_key == "buying")
    )
    st.markdown(html, unsafe_allow_html=True)
