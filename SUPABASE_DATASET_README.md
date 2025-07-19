# Nelson Pediatrics Supabase Dataset

This directory contains a comprehensive dataset extracted from Nelson's Textbook of Pediatrics, formatted for use with Supabase and pgvector for semantic search capabilities.

## 📊 Dataset Overview

- **Total Records**: 800 medical text chunks
- **Source**: Nelson Textbook of Pediatrics (23 chapters)
- **Format**: CSV with content and metadata columns
- **Chunk Size**: 150-1200 characters per chunk
- **Embedding Dimension**: 1024 (compatible with OpenAI text-embedding-ada-002)

## 📁 Files Included

### 1. `nelson_pediatrics_supabase_dataset.csv`
The main dataset file containing:
- **content**: Medical text content from Nelson Textbook
- **metadata**: JSON metadata with chapter, title, source information

### 2. `supabase_setup.sql`
Complete SQL setup script including:
- Database schema creation
- pgvector extension setup
- Semantic search functions
- Performance indexes
- Sample data insertion

## 🏥 Medical Specialties Covered

| Chapter | Records | Content Focus |
|---------|---------|---------------|
| Allergic Disorders | ~80 | Asthma, allergies, immunologic reactions |
| Cardiovascular Disorders | ~100 | Heart conditions, congenital defects |
| Respiratory Disorders | ~120 | Pneumonia, bronchitis, respiratory infections |
| Neurologic Disorders | ~110 | Seizures, developmental delays, CNS conditions |
| Endocrine Disorders | ~90 | Diabetes, thyroid, growth disorders |
| Gastroenterology | ~130 | GI infections, inflammatory bowel disease |
| Hematology | ~70 | Blood disorders, anemia, bleeding disorders |
| Immunology | ~50 | Immune deficiencies, autoimmune conditions |
| Metabolic Disorders | ~80 | Inborn errors of metabolism |
| Dermatology | ~60 | Skin conditions, rashes, infections |

## 🚀 Quick Setup Guide

### 1. Database Setup
```sql
-- Run the complete setup script
\i supabase_setup.sql
```

### 2. Import Dataset
```sql
-- Import CSV data (after generating embeddings)
COPY documents(content, metadata) 
FROM '/path/to/nelson_pediatrics_supabase_dataset.csv' 
DELIMITER ',' CSV HEADER;
```

### 3. Generate Embeddings
You'll need to generate embeddings for each record using your preferred embedding model:

```python
import openai
import pandas as pd
import numpy as np
from supabase import create_client

# Load dataset
df = pd.read_csv('nelson_pediatrics_supabase_dataset.csv')

# Generate embeddings (example with OpenAI)
def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']

# Update database with embeddings
supabase = create_client(url, key)
for index, row in df.iterrows():
    embedding = get_embedding(row['content'])
    supabase.table('documents').update({
        'embedding': embedding
    }).eq('id', index + 1).execute()
```

## 🔍 Usage Examples

### Basic Semantic Search
```sql
-- Search for content similar to a query
SELECT * FROM match_documents(
  query_embedding := '[your_query_embedding_vector]',
  match_threshold := 0.5,
  match_count := 5
);
```

### Chapter-Specific Search
```sql
-- Search within a specific medical specialty
SELECT * FROM search_by_chapter(
  chapter_name := 'Cardiovascular Disorders',
  query_embedding := '[your_query_embedding_vector]',
  match_threshold := 0.3,
  match_count := 10
);
```

### Get Chapter Statistics
```sql
-- View content distribution by medical specialty
SELECT * FROM get_chapter_stats();
```

## 📋 Metadata Schema

Each record includes comprehensive metadata:

```json
{
  "title": "Allergic Disorders - Section 1",
  "source": "Nelson Textbook of Pediatrics",
  "chapter": "Allergic Disorders",
  "content_type": "medical_text",
  "id": 1
}
```

## 🎯 Use Cases

### Medical Education
- **Question Answering**: Build AI tutors for medical students
- **Case Studies**: Generate clinical scenarios and explanations
- **Differential Diagnosis**: Support diagnostic reasoning

### Clinical Decision Support
- **Symptom Analysis**: Match patient presentations to conditions
- **Treatment Guidelines**: Retrieve relevant treatment protocols
- **Drug Information**: Find medication dosing and contraindications

### Research Applications
- **Literature Mining**: Extract specific medical concepts
- **Knowledge Graphs**: Build relationships between conditions
- **Clinical NLP**: Train domain-specific language models

## ⚡ Performance Optimization

The setup includes several performance optimizations:

1. **Vector Index**: IVFFlat index for fast similarity search
2. **Metadata Indexes**: GIN index on chapter field
3. **Timestamp Indexes**: For temporal queries
4. **Optimized Functions**: SQL-based functions for better performance

## 🔧 Customization Options

### Adjust Similarity Thresholds
- **High Precision**: threshold > 0.7
- **Balanced**: threshold 0.4-0.7  
- **High Recall**: threshold < 0.4

### Modify Chunk Sizes
The current chunking strategy can be adjusted based on your needs:
- **Smaller chunks**: Better for specific facts
- **Larger chunks**: Better for contextual understanding

### Add Custom Metadata
Extend the metadata schema to include:
- Page numbers
- Section headings
- Medical codes (ICD-10, CPT)
- Severity levels
- Age groups

## 📚 Data Quality Notes

- **Content Cleaning**: Removed copyright notices, figure references
- **Medical Accuracy**: Content directly from authoritative Nelson Textbook
- **Completeness**: Covers major pediatric medical specialties
- **Consistency**: Standardized metadata format across all records

## 🔒 Usage Guidelines

- **Educational Use**: Appropriate for medical education and training
- **Clinical Support**: Can supplement but not replace clinical judgment
- **Research**: Suitable for medical NLP and AI research projects
- **Attribution**: Please cite Nelson Textbook of Pediatrics as source

## 🆘 Troubleshooting

### Common Issues

1. **Embedding Generation Fails**
   - Check API keys and rate limits
   - Verify text encoding (UTF-8)
   - Handle special characters in medical text

2. **Search Returns No Results**
   - Lower similarity threshold
   - Check embedding dimensions (must be 1024)
   - Verify vector index is created

3. **Performance Issues**
   - Increase `lists` parameter in vector index
   - Consider partitioning by chapter
   - Use connection pooling

### Support
For technical issues or questions about the dataset, please refer to the main repository documentation or create an issue.

---

**Dataset Version**: 1.0  
**Last Updated**: 2024-07-19  
**Total Size**: ~800 records, ~18MB text content  
**License**: Educational use, cite Nelson Textbook of Pediatrics

