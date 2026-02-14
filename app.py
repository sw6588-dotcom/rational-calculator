import streamlit as st

# --- 0. 설정 및 함수 ---
st.set_page_config(page_title="이성적 주거 판단기", layout="centered")

def format_currency(value):
    """만원 단위를 억/만원 단위로 변환해서 보여주는 함수"""
    if value >= 10000:
        uk = int(value // 10000)
        man = int(value % 10000)
        if man > 0:
            return f"{uk}억 {man}만원"
        return f"{uk}억원"
    return f"{int(value)}만원"

st.title("🏠 전세 vs 월세 vs 매매: 이성적 판단기")
st.markdown("감정을 배제하고, **총 비용(이자+기회비용)**과 **투자 수익**을 합산하여 계산합니다.")

# --- 1. 입력 섹션 (Sidebar) ---
st.sidebar.header("1. 자산 및 시장 가정")

# 가용 현금
my_money = st.sidebar.number_input("내 가용 현금 (만원)", value=10000, step=1000)
st.sidebar.caption(f"💰 환산: **{format_currency(my_money)}**")

# 수익률 및 금리
stock_return_pct = st.sidebar.select_slider(
    "나의 기대 투자 수익률 (%)",
    options=[4, 6, 8, 10, 15, 20],
    value=8
)
stock_return = stock_return_pct / 100

loan_rate_pct = st.sidebar.select_slider(
    "대출 금리 (%)",
    options=[2, 3, 4, 5, 6, 7],
    value=4
)
loan_rate = loan_rate_pct / 100

# 집값 상승률
house_growth_pct = st.sidebar.slider("예상 집값 상승률 (연 %)", -5.0, 10.0, 2.0, step=0.5)
house_growth = house_growth_pct / 100


st.sidebar.header("2. 매물 및 대출 정보")

# [월세 입력]
st.sidebar.subheader("[월세]")
monthly_deposit = st.sidebar.number_input("월세 보증금 (만원)", value=5000, step=500)
monthly_rent = st.sidebar.number_input("월세 (만원)", value=100, step=5)
monthly_loan = st.sidebar.number_input("월세 대출금액 (만원)", value=0, step=500) # 추가됨

# [전세 입력]
st.sidebar.subheader("[전세]")
jeonse_deposit = st.sidebar.number_input("전세 보증금 (만원)", value=30000, step=1000)
jeonse_loan = st.sidebar.number_input("전세 대출금액 (만원)", value=20000, step=1000) # 추가됨

# [매매 입력]
st.sidebar.subheader("[매매]")
buying_price = st.sidebar.number_input("매매 가격 (만원)", value=50000, step=1000)
buying_loan = st.sidebar.number_input("매매 담보대출금액 (만원)", value=20000, step=1000) # 추가됨


# --- 2. 계산 로직 (핵심 변경) ---
# 공통 공식:
# 1. 집에 들어가는 순수 내 돈 = 보증금(매매가) - 대출금
# 2. 투자 가능한 남은 돈(잉여현금) = 내 가용 현금 - 집에 들어가는 순수 내 돈
# 3. 투자 수익 = 잉여현금 * 수익률
# 4. 대출 이자 = 대출금 * 대출금리
# 5. 최종 비용 = (지출 + 대출이자) - (투자수익 + 집값상승)

# A. [월세 계산]
real_my_money_in_monthly = monthly_deposit - monthly_loan # 보증금에 들어간 내 돈
surplus_cash_monthly = my_money - real_my_money_in_monthly # 굴릴 수 있는 돈

investment_profit_monthly = surplus_cash_monthly * stock_return # (+) 수익
loan_cost_monthly = monthly_loan * loan_rate # (-) 이자비용
rent_cost_yearly = monthly_rent * 12 # (-) 월세 지출

# 총 비용 (지출은 더하고 수익은 뺌)
total_cost_monthly = rent_cost_yearly + loan_cost_monthly - investment_profit_monthly


# B. [전세 계산]
real_my_money_in_jeonse = jeonse_deposit - jeonse_loan
surplus_cash_jeonse = my_money - real_my_money_in_jeonse

investment_profit_jeonse = surplus_cash_jeonse * stock_return # (+) 수익
loan_cost_jeonse = jeonse_loan * loan_rate # (-) 이자비용

# 총 비용
total_cost_jeonse = loan_cost_jeonse - investment_profit_jeonse


# C. [매매 계산]
acquisition_tax = buying_price * 0.011  # 취득세 (첫해 비용)
maintenance_cost = buying_price * 0.002 # 보유세/유지비

real_my_money_in_buying = buying_price - buying_loan
surplus_cash_buying = my_money - real_my_money_in_buying

investment_profit_buying = surplus_cash_buying * stock_return # (+) 수익
loan_cost_buying = buying_loan * loan_rate # (-) 이자비용
capital_gain = buying_price * house_growth # (+) 집값 상승분

# 총 비용 (취득세는 1/N 하지 않고 첫해 기준 전액 반영 - 보수적 접근)
# 비용 = 이자 + 세금/유지비 - (투자수익 + 집값상승)
total_cost_buying = (loan_cost_buying + acquisition_tax + maintenance_cost) - \
                    (investment_profit_buying + capital_gain)


# --- 3. 결과 출력 ---
st.divider()

st.subheader("📊 1년 간 최종 손익 계산서 (마이너스가 이득)")
st.caption("※ (+)는 지갑에서 나가는 돈, (-)는 지갑으로 들어오는 이득을 의미합니다.")

col1, col2, col3 = st.columns(3)

# 1. 월세 결과
with col1:
    st.metric(label="월세 선택 시 (연간)", value=f"{int(total_cost_monthly)} 만원")
    st.markdown(f"""
    <div style='font-size:14px; color:gray'>
    • 월세지출: +{int(rent_cost_yearly)}<br>
    • 대출이자: +{int(loan_cost_monthly)}<br>
    • 투자수익: <span style='color:blue'>-{int(investment_profit_monthly)}</span>
    <br><br>
    <b>💰 굴리는 돈: {format_currency(surplus_cash_monthly)}</b>
    </div>
    """, unsafe_allow_html=True)

# 2. 전세 결과
with col2:
    st.metric(label="전세 선택 시 (연간)", value=f"{int(total_cost_jeonse)} 만원", 
              delta=int(total_cost_monthly - total_cost_jeonse), delta_color="inverse")
    st.markdown(f"""
    <div style='font-size:14px; color:gray'>
    • 대출이자: +{int(loan_cost_jeonse)}<br>
    • 투자수익: <span style='color:blue'>-{int(investment_profit_jeonse)}</span>
    <br><br><br>
    <b>💰 굴리는 돈: {format_currency(surplus_cash_jeonse)}</b>
    </div>
    """, unsafe_allow_html=True)

# 3. 매매 결과
with col3:
    st.metric(label="매매 선택 시 (연간)", value=f"{int(total_cost_buying)} 만원", 
              delta=int(total_cost_monthly - total_cost_buying), delta_color="inverse")
    st.markdown(f"""
    <div style='font-size:14px; color:gray'>
    • 대출이자: +{int(loan_cost_buying)}<br>
    • 세금/유지: +{int(acquisition_tax + maintenance_cost)}<br>
    • 투자수익: <span style='color:blue'>-{int(investment_profit_buying)}</span><br>
    • 집값변동: <span style='color:red'>-{int(capital_gain)}</span>
    <br>
    <b>💰 굴리는 돈: {format_currency(surplus_cash_buying)}</b>
    </div>
    """, unsafe_allow_html=True)

# --- 4. 최종 판단 ---
st.divider()
best_cost = min(total_cost_monthly, total_cost_jeonse, total_cost_buying)

if best_cost == total_cost_buying:
    st.success(f"🏆 결론: **매매**가 가장 유리합니다! (집값 상승과 레버리지 효과)")
elif best_cost == total_cost_jeonse:
    st.warning(f"🏆 결론: **전세**가 가장 유리합니다! (투자 수익으로 이자 상쇄)")
else:
    st.error(f"🏆 결론: **월세**가 정답입니다! (현금 유동성 확보가 최고)")
