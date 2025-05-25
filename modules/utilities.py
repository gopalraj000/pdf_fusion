import streamlit as st
import os
import qrcode
from io import BytesIO
import base64
import zipfile
import tempfile
from typing import List, Tuple
import time

class UIUtilities:
    """Utility functions for UI components and user experience"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def create_download_section(self, file_path: str, filename: str):
        """Create a download section with preview and QR code"""
        try:
            if not os.path.exists(file_path):
                st.error("❌ File not found for download.")
                return
            
            # Read file for download
            with open(file_path, "rb") as file:
                file_data = file.read()
            
            # File size info
            file_size = len(file_data) / (1024 * 1024)  # MB
            st.write(f"📊 File size: {file_size:.2f} MB")
            
            # Create download button
            st.download_button(
                label=f"📥 Download {filename}",
                data=file_data,
                file_name=filename,
                mime=self._get_mime_type(filename),
                key=f"download_{int(time.time())}"
            )
            
            # QR codes removed from PDF tools - only available in File Transfer tool
            
            # Expiration notice
            st.info("⏰ Download link expires in 30 minutes for security.")
            
        except Exception as e:
            st.error(f"❌ Error creating download section: {str(e)}")
    
    def create_progress_bar(self, current: int, total: int, message: str = "Processing..."):
        """Create an animated progress bar"""
        progress = current / total if total > 0 else 0
        progress_bar = st.progress(progress)
        st.write(f"{message} ({current}/{total}) - {progress*100:.1f}%")
        return progress_bar
    
    def create_file_preview(self, file_path: str, max_pages: int = 3):
        """Create a preview of the file content"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                self._preview_pdf(file_path, max_pages)
            elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                self._preview_image(file_path)
            elif file_ext in ['.txt']:
                self._preview_text(file_path)
            else:
                st.info("📄 Preview not available for this file type.")
                
        except Exception as e:
            st.warning(f"⚠️ Could not generate preview: {str(e)}")
    
    def _preview_pdf(self, pdf_path: str, max_pages: int = 3):
        """Preview PDF pages"""
        try:
            import fitz
            import pdf2image
            
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            st.write(f"📄 PDF Preview (showing first {min(max_pages, total_pages)} of {total_pages} pages)")
            
            # Convert first few pages to images for preview
            images = pdf2image.convert_from_path(
                pdf_path,
                dpi=150,
                first_page=1,
                last_page=min(max_pages, total_pages)
            )
            
            cols = st.columns(min(len(images), 3))
            for i, image in enumerate(images):
                with cols[i % 3]:
                    st.image(image, caption=f"Page {i+1}", width=200)
            
            doc.close()
            
        except Exception as e:
            st.warning(f"⚠️ Could not generate PDF preview: {str(e)}")
    
    def _preview_image(self, image_path: str):
        """Preview image file"""
        try:
            st.write("🖼️ Image Preview")
            st.image(image_path, caption="Image Preview", width=400)
            
        except Exception as e:
            st.warning(f"⚠️ Could not generate image preview: {str(e)}")
    
    def _preview_text(self, text_path: str):
        """Preview text file"""
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            st.write("📝 Text Preview")
            preview = content[:1000] + "..." if len(content) > 1000 else content
            st.text_area("Content", preview, height=200, disabled=True)
            
        except Exception as e:
            st.warning(f"⚠️ Could not generate text preview: {str(e)}")
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type for file"""
        ext = os.path.splitext(filename)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.zip': 'application/zip'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def create_batch_download_zip(self, files: List[Tuple[str, str]], operation_name: str) -> str:
        """Create a ZIP file for batch download"""
        try:
            zip_path = os.path.join(self.temp_dir, f"batch_{operation_name}_{int(time.time())}.zip")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path, filename in files:
                    if os.path.exists(file_path):
                        zipf.write(file_path, filename)
            
            return zip_path
            
        except Exception as e:
            raise Exception(f"Error creating batch ZIP: {str(e)}")
    
    def create_status_panel(self):
        """Create a status panel for operation feedback"""
        status_container = st.container()
        with status_container:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                success_count = st.empty()
            with col2:
                error_count = st.empty()
            with col3:
                progress_status = st.empty()
        
        return {
            'success': success_count,
            'error': error_count,
            'progress': progress_status
        }
    
    def show_file_info(self, file_path: str):
        """Display file information"""
        try:
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_path)[1].upper()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("File Name", file_name)
            with col2:
                st.metric("File Type", file_ext)
            with col3:
                st.metric("File Size", f"{file_size:.2f} MB")
                
        except Exception as e:
            st.warning(f"⚠️ Could not read file information: {str(e)}")

class QRGenerator:
    """Generate QR codes for download links and file sharing"""
    
    def __init__(self):
        pass
    
    def create_download_qr(self, file_data: bytes, filename: str) -> BytesIO:
        """Create QR code for file download"""
        try:
            # Create file information QR code (since embedding large files in QR is impractical)
            file_size_mb = len(file_data) / (1024 * 1024)
            qr_data = f"Document: {filename}\nSize: {file_size_mb:.2f} MB\nProcessed: {time.strftime('%Y-%m-%d %H:%M:%S')}\nDownload from your browser"
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=2,  # Increased version for more data
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=8,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Create QR code image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to BytesIO for Streamlit
            img_buffer = BytesIO()
            qr_image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            st.warning(f"⚠️ Could not generate QR code: {str(e)}")
            return None
    
    def create_url_qr(self, url: str) -> BytesIO:
        """Create QR code for URL"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            img_buffer = BytesIO()
            qr_image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            st.warning(f"⚠️ Could not generate URL QR code: {str(e)}")
            return None
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type for file"""
        ext = os.path.splitext(filename)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.zip': 'application/zip'
        }
        return mime_types.get(ext, 'application/octet-stream')
