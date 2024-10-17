import streamlit as st
#to run streamlit, do not click run button. In the shell, type: streamlit run [filename].py
#set the app title
st.title('My first streamlit app')

st.write('Welcome to my first streamlit app')

#Display a button
st.button("Reset", type="primary")
if st.button("Say Hello"):
  st.write("CHUMIMINNNNNNN")
else: #else means before even click the button
  st.write("chumimin.....")