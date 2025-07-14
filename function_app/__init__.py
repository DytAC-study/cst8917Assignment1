import azure.functions as func
import logging
import json
import os
import uuid
from datetime import datetime
from PIL import Image
import io

def main(blobTrigger: func.InputStream):
    """Blob trigger function - Entry point for image processing"""
    
    # Check if the file is an image
    blob_name = blobTrigger.name
    file_extension = blob_name.lower().split('.')[-1]
    
    if file_extension not in ['jpg', 'jpeg', 'png', 'gif']:
        logging.info(f"Skipping non-image file: {blob_name}")
        return
    
    logging.info(f"Image uploaded: {blob_name}, starting processing...")
    
    try:
        # Read the blob content
        blob_content = blobTrigger.read()
        
        # Extract metadata using PIL
        image = Image.open(io.BytesIO(blob_content))
        
        metadata = {
            "id": str(uuid.uuid4()),
            "filename": blob_name,
            "file_size_kb": len(blob_content) / 1024,
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode,
            "created_at": datetime.utcnow().isoformat(),
            "processing_time": datetime.utcnow().isoformat()
        }
        
        logging.info(f"Metadata extracted: {metadata}")
        
        # Process metadata using separate functions
        process_metadata(metadata, blob_name)
        
        logging.info(f"Image processing completed for: {blob_name}")
        
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")

def process_metadata(metadata: dict, filename: str):
    """Process metadata through different functions"""
    
    # Step 1: Save to SQL Database
    save_to_sql_database(metadata)
    
    # Step 2: Send to Queue
    send_to_queue(metadata)
    
    # Step 3: Generate Report
    generate_processing_report(metadata, filename)

def save_to_sql_database(metadata: dict):
    """Save image metadata to SQL Database - Lab 1 functionality"""
    try:
        import pyodbc
        
        # Get SQL connection string
        connection_string = os.environ.get('SqlConnectionString')
        
        if not connection_string:
            logging.error("SQL Connection String not configured")
            return
        
        # Connect to database
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Create table if not exists (matching existing table structure)
        table_check_sql = """
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'ImageMetadata'
        """
        cursor.execute(table_check_sql)
        exists = cursor.fetchone()[0]

        if not exists:
            create_table_sql = """
            CREATE TABLE ImageMetadata (
                Id UNIQUEIDENTIFIER PRIMARY KEY,
                FileName NVARCHAR(255),
                Format NVARCHAR(50),
                Mode NVARCHAR(50),
                Width INT,
                Height INT,
                FileSizeKB FLOAT,
                CreatedAt DATETIME2,
                ProcessingTime DATETIME2
            )
            """
            cursor.execute(create_table_sql)
            conn.commit()
        
        # Insert metadata (matching existing table structure)
        insert_sql = """
        INSERT INTO ImageMetadata (Id, FileName, Format, Mode, Width, Height, FileSizeKB, CreatedAt, ProcessingTime)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Convert string datetime to datetime2
        from datetime import datetime
        created_at = datetime.fromisoformat(metadata.get('created_at', datetime.utcnow().isoformat()))
        processing_time = datetime.fromisoformat(metadata.get('processing_time', datetime.utcnow().isoformat()))
        
        cursor.execute(insert_sql, (
            metadata['id'],
            metadata['filename'],
            metadata.get('format', ''),
            metadata.get('mode', ''),
            metadata.get('width', 0),
            metadata.get('height', 0),
            metadata.get('file_size_kb', 0),
            created_at,
            processing_time
        ))
        
        conn.commit()
        conn.close()
        
        logging.info("✅ SQL Database Save: Success")
        
    except Exception as e:
        logging.error(f"Error saving to SQL database: {str(e)}")

def send_to_queue(metadata: dict):
    """Send metadata to Azure Storage Queue - Lab 1 functionality"""
    try:
        from azure.storage.queue import QueueClient
        
        # Get connection string
        connection_string = os.environ.get('AzureWebJobsStorage')
        
        # Create queue client
        queue_client = QueueClient.from_connection_string(
            connection_string, 
            queue_name="image-processing-queue"
        )
        
        # Create queue if it doesn't exist
        try:
            queue_client.get_queue_properties()
        except:
            queue_client.create_queue()
        
        # Send message to queue
        message = {
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat(),
            "message_type": "image_metadata"
        }
        
        queue_client.send_message(json.dumps(message))
        
        logging.info("✅ Queue Send: Success")
        
    except Exception as e:
        logging.error(f"Error sending to queue: {str(e)}")

def generate_processing_report(metadata: dict, original_filename: str):
    """Generate and save processing report to blob storage - Lab 2 functionality"""
    try:
        from azure.storage.blob import BlobServiceClient
        
        # Get connection string
        connection_string = os.environ.get('AzureWebJobsStorage')
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Create output container if it doesn't exist
        container_name = "output"
        try:
            container_client = blob_service_client.get_container_client(container_name)
            container_client.get_container_properties()
        except:
            blob_service_client.create_container(container_name)
        
        # Generate report filename
        base_name = original_filename.split('/')[-1].replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
        report_filename = f"{base_name}_processing_report.txt"
        
        # Format report
        report_content = format_processing_report(metadata)
        
        # Upload report
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=report_filename
        )
        blob_client.upload_blob(report_content, overwrite=True)
        
        logging.info(f"Processing report saved: {report_filename}")
        
    except Exception as e:
        logging.error(f"Error generating report: {str(e)}")

def format_processing_report(metadata: dict) -> str:
    """Generate a concise image processing report."""
    return f"""Image Processing Report
--------------------------
File: {metadata.get('filename', 'Unknown')}
ID: {metadata.get('id', 'Unknown')}
Size: {metadata.get('file_size_kb', 0):.2f} KB
Dimensions: {metadata.get('width', '?')} x {metadata.get('height', '?')}
Format: {metadata.get('format', 'Unknown')}
Mode: {metadata.get('mode', 'Unknown')}
Processed At: {metadata.get('processing_time', 'Unknown')}

Status:
- File Received ✅
- Metadata Extracted ✅
- Saved to SQL ✅
- Report Generated ✅
"""
