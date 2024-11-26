import streamlit as st
from auth.register import register_user
from auth.Login import login
from auth.Logout import logout
from features.github_clone import github_clone

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False


login_page=st.Page(login,title='Login',icon=':material/login:')
register_page=st.Page(register_user,title='Register',icon=':material/person_add:')
logout_page=st.Page(logout,title='Logout',icon=':material/logout:')

welcome_page=st.Page(github_clone,title='Welcome',icon=':material/home:')

if st.session_state.logged_in:
    pg=st.navigation({
        "Features":[welcome_page],
        "Account":[logout_page]})
    
else:
    pg=st.navigation([login_page,register_page])

st.set_page_config(page_title='Open Source Code Agent',page_icon=':material/lock:')
pg.run()

