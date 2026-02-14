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
surplus_cash_monthly = my_money - real_my_money
