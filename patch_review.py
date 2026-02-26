content = open('/Users/regulatorsnation/Desktop/focus/focus_app.py', encoding='utf-8').read()

old = '''            st.markdown(f"""
            <div class="ob-card">
                <div class="ob-icon">&#10003;</div>
                <div class="ob-title">Review Your Accounts</div>
                <div class="ob-sub">Everything look right?</div>
                {rows}
            </div>""", unsafe_allow_html=True)'''

new = '''            st.markdown("""
            <div class="ob-card">
                <div class="ob-icon">&#10003;</div>
                <div class="ob-title">Review Your Accounts</div>
                <div class="ob-sub">Everything look right?</div>
            </div>""", unsafe_allow_html=True)
            for a in st.session_state.ob_accounts:
                dot = {"green":"#30d158","yellow":"#ffd60a","red":"#ff453a"}.get(a["health"],"#555")
                st.markdown(f\'\'\'<div class="ob-row">
                    <div class="ob-row-name">{a[\'icon\']}&nbsp;&nbsp;{a[\'name\']}</div>
                    <div class="ob-row-vals"><span class="ob-row-bal">${a[\'balance\']:,.2f}</span><br>goal ${a[\'goal\']:,.0f} <span style="color:{dot}">&#9679;</span></div>
                </div>\'\'\', unsafe_allow_html=True)'''

content = content.replace(old, new)
open('/Users/regulatorsnation/Desktop/focus/focus_app.py', 'w', encoding='utf-8').write(content)
print("Patched!" if old in open('/Users/regulatorsnation/Desktop/focus/focus_app.py', encoding='utf-8').read() == False else "Done")
