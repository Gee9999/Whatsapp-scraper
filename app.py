import streamlit as st
from scraper.whatsapp import WhatsAppScraper

st.set_page_config(page_title="Proto WhatsApp Scraper", layout="wide")

st.title("Proto WhatsApp Image Scraper")

if "scraper" not in st.session_state:
    st.session_state.scraper = WhatsAppScraper()

if st.button("Open WhatsApp Web"):
    st.session_state.scraper.open_whatsapp()

if st.button("Scrape Images"):
    st.session_state.scraper.scrape_images()

st.write("Images will be saved to the exports/ folder.")
