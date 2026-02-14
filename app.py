import streamlit as st

# 페이지 설정
st.set_page_config(page_title="이성적 주거 판단기", layout="centered")

st.title("🏠 전세 vs 월세 vs 매매: 이성적 판단기")
st.markdown("감정을 배제하고, **기회비용(미국 주식 투자)**과 **금융 비용**만으로 계산합니다.")

# --- 1. 입력 섹션 (Sidebar) ---
st.sidebar.header("1. 자산 및 시장 가정")
my_money = st.sidebar.number_input("내 가용 현금 (만원)", value=20000, step=1000)
stock_return = st.sidebar.slider("나의 기대 투자 수익률 (%, 미국주식 등)", 0.0, 20.0, 8.0) / 100
loan_rate = st.sidebar.slider("대출 금리 (%)", 0.0, 10.0, 4.0) / 100

st.sidebar.header("2. 매물 정보 입력")
# 월세 정보
st.sidebar.subheader("[월세]")
monthly_deposit = st.sidebar.number_input("월세 보증금 (만원)", value=5000)
monthly_rent = st.sidebar.number_input("월세 (만원)", value=100)

# 전세 정보
st.sidebar.subheader("[전세]")
jeonse_deposit = st.sidebar.number_input("전세 보증금 (만원)", value=30000)

# 매매 정보
st.sidebar.subheader("[매매]")
buying_price = st.sidebar.number_input("매매 가격 (만원)", value=50000)
house_growth = st.sidebar.slider("예상 집값 상승률 (연 %)", -5.0, 10.0, 2.0) / 100
acquisition_tax = buying_price * 0.011 # 취득세 대략 1.1% 가정

# --- 2. 계산 로직 (기회비용의 핵심) ---
# [월세 비용] = 1년치 월세 + (보증금 못 굴린 손해)
cost_monthly = (monthly_rent * 12) + (monthly_deposit * stock_return)

# [전세 비용] = (부족분 대출 이자) + (내 돈 못 굴린 손해)
loan_needed_jeonse = max(0, jeonse_deposit - my_money)
my_money_in_jeonse = min(jeonse_deposit, my_money)
cost_jeonse = (loan_needed_jeonse * loan_rate) + (my_money_in_jeonse * stock_return)

# [매매 비용] = (대출 이자) + (내 돈 못 굴린 손해) + (재산세/유지비) - (집값 상승분)
loan_needed_buying = max(0, buying_price - my_money)
my_money_in_buying = min(buying_price, my_money)
maintenance_cost = buying_price * 0.002 # 유지보수비/세금 0.2% 가정
capital_gain = buying_price * house_growth # 집값 상승 이익

cost_buying = (loan_needed_buying * loan_rate) + \
              (my_money_in_buying * stock_return) + \
              maintenance_cost - capital_gain

# --- 3. 결과 출력 ---
st.divider()

st.subheader("📊 1년 간 진짜 사라지는 비용 (기회비용 포함)")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="월세 선택 시", value=f"{int(cost_monthly)} 만원")
with col2:
    st.metric(label="전세 선택 시", value=f"{int(cost_jeonse)} 만원", delta=int(cost_monthly - cost_jeonse))
with col3:
    st.metric(label="매매 선택 시", value=f"{int(cost_buying)} 만원", delta=int(cost_monthly - cost_buying))

# 판단 로직
best_choice = min(cost_monthly, cost_jeonse, cost_buying)

st.info("💡 해석: 빨간색 숫자가 작을수록 이성적인 선택입니다.")
if best_choice == cost_buying:
    st.success(f"결론: **매매**가 가장 유리합니다. 집값 상승분({int(capital_gain)}만원)이 기회비용을 상쇄했습니다.")
elif best_choice == cost_jeonse:
    st.warning("결론: **전세**가 가장 유리합니다. 투자를 잘 못한다면 전세가 답일 수 있습니다.")
else:
    st.error("결론: **월세**가 정답입니다. 보증금을 줄이고 그 돈으로 미국 주식을 사세요!")