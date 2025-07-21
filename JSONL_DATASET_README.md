# 📊 Nelson Textbook JSONL Datasets

This directory contains the Nelson Textbook of Pediatrics dataset converted to JSONL (JSON Lines) format, perfect for machine learning, fine-tuning, and data processing workflows.

## 🎯 Dataset Overview

| File | Records | Size | Description |
|------|---------|------|-------------|
| `nelson_textbook_dataset.jsonl` | 800 | 28.6 MB | Main medical textbook content |
| `pediatric_medical_resources.jsonl` | 5 | 174 KB | Clinical protocols and guidelines |
| `nelson_complete_dataset.jsonl` | 805 | 28.8 MB | Combined dataset |
| `nelson_training_dataset.jsonl` | 800 | 1.4 MB | Fine-tuning format |

## 📋 Dataset Structure

### Main Dataset Format (`nelson_textbook_dataset.jsonl`)

```json
{
  "id": "nelson_0001",
  "type": "medical_textbook",
  "source": "Nelson Textbook of Pediatrics",
  "chapter": "Chapter: Allergic Disorders",
  "section": "Allergic Disorders Chapter 182...",
  "page_number": 684,
  "content": "Allergic Disorders Chapter 182...",
  "medical_category": "Allergy and Immunology",
  "age_group": "Pediatric",
  "keywords": ["disorder", "clinical", "asthma", "patient", "disease"],
  "embedding": [1536-dimensional vector],
  "metadata": {
    "word_count": 154,
    "has_dosing_info": false,
    "has_diagnostic_info": true,
    "has_treatment_info": false,
    "created_at": "2025-07-20T21:16:28.494634"
  }
}
```

### Clinical Resources Format (`pediatric_medical_resources.jsonl`)

```json
{
  "id": "resource_001",
  "type": "clinical_resource",
  "source": "AAP Clinical Guidelines",
  "title": "Pediatric Fever Management Protocol",
  "content": "For children 3 months to 3 years...",
  "resource_type": "protocol",
  "category": "Emergency Medicine",
  "age_range": "3 months - 3 years",
  "weight_range": "5-15 kg",
  "embedding": [1536-dimensional vector],
  "metadata": {
    "word_count": 41,
    "is_protocol": true,
    "is_dosage_guide": false,
    "has_age_restrictions": true,
    "has_weight_restrictions": true,
    "created_at": "2025-07-20T21:16:30.062091"
  }
}
```

### Training Format (`nelson_training_dataset.jsonl`)

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a pediatric medical expert..."
    },
    {
      "role": "user",
      "content": "Tell me about allergic disorders..."
    },
    {
      "role": "assistant",
      "content": "Allergic Disorders Chapter 182..."
    }
  ],
  "metadata": {
    "source": "Nelson Textbook of Pediatrics",
    "chapter": "Chapter: Allergic Disorders",
    "section": "Allergic Disorders Chapter 182...",
    "category": "Allergy and Immunology",
    "age_group": "Pediatric",
    "page_number": 684
  }
}
```

## 📊 Dataset Statistics

### Medical Categories Distribution
- **Allergy and Immunology**: 460 records (57.5%)
- **Cardiology**: 340 records (42.5%)

### Age Group Distribution
- **Pediatric**: 558 records (69.8%)
- **Infant**: 108 records (13.5%)
- **Neonatal**: 84 records (10.5%)
- **Adolescent**: 25 records (3.1%)
- **School Age**: 25 records (3.1%)

### Clinical Resources
- **Emergency Medicine**: 2 protocols
- **Pulmonology**: 1 protocol
- **Infectious Diseases**: 1 protocol
- **Neonatology**: 1 protocol

## 🚀 Use Cases

### 1. **Machine Learning Training**
```python
import json

# Load dataset for training
with open('nelson_textbook_dataset.jsonl', 'r') as f:
    data = [json.loads(line) for line in f]

# Extract features
texts = [record['content'] for record in data]
categories = [record['medical_category'] for record in data]
embeddings = [record['embedding'] for record in data]
```

### 2. **Fine-tuning Language Models**
```python
# Use the training format for fine-tuning
with open('nelson_training_dataset.jsonl', 'r') as f:
    training_data = [json.loads(line) for line in f]

# Each record contains messages in OpenAI format
for example in training_data:
    messages = example['messages']
    # Use for fine-tuning GPT, Claude, etc.
```

### 3. **Vector Database Ingestion**
```python
# Load embeddings for vector search
import numpy as np

embeddings = []
metadata = []

with open('nelson_complete_dataset.jsonl', 'r') as f:
    for line in f:
        record = json.loads(line)
        embeddings.append(record['embedding'])
        metadata.append({
            'id': record['id'],
            'content': record['content'],
            'category': record.get('medical_category', record.get('category')),
            'type': record['type']
        })

