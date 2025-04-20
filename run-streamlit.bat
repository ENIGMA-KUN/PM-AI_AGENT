@echo off
call C:\Users\chakr\Anaconda3\Scripts\activate.bat pm-agent
cd streamlit-frontend
streamlit run app.py
pause
