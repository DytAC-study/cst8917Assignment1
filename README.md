# CST8917 Assignment-1: Image Metadata Processing Pipeline with Azure Durable Functions

Video: https://youtu.be/7O-64eKigZo

## Overview

This project implements an end-to-end image processing pipeline using **Azure Durable Functions**, designed to automatically:

- Trigger on new image uploads in Blob Storage
- Extract image metadata (format, size, dimensions)
- Store the metadata in **Azure SQL Database**
- Send a summary message to **Azure Queue**
- Generate a plain-text processing report in Blob Storage

It combines concepts from Lab 1 (SQL + Queue output) and Lab 2 (Blob-triggered metadata extraction) into a unified serverless workflow.

------

## Architecture

```
pgsqlCopyEditBlob Upload (images-input/)
         ↓
Durable Function Trigger
         ↓
Metadata Extraction (Pillow)
         ↓
→ Store in Azure SQL Database
→ Send summary to Azure Queue
→ Write report to Blob (reports/)
```

------

## Project Structure

```
pgsqlCopyEditassignment1-image-metadata-pipeline/
├── function_app/
│   ├── __init__.py
│   └── function.json
├── requirements.txt
├── host.json
├── local.settings.json
└── README.md
```

------

## Requirements

- Python 3.10
- Azure Functions Core Tools
- Azure CLI
- Dependencies in `requirements.txt`:
  - `azure-functions`
  - `azure-storage-blob`
  - `azure-storage-queue`
  - `pyodbc`
  - `Pillow`

------

## Deployment to Azure

```
# 1. Create the Function App (if not already created)
az functionapp create \
  --name durableimagemetadataapp \
  --resource-group DurableAssignmentRG \
  --storage-account durableassignstorage \
  --consumption-plan-location canadacentral \
  --runtime python \
  --runtime-version 3.10 \
  --functions-version 4 \
  --os-type Linux

# 2. Set the SQL connection string (ODBC Driver 17 was used due to Azure limitation)
az functionapp config appsettings set \
  --name durableimagemetadataapp \
  --resource-group DurableAssignmentRG \
  --settings "SqlConnectionString=Driver={ODBC Driver 17 for SQL Server};Server=tcp:durablesqlserver7740.database.windows.net,1433;Database=ImageMetadataDB;Uid=sqladmin;Pwd=YourStrongP@ssw0rd;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

# 3. Deploy the function
func azure functionapp publish durableimagemetadataapp
```

------

## Usage

1. Upload an image file (e.g., PNG or JPG) to the `images-input` container.
2. The function is automatically triggered.
3. Metadata is extracted and saved to Azure SQL.
4. A short report is sent to the queue and also saved in the `reports/` container.

------

## Issues We Encountered

| Problem                                                 | Solution                                                     |
| ------------------------------------------------------- | ------------------------------------------------------------ |
| ❌ `Can't open lib 'ODBC Driver 18'` on Azure Linux plan | ✅ Switched to `ODBC Driver 17` in connection string          |
| ❌ IP not allowed to access Azure SQL                    | ✅ Added outbound IP of Function App to the Azure SQL server firewall |
| ❌ No data in SQL after function ran                     | ✅ Realized function failed silently due to missing driver, resolved with the change above |
| ❌ Delayed Function triggers                             | ✅ Used `az functionapp log stream` for real-time logs and debugging |

------

## Sample Output (Log)

```
pgsqlCopyEditImage uploaded: images-input/test.png
Metadata extracted: {'width': 1024, 'height': 768, 'format': 'PNG'}
Saved to SQL successfully
Queue message sent
Report written to Blob Storage
```