#!/usr/bin/env python
"""
Automated Database Backup Script for MediPlus
Run this script daily to backup MySQL database
"""

import os
import sys
import datetime
import subprocess
import shutil
from pathlib import Path
import logging
import gzip
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup.log'),
        logging.StreamHandler()
    ]
)

# Database configuration
DB_NAME = 'mediplus_db'
DB_USER = 'root'
DB_PASSWORD = ''  # Set your MySQL password
DB_HOST = 'localhost'
DB_PORT = '3306'

# Backup configuration
BACKUP_DIR = Path(__file__).parent.parent / 'backups'
BACKUP_DIR.mkdir(exist_ok=True)
RETENTION_DAYS = 30  # Keep backups for 30 days

# Email configuration (optional)
EMAIL_ENABLED = False
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'your-email@gmail.com'
EMAIL_PASSWORD = 'your-password'
EMAIL_TO = 'admin@mediplus.com'

def create_backup():
    """Create MySQL database backup"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f'mediplus_backup_{timestamp}.sql'
    compressed_file = BACKUP_DIR / f'mediplus_backup_{timestamp}.sql.gz'
    
    try:
        logging.info(f"Starting database backup: {backup_file}")
        
        # MySQL dump command
        cmd = [
            'mysqldump',
            f'--host={DB_HOST}',
            f'--port={DB_PORT}',
            f'--user={DB_USER}',
            f'--password={DB_PASSWORD}' if DB_PASSWORD else '',
            '--databases', DB_NAME,
            '--routines',      # Include stored procedures
            '--triggers',       # Include triggers
            '--events',         # Include events
            '--single-transaction',  # For InnoDB consistency
            '--quick',          # For large tables
            '--lock-tables=false',  # Don't lock tables
            '--compress'         # Compress data transfer
        ]
        
        # Remove empty password argument
        cmd = [arg for arg in cmd if arg]
        
        # Execute mysqldump
        with open(backup_file, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            logging.error(f"Backup failed: {result.stderr}")
            return False
        
        # Compress the backup file
        with open(backup_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove uncompressed file
        backup_file.unlink()
        
        # Get file size
        file_size = compressed_file.stat().st_size
        size_mb = file_size / (1024 * 1024)
        
        logging.info(f"Backup completed successfully: {compressed_file} ({size_mb:.2f} MB)")
        return compressed_file
        
    except Exception as e:
        logging.error(f"Backup failed: {str(e)}")
        return False

def cleanup_old_backups():
    """Remove backups older than RETENTION_DAYS"""
    try:
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=RETENTION_DAYS)
        deleted_count = 0
        
        for backup_file in BACKUP_DIR.glob('mediplus_backup_*.sql.gz'):
            # Extract date from filename
            try:
                file_date_str = backup_file.stem.replace('mediplus_backup_', '')
                file_date = datetime.datetime.strptime(file_date_str, '%Y%m%d_%H%M%S')
                
                if file_date < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
                    logging.info(f"Deleted old backup: {backup_file}")
            except ValueError:
                # Skip files with invalid date format
                continue
        
        logging.info(f"Cleanup completed. Deleted {deleted_count} old backups.")
        
    except Exception as e:
        logging.error(f"Cleanup failed: {str(e)}")

def send_email_notification(backup_file, status, error_msg=None):
    """Send email notification about backup status"""
    if not EMAIL_ENABLED:
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = f"MediPlus Backup {'Success' if status else 'Failed'} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        body = f"""
        <h2>MediPlus Database Backup Report</h2>
        <p><strong>Status:</strong> {'✅ Success' if status else '❌ Failed'}</p>
        <p><strong>Time:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        if status and backup_file:
            file_size = backup_file.stat().st_size / (1024 * 1024)
            body += f"""
            <p><strong>Backup File:</strong> {backup_file.name}</p>
            <p><strong>File Size:</strong> {file_size:.2f} MB</p>
            """
            
            # Attach backup file
            with open(backup_file, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{backup_file.name}"'
                )
                msg.attach(part)
        elif error_msg:
            body += f"<p><strong>Error:</strong> {error_msg}</p>"
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logging.info("Email notification sent")
        
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")

def main():
    """Main backup function"""
    logging.info("=" * 50)
    logging.info("Starting backup process...")
    
    # Create backup
    backup_file = create_backup()
    
    # Cleanup old backups
    cleanup_old_backups()
    
    # Send notification
    if backup_file:
        send_email_notification(backup_file, True)
    else:
        send_email_notification(None, False, "Backup creation failed")
    
    logging.info("Backup process completed")
    logging.info("=" * 50)

if __name__ == "__main__":
    main()