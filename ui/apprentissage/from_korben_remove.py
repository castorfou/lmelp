# https://www.youtube.com/watch?v=7pbhs1jLhRA

# un script python pour streamlit qui utilise rembg pour enlever l'arrière plan d'une image
# https://github.com/danielgatis/rembg

# on choppe les images sous unsplash


import streamlit as st
from PIL import Image
from rembg import remove
from io import BytesIO


st.set_page_config(
    page_title="rimouveur de la mort",
    page_icon=":skull:",
    layout="wide",
    initial_sidebar_state="auto",
)

st.write("## Rimouveur de la mort")
st.write("débarrassez vous de l'arrière plan de vos images en un clic")
st.sidebar.write("## uploader")

col1, col2 = st.columns(2)


def convert_image(image):
    buf = BytesIO()
    image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im


def fix_image(image):
    image = Image.open(image)
    col1.write("Image originale")
    col1.image(image)
    fixed = remove(image)
    col2.write("Image détourée")
    col2.image(fixed)
    st.sidebar.write("\\n")
    st.sidebar.download_button(
        "Telecharger l'image détourée",
        convert_image(fixed),
        file_name="image_detouree.png",
        mime="image/png",
    )


# on charge l'image
image_upload = st.sidebar.file_uploader(
    "Choisissez une image", type=["png", "jpg", "jpeg"]
)

if image_upload is not None:
    fix_image(image_upload)
else:
    fix_image("ui/oiseau.jpg")
