import streamlit as st
import instaloader
import tempfile
import os
from zipfile import ZipFile
from pathlib import Path

st.set_page_config(page_title="Instagram Story Downloader", page_icon="📸")

st.title("📸 Instagram Story Downloader")

st.write("Log in to your Instagram account and download stories from any public or followed private account.")

# --- Input form ---
with st.form("login_form"):
    col1, col2 = st.columns(2)
    with col1:
        ig_username = st.text_input("Your Instagram username", key="username")
    with col2:
        ig_password = st.text_input("Your Instagram password", type="password", key="password")
    target_username = st.text_input("Target Instagram username", key="target")

    submitted = st.form_submit_button("Download Stories")

if submitted:
    if not ig_username or not ig_password or not target_username:
        st.error("Please fill in all fields.")
    else:
        L = instaloader.Instaloader(dirname_pattern=tempfile.mkdtemp())

        with st.spinner("Logging in to Instagram..."):
            try:
                L.login(ig_username, ig_password)
                st.success(f"Logged in as {ig_username}")
            except Exception as e:
                st.error(f"Login failed: {e}")
                st.stop()

        try:
            profile = instaloader.Profile.from_username(L.context, target_username)
        except Exception as e:
            st.error(f"Failed to find target user: {e}")
            st.stop()

        story_items = []
        for story in L.get_stories(userids=[profile.userid]):
            for item in story.get_items():
                story_items.append(item)

        if not story_items:
            st.info("No active stories found for this user.")
            st.stop()

        st.success(f"Found {len(story_items)} story items.")
        temp_dir = Path(tempfile.mkdtemp())
        zip_path = temp_dir / f"{target_username}_stories.zip"

        with ZipFile(zip_path, 'w') as zipf:
            for idx, item in enumerate(story_items, 1):
                st.write(f"📅 {item.date_utc}")
                if item.is_video:
                    video_path = temp_dir / f"story_{idx}.mp4"
                    L.download_storyitem(item, str(video_path.parent))
                    for f in video_path.parent.glob("*.mp4"):
                        zipf.write(f, arcname=f.name)
                        st.video(str(f))
                        f.unlink()
                else:
                    img_path = temp_dir / f"story_{idx}.jpg"
                    L.download_storyitem(item, str(img_path.parent))
                    for f in img_path.parent.glob("*.jpg"):
                        zipf.write(f, arcname=f.name)
                        st.image(str(f))
                        f.unlink()

        with open(zip_path, 'rb') as zf:
            st.download_button(
                label="📥 Download all stories as ZIP",
                data=zf,
                file_name=f"{target_username}_stories.zip",
                mime="application/zip"
            )

        st.balloons()