import streamlit as st
import threading
from scraper.whatsapp import open_whatsapp_and_prepare

st.set_page_config(page_title="Proto WhatsApp Selenium", page_icon="💬")

st.title("💬 Proto WhatsApp Scraper (Selenium, basic)")

st.write(
    "1️⃣ Click the button below to open WhatsApp Web in Chrome.\n"
    "2️⃣ Scan the QR code.\n"
    "3️⃣ Click the chat whose photos you eventually want to download.\n\n"
    "Right now this version only opens WhatsApp reliably. We’ll add the photo download step next."
)

def run_selenium():
    open_whatsapp_and_prepare()

if st.button("Open WhatsApp Web"):
    st.success("Launching Chrome with WhatsApp Web…")
    threading.Thread(target=run_selenium, daemon=True).start()
else:
    st.info("Waiting for you to click the button…")
