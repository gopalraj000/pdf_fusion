import streamlit as st
import os
import tempfile
import time
from datetime import datetime, timedelta
import uuid

# Import custom modules
from modules.pdf_operations import PDFOperations
from modules.ocr_processor import OCRProcessor
from modules.converters import DocumentConverter
from modules.utilities import UIUtilities, QRGenerator
from modules.file_manager import FileManager

def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="Professional Document Processor",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'file_manager' not in st.session_state:
        st.session_state.file_manager = FileManager()
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'admin_password' not in st.session_state:
        st.session_state.admin_password = "admin123"  # Change this to your desired password
    if 'home_button_url' not in st.session_state:
        st.session_state.home_button_url = "https://www.google.com"  # Default home URL
    
    # Initialize processors
    pdf_ops = PDFOperations()
    ocr_processor = OCRProcessor()
    converter = DocumentConverter()
    ui_utils = UIUtilities()
    qr_gen = QRGenerator()
    
    # Header with Home Button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("📄 Professional Document Processor")
        st.markdown("Advanced PDF, Word, and Image conversion and manipulation tool")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        if st.button("🏠 Home", use_container_width=True, type="primary"):
            st.markdown(f'<script>window.open("{st.session_state.home_button_url}", "_blank");</script>', unsafe_allow_html=True)
            st.success(f"Opening: {st.session_state.home_button_url}")
    
    # Top controls
    col1, col2, col3 = st.columns([8, 1, 1])
    
    with col2:
        # Three dots menu for admin options and settings
        if st.button("⋮", help="Settings & Admin"):
            st.session_state.show_admin_menu = not st.session_state.get('show_admin_menu', False)
        
        if st.session_state.get('show_admin_menu', False):
            with st.container():
                # Dark mode toggle inside menu
                if st.button("🌓 Toggle Mode", use_container_width=True):
                    st.session_state.dark_mode = not st.session_state.dark_mode
                    st.rerun()
                
                mode_text = "Dark Mode" if st.session_state.dark_mode else "Light Mode"
                st.write(f"Current: {mode_text}")
                
                st.markdown("---")
                
                if not st.session_state.is_admin:
                    admin_password = st.text_input("🔐 Admin Password:", type="password", key="admin_login", placeholder="Enter admin password")
                    if admin_password == st.session_state.admin_password:
                        st.session_state.is_admin = True
                        st.session_state.show_admin_menu = False
                        st.success("✅ Admin login successful!")
                        st.rerun()
                    elif admin_password:
                        st.error("❌ Invalid password")
                else:
                    st.success("👨‍💼 Admin Mode Active")
                    if st.button("🔓 Logout", key="admin_logout"):
                        st.session_state.is_admin = False
                        st.session_state.show_admin_menu = False
                        st.rerun()
    
    # Sidebar navigation
    st.sidebar.title("🔧 Tools")
    
    # Prominent File Transfer button
    if st.sidebar.button("🔄 File Transfer", use_container_width=True, type="primary"):
        st.session_state.selected_tool = "🔄 File Transfer"
    
    st.sidebar.markdown("---")
    
    tool_options = [
        "📄 PDF to Searchable PDF (OCR)",
        "🔗 Merge PDFs",
        "✂️ Split PDF",
        "📝 PDF to Word",
        "📄 Word to PDF",
        "🖼️ PDF to Images",
        "📄 Images to PDF",
        "🗜️ Compress PDF",
        "🔄 Reorder PDF Pages",
        "🔒 Password Protect/Unlock PDF",
        "🖼️ Extract Images from PDF",
        "📝 Extract Text from PDF",
        "📦 Batch Processing"
    ]
    
    # Add admin panel option if logged in as admin
    if st.session_state.is_admin:
        tool_options.append("🔧 Admin Panel")
    
    selected_tool = st.sidebar.selectbox("PDF Processing Tools", tool_options)
    
    # Use session state to track selected tool
    if 'selected_tool' not in st.session_state:
        st.session_state.selected_tool = selected_tool
    else:
        # Update only if user selects from dropdown (not file transfer button)
        if selected_tool != st.session_state.get('last_dropdown_selection', ''):
            st.session_state.selected_tool = selected_tool
    
    st.session_state.last_dropdown_selection = selected_tool
    
    # Main content area
    if st.session_state.selected_tool == "🔄 File Transfer":
        handle_file_transfer(ui_utils)
    
    elif st.session_state.selected_tool == "📄 PDF to Searchable PDF (OCR)":
        handle_pdf_ocr(pdf_ops, ocr_processor, ui_utils)
    
    elif selected_tool == "🔗 Merge PDFs":
        handle_pdf_merge(pdf_ops, ui_utils)
    
    elif selected_tool == "✂️ Split PDF":
        handle_pdf_split(pdf_ops, ui_utils)
    
    elif selected_tool == "📝 PDF to Word":
        handle_pdf_to_word(converter, ui_utils)
    
    elif selected_tool == "📄 Word to PDF":
        handle_word_to_pdf(converter, ui_utils)
    
    elif selected_tool == "🖼️ PDF to Images":
        handle_pdf_to_images(converter, ui_utils)
    
    elif selected_tool == "📄 Images to PDF":
        handle_images_to_pdf(converter, ui_utils)
    
    elif selected_tool == "🗜️ Compress PDF":
        handle_pdf_compress(pdf_ops, ui_utils)
    
    elif selected_tool == "🔄 Reorder PDF Pages":
        handle_pdf_reorder(pdf_ops, ui_utils)
    
    elif selected_tool == "🔒 Password Protect/Unlock PDF":
        handle_pdf_password(pdf_ops, ui_utils)
    
    elif selected_tool == "🖼️ Extract Images from PDF":
        handle_extract_images(pdf_ops, ui_utils)
    
    elif selected_tool == "📝 Extract Text from PDF":
        handle_extract_text(pdf_ops, ocr_processor, ui_utils)
    
    elif selected_tool == "📦 Batch Processing":
        handle_batch_processing(pdf_ops, converter, ui_utils)
    
    elif selected_tool == "🔄 File Transfer":
        handle_file_transfer(ui_utils)
    
    elif selected_tool == "🔧 Admin Panel":
        handle_admin_panel(ui_utils)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Note:** Files are temporarily stored and automatically deleted after 30 minutes.")
    
    # Cleanup expired files
    st.session_state.file_manager.cleanup_expired_files()

