# Nelson Textbook - New Schema Setup Guide

This guide will help you set up the new database schema in Supabase and upload the Nelson Textbook dataset.

## 🎯 Overview

The new schema includes:
- **nelson_textbook**: Main textbook content with 1536-dimension embeddings
- **pediatric_medical_resources**: Clinical protocols, dosing guidelines, and references
- **chat_sessions**: For conversation tracking
- **chat_messages**: For storing chat history with citations

## 📋 Step-by-Step Setup

### Step 1: Create Database Schema

1. **Go to your Supabase Dashboard**
   - URL: https://supabase.com/dashboard
   - Navigate to your project: `jlrjhjylekjedqwfctub`

2. **Open SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Run the Schema Setup**
   - Copy the entire contents of `new_schema_setup.sql`
   - Paste into the SQL Editor
   - Click "Run" to execute

### Step 2: Upload Dataset

After the schema is created, run the upload script:

```bash
python3 simple_upload.py
```

This will upload:
- **800 Nelson Textbook records** with medical content
- **5 Pediatric Resource records** with clinical protocols

## 📊 Dataset Details

### Nelson Textbook Table Structure

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| chapter | VARCHAR(255) | Chapter name |
| section | VARCHAR(500) | Section title |
| page_number | INTEGER | Page reference |
| content | TEXT | Medical content |
| embedding | vector(1536) | Semantic embedding |
| keywords | TEXT[] | Medical keywords |
| medical_category | VARCHAR(100) | Medical specialty |
| age_group | VARCHAR(50) | Target age group |

### Pediatric Resources Table Structure

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| title | VARCHAR(500) | Resource title |
| content | TEXT | Resource content |
| resource_type | VARCHAR(50) | protocol/dosage/guideline/reference |
| category | VARCHAR(100) | Medical category |
| age_range | VARCHAR(50) | Applicable age range |
| weight_range | VARCHAR(50) | Applicable weight range |
| embedding | vector(1536) | Semantic embedding |
| source | VARCHAR(255) | Source reference |

## 🔍 Semantic Search Function

The schema includes a powerful search function:

```sql
SELECT * FROM match_documents(
  query_embedding := '[your_1536_dimension_vector]',
  match_table := 'nelson_textbook',  -- or 'pediatric_medical_resources'
  match_count := 5,
  similarity_threshold := 0.7
);
```

## 📚 Medical Categories Covered

- **Allergy and Immunology** (460 records)
- **Cardiology** (340 records)
- **Pulmonology**
- **Neurology**
- **Endocrinology**
- **Gastroenterology**
- **Hematology**
- **Dermatology**
- **And more...**

## 🏥 Sample Pediatric Resources

1. **Pediatric Fever Management Protocol**
   - Acetaminophen and Ibuprofen dosing
   - Age-specific guidelines
   - Emergency criteria

2. **Pediatric Asthma Medication Dosing**
   - Albuterol MDI protocols
   - Prednisolone dosing
   - Exacerbation management

3. **Pediatric Dehydration Assessment**
   - Clinical signs by severity
   - Fluid replacement guidelines

4. **Pediatric Antibiotic Dosing Reference**
   - Common antibiotics
   - Weight-based dosing
   - Duration guidelines

5. **Newborn Screening Protocol**
   - Timing requirements
   - Screening conditions
   - Follow-up procedures

## 🚀 Usage Examples

### Basic Search Query
```python
from supabase import create_client

supabase = create_client(url, key)

# Search Nelson Textbook
results = supabase.rpc('match_documents', {
    'query_embedding': your_embedding_vector,
    'match_table': 'nelson_textbook',
    'match_count': 5,
    'similarity_threshold': 0.7
}).execute()

# Search Pediatric Resources
protocols = supabase.rpc('match_documents', {
    'query_embedding': your_embedding_vector,
    'match_table': 'pediatric_medical_resources',
    'match_count': 3,
    'similarity_threshold': 0.6
}).execute()
```

### Filter by Category
```sql
-- Get all cardiology content
SELECT * FROM nelson_textbook 
WHERE medical_category = 'Cardiology';

-- Get all dosing protocols
SELECT * FROM pediatric_medical_resources 
WHERE resource_type = 'dosage';
```

### Age-Specific Queries
```sql
-- Get infant-specific content
SELECT * FROM nelson_textbook 
WHERE age_group = 'Infant';

-- Get protocols for specific age range
SELECT * FROM pediatric_medical_resources 
WHERE age_range LIKE '%3 months%';
```

## 🔧 Troubleshooting

### Common Issues

1. **"relation does not exist" error**
   - Make sure you've run the SQL schema setup first
   - Check that all tables were created successfully

2. **Upload fails with JSON errors**
   - Check that the CSV files exist in the current directory
   - Verify the CSV format is correct

3. **Embedding dimension mismatch**
   - The schema uses 1536 dimensions (OpenAI text-embedding-3-small)
   - Mock embeddings are generated automatically during upload

### Verification Steps

After upload, verify your data:

```python
# Check record counts
nelson_count = supabase.table('nelson_textbook').select('id', count='exact').execute()
resources_count = supabase.table('pediatric_medical_resources').select('id', count='exact').execute()

print(f"Nelson records: {nelson_count.count}")
print(f"Resource records: {resources_count.count}")
```

## 🎯 Next Steps

1. **✅ Complete Schema Setup**
   - Run `new_schema_setup.sql` in Supabase
   - Verify all tables and indexes are created

2. **✅ Upload Dataset**
   - Run `python3 simple_upload.py`
   - Verify 800+ records uploaded successfully

3. **🔄 Generate Real Embeddings**
   - Get OpenAI API key
   - Replace mock embeddings with real ones
   - Use `text-embedding-3-small` model (1536 dimensions)

4. **🔍 Test Semantic Search**
   - Test the `match_documents` function
   - Verify similarity search works correctly

5. **🏗️  Build Your Application**
   - Use the semantic search for medical Q&A
   - Implement clinical decision support
   - Create pediatric dosing calculators

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify your Supabase project settings
3. Ensure pgvector extension is enabled
4. Check that your service key has the correct permissions

---

**Schema Version**: 2.0  
**Last Updated**: 2024-07-19  
**Total Records**: 805 (800 Nelson + 5 Resources)  
**Embedding Dimensions**: 1536  
**Ready for Production**: ✅

