# CST8917 Assignment 1: Azure Durable Functions Image Processing Pipeline

> **All documentation is included in this file.**

---

## 📋 Project Overview

This assignment implements an Azure Durable Functions pipeline for image metadata processing, combining Lab 1 (Queue and SQL dual output) and Lab 2 (Blob trigger and image processing). The solution processes uploaded images, extracts metadata, stores it in SQL database, sends messages to queues, and generates processing reports.

---

## 🎯 Assignment Requirements Met & Summary

- ✅ **Lab 1 Integration**: Queue output, SQL database storage, dual output system
- ✅ **Lab 2 Integration**: Blob trigger, image processing, metadata extraction
- ✅ **Assignment 1**: Durable Functions pipeline, error handling, local & Azure deployment, comprehensive verification, full English documentation

---

**Date**: July 10, 2025

**Student**: CST8917 Assignment 1

**Demo Video**: [YouTube Demo](https://youtu.be/hmpAPskZWQY)

---

## 🏗️ Architecture

```
Image Upload → Blob Trigger → Metadata Extraction → SQL Storage → Queue Message → Report Generation
```

### Components:
- **Azure Blob Storage**: Input/output containers
- **Azure Function App**: Python-based blob trigger function
- **Azure SQL Database**: Metadata storage
- **Azure Storage Queue**: Processing notifications
- **PIL (Python Imaging Library)**: Image metadata extraction

---

## 📁 Project Structure & File List

```
as1/
├── function_app/
│   ├── __init__.py          # Main function code (English)
│   └── function.json        # Function configuration (English)
├── requirements.txt         # Python dependencies (English)
├── local.settings.json      # Local development settings (English)
├── host.json                # Function app configuration (English)
├── README.md                # Comprehensive documentation (English)
```

| File | Purpose |
|------|---------|
| `function_app/__init__.py` | Main function implementation |
| `function_app/function.json` | Function configuration |
| `requirements.txt` | Python dependencies |
| `local.settings.json` | Local development settings |
| `host.json` | Function app configuration |
| `README.md` | Main documentation |

---

## 🚀 Setup and Deployment

### Prerequisites
- Azure CLI installed
- Python 3.10+
- Azure Functions Core Tools
- Azure subscription

### 1. Local Development Setup

```bash
pip install -r requirements.txt
# Update local.settings.json with your Azure connection strings
func start
```

### 2. Azure Deployment

```bash
az functionapp create \
  --name cst8917-assignment1-func \
  --resource-group cst8917-assignment1-rg \
  --storage-account cst8917assignment1sa \
  --consumption-plan-location canadacentral \
  --runtime python \
  --runtime-version 3.10 \
  --functions-version 4 \
  --os-type Linux

az functionapp config appsettings set \
  --name cst8917-assignment1-func \
  --resource-group cst8917-assignment1-rg \
  --settings "SqlConnectionString=Driver={ODBC Driver 18 for SQL Server};Server=tcp:cst8917-assignment1-sql.database.windows.net,1433;Database=ImageMetadataDB;Uid=cst8917admin;Pwd=Azure@8917;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

func azure functionapp publish cst8917-assignment1-func
```

---

## 🔧 Configuration

- **Resource Group**: `cst8917-assignment1-rg`
- **Storage Account**: `cst8917assignment1sa`
- **SQL Server**: `cst8917-assignment1-sql`
- **Database**: `ImageMetadataDB`
- **Function App**: `cst8917-assignment1-func`
- **AzureWebJobsStorage**: Storage account connection string
- **SqlConnectionString**: SQL database connection string

---

## 🧪 Testing & Verification

### Local Development Testing

#### 1. Start Local Function App
```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the function app locally
func start
```

**Expected Output**: Function app should start successfully with messages like:
```
Azure Functions Core Tools
Core Tools Version: 4.x.x
Function Runtime Version: 4.x.x

Functions:

        function_app: [GET,POST] http://localhost:7071/api/function_app
```

#### 2. Manual Local Testing
1. **Upload Test Image**: Place an image file in your local blob storage container (as configured in `local.settings.json`)
2. **Monitor Terminal**: Watch the function app terminal for processing logs
3. **Check Logs**: Look for messages like:
   ```
   Image uploaded: [filename]
   Metadata extracted: [details]
   SQL Database Save: [status]
   Queue Send: [status]
   Processing report: [status]
   ```

#### 3. Local Verification Steps
- **Database Check**: Verify data is inserted into your local SQL database (if configured)
- **Queue Check**: Confirm messages are sent to your local storage queue
- **Output Check**: Check if processing reports are generated in the output container

### Azure Portal Verification

#### 1. Manual Image Upload to Azure Blob Storage
1. **Access Azure Portal**: https://portal.azure.com
2. **Navigate to Storage Account**: `cst8917assignment1sa`
3. **Go to Containers**: Click "Containers" in the left menu
4. **Select Container**: Click on `images-input` container
5. **Upload Image**: Click "Upload" → Select any image file (JPG, PNG, etc.)
6. **Confirm Upload**: Click "Upload" to complete

**Expected Result**: Function App should automatically trigger within 1-2 minutes

#### 2. Verify Function App Execution
1. **Navigate to Function App**: `cst8917-assignment1-func`
2. **Check Functions**: Should show `function_app` (blobTrigger)
3. **View Logs**: Click on the function → "Monitor" → Check recent executions
4. **Expected Log Messages**:
   ```
   Image uploaded: [filename]
   Metadata extracted: [details]
   SQL Database Save: [status]
   Queue Send: [status]
   Processing report: [status]
   ```

#### 3. Verify SQL Database Records
1. **Navigate to SQL Server**: `cst8917-assignment1-sql`
2. **Open Query Editor**: Click "Query editor"
3. **Run Query**:
   ```sql
   SELECT * FROM ImageMetadata ORDER BY CreatedAt DESC;
   ```
4. **Expected Result**: Should show your uploaded image metadata

#### 4. Verify Storage Queue Messages
1. **Navigate to Storage Account**: `cst8917assignment1sa`
2. **Go to Queues**: Click "Queues" in the left menu
3. **Check Queue**: Click on `image-processing-queue`
4. **Expected Result**: Should show processing messages

#### 5. Verify Output Reports
1. **Navigate to Storage Account**: `cst8917assignment1sa`
2. **Go to Containers**: Click "Containers"
3. **Check Output Container**: Click on `output` container
4. **Expected Result**: Should contain processing reports (JSON files)

#### Alternative: Using Azure Storage Explorer
1. **Download Azure Storage Explorer**: https://azure.microsoft.com/en-us/features/storage-explorer/
2. **Connect to Storage Account**: Add your storage account using connection string
3. **Navigate to Container**: `images-input`
4. **Upload Image**: Right-click → "Upload" → Select image file
5. **Monitor Results**: Check other containers and queues for results

### KQL Query Verification (Application Insights)
- Go to Function App → Application Insights → Logs (Analytics)
- Paste and run KQL queries below

---

## 📊 KQL Query Examples

### 1. Basic Log Queries
```kql
// View all Function App logs
traces
| where timestamp > ago(1h)
| where cloud_RoleName == "cst8917-assignment1-func"
| order by timestamp desc

// View function execution logs
traces
| where timestamp > ago(1h)
| where cloud_RoleName == "cst8917-assignment1-func"
| where message contains "function_app"
| order by timestamp desc
```

### 2. Function Execution Details
```kql
// View function execution success/failure
traces
| where timestamp > ago(1h)
| where cloud_RoleName == "cst8917-assignment1-func"
| where message contains "Executed" or message contains "Failed"
| project timestamp, message, severityLevel
| order by timestamp desc

// View Blob Trigger execution
traces
| where timestamp > ago(1h)
| where cloud_RoleName == "cst8917-assignment1-func"
| where message contains "blobTrigger" or message contains "Image uploaded"
| project timestamp, message
| order by timestamp desc
```

### 3. Error and Exception Queries
```kql
// View error logs
traces
| where timestamp > ago(1h)
| where cloud_RoleName == "cst8917-assignment1-func"
| where severityLevel == 3
| project timestamp, message, customDimensions
| order by timestamp desc

// View exceptions
exceptions
| where timestamp > ago(1h)
| where cloud_RoleName == "cst8917-assignment1-func"
| project timestamp, type, message, operation_Name
| order by timestamp desc
```

### 4. Performance Monitoring
```kql
// View function execution time
traces
| where timestamp > ago(1h)
| where cloud_RoleName == "cst8917-assignment1-func"
| where message contains "Duration"
| project timestamp, message
| order by timestamp desc

// View memory usage
performanceCounters
| where timestamp > ago(1h)
| where cloud_RoleName == "cst8917-assignment1-func"
| where name contains "Memory"
| project timestamp, name, value
| order by timestamp desc
```

### 5. Custom Queries - Assignment 1 Specific
```kql
// View image processing workflow
traces
| where timestamp > ago(1h)
| where cloud_RoleName == "cst8917-assignment1-func"
| where message contains "Image uploaded" or 
      message contains "Metadata extracted" or
      message contains "SQL Database Save" or
      message contains "Queue Send" or
      message contains "Processing report"
| project timestamp, message, severityLevel
| order by timestamp desc

// View SQL database operations
traces
| where timestamp > ago(1h)
| where cloud_RoleName == "cst8917-assignment1-func"
| where message contains "SQL" or message contains "database"
| project timestamp, message
| order by timestamp desc

// View queue operations
traces
| where timestamp > ago(1h)
| where cloud_RoleName == "cst8917-assignment1-func"
| where message contains "Queue" or message contains "queue"
| project timestamp, message
| order by timestamp desc
```

### 6. Real-time Monitoring Queries
```kql
// Real-time function execution monitoring
traces
| where timestamp > ago(10m)
| where cloud_RoleName == "cst8917-assignment1-func"
| where message contains "Executing" or message contains "Executed"
| project timestamp, message
| order by timestamp desc

// View recent errors
traces
| where timestamp > ago(30m)
| where cloud_RoleName == "cst8917-assignment1-func"
| where severityLevel >= 2
| project timestamp, message, severityLevel
| order by timestamp desc
```

#### How to Use in Azure Portal
1. Go to Function App → Application Insights → Logs (Analytics)
2. Paste the above KQL queries in the query editor
3. Click "Run" to execute the query
4. Save queries or create dashboards as needed

---

## 📈 Expected Results & Checklist

### Successful Processing Flow:
1. **Image Upload**: `test_azure_apple.png` uploaded to blob container
2. **Blob Trigger**: Function automatically triggered
3. **Metadata Extraction**: Image properties extracted (2400x1889, PNG, 560.28KB)
4. **SQL Storage**: Metadata saved to `ImageMetadata` table
5. **Queue Message**: Processing notification sent to queue
6. **Report Generation**: Processing report saved to output container

### Verification Checklist:
- ✅ Function App deployed and running
- ✅ Blob trigger automatically triggered
- ✅ Metadata correctly extracted
- ✅ SQL database operations successful
- ✅ Queue messages sent
- ✅ Processing reports generated
- ✅ Error handling working
- ✅ Logging comprehensive

---

## 🔍 Troubleshooting & Support

### Common Issues
- ODBC Driver Issues: `brew install msodbcsql18`
- Connection String Issues: Check format, firewall, credentials
- Function App Deployment Issues: Check Azure CLI login, resource group, Python version

### Debug Commands
```bash
az account show
az functionapp list --resource-group cst8917-assignment1-rg
az functionapp logs tail --name cst8917-assignment1-func --resource-group cst8917-assignment1-rg
```

For issues or questions:
- Check troubleshooting section
- Review Azure Portal logs
- Verify configuration settings
- Test with provided verification scripts

---

## 🎉 Final Status

- ✅ All files are English only
- ✅ All files are assignment related
- ✅ All requirements and features implemented
- ✅ Comprehensive documentation and verification
- ✅ Ready for submission 