def handle_admin_panel(ui_utils):
    """Handle admin panel functionality"""
    st.header("🔧 Admin Panel")
    st.markdown("**Admin Dashboard** - View and manage all files with 48-hour retention")
    
    # Get all files
    all_files = st.session_state.file_manager.get_all_files()
    
    if not all_files:
        st.info("📁 No files currently stored in the system.")
        return
    
    # Display file statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_files = len(all_files)
        st.metric("Total Files", total_files)
    
    with col2:
        total_size = sum(file_info['size'] for file_info in all_files.values()) / (1024 * 1024)
        st.metric("Total Size (MB)", f"{total_size:.2f}")
    
    with col3:
        admin_files = sum(1 for file_info in all_files.values() if file_info.get('is_admin', False))
        st.metric("Admin Files", admin_files)
    
    st.markdown("---")
    
    # Home Button URL Configuration
    st.subheader("🏠 Home Button Settings")
    with st.expander("Configure Home Button"):
        new_home_url = st.text_input(
            "Home Button URL:",
            value=st.session_state.home_button_url,
            placeholder="https://www.example.com",
            help="Set the URL that opens when users click the Home button"
        )
        
        if st.button("🔄 Update Home URL", key="update_home_url"):
            if new_home_url:
                st.session_state.home_button_url = new_home_url
                st.success(f"✅ Home button URL updated to: {new_home_url}")
                st.rerun()
            else:
                st.warning("⚠️ Please enter a valid URL")
        
        st.info(f"Current Home URL: {st.session_state.home_button_url}")
    
    st.markdown("---")
    
    # File management table
    st.subheader("📋 File Management")
    
    for file_id, file_info in all_files.items():
        with st.expander(f"📄 {file_info['original_name']} ({file_info['size'] / (1024 * 1024):.2f} MB)"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**Created:** {file_info['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Expires:** {file_info['expires_at'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            with col2:
                st.write(f"**Type:** {'Admin' if file_info.get('is_admin', False) else 'User'}")
                st.write(f"**File ID:** {file_id[:8]}...")
            
            with col3:
                # Download button
                if os.path.exists(file_info['path']):
                    with open(file_info['path'], "rb") as f:
                        file_data = f.read()
                    st.download_button(
                        label="📥 Download",
                        data=file_data,
                        file_name=file_info['original_name'],
                        key=f"admin_download_{file_id}"
                    )
            
            with col4:
                # Delete button
                if st.button("🗑️ Delete", key=f"delete_{file_id}"):
                    if st.session_state.file_manager.delete_file(file_id):
                        st.success(f"✅ Deleted {file_info['original_name']}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete file")

def handle_file_transfer(ui_utils):
    """Handle file transfer with 4-digit codes"""
    st.header("🔄 File Transfer")
    st.markdown("Share files securely using 4-digit codes - valid for 24 hours")
    
    tab1, tab2 = st.tabs(["📤 Send File", "📥 Receive File"])
    
    with tab1:
        st.subheader("📤 Send File")
        st.markdown("Upload a file and get a 4-digit code to share")
        
        uploaded_file = st.file_uploader(
            "Choose file to share", 
            type=['pdf', 'docx', 'doc', 'txt', 'png', 'jpg', 'jpeg', 'zip'],
            key="transfer_upload"
        )
        
        if uploaded_file:
            st.write(f"📄 **File:** {uploaded_file.name}")
            st.write(f"📊 **Size:** {len(uploaded_file.getvalue()) / (1024 * 1024):.2f} MB")
            
            if st.button("🔗 Generate Transfer Code", key="generate_code"):
                try:
                    transfer_code = st.session_state.file_manager.create_transfer_code(uploaded_file)
                    
                    st.success(f"✅ Transfer code generated successfully!")
                    
                    # Display code prominently
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        ### 🔢 Transfer Code
                        # {transfer_code}
                        **Valid for 24 hours**
                        """)
                    
                    with col2:
                        # Generate QR code with direct download capability
                        try:
                            import qrcode
                            from io import BytesIO
                            import base64
                            
                            # Create direct download QR for ALL files
                            file_data = uploaded_file.getvalue()
                            file_size = len(file_data)
                            
                            # Always create direct download QR
                            file_b64 = base64.b64encode(file_data).decode()
                            
                            # Create proper data URL with filename for download
                            mime_type = "application/octet-stream"
                            if uploaded_file.name.lower().endswith('.pdf'):
                                mime_type = "application/pdf"
                            elif uploaded_file.name.lower().endswith(('.jpg', '.jpeg')):
                                mime_type = "image/jpeg"
                            elif uploaded_file.name.lower().endswith('.png'):
                                mime_type = "image/png"
                            elif uploaded_file.name.lower().endswith('.docx'):
                                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            elif uploaded_file.name.lower().endswith('.txt'):
                                mime_type = "text/plain"
                            elif uploaded_file.name.lower().endswith('.zip'):
                                mime_type = "application/zip"
                            
                            # Create direct downloadable data URL with proper filename
                            filename_safe = uploaded_file.name.replace(" ", "_")
                            download_url = f"data:{mime_type};base64,{file_b64}"
                            
                            # Use appropriate QR version based on file size (max 40)
                            if file_size < 50000:  # Under 50KB
                                qr_version = 10
                                box_size = 4
                            elif file_size < 200000:  # Under 200KB
                                qr_version = 20
                                box_size = 3
                            elif file_size < 1000000:  # Under 1MB
                                qr_version = 30
                                box_size = 2
                            else:  # Larger files
                                qr_version = 40
                                box_size = 2
                            
                            qr = qrcode.QRCode(version=qr_version, box_size=box_size, border=1)
                            qr.add_data(download_url)
                            qr.make(fit=True)
                            
                            qr_image = qr.make_image(fill_color="black", back_color="white")
                            img_buffer = BytesIO()
                            qr_image.save(img_buffer, format='PNG')
                            img_buffer.seek(0)
                            
                            st.image(img_buffer, caption="📱 Scan to download directly", width=250)
                            st.success("🔗 Direct download QR code - Scan with any QR reader")
                            st.info(f"📊 File size: {file_size/1024:.1f}KB")
                                
                        except Exception as e:
                            st.error(f"QR generation error: {str(e)}")
                    
                    st.info("💡 Share this code with others to let them download your file")
                    
                except Exception as e:
                    st.error(f"❌ Error generating transfer code: {str(e)}")
    
    with tab2:
        st.subheader("📥 Receive File")
        st.markdown("Enter a 4-digit code to download a shared file")
        
        transfer_code = st.text_input(
            "Enter 4-digit transfer code:",
            max_chars=4,
            placeholder="1234",
            key="download_code"
        )
        
        if transfer_code and len(transfer_code) == 4:
            if st.button("📥 Download File", key="download_transfer"):
                try:
                    file_info = st.session_state.file_manager.get_file_by_code(transfer_code)
                    
                    if file_info:
                        # Check if expired
                        from datetime import datetime
                        if datetime.now() > file_info['expires_at']:
                            st.error("❌ Transfer code has expired")
                        else:
                            # Download file
                            result = st.session_state.file_manager.download_by_code(transfer_code)
                            
                            if result:
                                file_data, filename = result
                                
                                st.success(f"✅ File found: {filename}")
                                
                                # File info
                                st.write(f"📄 **Filename:** {filename}")
                                st.write(f"📊 **Size:** {len(file_data) / (1024 * 1024):.2f} MB")
                                st.write(f"📅 **Shared:** {file_info['created_at'].strftime('%Y-%m-%d %H:%M')}")
                                
                                # Download button
                                st.download_button(
                                    label=f"📥 Download {filename}",
                                    data=file_data,
                                    file_name=filename,
                                    key="transfer_download_btn"
                                )
                                
                                st.info("✅ File downloaded successfully!")
                            else:
                                st.error("❌ Failed to download file")
                    else:
                        st.error("❌ Invalid or expired transfer code")
                        
                except Exception as e:
                    st.error(f"❌ Error downloading file: {str(e)}")

def handle_pdf_ocr(pdf_ops, ocr_processor, ui_utils):
    """Handle PDF OCR functionality"""
    st.header("📄 PDF to Searchable PDF (OCR)")
    st.markdown("Convert scanned PDFs to searchable PDFs using OCR technology.")
    
    uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'], key="ocr_upload")
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            language = st.selectbox("OCR Language", ["Auto Detect", "English", "Hindi", "English + Hindi"])
        
        with col2:
            force_english_numbers = st.checkbox("Force numbers in English", value=True)
        
        if st.button("🔍 Process OCR", key="process_ocr"):
            with st.spinner("Processing OCR... This may take a few minutes."):
                try:
                    # Save uploaded file temporarily
                    temp_input = st.session_state.file_manager.save_uploaded_file(uploaded_file, st.session_state.is_admin)
                    
                    # Process OCR
                    output_path = ocr_processor.process_pdf_ocr(
                        temp_input, 
                        language.lower().replace(" ", "_"),
                        force_english_numbers
                    )
                    
                    if output_path:
                        st.success("✅ OCR processing completed!")
                        
                        # Generate download link
                        download_link = st.session_state.file_manager.create_download_link(
                            output_path, 
                            f"searchable_{uploaded_file.name}"
                        )
                        
                        ui_utils.create_download_section(output_path, f"searchable_{uploaded_file.name}")
                        
                    else:
                        st.error("❌ OCR processing failed. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error during OCR processing: {str(e)}")

def handle_pdf_merge(pdf_ops, ui_utils):
    """Handle PDF merging functionality"""
    st.header("🔗 Merge PDFs")
    st.markdown("Combine multiple PDF files into a single document.")
    
    uploaded_files = st.file_uploader(
        "Upload PDF files to merge", 
        type=['pdf'], 
        accept_multiple_files=True,
        key="merge_upload"
    )
    
    if uploaded_files and len(uploaded_files) > 1:
        st.write(f"📁 {len(uploaded_files)} files selected for merging")
        
        # Display file list
        for i, file in enumerate(uploaded_files):
            st.write(f"{i+1}. {file.name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            add_blank_pages = st.checkbox(
                "Add blank page after odd-page PDFs", 
                value=False,
                help="Ensures each new file starts on a fresh sheet when printing double-sided"
            )
        
        with col2:
            add_bookmarks = st.checkbox("Add bookmarks for each file", value=True)
        
        if st.button("🔗 Merge PDFs", key="merge_pdfs"):
            with st.spinner("Merging PDFs..."):
                try:
                    # Save uploaded files temporarily
                    temp_files = []
                    for file in uploaded_files:
                        temp_path = st.session_state.file_manager.save_uploaded_file(file)
                        temp_files.append(temp_path)
                    
                    # Merge PDFs
                    output_path = pdf_ops.merge_pdfs(
                        temp_files, 
                        add_blank_pages=add_blank_pages,
                        add_bookmarks=add_bookmarks
                    )
                    
                    if output_path:
                        st.success("✅ PDFs merged successfully!")
                        ui_utils.create_download_section(output_path, "merged_document.pdf")
                    else:
                        st.error("❌ PDF merging failed. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error during PDF merging: {str(e)}")
    
    elif uploaded_files and len(uploaded_files) == 1:
        st.warning("⚠️ Please upload at least 2 PDF files to merge.")
    else:
        st.info("👆 Upload multiple PDF files to get started.")

def handle_pdf_split(pdf_ops, ui_utils):
    """Handle PDF splitting functionality"""
    st.header("✂️ Split PDF")
    st.markdown("Split a PDF into multiple documents by page range.")
    
    uploaded_file = st.file_uploader("Upload PDF file to split", type=['pdf'], key="split_upload")
    
    if uploaded_file:
        temp_input = st.session_state.file_manager.save_uploaded_file(uploaded_file)
        
        # Get PDF info
        try:
            page_count = pdf_ops.get_page_count(temp_input)
            st.write(f"📄 Total pages: {page_count}")
            
            # Split options
            split_method = st.radio(
                "Split method:",
                ["Split by page ranges", "Extract specific pages", "Split into equal parts"]
            )
            
            if split_method == "Split by page ranges":
                ranges_input = st.text_input(
                    "Enter page ranges (e.g., 1-5, 8-12, 15-20):",
                    placeholder="1-5, 8-12, 15-20"
                )
                
                if st.button("✂️ Split PDF", key="split_ranges"):
                    if ranges_input:
                        with st.spinner("Splitting PDF..."):
                            try:
                                output_paths = pdf_ops.split_pdf_by_ranges(temp_input, ranges_input)
                                if output_paths:
                                    st.success(f"✅ PDF split into {len(output_paths)} parts!")
                                    for i, path in enumerate(output_paths):
                                        ui_utils.create_download_section(
                                            path, 
                                            f"split_part_{i+1}.pdf"
                                        )
                                else:
                                    st.error("❌ PDF splitting failed.")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    else:
                        st.warning("⚠️ Please enter page ranges.")
            
            elif split_method == "Extract specific pages":
                pages_input = st.text_input(
                    "Enter specific pages (e.g., 1, 3, 5, 8):",
                    placeholder="1, 3, 5, 8"
                )
                
                if st.button("✂️ Extract Pages", key="extract_pages"):
                    if pages_input:
                        with st.spinner("Extracting pages..."):
                            try:
                                output_path = pdf_ops.extract_specific_pages(temp_input, pages_input)
                                if output_path:
                                    st.success("✅ Pages extracted successfully!")
                                    ui_utils.create_download_section(output_path, "extracted_pages.pdf")
                                else:
                                    st.error("❌ Page extraction failed.")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    else:
                        st.warning("⚠️ Please enter page numbers.")
            
            else:  # Split into equal parts
                num_parts = st.number_input("Number of parts:", min_value=2, max_value=20, value=2)
                
                if st.button("✂️ Split into Parts", key="split_parts"):
                    with st.spinner("Splitting PDF..."):
                        try:
                            output_paths = pdf_ops.split_pdf_equal_parts(temp_input, num_parts)
                            if output_paths:
                                st.success(f"✅ PDF split into {len(output_paths)} parts!")
                                for i, path in enumerate(output_paths):
                                    ui_utils.create_download_section(
                                        path, 
                                        f"part_{i+1}.pdf"
                                    )
                            else:
                                st.error("❌ PDF splitting failed.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                            
        except Exception as e:
            st.error(f"❌ Error reading PDF: {str(e)}")

def handle_pdf_to_word(converter, ui_utils):
    """Handle PDF to Word conversion"""
    st.header("📝 PDF to Word")
    st.markdown("Convert PDF documents to editable Word format with OCR support.")
    
    uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'], key="pdf_to_word_upload")
    
    if uploaded_file:
        # OCR Language Selection
        col1, col2 = st.columns(2)
        with col1:
            ocr_language = st.selectbox(
                "🔤 OCR Language:",
                ["English", "Hindi", "English + Hindi"],
                help="Select language for text recognition"
            )
        
        with col2:
            preserve_formatting = st.checkbox("📐 Preserve Formatting", value=True)
            force_english_numbers = st.checkbox("🔢 Convert to English Numbers", value=True)
        
        if st.button("📝 Convert to Word", key="convert_to_word"):
            with st.spinner("Converting PDF to Word..."):
                try:
                    temp_input = st.session_state.file_manager.save_uploaded_file(uploaded_file)
                    
                    # Convert language selection to format expected by converter
                    language_map = {
                        "English": "eng",
                        "Hindi": "hin", 
                        "English + Hindi": "eng+hin"
                    }
                    ocr_lang = language_map.get(ocr_language, "eng")
                    
                    output_path = converter.pdf_to_word(
                        temp_input,
                        force_english_numbers=force_english_numbers,
                        preserve_formatting=preserve_formatting,
                        ocr_language=ocr_lang
                    )
                    
                    if output_path:
                        st.success("✅ PDF converted to Word successfully!")
                        filename = uploaded_file.name.replace('.pdf', '.docx')
                        ui_utils.create_download_section(output_path, filename)
                    else:
                        st.error("❌ Conversion failed. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error during conversion: {str(e)}")

def handle_word_to_pdf(converter, ui_utils):
    """Handle Word to PDF conversion"""
    st.header("📄 Word to PDF")
    st.markdown("Convert Word documents to PDF format.")
    
    uploaded_file = st.file_uploader(
        "Upload Word file", 
        type=['docx', 'doc'], 
        key="word_to_pdf_upload"
    )
    
    if uploaded_file:
        if st.button("📄 Convert to PDF", key="convert_to_pdf"):
            with st.spinner("Converting Word to PDF..."):
                try:
                    temp_input = st.session_state.file_manager.save_uploaded_file(uploaded_file)
                    
                    output_path = converter.word_to_pdf(temp_input)
                    
                    if output_path:
                        st.success("✅ Word document converted to PDF successfully!")
                        filename = uploaded_file.name.replace('.docx', '.pdf').replace('.doc', '.pdf')
                        ui_utils.create_download_section(output_path, filename)
                    else:
                        st.error("❌ Conversion failed. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error during conversion: {str(e)}")

def handle_pdf_to_images(converter, ui_utils):
    """Handle PDF to Images conversion"""
    st.header("🖼️ PDF to Images")
    st.markdown("Convert PDF pages to image files.")
    
    uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'], key="pdf_to_images_upload")
    
    if uploaded_file:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dpi = st.selectbox("Resolution (DPI)", [150, 200, 300, 400, 600], index=2)
        
        with col2:
            image_format = st.selectbox("Image Format", ["PNG", "JPEG"])
        
        with col3:
            page_range = st.text_input("Page range (optional)", placeholder="1-5 or leave empty for all")
        
        if st.button("🖼️ Convert to Images", key="convert_to_images"):
            with st.spinner("Converting PDF to images..."):
                try:
                    temp_input = st.session_state.file_manager.save_uploaded_file(uploaded_file)
                    
                    output_paths = converter.pdf_to_images(
                        temp_input,
                        dpi=dpi,
                        format=image_format.lower(),
                        page_range=page_range if page_range else None
                    )
                    
                    if output_paths:
                        st.success(f"✅ PDF converted to {len(output_paths)} images!")
                        
                        # Create a ZIP file for download
                        zip_path = converter.create_images_zip(output_paths, uploaded_file.name)
                        ui_utils.create_download_section(zip_path, f"{uploaded_file.name}_images.zip")
                    else:
                        st.error("❌ Conversion failed. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error during conversion: {str(e)}")

def handle_images_to_pdf(converter, ui_utils):
    """Handle Images to PDF conversion"""
    st.header("📄 Images to PDF")
    st.markdown("Combine multiple images into a single PDF document.")
    
    uploaded_files = st.file_uploader(
        "Upload image files", 
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'], 
        accept_multiple_files=True,
        key="images_to_pdf_upload"
    )
    
    if uploaded_files:
        st.write(f"🖼️ {len(uploaded_files)} images selected")
        
        # Display uploaded images
        cols = st.columns(min(len(uploaded_files), 4))
        for i, file in enumerate(uploaded_files):
            with cols[i % 4]:
                st.image(file, caption=file.name, width=150)
        
        # OCR and PDF options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            page_size = st.selectbox("📄 Page Size", ["A4", "Letter", "A3", "Custom"])
        
        with col2:
            orientation = st.selectbox("🔄 Orientation", ["Portrait", "Landscape"])
            
        with col3:
            ocr_language = st.selectbox(
                "🔤 OCR Language:",
                ["English", "Hindi", "English + Hindi"],
                help="For text recognition in images"
            )
        
        if st.button("📄 Create PDF", key="create_pdf_from_images"):
            with st.spinner("Creating PDF from images..."):
                try:
                    # Save uploaded files temporarily
                    temp_files = []
                    for file in uploaded_files:
                        temp_path = st.session_state.file_manager.save_uploaded_file(file)
                        temp_files.append(temp_path)
                    
                    output_path = converter.images_to_pdf(
                        temp_files,
                        page_size=page_size,
                        orientation=orientation.lower()
                    )
                    
                    if output_path:
                        st.success("✅ PDF created from images successfully!")
                        ui_utils.create_download_section(output_path, "images_to_pdf.pdf")
                    else:
                        st.error("❌ PDF creation failed. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error during PDF creation: {str(e)}")

def handle_pdf_compress(pdf_ops, ui_utils):
    """Handle PDF compression"""
    st.header("🗜️ Compress PDF")
    st.markdown("Reduce PDF file size while maintaining quality.")
    
    uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'], key="compress_upload")
    
    if uploaded_file:
        # Show current file size
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
        st.write(f"📊 Current file size: {file_size:.2f} MB")
        
        compression_level = st.select_slider(
            "Compression Level",
            options=["Low", "Medium", "High", "Maximum"],
            value="Medium",
            help="Higher compression = smaller file size but potentially lower quality"
        )
        
        if st.button("🗜️ Compress PDF", key="compress_pdf"):
            with st.spinner("Compressing PDF..."):
                try:
                    temp_input = st.session_state.file_manager.save_uploaded_file(uploaded_file)
                    
                    output_path = pdf_ops.compress_pdf(temp_input, compression_level.lower())
                    
                    if output_path:
                        # Calculate compression ratio
                        compressed_size = os.path.getsize(output_path) / (1024 * 1024)
                        compression_ratio = ((file_size - compressed_size) / file_size) * 100
                        
                        st.success("✅ PDF compressed successfully!")
                        st.write(f"📊 New file size: {compressed_size:.2f} MB")
                        st.write(f"📈 Size reduction: {compression_ratio:.1f}%")
                        
                        filename = uploaded_file.name.replace('.pdf', '_compressed.pdf')
                        ui_utils.create_download_section(output_path, filename)
                    else:
                        st.error("❌ Compression failed. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error during compression: {str(e)}")

def handle_pdf_reorder(pdf_ops, ui_utils):
    """Handle PDF page reordering"""
    st.header("🔄 Reorder PDF Pages")
    st.markdown("Rearrange pages in your PDF document.")
    
    uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'], key="reorder_upload")
    
    if uploaded_file:
        temp_input = st.session_state.file_manager.save_uploaded_file(uploaded_file)
        
        try:
            page_count = pdf_ops.get_page_count(temp_input)
            st.write(f"📄 Total pages: {page_count}")
            
            # Simple page reordering interface
            new_order = st.text_input(
                "Enter new page order (e.g., 3,1,2,4,5):",
                placeholder=f"1,2,3,...,{page_count}",
                help="Specify the new order of pages using comma-separated page numbers"
            )
            
            if st.button("🔄 Reorder Pages", key="reorder_pages"):
                if new_order:
                    with st.spinner("Reordering pages..."):
                        try:
                            output_path = pdf_ops.reorder_pages(temp_input, new_order)
                            
                            if output_path:
                                st.success("✅ Pages reordered successfully!")
                                filename = uploaded_file.name.replace('.pdf', '_reordered.pdf')
                                ui_utils.create_download_section(output_path, filename)
                            else:
                                st.error("❌ Page reordering failed.")
                                
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter the new page order.")
                    
        except Exception as e:
            st.error(f"❌ Error reading PDF: {str(e)}")

def handle_pdf_password(pdf_ops, ui_utils):
    """Handle PDF password protection/unlocking"""
    st.header("🔒 Password Protect/Unlock PDF")
    st.markdown("Add or remove password protection from PDF files.")
    
    operation = st.radio("Select operation:", ["Add Password Protection", "Remove Password Protection"])
    
    uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'], key="password_upload")
    
    if uploaded_file:
        if operation == "Add Password Protection":
            col1, col2 = st.columns(2)
            
            with col1:
                user_password = st.text_input("User Password", type="password", help="Password to open the PDF")
            
            with col2:
                owner_password = st.text_input("Owner Password", type="password", help="Password to modify the PDF")
            
            permissions = st.multiselect(
                "Permissions",
                ["Print", "Copy Text", "Modify", "Add Annotations"],
                default=["Print"]
            )
            
            if st.button("🔒 Add Password Protection", key="add_password"):
                if user_password:
                    with st.spinner("Adding password protection..."):
                        try:
                            temp_input = st.session_state.file_manager.save_uploaded_file(uploaded_file)
                            
                            output_path = pdf_ops.add_password_protection(
                                temp_input, 
                                user_password, 
                                owner_password or user_password,
                                permissions
                            )
                            
                            if output_path:
                                st.success("✅ Password protection added successfully!")
                                filename = uploaded_file.name.replace('.pdf', '_protected.pdf')
                                ui_utils.create_download_section(output_path, filename)
                            else:
                                st.error("❌ Failed to add password protection.")
                                
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter a user password.")
        
        else:  # Remove Password Protection
            current_password = st.text_input("Current Password", type="password")
            
            if st.button("🔓 Remove Password Protection", key="remove_password"):
                if current_password:
                    with st.spinner("Removing password protection..."):
                        try:
                            temp_input = st.session_state.file_manager.save_uploaded_file(uploaded_file)
                            
                            output_path = pdf_ops.remove_password_protection(temp_input, current_password)
                            
                            if output_path:
                                st.success("✅ Password protection removed successfully!")
                                filename = uploaded_file.name.replace('.pdf', '_unlocked.pdf')
                                ui_utils.create_download_section(output_path, filename)
                            else:
                                st.error("❌ Failed to remove password protection. Check your password.")
                                
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter the current password.")

def handle_extract_images(pdf_ops, ui_utils):
    """Handle image extraction from PDF"""
    st.header("🖼️ Extract Images from PDF")
    st.markdown("Extract all images from a PDF document.")
    
    uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'], key="extract_images_upload")
    
    if uploaded_file:
        image_format = st.selectbox("Image Format", ["PNG", "JPEG"], key="extract_format")
        min_size = st.number_input("Minimum image size (pixels)", min_value=50, value=100)
        
        if st.button("🖼️ Extract Images", key="extract_images_btn"):
            with st.spinner("Extracting images..."):
                try:
                    temp_input = st.session_state.file_manager.save_uploaded_file(uploaded_file)
                    
                    image_paths = pdf_ops.extract_images(
                        temp_input, 
                        format=image_format.lower(),
                        min_size=min_size
                    )
                    
                    if image_paths:
                        st.success(f"✅ Extracted {len(image_paths)} images!")
                        
                        # Create ZIP file for download
                        zip_path = pdf_ops.create_images_zip(image_paths, uploaded_file.name)
                        ui_utils.create_download_section(
                            zip_path, 
                            f"{uploaded_file.name}_extracted_images.zip"
                        )
                        
                        # Preview first few images
                        st.subheader("Image Preview")
                        cols = st.columns(min(len(image_paths), 4))
                        for i, img_path in enumerate(image_paths[:4]):
                            with cols[i]:
                                st.image(img_path, caption=f"Image {i+1}", width=150)
                    else:
                        st.warning("⚠️ No images found in the PDF.")
                        
                except Exception as e:
                    st.error(f"❌ Error extracting images: {str(e)}")

def handle_extract_text(pdf_ops, ocr_processor, ui_utils):
    """Handle text extraction from PDF"""
    st.header("📝 Extract Text from PDF")
    st.markdown("Extract text content from PDF documents.")
    
    uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'], key="extract_text_upload")
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            use_ocr_fallback = st.checkbox("Use OCR for scanned PDFs", value=True)
        
        with col2:
            output_format = st.selectbox("Output Format", ["Plain Text", "Word Document"])
        
        if use_ocr_fallback:
            ocr_language = st.selectbox("OCR Language", ["Auto Detect", "English", "Hindi", "English + Hindi"])
        
        if st.button("📝 Extract Text", key="extract_text_btn"):
            with st.spinner("Extracting text..."):
                try:
                    temp_input = st.session_state.file_manager.save_uploaded_file(uploaded_file)
                    
                    if use_ocr_fallback:
                        output_path = ocr_processor.extract_text_with_ocr(
                            temp_input,
                            language=ocr_language.lower().replace(" ", "_"),
                            output_format=output_format.lower()
                        )
                    else:
                        output_path = pdf_ops.extract_text(temp_input, output_format.lower())
                    
                    if output_path:
                        st.success("✅ Text extracted successfully!")
                        
                        # Show preview of extracted text
                        if output_format == "Plain Text":
                            with open(output_path, 'r', encoding='utf-8') as f:
                                text_content = f.read()
                                st.text_area("Text Preview", text_content[:1000] + "..." if len(text_content) > 1000 else text_content, height=200)
                        
                        # Create download
                        extension = ".txt" if output_format == "Plain Text" else ".docx"
                        filename = uploaded_file.name.replace('.pdf', f'_extracted_text{extension}')
                        ui_utils.create_download_section(output_path, filename)
                    else:
                        st.error("❌ Text extraction failed.")
                        
                except Exception as e:
                    st.error(f"❌ Error extracting text: {str(e)}")

def handle_batch_processing(pdf_ops, converter, ui_utils):
    """Handle batch processing of multiple files"""
    st.header("📦 Batch Processing")
    st.markdown("Process multiple files at once with the same operation.")
    
    operation = st.selectbox(
        "Select batch operation:",
        [
            "Compress PDFs",
            "Convert PDFs to Word",
            "Convert Images to PDFs",
            "Extract Text from PDFs",
            "Add Password Protection"
        ]
    )
    
    if operation in ["Compress PDFs", "Convert PDFs to Word", "Extract Text from PDFs", "Add Password Protection"]:
        uploaded_files = st.file_uploader(
            "Upload PDF files", 
            type=['pdf'], 
            accept_multiple_files=True,
            key="batch_pdf_upload"
        )
    else:  # Convert Images to PDFs
        uploaded_files = st.file_uploader(
            "Upload image files", 
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'], 
            accept_multiple_files=True,
            key="batch_image_upload"
        )
    
    if uploaded_files:
        st.write(f"📁 {len(uploaded_files)} files selected for batch processing")
        
        # Operation-specific settings
        if operation == "Compress PDFs":
            compression_level = st.selectbox("Compression Level", ["Low", "Medium", "High", "Maximum"])
        elif operation == "Add Password Protection":
            batch_password = st.text_input("Password for all files", type="password")
        
        if st.button(f"🚀 Start Batch {operation}", key="start_batch"):
            if operation == "Add Password Protection" and not batch_password:
                st.warning("⚠️ Please enter a password for batch protection.")
                return
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            results = []
            
            for i, file in enumerate(uploaded_files):
                try:
                    status_text.text(f"Processing {file.name}...")
                    temp_input = st.session_state.file_manager.save_uploaded_file(file)
                    
                    if operation == "Compress PDFs":
                        output_path = pdf_ops.compress_pdf(temp_input, compression_level.lower())
                        result_name = file.name.replace('.pdf', '_compressed.pdf')
                    
                    elif operation == "Convert PDFs to Word":
                        output_path = converter.pdf_to_word(temp_input)
                        result_name = file.name.replace('.pdf', '.docx')
                    
                    elif operation == "Extract Text from PDFs":
                        output_path = pdf_ops.extract_text(temp_input, "plain text")
                        result_name = file.name.replace('.pdf', '_text.txt')
                    
                    elif operation == "Add Password Protection":
                        output_path = pdf_ops.add_password_protection(temp_input, batch_password, batch_password, ["Print"])
                        result_name = file.name.replace('.pdf', '_protected.pdf')
                    
                    elif operation == "Convert Images to PDFs":
                        output_path = converter.images_to_pdf([temp_input])
                        result_name = file.name.replace(file.name.split('.')[-1], 'pdf')
                    
                    if output_path:
                        results.append((output_path, result_name))
                    
                    progress_bar.progress((i + 1) / len(uploaded_files))
                    
                except Exception as e:
                    st.error(f"❌ Error processing {file.name}: {str(e)}")
            
            status_text.text("Creating download package...")
            
            if results:
                # Create ZIP file with all results
                zip_path = ui_utils.create_batch_download_zip(results, operation)
                st.success(f"✅ Batch processing completed! {len(results)} files processed.")
                ui_utils.create_download_section(zip_path, f"batch_{operation.lower().replace(' ', '_')}_results.zip")
            else:
                st.error("❌ No files were processed successfully.")

if __name__ == "__main__":
    main()
