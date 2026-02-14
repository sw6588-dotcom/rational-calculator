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

# 초기 세션 상태 설정 (버튼 클릭 처리를 위해)
if 'stock_return_val' not in st.session_state:
    st.session_state.stock_return_val = 8.0
if 'loan_rate_val' not in st.session_state:
    st.session_state.loan_rate_val = 4.0

def set_stock_return(val):
    st.session_state.stock_return_val = val

def set_loan_rate(val):
    st.session_state.loan_rate_val = val

st.title("🏠 전세 vs 월세 vs 매매: 이성적 판단기")
st.markdown("수익은 **(+)**, 지출은 **(-)**로 계산하여 합산한 **토탈 현금흐름**을 비교합니다.")

# --- 1. 입력 섹션 (Sidebar) ---
st.sidebar.header("1. 자산 및 금리 설정")

# 가용 현금
my_money = st.sidebar.number_input("내 가용 현금 (만원)", value=10000, step=1000, format="%d")
st.sidebar.caption(f"💰 환산: **{format_currency(my_money)}**")

# [변경] 기대 수익률 (입력창 + 버튼)
st.sidebar.subheader("나의 기대 투자 수익률 (%)")
stock_return_pct = st.sidebar.number_input("연 수익률 입력", value=st.session_state.stock_return_val, step=0.1, key='stock_input')
# 버튼 생성
cols_ret = st.sidebar.columns(4)
if cols_ret[0].button("4%", key='r4'): set_stock_return(4.0); st.rerun()
if cols_ret[1].button("6%", key='r6'): set_stock_return(6.0); st.rerun()
if cols_ret[2].button("8%", key='r8'): set_stock_return(8.0); st.rerun()
if cols_ret[3].button("10%", key='r10'): set_stock_return(10.0); st.rerun()
stock_return = stock_return_pct / 100

# [변경] 대출 금리 (입력창 + 버튼)
st.sidebar.subheader("대출 금리 (%)")
loan_rate_pct = st.sidebar.number_input("연 금리 입력", value=st.session_state.loan_rate_val, step=0.1, key='loan_input')
# 버튼 생성
cols_loan = st.sidebar.columns(4)
if cols_loan[0].button("2%", key='l2'): set_loan_rate(2.0); st.rerun()
if cols_loan[1].button("3%", key='l3'): set_loan_rate(3.0); st.rerun()
if cols_loan[2].button("4%", key='l4'): set_loan_rate(4.0); st.rerun()
if cols_loan[3].button("5%", key='l5'): set_loan_rate(5.0); st.rerun()
loan_rate = loan_rate_pct / 100

# 집값 상승률
st.sidebar.subheader("예상 집값 상승률 (%)")
house_growth_pct = st.sidebar.number_input("연 상승률 입력", value=2.0, step=0.5)
house_growth = house_growth_pct / 100


st.sidebar.header("2. 매물 및 대출 정보")

# [월세 입력]
st.sidebar.subheader("[월세]")
monthly_deposit = st.sidebar.number_input("월세 보증금 (만원)", value=5000, step=500, format="%d")
monthly_rent = st.sidebar.number_input("월세 (만원)", value=100, step=5, format="%d")
monthly_loan = st.sidebar.number_input("월세 보증금 대출 (만원)", value=0, step=500, format="%d") # 이름 변경

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

# 현금흐름 요소
income_invest_monthly = surplus_cash_monthly * stock_return # (+) 투자수익
expense_rent_yearly = -(monthly_rent * 12)                  # (-) 월세지출
expense_loan_monthly = -(monthly_loan * loan_rate)          # (-) 대출이자

# 토탈 현금흐름
total_flow_monthly = income_invest_monthly + expense_rent_yearly + expense_loan_monthly


# B. [전세 계산]
real_my_money_jeonse = jeonse_deposit - jeonse_loan
surplus_cash_jeonse = my_money - real_my_money_jeonse

# 현금흐름 요소
income_invest_jeonse = surplus_cash_jeonse * stock_return   # (+) 투자수익
expense_loan_jeonse = -(jeonse_loan * loan_rate)            # (-) 대출이자

