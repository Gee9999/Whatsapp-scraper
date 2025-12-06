import os
import streamlit as st

from scraper.engine import WhatsAppPhotoScraper, ScrapeMode

st.set_page_config(
    page_title="Proto WhatsApp Photo Saver",
    page_icon="📸",
    layout="centered"
)

# --- Splash / Header ---
st.title("📸 Proto WhatsApp Photo Saver")
st.caption("Fast mode – scrape recent photos from selected contacts on WhatsApp Web.")

st.markdown(
    "1. Make sure **Google Chrome** is installed.  
"
    "2. When prompted, a Chrome window will open on **web.whatsapp.com**.  
"
    "3. **Scan the QR code** with your phone to log in.  
"
    "4. Come back here to choose contacts and save photos."
)

# --- Export directory selection ---
default_export = os.path.join(os.path.expanduser("~"), "Pictures", "WhatsApp_Photos")
export_dir = st.text_input("Save photos to this folder:", default_export)

if not export_dir:
    st.stop()

# --- Fast mode settings (fixed for Option A) ---
st.subheader("Scrape Mode: Fast (recent history only)")
st.caption("This mode scrolls through a limited portion of each chat to grab recent photos quickly.")

max_scrolls = st.slider(
    "How deep to scroll per chat (higher = more history, slower):",
    min_value=5,
    max_value=60,
    value=25,
    help="Each step scrolls the chat a bit upwards to load older messages."
)

# --- Start browser / connect section ---
if "scraper" not in st.session_state:
    st.session_state.scraper = None
if "contacts" not in st.session_state:
    st.session_state.contacts = []

start_col1, start_col2 = st.columns([1, 2])

with start_col1:
    start_clicked = st.button("🚀 Launch WhatsApp Web", type="primary")
with start_col2:
    st.write("First launch opens WhatsApp Web in a Chrome window. Scan the QR code there, then return here.")

log_box = st.empty()

def log(msg: str):
    log_box.write(msg)

if start_clicked:
    os.makedirs(export_dir, exist_ok=True)
    log("Starting Chrome and opening WhatsApp Web…")
    scraper = WhatsAppPhotoScraper(download_root=export_dir, log_callback=log)
    try:
        scraper.start()
        st.session_state.scraper = scraper
        log("✅ Chrome started. Please scan the QR code in the WhatsApp Web window.")
    except Exception as e:
        log(f"❌ Failed to start browser: {e}")

# --- Load contacts ---
if st.session_state.scraper:
    if st.button("📒 Load WhatsApp Contacts"):
        try:
            contacts = st.session_state.scraper.get_contacts()
            st.session_state.contacts = contacts
            if contacts:
                st.success(f"Found {len(contacts)} contacts/chats.")
            else:
                st.warning("No contacts found. Make sure your WhatsApp chat list is visible.")
        except Exception as e:
            st.error(f"Error while reading contacts: {e}")

# --- Contact selection UI ---
contacts = st.session_state.contacts
if contacts:
    st.subheader("Choose who to scrape")
    mode = st.radio(
        "Scrape mode",
        [ScrapeMode.SINGLE.value, ScrapeMode.MULTI.value, ScrapeMode.EXCLUDE.value],
        format_func=lambda v: {
            ScrapeMode.SINGLE.value: "Single contact",
            ScrapeMode.MULTI.value: "Multiple contacts",
            ScrapeMode.EXCLUDE.value: "All except selected"
        }[v]
    )

    selected_contacts = []

    if mode == ScrapeMode.SINGLE.value:
        contact = st.selectbox("Select contact", options=contacts)
        if contact:
            selected_contacts = [contact]

    elif mode == ScrapeMode.MULTI.value:
        selected_contacts = st.multiselect("Select one or more contacts", options=contacts)

    else:  # EXCLUDE
        excluded = st.multiselect("Select contacts to EXCLUDE", options=contacts)
        selected_contacts = [c for c in contacts if c not in excluded]

    # --- Run scraping ---
    if selected_contacts:
        st.markdown("---")
        st.subheader("Run Scraper")
        run_clicked = st.button("💾 Save Photos Now", type="primary")
        progress = st.progress(0, text="Waiting to start…")
        status_box = st.empty()

        if run_clicked:
            scraper = st.session_state.scraper
            total_saved = 0
            total_targets = len(selected_contacts)

            for idx, contact in enumerate(selected_contacts, start=1):
                progress.progress(idx / total_targets, text=f"Scraping {contact} ({idx}/{total_targets})…")
                status_box.write(f"Opening chat with **{contact}** and scanning for photos…")

                try:
                    saved_for_contact = scraper.scrape_contact_photos(
                        contact_name=contact,
                        max_scroll_steps=max_scrolls
                    )
                    total_saved += saved_for_contact
                    status_box.write(f"✅ {contact}: saved {saved_for_contact} photos.")
                except Exception as e:
                    status_box.write(f"❌ Error scraping {contact}: {e}")

            progress.progress(1.0, text="Done!")
            st.success(f"Finished. Total photos saved: {total_saved}")
            st.info(f"Photos are saved under: `{export_dir}`")
else:
    st.info("Load contacts after launching WhatsApp Web to select which chats to scrape.")
