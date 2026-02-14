# 카드 HTML 생성 함수 (공백 문제 수정본)
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

    # 1. 굴리는 돈 수식
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

    # 최종 HTML 조립 (중요: 들여쓰기 제거)
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
