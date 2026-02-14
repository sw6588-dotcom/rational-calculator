import streamlit as st

# --- 0. 설정 및 함수 ---
st.set_page_config(page_title="이성적 주거 판단기", layout="centered")

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

# 카드 HTML 생성 함수 (공백 문제 해결됨)
def create_card_html(title, total_flow, diff_val, 
                     my_money, deposit, loan, investable, 
                     income_invest, expense_main, expense_loan, 
                     income_capital=0, is_monthly=False, is_jeonse=False):
    
    # 색상 및 부호 설정
    color_flow = "black"
    if total_flow > 0: color_flow = "blue"
    elif total_flow < 0: color_flow = "red"
    
    # 차이(Delta) 표시 텍스트
    if diff_val == 0:
        diff_html = "<span style='color:gray; font-size:0.9em'>- (기준)</span>"
    elif diff_val > 0:
        diff_html = f"<span style='color:blue; font-size:0.9em'>▲ {diff_val:,}만원 더 이득</span>"
    else:
        diff_html = f"<span style='color:red; font-size:0.9em'>▼ {abs(diff_val):,}만원 더 손해</span>"

    # 1. 굴리는 돈 수식 (왼쪽 정렬로 공백 제거)
    formula_html = f"""
<div style='background-color:#f9f9f9; padding:8px; border-radius:5px; margin-bottom:10px; font-size:0.85em; color:#333; text-align:center;'>
    <strong>💰 굴리는 돈 계산</strong><br>
    {int(my_money):,} - ({int(deposit):,} - {int(loan):,})<br>
    = <b>{int(investable):,} 만원</b>
</div>"""

    # 2. 상세 내역 생성
    details_html = ""
    
    # 투자수익 (공통)
    details_html += f"<div style='display:flex; justify-content:space-between;'><span style='color:blue'>+ 투자수익</span> <span>{int(income_invest):,} 만원</span></div>"
    
    if is_monthly:
        details_html += f"<div style='display:flex; justify-content:space-between;'><span style='color:red'>- 월세지출</span> <span>{abs(int(expense_main)):,} 만원</span></div>"
        details_html += f"<div style='display:flex; justify-content:space-between;'><span style='color:red'>- 대출이자</span> <span>{abs(int(expense_loan)):,} 만원</span></div>"
        details_html += "<div style='visibility:hidden;'>.</div>" 
    elif is_jeonse:
        details_html += f"<div style='display:flex; justify-content:space-between;'><span style='color:red'>- 대출이자</span> <span>{abs(int(expense_loan)):,} 만원</span></div>"
        details_html += "<div style='display:flex; justify-content:space-between; color:gray; opacity:0.5;'><span>- 월세지출</span> <span>0 만원</span></div>"
        details_html += "<div style='visibility:hidden;'>.</div>" 
    else: 
        details_html += f"<div style='display:flex; justify-content:space-between;'><span style='color:blue'>+ 집값상승</span> <span>{int(income_capital):,} 만원</span></div>"
        details_html += f"<div style='display:flex; justify-content:space-between;'><span style='color:red'>- 대출이자</span> <span>{abs(int(expense_loan)):,} 만원</span></div>"
        details_html += "<div style='visibility:hidden;'>.</div>" 

    # 최종 HTML 조립 (왼쪽 정렬로 공백 제거)
    html = f"""
<div style='border:1px solid #ddd; border-radius:10px; padding:15px; height:100%; display:flex; flex-direction:column;'>
    <h3 style='margin-top:0; text-align:center; font-size:1.2em; margin-bottom:5px;'>{title}</h3>
    <div style='text-align:center; margin-bottom:5px;'>
        <span style='font-size:1.6em; font-weight:bold; color:{color_flow};'>{int(total_flow):,} 만원</span>
    </div>
    <div style='text-align:center; margin-bottom:15px; height:20px;'>
        {diff_html}
    </div>
    {formula_html}
    <div style='font-size:0.95em; line-height:1.8; border-top:1px solid #eee; padding-top:10px; flex-grow:1;'>
        {details_html}
    </div>
</div>
"""
    return html


st.title("🏠 전세 vs 월세 vs 매매: 판단 참고용")
st.markdown("감정을 배제하고 현금흐름(수익-지출)을 비교합니다.")

# --- 1. 입력 섹션 (Sidebar) ---
st.sidebar.header("1. 자산 및 금리 설정")

# 가용 현금
my_money = st.sidebar.number_input("내 가용 현금 (만원)", value=10000, step=1000, format="%d")
st.sidebar.caption(f"💰 환산: **{format_currency(my_money)}**")

# 투자 기대 수익률
stock_return_pct = st.sidebar.number_input("투자 기대 수익률 (%)", value=8.0, step=0.1, format="%.1f")
stock_return = stock_return_pct / 100

# 대출 금리
loan_rate_pct = st.sidebar.number_input("대출 금리 (%)", value=4.0, step=0.1, format="%.1f")
loan_rate = loan_rate_pct / 100

# 집값 기대 상승률
house_growth_pct = st.sidebar.number_input("기대 집값 상승률 (%)", value=2.0, step=0.1, format="%.1f")
house_growth = house_growth_pct / 100


