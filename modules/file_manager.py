import os
import tempfile
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
import streamlit as st
import shutil

class FileManager:
    """Manages temporary file storage and cleanup"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.app_temp_dir = os.path.join(self.temp_dir, "pdf_processor")
        self.file_registry: Dict[str, Dict] = {}
        self.transfer_codes: Dict[str, Dict] = {}  # 4-digit code transfers
        self.expiration_minutes = 30
        self.admin_expiration_hours = 48
        
        # Create app-specific temp directory
        os.makedirs(self.app_temp_dir, exist_ok=True)
    
    def save_uploaded_file(self, uploaded_file, is_admin=False) -> str:
        """Save uploaded file to temporary location"""
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = os.path.splitext(uploaded_file.name)[1]
            temp_filename = f"{file_id}{file_extension}"
            temp_path = os.path.join(self.app_temp_dir, temp_filename)
            
            # Save file
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Set expiration based on user type
            if is_admin:
                expiration_time = datetime.now() + timedelta(hours=self.admin_expiration_hours)
            else:
                expiration_time = datetime.now() + timedelta(minutes=self.expiration_minutes)
            
            # Register file with expiration
            self.file_registry[file_id] = {
                'path': temp_path,
                'original_name': uploaded_file.name,
                'created_at': datetime.now(),
                'expires_at': expiration_time,
                'size': len(uploaded_file.getvalue()),
                'is_admin': is_admin,
                'file_id': file_id
            }
            
            return temp_path
            
        except Exception as e:
            raise Exception(f"Error saving uploaded file: {str(e)}")
    
    def save_processed_file(self, source_path: str, output_name: str) -> str:
        """Save processed file to temporary location"""
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = os.path.splitext(output_name)[1]
            temp_filename = f"{file_id}{file_extension}"
            temp_path = os.path.join(self.app_temp_dir, temp_filename)
            
            # Copy processed file
            shutil.copy2(source_path, temp_path)
            
            # Get file size
            file_size = os.path.getsize(temp_path)
            
            # Register file with expiration
            self.file_registry[file_id] = {
                'path': temp_path,
                'original_name': output_name,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(minutes=self.expiration_minutes),
                'size': file_size
            }
            
            return temp_path
            
        except Exception as e:
            raise Exception(f"Error saving processed file: {str(e)}")
    
    def create_download_link(self, file_path: str, download_name: str) -> str:
        """Create a download link for the file"""
        try:
            # Copy file to managed temporary location
            managed_path = self.save_processed_file(file_path, download_name)
            
            # Return the managed path (Streamlit will handle the download)
            return managed_path
            
        except Exception as e:
            raise Exception(f"Error creating download link: {str(e)}")
    
    def cleanup_expired_files(self):
        """Clean up expired files from temporary storage"""
        try:
            current_time = datetime.now()
            expired_files = []
            
            for file_id, file_info in self.file_registry.items():
                if current_time > file_info['expires_at']:
                    expired_files.append(file_id)
            
            # Remove expired files
            for file_id in expired_files:
                file_info = self.file_registry[file_id]
                file_path = file_info['path']
                
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    # Log error but continue cleanup
                    pass
                
                # Remove from registry
                del self.file_registry[file_id]
            
            # Also clean up any orphaned files in temp directory
            self._cleanup_orphaned_files()
            
        except Exception as e:
            # Cleanup should not break the app
            pass
    
    def _cleanup_orphaned_files(self):
        """Clean up files in temp directory that are not in registry"""
        try:
            if not os.path.exists(self.app_temp_dir):
                return
            
            current_time = datetime.now()
            registered_paths = {info['path'] for info in self.file_registry.values()}
            
            for filename in os.listdir(self.app_temp_dir):
                file_path = os.path.join(self.app_temp_dir, filename)
                
                # Skip if file is in registry
                if file_path in registered_paths:
                    continue
                
                # Check file age
                try:
                    file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                    file_age = current_time - file_modified
                    
                    # Remove files older than expiration period
                    if file_age.total_seconds() > (self.expiration_minutes * 60):
                        os.remove(file_path)
                        
                except Exception as e:
                    # Continue cleanup even if individual file fails
                    continue
                    
        except Exception as e:
            # Cleanup should not break the app
            pass
    
    def get_file_info(self, file_id: str) -> Optional[Dict]:
        """Get information about a managed file"""
        return self.file_registry.get(file_id)
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        try:
            total_files = len(self.file_registry)
            total_size = sum(info['size'] for info in self.file_registry.values())
            
            # Check disk usage
            temp_dir_size = 0
            if os.path.exists(self.app_temp_dir):
                for filename in os.listdir(self.app_temp_dir):
                    file_path = os.path.join(self.app_temp_dir, filename)
                    if os.path.isfile(file_path):
                        temp_dir_size += os.path.getsize(file_path)
            
            return {
                'managed_files': total_files,
                'managed_size_mb': total_size / (1024 * 1024),
                'temp_dir_size_mb': temp_dir_size / (1024 * 1024),
                'expiration_minutes': self.expiration_minutes
            }
            
        except Exception as e:
            return {
                'managed_files': 0,
                'managed_size_mb': 0,
                'temp_dir_size_mb': 0,
                'expiration_minutes': self.expiration_minutes
            }
    
    def force_cleanup_all(self):
        """Force cleanup of all managed files (for maintenance)"""
        try:
            # Remove all registered files
            for file_id, file_info in self.file_registry.items():
                file_path = file_info['path']
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    continue
            
            # Clear registry
            self.file_registry.clear()
            
            # Remove all files from temp directory
            if os.path.exists(self.app_temp_dir):
                for filename in os.listdir(self.app_temp_dir):
                    file_path = os.path.join(self.app_temp_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            # Force cleanup should not break the app
            pass
    
    def extend_file_expiration(self, file_path: str, additional_minutes: int = 30):
        """Extend expiration time for a specific file"""
        try:
            # Find file in registry by path
            for file_id, file_info in self.file_registry.items():
                if file_info['path'] == file_path:
                    new_expiration = file_info['expires_at'] + timedelta(minutes=additional_minutes)
                    file_info['expires_at'] = new_expiration
                    return True
            
            return False
            
        except Exception as e:
            return False
    
    def get_all_files(self) -> Dict:
        """Get all files for admin view"""
        return self.file_registry
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a specific file (admin function)"""
        try:
            if file_id in self.file_registry:
                file_path = self.file_registry[file_id]['path']
                if os.path.exists(file_path):
                    os.remove(file_path)
                del self.file_registry[file_id]
                return True
            return False
        except Exception as e:
            return False
    
    def create_transfer_code(self, uploaded_file) -> str:
        """Create a 4-digit transfer code for file sharing"""
        try:
            import random
            
            # Generate unique 4-digit code
            while True:
                code = f"{random.randint(1000, 9999)}"
                if code not in self.transfer_codes:
                    break
            
            # Save file
            file_id = str(uuid.uuid4())
            file_extension = os.path.splitext(uploaded_file.name)[1]
            temp_filename = f"transfer_{file_id}{file_extension}"
            temp_path = os.path.join(self.app_temp_dir, temp_filename)
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Store transfer info
            self.transfer_codes[code] = {
                'file_path': temp_path,
                'original_name': uploaded_file.name,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=24),  # 24 hour expiry
                'size': len(uploaded_file.getvalue()),
                'downloaded': False
            }
            
            return code
            
        except Exception as e:
            raise Exception(f"Error creating transfer code: {str(e)}")
    
    def get_file_by_code(self, code: str) -> Optional[Dict]:
        """Get file information by transfer code"""
        return self.transfer_codes.get(code)
    
    def download_by_code(self, code: str) -> Optional[tuple]:
        """Download file by transfer code and mark as downloaded"""
        try:
            if code in self.transfer_codes:
                file_info = self.transfer_codes[code]
                
                # Check if expired
                if datetime.now() > file_info['expires_at']:
                    return None
                
                # Check if file exists
                if not os.path.exists(file_info['file_path']):
                    return None
                
                # Read file data
                with open(file_info['file_path'], 'rb') as f:
                    file_data = f.read()
                
                # Mark as downloaded
                file_info['downloaded'] = True
                
                return (file_data, file_info['original_name'])
            
            return None
            
        except Exception as e:
            return None
