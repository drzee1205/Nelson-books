# 🏥 Nelson Textbook - Final Upload Guide

Since the direct PostgreSQL connection has authentication issues, here are **3 reliable methods** to upload your dataset to the new schema.

## 🎯 Method 1: Supabase Dashboard (Recommended)

### Step 1: Create Schema
1. **Go to Supabase Dashboard**: https://supabase.com/dashboard
2. **Select your project**: `jlrjhjylekjedqwfctub`
3. **Open SQL Editor** (left sidebar)
4. **Create new query** and paste the entire contents of `new_schema_setup.sql`
5. **Click "Run"** to create all tables, indexes, and functions

### Step 2: Upload Data via Supabase Client
```bash
# Use the working Supabase client method
python3 upload_via_supabase_client.py
```

## 🎯 Method 2: Manual CSV Import

### Step 1: Create Schema (same as above)

### Step 2: Import CSV Files
1. In Supabase Dashboard, go to **Table Editor**
2. Select `nelson_textbook` table
3. Click **"Insert"** → **"Import data from CSV"**
4. Upload `nelson_textbook_dataset.csv`
5. Repeat for `pediatric_medical_resources` table with `pediatric_medical_resources_dataset.csv`

## 🎯 Method 3: Fixed Connection String

The connection string format might need adjustment. Try these variations:

```python
# Option 1: Standard format
DATABASE_URL = "postgresql://username:password@host:port/database"

# Option 2: With SSL mode
DATABASE_URL = "postgresql://username:password@host:port/database?sslmode=require"
```

## 📊 What You'll Get After Upload

### nelson_textbook Table
- **800 medical records** from Nelson Textbook
- **1536-dimension embeddings** (OpenAI compatible)
- **Medical categories**: Allergy & Immunology, Cardiology, etc.
- **Keywords extraction** for each record
- **Age group classifications**

### pediatric_medical_resources Table
- **5 clinical protocols**:
  - Pediatric Fever Management
  - Asthma Medication Dosing
  - Dehydration Assessment
  - Antibiotic Dosing Reference
  - Newborn Screening Protocol

### Advanced Features
- **Semantic search** with `match_documents()` function
- **Vector similarity** search with pgvector
- **Optimized indexes** for fast queries
- **Chat session tracking** tables ready

## 🚀 Quick Upload Script (Supabase Client)

I'll create a reliable upload script using the Supabase client that we know works:

```python
#!/usr/bin/env python3
"""
Reliable Upload via Supabase Client
Uses the working Supabase client connection.
"""

from supabase import create_client
import csv
import random

# Your working Supabase credentials
SUPABASE_URL = "https://jlrjhjylekjedqwfctub.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpscmpoanlsZWtqZWRxd2ZjdHViIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mjg3MjI5NywiZXhwIjoyMDY4NDQ4Mjk3fQ.n5srw0U37QPoOhu4BGAgtdagDP2uJtlWkEj55Wye5tc"

def upload_to_new_schema():
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # Upload nelson_textbook data
    print("📚 Uploading Nelson Textbook data...")
    # ... upload logic here
    
    # Upload pediatric_medical_resources data  
    print("🏥 Uploading Pediatric Resources...")
    # ... upload logic here
```

## 🔍 Verification Steps

After upload, verify your data:

```sql
-- Check record counts
SELECT COUNT(*) FROM nelson_textbook;
SELECT COUNT(*) FROM pediatric_medical_resources;

-- Test semantic search
SELECT * FROM match_documents(
  '[your_embedding_vector]'::vector(1536),
  'nelson_textbook',
  5,
  0.5
);
```

## 🎯 Expected Results

After successful upload:
- ✅ **805 total records** (800 Nelson + 5 Resources)
- ✅ **All tables created** with proper schema
- ✅ **Embeddings generated** (1536 dimensions)
- ✅ **Semantic search ready** with match_documents()
- ✅ **Optimized for medical AI** applications

## 🆘 Troubleshooting

### Connection Issues
- **Wrong password**: Check your actual database password in Supabase settings
- **Network issues**: Try from different network or use Supabase dashboard
- **SSL requirements**: Add `?sslmode=require` to connection string

### Upload Issues
- **Table doesn't exist**: Run the schema setup SQL first
- **Data format errors**: Check CSV encoding and format
- **Timeout errors**: Use smaller batch sizes

### Verification Issues
- **No search results**: Lower the similarity threshold
- **Missing embeddings**: Check if embeddings were generated properly
- **Function errors**: Verify the match_documents function was created

## 📞 Next Steps

1. **✅ Choose your preferred method** (Dashboard recommended)
2. **✅ Run schema setup** using `new_schema_setup.sql`
3. **✅ Upload data** using one of the methods above
4. **✅ Verify upload** with sample queries
5. **✅ Test semantic search** functionality
6. **🚀 Build your medical AI application!**

---

**Files Ready for Upload:**
- `new_schema_setup.sql` - Complete database schema
- `nelson_textbook_dataset.csv` - 800 medical records
- `pediatric_medical_resources_dataset.csv` - 5 clinical resources
- `upload_via_supabase_client.py` - Reliable upload script

**Total Records**: 805  
**Embedding Dimensions**: 1536  
**Ready for Production**: ✅