st.sidebar.header("2. 매물 및 대출 정보")

# [월세 입력]
st.sidebar.subheader("[월세]")
monthly_deposit = st.sidebar.number_input("월세 보증금 (만원)", value=5000, step=500, format="%d")
monthly_rent = st.sidebar.number_input("월세 (만원)", value=100, step=5, format="%d")
monthly_loan = st.sidebar.number_input("월세 보증금 대출 (만원)", value=0, step=500, format="%d")

# [전세 입력]
st.sidebar.subheader("[전세]")
jeonse_deposit = st.sidebar.number_input("전세 보증금 (만원)", value=30000, step=1000, format="%d")
jeonse_loan = st.sidebar.number_input("전세 자금 대출 (만원)", value=20000, step=1000, format="%d")

# [매매 입력]
st.sidebar.subheader("[매매]")
buying_price = st.sidebar.number_input("매매 가격 (만원)", value=50000, step=1000, format="%d")
buying_loan = st.sidebar.number_input("매매 담보 대출 (만원)", value=20000, step=1000, format="%d")


# --- 2. 계산 로직 ---

# A. [월세 계산]
real_my_money_monthly = monthly_deposit - monthly_loan
surplus_cash_monthly = my_money - real_my_money_monthly # 굴릴 수 있는 돈

income_invest_monthly = surplus_cash_monthly * stock_return # (+) 투자수익
expense_rent_yearly = -(monthly_rent * 12)                  # (-) 월세지출
expense_loan_monthly = -(monthly_loan * loan_rate)          # (-) 대출이자

total_flow_monthly = income_invest_monthly + expense_rent_yearly + expense_loan_monthly


# B. [전세 계산]
real_my_money_jeonse = jeonse_deposit - jeonse_loan
surplus_cash_jeonse = my_money - real_my_money_jeonse

income_invest_jeonse = surplus_cash_jeonse * stock_return   # (+) 투자수익
expense_loan_jeonse = -(jeonse_loan * loan_rate)            # (-) 대출이자

total_flow_jeonse = income_invest_jeonse + expense_loan_jeonse


# C. [매매 계산]
real_my_money_buying = buying_price - buying_loan
surplus_cash_buying = my_money - real_my_money_buying

income_invest_buying = surplus_cash_buying * stock_return   # (+) 투자수익
expense_loan_buying = -(buying_loan * loan_rate)            # (-) 대출이자
income_capital_gain = buying_price * house_growth           # (+) 집값상승

total_flow_buying = income_invest_buying + expense_loan_buying + income_capital_gain


# --- 3. 결과 출력 ---
st.divider()

st.subheader("📊 연간 토탈 현금흐름 비교")
st.caption("※ 토탈 현금흐름 = 투자수익 + 집값변동 - 대출이자 - 월세지출")

# 비교 기준값 (월세 기준)
base_flow = total_flow_monthly

col1, col2, col3 = st.columns(3)

with col1:
    html = create_card_html(
        title="월세 선택 시",
        total_flow=total_flow_monthly,
        diff_val=0, # 기준
        my_money=my_money,
        deposit=monthly_deposit,
        loan=monthly_loan,
        investable=surplus_cash_monthly,
        income_invest=income_invest_monthly,
        expense_main=expense_rent_yearly,
        expense_loan=expense_loan_monthly,
        is_monthly=True
    )
    st.markdown(html, unsafe_allow_html=True)

with col2:
    html = create_card_html(
        title="전세 선택 시",
        total_flow=total_flow_jeonse,
        diff_val=int(total_flow_jeonse - base_flow),
        my_money=my_money,
        deposit=jeonse_deposit,
        loan=jeonse_loan,
        investable=surplus_cash_jeonse,
        income_invest=income_invest_jeonse,
        expense_main=0,
        expense_loan=expense_loan_jeonse,
        is_jeonse=True
    )
    st.markdown(html, unsafe_allow_html=True)

with col3:
    html = create_card_html(
        title="매매 선택 시",
        total_flow=total_flow_buying,
        diff_val=int(total_flow_buying - base_flow),
        my_money=my_money,
        deposit=buying_price,
        loan=buying_loan,
        investable=surplus_cash_buying,
        income_invest=income_invest_buying,
        expense_main=0,
        expense_loan=expense_loan_buying,
        income_capital=income_capital_gain
    )
    st.markdown(html, unsafe_allow_html=True)


# --- 4. 최종 판단 ---
st.divider()
best_flow = max(total_flow_monthly, total_flow_jeonse, total_flow_buying)

if best_flow == total_flow_buying:
    st.success(f"🏆 결론: **매매**가 가장 이득입니다! (연간 {int(best_flow):,}만원 확보)")
elif best_flow == total_flow_jeonse:
    st.warning(f"🏆 결론: **전세**가 가장 이득입니다! (연간 {int(best_flow):,}만원 확보)")
else:
    st.info(f"🏆 결론: **월세**가 가장 이득입니다! (연간 {int(best_flow):,}만원 확보)")
