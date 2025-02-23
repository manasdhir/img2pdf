import streamlit as st
from PIL import Image
from io import BytesIO
import hashlib
from streamlit_sortables import sort_items

# Title
st.title("📸 Image to PDF Converter")

if "images" not in st.session_state:
    st.session_state.images = []

if "image_hashes" not in st.session_state:
    st.session_state.image_hashes = {}

def get_image_hash(img):
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    return hashlib.md5(img_bytes.getvalue()).hexdigest()

def add_image(img):
    img_hash = get_image_hash(img)

    if img_hash not in st.session_state.image_hashes:
        unique_name = f"Image_{len(st.session_state.images) + 1}.png"
        st.session_state.images.append((unique_name, img))
        st.session_state.image_hashes[img_hash] = unique_name

captured_image = st.camera_input("Capture an image")

if captured_image:
    img = Image.open(captured_image).convert("RGB")
    st.image(img, caption="Captured Image", use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Keep Photo"):
            add_image(img)
            st.success("Photo added!")
            st.rerun()
    with col2:
        if st.button("🗑️ Delete Photo"):
            st.warning("Photo discarded!")

if st.session_state.images:
    st.subheader("🗂 Reorder & Manage Images")
    
    image_ids = [name for name, _ in st.session_state.images]
    
    reordered_ids = sort_items(image_ids)

    reordered_images = [img for name in reordered_ids for img_name, img in st.session_state.images if img_name == name]
    st.session_state.images = list(zip(reordered_ids, reordered_images))

    for idx, (img_name, img) in enumerate(st.session_state.images):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.image(img, caption=f"{img_name}", use_container_width=True)
        with col2:
            if st.button(f"🗑️ Delete", key=f"delete_{idx}"):
                img_hash = get_image_hash(img)
                del st.session_state.image_hashes[img_hash]
                st.session_state.images.pop(idx)
                st.rerun()  

if st.session_state.images and st.button("📝 Convert to PDF"):
    pdf_bytes = BytesIO()
    images_only = [img for _, img in st.session_state.images]
    images_only[0].save(pdf_bytes, format="PDF", save_all=True, append_images=images_only[1:])
    pdf_bytes.seek(0)  

    st.download_button(
        label="📥 Download PDF",
        data=pdf_bytes,
        file_name="converted.pdf",
        mime="application/pdf"
    )