# 토탈 현금흐름
total_flow_jeonse = income_invest_jeonse + expense_loan_jeonse


# C. [매매 계산]
# 세금/유지 삭제 요청 반영하여 제외함
real_my_money_buying = buying_price - buying_loan
surplus_cash_buying = my_money - real_my_money_buying

# 현금흐름 요소
income_invest_buying = surplus_cash_buying * stock_return   # (+) 투자수익
expense_loan_buying = -(buying_loan * loan_rate)            # (-) 대출이자
income_capital_gain = buying_price * house_growth           # (+) 집값상승

# 토탈 현금흐름
total_flow_buying = income_invest_buying + expense_loan_buying + income_capital_gain


# --- 3. 결과 출력 ---
st.divider()

st.subheader("📊 연간 토탈 현금흐름 (높을수록 좋음)")
st.caption("※ 토탈 현금흐름 = 투자수익(내 돈 굴린 것) + 집값변동 - 대출이자 - 월세지출")

col1, col2, col3 = st.columns(3)

# 1. 월세 결과
with col1:
    st.metric(label="월세 선택 시", value=f"{int(total_flow_monthly):,} 만원")
    st.markdown(f"""
    <div style='font-size:14px; line-height:1.5'>
    <span style='color:blue'>+ 투자수익: {int(income_invest_monthly):,}</span><br>
    <span style='color:red'>- 월세지출: {int(expense_rent_yearly):,}</span><br>
    <span style='color:red'>- 대출이자: {int(expense_loan_monthly):,}</span>
    <hr style='margin:5px 0'>
    <b>💰 굴리는 돈: {format_currency(surplus_cash_monthly)}</b>
    </div>
    """, unsafe_allow_html=True)

# 2. 전세 결과
with col2:
    delta_jeonse = int(total_flow_jeonse - total_flow_monthly)
    st.metric(label="전세 선택 시", value=f"{int(total_flow_jeonse):,} 만원", 
              delta=f"{delta_jeonse:,} 차이")
    st.markdown(f"""
    <div style='font-size:14px; line-height:1.5'>
    <span style='color:blue'>+ 투자수익: {int(income_invest_jeonse):,}</span><br>
    <span style='color:red'>- 대출이자: {int(expense_loan_jeonse):,}</span><br>
    <span style='color:gray; opacity:0.5'>- 월세지출: 0</span>
    <hr style='margin:5px 0'>
    <b>💰 굴리는 돈: {format_currency(surplus_cash_jeonse)}</b>
    </div>
    """, unsafe_allow_html=True)

# 3. 매매 결과
with col3:
    delta_buying = int(total_flow_buying - total_flow_monthly)
    st.metric(label="매매 선택 시", value=f"{int(total_flow_buying):,} 만원", 
              delta=f"{delta_buying:,} 차이")
    st.markdown(f"""
    <div style='font-size:14px; line-height:1.5'>
    <span style='color:blue'>+ 투자수익: {int(income_invest_buying):,}</span><br>
    <span style='color:blue'>+ 집값상승: {int(income_capital_gain):,}</span><br>
    <span style='color:red'>- 대출이자: {int(expense_loan_buying):,}</span>
    <hr style='margin:5px 0'>
    <b>💰 굴리는 돈: {format_currency(surplus_cash_buying)}</b>
    </div>
    """, unsafe_allow_html=True)

# --- 4. 최종 판단 ---
st.divider()
best_flow = max(total_flow_monthly, total_flow_jeonse, total_flow_buying)

if best_flow == total_flow_buying:
    st.success(f"🏆 결론: **매매**가 가장 이득입니다! (총 {int(best_flow):,}만원 이익)")
elif best_flow == total_flow_jeonse:
    st.warning(f"🏆 결론: **전세**가 가장 이득입니다! (총 {int(best_flow):,}만원 이익)")
else:
    st.info(f"🏆 결론: **월세**가 가장 이득입니다! (총 {int(best_flow):,}만원 이익)")
