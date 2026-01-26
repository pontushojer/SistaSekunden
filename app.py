from sl_api import get_all_departures, BUFFER_MIN
import streamlit as st
from datetime import datetime

RUN_EVERY = "30s"

def get_color(time):
    if time <= 0:
        return "red"
    elif time <= 2:
        return "orange"
    elif time <= 4:
        return "yellow"
    else:
        return "green"

def update_run_cycle():
    # Update the RUN_EVERY variable based on the time of day:
    # - Rush hour on weekdays (6am-10am): 30s
    # - Rush hour on weekend (6am-10am): 1m
    # - Normal hours (10am-8pm): 1m
    # - Low traffic hours (8pm-6am): 5m
    global RUN_EVERY
    now = datetime.now()
    if now.hour >= 6 and now.hour < 10:
        if now.weekday() < 5:
            RUN_EVERY = "30s"
        else:
            RUN_EVERY = "1m"
    elif now.hour >= 10 and now.hour < 20:
        RUN_EVERY = "1m"
    else:
        RUN_EVERY = "5m"
    

st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="SistaSekunden",
    page_icon="🚶",
    # Make the content take up the width of the page:
    layout="wide",
)

# Custom CSS
# https://discuss.streamlit.io/t/how-do-you-change-the-background-of-a-container/115043/2
css = """
.stVerticalBlock {}
div[class*='blue-container'],div[class^='blue-container'] {
    background-color: #080816ff;
}
"""

st.html(f"<style>{css}</style>")

@st.fragment(run_every="30s")
def departure_board():
    departures = get_all_departures()

    n = 0
    for d in departures:
        if d.is_too_late():
            continue
        
        with st.container(gap="small", border=True, key=f"blue-container-{n}"):
            cols = st.columns(4, gap="xsmall", width="stretch")
            
            with cols[0]:
                st.markdown(f"**:blue[{d.stop_name}]**")
                st.markdown(f"{d.line}")
                st.markdown(f"*{d.destination}*")

            with cols[1]:
                st.metric(
                    label="Avgår om", 
                    value=f"{d.departure_minutes} min", 
                )
            
            with cols[2]:
                if d.walk_leave_in >= -BUFFER_MIN:
                    st.metric(
                        label="Gå om 🚶", 
                        value=f":{get_color(d.walk_leave_in)}[{d.walk_leave_in} min]", 
                    )
            with cols[3]:
                if d.bike_leave_in >= -BUFFER_MIN:
                    st.metric(
                        label="Cykla om 🚴", 
                        value=f":{get_color(d.bike_leave_in)}[{d.bike_leave_in} min]",
                    )
            
            #st.space("small")

            n += 1
            if n >= 5:
                break

    update_run_cycle()
        
# Kör igång brädan
departure_board()

# Statisk info som aldrig behöver laddas om (t.ex. väder eller påminnelser)
st.divider()
st.caption(f"Senast uppdaterad: {datetime.now().strftime('%H:%M:%S')} (updates every {RUN_EVERY})")