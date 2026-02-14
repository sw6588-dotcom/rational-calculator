import streamlit as st

# --- 0. 설정 및 함수 ---
st.set_page_config(page_title="이성적 주거 판단기", layout="centered")

def format_currency(value):
    """만원 단위를 억/만원 단위로 변환해서 보여주는 함수"""
    if value >= 10000:
        uk = value // 10000
        man = value % 10000
        if man > 0:
            return f"{uk}억 {man}만원"
        return f"{uk}억원"
    return f"{value}만원"

st.title("🏠 전세 vs 월세 vs 매매: 이성적 판단기")
st.markdown("감정을 배제하고, **기회비용**과 **금융 비용**만으로 계산합니다.")

# --- 1. 입력 섹션 (Sidebar) ---
st.sidebar.header("1. 자산 및 시장 가정")

# 1, 2. 가용 현금 (기본값 1억, 억 단위 표시)
my_money = st.sidebar.number_input("내 가용 현금 (만원)", value=10000, step=1000)
st.sidebar.caption(f"💰 환산: **{format_currency(my_money)}**")

# 3, 4, 5. 기대 수익률 (스케일 통일, 미국주식 텍스트 제거, 선택형)
stock_return_pct = st.sidebar.select_slider(
    "나의 기대 투자 수익률 (%)",
    options=[4, 6, 8, 10, 15, 20],
    value=8
)
stock_return = stock_return_pct / 100

# 3, 6. 대출 금리 (스케일 통일, 선택형)
loan_rate_pct = st.sidebar.select_slider(
    "대출 금리 (%)",
    options=[2, 3, 4, 5],
    value=4
)
loan_rate = loan_rate_pct / 100

# 11. 집값 상승률 (위치 이동, 스케일 맞춤)
house_growth_pct = st.sidebar.slider("예상 집값 상승률 (연 %)", -5.0, 10.0, 2.0, step=0.5)
house_growth = house_growth_pct / 100


st.sidebar.header("2. 매물 정보 입력")

# 7, 8. 월세 (Step 변경)
st.sidebar.subheader("[월세]")
monthly_deposit = st.sidebar.number_input("월세 보증금 (만원)", value=5000, step=500)
monthly_rent = st.sidebar.number_input("월세 (만원)", value=100, step=5)

# 9. 전세 (Step 변경)
st.sidebar.subheader("[전세]")
jeonse_deposit = st.sidebar.number_input("전세 보증금 (만원)", value=30000, step=1000)

# 10. 매매 (Step 변경)
st.sidebar.subheader("[매매]")
buying_price = st.sidebar.number_input("매매 가격 (만원)", value=50000, step=1000)


# --- 2. 계산 로직 ---
acquisition_tax = buying_price * 0.011  # 취득세 1.1% 가정
maintenance_cost = buying_price * 0.002 # 보유세/유지비 0.2% 가정

# [월세 비용 계산]
# 남은 현금 = 내 돈 - 보증금 (음수면 0)
surplus_cash_monthly = max(0, my_money - monthly_deposit)
# 남은 현금으로 버는 돈 (투자 수익)
investment_profit_monthly = surplus_cash_monthly * stock_return

# 총 비용 = 1년 월세 + (보증금 기회비용: 보증금만큼 투자를 못 했으므로 손해)
# *수정: 더 직관적인 비교를 위해 '순수 지출' 관점에서 계산
# 지출: 1년치 월세
# 기회비용 손실: 보증금 * 수익률
cost_monthly = (monthly_rent * 12) + (monthly_deposit * stock_return)


# [전세 비용 계산]
loan_needed_jeonse = max(0, jeonse_deposit - my_money) # 대출 필요액
my_money_in_jeonse = min(jeonse_deposit, my_money)     # 묶인 내 돈
surplus_cash_jeonse = max(0, my_money - jeonse_deposit) # 전세 내고도 남은 돈

# 남은 돈 투자 수익
investment_profit_jeonse = surplus_cash_jeonse * stock_return

# 비용 = 대출이자 + 내 돈의 기회비용
cost_jeonse = (loan_needed_jeonse * loan_rate) + (my_money_in_jeonse * stock_return)


# [매매 비용 계산]
loan_needed_buying = max(0, buying_price - my_money)
my_money_in_buying = min(buying_price, my_money)

# 비용 = 대출이자 + 내 돈 기회비용 + 세금 - 집값상승분
capital_gain = buying_price * house_growth
cost_buying = (loan_needed_buying * loan_rate) + \
              (my_money_in_buying * stock_return) + \
              maintenance_cost - capital_gain


# --- 3. 결과 출력 ---
st.divider()

# 12. 텍스트 변경 (기회비용)
st.subheader("📊 1년 간 진짜 사라지는 비용 (기회비용 포함)")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="월세 선택 시", value=f"{int(cost_monthly)} 만원")
    # 13. 남은 돈 수익률 표시
    if surplus_cash_monthly > 0:
        st.caption(f"➕ 남은 돈 {format_currency(surplus_cash_monthly)} 굴려서\n연 {int(investment_profit_monthly)}만원 수익 가능")

with col2:
    diff_jeonse = int(cost_monthly - cost_jeonse)
    st.metric(label="전세 선택 시", value=f"{int(cost_jeonse)} 만원", delta=diff_jeonse)
    # 13. 남은 돈 수익률 표시
    if surplus_cash_jeonse > 0:
        st.caption(f"➕ 남은 돈 {format_currency(surplus_cash_jeonse)} 굴려서\n연 {int(investment_profit_jeonse)}만원 수익 가능")
    elif loan_needed_jeonse > 0:
        st.caption(f"➖ 대출 {format_currency(loan_needed_jeonse)} 발생\n(이자 연 {int(loan_needed_jeonse * loan_rate)}만원)")

with col3:
    diff_buying = int(cost_monthly - cost_buying)
    st.metric(label="매매 선택 시", value=f"{int(cost_buying)} 만원", delta=diff_buying)
    st.caption(f"📈 집값 변동: {int(capital_gain)}만원\n(세금/유지비 포함)")

# --- 4. 판단 및 조언 ---
best_choice = min(cost_monthly, cost_jeonse, cost_buying)

st.info("💡 해석: 빨간색 숫자가 작을수록(혹은 마이너스가 클수록) 이성적인 선택입니다.")

if best_choice == cost_buying:
    st.success(f"결론: **매매**가 가장 유리합니다. 집값 상승분({int(capital_gain)}만원)이 기회비용을 상쇄했습니다.")
elif best_choice == cost_jeonse:
    st.warning("결론: **전세**가 가장 유리합니다. 투자를 공격적으로 하지 않는다면 전세가 답일 수 있습니다.")
else:
    st.error("결론: **월세**가 정답입니다. 보증금을 최소화하고 그 돈으로 투자를 하세요!")