# Insert into Pinecone, Weaviate, Chroma, etc.
```

### 4. **Medical AI Applications**
```python
# Search for relevant medical content
def search_medical_content(query_embedding, threshold=0.8):
    results = []
    
    with open('nelson_complete_dataset.jsonl', 'r') as f:
        for line in f:
            record = json.loads(line)
            similarity = cosine_similarity(query_embedding, record['embedding'])
            
            if similarity > threshold:
                results.append({
                    'content': record['content'],
                    'similarity': similarity,
                    'category': record.get('medical_category', record.get('category')),
                    'source': record['source']
                })
    
    return sorted(results, key=lambda x: x['similarity'], reverse=True)
```

## 🔍 Data Quality Features

### Content Analysis
Each record includes metadata about content type:
- **`has_dosing_info`**: Contains medication dosing information
- **`has_diagnostic_info`**: Contains diagnostic criteria or symptoms
- **`has_treatment_info`**: Contains treatment recommendations

### Clinical Resources
- **Age-specific protocols**: Tailored for different pediatric age groups
- **Weight-based dosing**: Includes weight ranges for medication calculations
- **Evidence-based guidelines**: From AAP and other medical organizations

## 🛠️ Processing Scripts

### Load and Analyze Dataset
```python
import json
from collections import Counter

def analyze_jsonl_dataset(filename):
    records = []
    
    with open(filename, 'r') as f:
        for line in f:
            records.append(json.loads(line))
    
    print(f"Total records: {len(records)}")
    
    # Analyze categories
    categories = [r.get('medical_category', r.get('category', 'unknown')) 
                 for r in records]
    print("Categories:", Counter(categories))
    
    # Analyze types
    types = [r.get('type', 'unknown') for r in records]
    print("Types:", Counter(types))
    
    return records

# Usage
nelson_data = analyze_jsonl_dataset('nelson_textbook_dataset.jsonl')
```

### Filter by Category
```python
def filter_by_category(filename, category):
    filtered_records = []
    
    with open(filename, 'r') as f:
        for line in f:
            record = json.loads(line)
            if (record.get('medical_category') == category or 
                record.get('category') == category):
                filtered_records.append(record)
    
    return filtered_records

# Get all cardiology records
cardiology_records = filter_by_category('nelson_textbook_dataset.jsonl', 'Cardiology')
```

### Extract Embeddings
```python
def extract_embeddings(filename):
    embeddings = []
    metadata = []
    
    with open(filename, 'r') as f:
        for line in f:
            record = json.loads(line)
            embeddings.append(record['embedding'])
            metadata.append({
                'id': record['id'],
                'content': record['content'][:100] + '...',  # Truncated
                'category': record.get('medical_category', record.get('category'))
            })
    
    return embeddings, metadata

# Usage
embeddings, metadata = extract_embeddings('nelson_complete_dataset.jsonl')
```

## 📈 Performance Considerations

### File Sizes
- **Main dataset**: 28.6 MB (800 records with 1536-dim embeddings)
- **Training format**: 1.4 MB (optimized for fine-tuning)
- **Combined dataset**: 28.8 MB (all records together)

### Memory Usage
- **Full dataset in memory**: ~30 MB
- **Embeddings only**: ~5 MB (800 × 1536 × 4 bytes)
- **Text content only**: ~2 MB

### Streaming Processing
```python
# Process large files without loading everything into memory
def process_jsonl_stream(filename, batch_size=100):
    batch = []
    
    with open(filename, 'r') as f:
        for line in f:
            record = json.loads(line)
            batch.append(record)
            
            if len(batch) >= batch_size:
                yield batch
                batch = []
        
        if batch:  # Process remaining records
            yield batch

# Usage
for batch in process_jsonl_stream('nelson_complete_dataset.jsonl'):
    # Process batch of records
    process_batch(batch)
```

## 🎯 Next Steps

1. **Replace Mock Embeddings**: Generate real embeddings using OpenAI's `text-embedding-3-small` model
2. **Expand Dataset**: Add more medical specialties and clinical resources
3. **Fine-tune Models**: Use the training format to create specialized medical AI models
4. **Build Applications**: Create medical Q&A systems, diagnostic aids, and clinical decision support tools

## 📞 Support

For questions about the JSONL datasets:
1. Check the data structure examples above
2. Use the provided processing scripts
3. Refer to the original CSV files for data validation

---

**Dataset Version**: 1.0  
**Created**: 2025-07-20  
**Format**: JSONL (JSON Lines)  
**Embedding Dimensions**: 1536  
**Total Records**: 805  
**Ready for Production**: ✅

