import streamlit as st

st.set_page_config(
    page_title="le masque et la plume",
    page_icon=":book:",
    layout="wide",
    initial_sidebar_state="auto",
)

st.write("## Quel critique du masque etes-vous ?")
st.write(
    "découvrez quel critique du masque vous êtes en fonction de vos gouts littéraires"
)

st.page_link("lmelp.py", label="Home", icon="🏠")

# https://fonts.google.com/icons?selected=Material+Symbols+Outlined:music_note:FILL@0;wght@400;GRAD@0;opsz@24&icon.query=music&icon.size=24&icon.color=%235f6368

st.page_link("pages/1_st_episodes.py", label="episodes", icon=":material/music_note:")
st.page_link("pages/2_st_auteurs.py", label="auteurs", icon=":material/person:")
st.page_link("pages/3_st_livres.py", label="livres", icon=":material/menu_book:")
