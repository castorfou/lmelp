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
st.title("rimouveur de la mort")

# on charge l'image
image_upload = st.file_uploader("Choisissez une image", type=["png", "jpg", "jpeg"])


def convert_image(image):
    buf = BytesIO()
    image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im


if image_upload:
    st.image(image_upload)
    image = Image.open(image_upload)
    fixed = remove(image)
    downloadable_image = convert_image(fixed)
    st.image(downloadable_image)

    st.download_button(
        "image detouree",
        downloadable_image,
        file_name="image_detouree.png",
        mime="image/png",
    )
