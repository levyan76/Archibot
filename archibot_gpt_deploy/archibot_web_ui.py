
import streamlit as st
from archibot_bot import Archibot
import fitz
import tempfile
import os

st.set_page_config(page_title="Archibot GPT", layout="centered")
st.title("📄 Analyseur de Devis / Plans - Archibot")

uploaded_file = st.file_uploader("Téléversez un fichier PDF", type="pdf")
bot = Archibot()

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    if st.button("Analyser et surligner"):
        with st.spinner("Analyse en cours..."):
            bot.extract_and_highlight_sections(tmp_path)
            st.success("Analyse terminée. Les fichiers PDF annotés sont enregistrés localement.")

    with fitz.open(tmp_path) as doc:
        st.subheader("Prévisualisation du fichier")
        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            img_path = os.path.join(tempfile.gettempdir(), f"page_{i}.png")
            pix.save(img_path)
            st.image(img_path, caption=f"Page {i+1}", use_column_width=True)

    with open(tmp_path, "rb") as f:
        st.download_button("📥 Télécharger le PDF original", f, file_name=uploaded_file.name)
