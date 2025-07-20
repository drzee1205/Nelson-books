#!/usr/bin/env python3
"""
Create JSONL Dataset from Nelson Textbook Data
Converts the CSV data into JSONL format for ML/AI applications.
"""

import csv
import json
import random
from typing import List, Dict, Any
from datetime import datetime

def parse_keywords_array(keywords_str: str) -> List[str]:
    """Parse PostgreSQL array format keywords string."""
    if not keywords_str or keywords_str == '{}':
        return []
    
    keywords_str = keywords_str.strip('{}')
    keywords = []
    
    for keyword in keywords_str.split(','):
        keyword = keyword.strip().strip('"').strip("'")
        if keyword:
            keywords.append(keyword)
    
    return keywords

def generate_mock_embedding_1536() -> List[float]:
    """Generate a mock 1536-dimensional embedding vector."""
    embedding = [random.uniform(-1, 1) for _ in range(1536)]
    magnitude = sum(x**2 for x in embedding) ** 0.5
    embedding = [x / magnitude for x in embedding]
    return embedding

def create_nelson_textbook_jsonl():
    """Create JSONL dataset from Nelson Textbook CSV."""
    
    print("📚 Creating Nelson Textbook JSONL dataset...")
    
    output_file = "nelson_textbook_dataset.jsonl"
    records_processed = 0
    
    try:
        with open('nelson_textbook_dataset.csv', 'r', encoding='utf-8', errors='replace') as csv_file:
            with open(output_file, 'w', encoding='utf-8') as jsonl_file:
                reader = csv.DictReader(csv_file)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Parse keywords
                        keywords = parse_keywords_array(row.get('keywords', '{}'))
                        
                        # Generate embedding
                        embedding = generate_mock_embedding_1536()
                        
                        # Create JSONL record
                        record = {
                            "id": f"nelson_{row_num:04d}",
                            "type": "medical_textbook",
                            "source": "Nelson Textbook of Pediatrics",
                            "chapter": row.get('chapter', '').strip(),
                            "section": row.get('section', '').strip(),
                            "page_number": int(row['page_number']) if row.get('page_number') and row['page_number'].isdigit() else None,
                            "content": row.get('content', '').strip(),
                            "medical_category": row.get('medical_category', '').strip(),
                            "age_group": row.get('age_group', '').strip(),
                            "keywords": keywords,
                            "embedding": embedding,
                            "metadata": {
                                "word_count": len(row.get('content', '').split()),
                                "has_dosing_info": any(term in row.get('content', '').lower() for term in ['dose', 'dosage', 'mg/kg', 'administration']),
                                "has_diagnostic_info": any(term in row.get('content', '').lower() for term in ['diagnosis', 'symptoms', 'signs', 'clinical']),
                                "has_treatment_info": any(term in row.get('content', '').lower() for term in ['treatment', 'therapy', 'management', 'intervention']),
                                "created_at": datetime.now().isoformat()
                            }
                        }
                        
                        # Write JSONL record
                        jsonl_file.write(json.dumps(record, ensure_ascii=False) + '\n')
                        records_processed += 1
                        
                        if row_num % 100 == 0:
                            print(f"  ✅ Processed {row_num} records...")
                    
                    except Exception as e:
                        print(f"  ⚠️  Error processing row {row_num}: {str(e)[:50]}...")
                        continue
    
    except Exception as e:
        print(f"❌ Error creating Nelson JSONL: {e}")
        return 0
    
    print(f"✅ Created {output_file} with {records_processed} records")
    return records_processed

def create_pediatric_resources_jsonl():
    """Create JSONL dataset from Pediatric Resources CSV."""
    
    print("🏥 Creating Pediatric Resources JSONL dataset...")
    
    output_file = "pediatric_medical_resources.jsonl"
    records_processed = 0
    
    try:
        with open('pediatric_medical_resources_dataset.csv', 'r', encoding='utf-8') as csv_file:
            with open(output_file, 'w', encoding='utf-8') as jsonl_file:
                reader = csv.DictReader(csv_file)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Generate embedding
                        embedding = generate_mock_embedding_1536()
                        
                        # Create JSONL record
                        record = {
                            "id": f"resource_{row_num:03d}",
                            "type": "clinical_resource",
                            "source": row.get('source', 'Clinical Guidelines').strip(),
                            "title": row.get('title', '').strip(),
                            "content": row.get('content', '').strip(),
                            "resource_type": row.get('resource_type', 'reference').strip(),
                            "category": row.get('category', '').strip(),
                            "age_range": row.get('age_range', '').strip() if row.get('age_range') else None,
                            "weight_range": row.get('weight_range', '').strip() if row.get('weight_range') else None,
                            "embedding": embedding,
                            "metadata": {
                                "word_count": len(row.get('content', '').split()),
                                "is_protocol": row.get('resource_type', '') == 'protocol',
                                "is_dosage_guide": row.get('resource_type', '') == 'dosage',
                                "has_age_restrictions": bool(row.get('age_range')),
                                "has_weight_restrictions": bool(row.get('weight_range')),
                                "created_at": datetime.now().isoformat()
                            }
                        }
                        
                        # Write JSONL record
                        jsonl_file.write(json.dumps(record, ensure_ascii=False) + '\n')
                        records_processed += 1
                    
                    except Exception as e:
                        print(f"  ⚠️  Error processing resource row {row_num}: {e}")
                        continue
    
    except Exception as e:
        print(f"❌ Error creating Resources JSONL: {e}")
        return 0
    
    print(f"✅ Created {output_file} with {records_processed} records")
    return records_processed

def create_combined_jsonl():
    """Create a combined JSONL dataset with all records."""
    
    print("🔄 Creating combined JSONL dataset...")
    
    output_file = "nelson_complete_dataset.jsonl"
    total_records = 0
    
    try:
        with open(output_file, 'w', encoding='utf-8') as combined_file:
            
            # Add Nelson Textbook records
            try:
                with open('nelson_textbook_dataset.jsonl', 'r', encoding='utf-8') as nelson_file:
                    for line in nelson_file:
                        combined_file.write(line)
                        total_records += 1
            except FileNotFoundError:
                print("  ⚠️  nelson_textbook_dataset.jsonl not found, skipping...")
            
            # Add Pediatric Resources records
            try:
                with open('pediatric_medical_resources.jsonl', 'r', encoding='utf-8') as resources_file:
                    for line in resources_file:
                        combined_file.write(line)
                        total_records += 1
            except FileNotFoundError:
                print("  ⚠️  pediatric_medical_resources.jsonl not found, skipping...")
    
    except Exception as e:
        print(f"❌ Error creating combined JSONL: {e}")
        return 0
    
    print(f"✅ Created {output_file} with {total_records} total records")
    return total_records

def create_training_format_jsonl():
    """Create JSONL in training format for fine-tuning."""
    
    print("🎯 Creating training format JSONL...")
    
    output_file = "nelson_training_dataset.jsonl"
    records_processed = 0
    
    try:
        with open('nelson_textbook_dataset.csv', 'r', encoding='utf-8', errors='replace') as csv_file:
            with open(output_file, 'w', encoding='utf-8') as jsonl_file:
                reader = csv.DictReader(csv_file)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        content = row.get('content', '').strip()
                        chapter = row.get('chapter', '').strip()
                        section = row.get('section', '').strip()
                        category = row.get('medical_category', '').strip()
                        
                        if not content:
                            continue
                        
                        # Create training format record
                        training_record = {
                            "messages": [
                                {
                                    "role": "system",
                                    "content": f"You are a pediatric medical expert. Provide accurate information from the Nelson Textbook of Pediatrics about {category.lower()}."
                                },
                                {
                                    "role": "user", 
                                    "content": f"Tell me about {section.lower() if section else chapter.lower()}"
                                },
                                {
                                    "role": "assistant",
                                    "content": content
                                }
                            ],
                            "metadata": {
                                "source": "Nelson Textbook of Pediatrics",
                                "chapter": chapter,
                                "section": section,
                                "category": category,
                                "age_group": row.get('age_group', '').strip(),
                                "page_number": int(row['page_number']) if row.get('page_number') and row['page_number'].isdigit() else None
                            }
                        }
                        
                        # Write training record
                        jsonl_file.write(json.dumps(training_record, ensure_ascii=False) + '\n')
                        records_processed += 1
                        
                        if row_num % 100 == 0:
                            print(f"  ✅ Created {row_num} training examples...")
                    
                    except Exception as e:
                        print(f"  ⚠️  Error processing training row {row_num}: {str(e)[:50]}...")
                        continue
    
    except Exception as e:
        print(f"❌ Error creating training JSONL: {e}")
        return 0
    
    print(f"✅ Created {output_file} with {records_processed} training examples")
    return records_processed

def analyze_jsonl_dataset(filename: str):
    """Analyze a JSONL dataset and provide statistics."""
    
    print(f"\n📊 Analyzing {filename}...")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            records = []
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line.strip())
                    records.append(record)
                except json.JSONDecodeError as e:
                    print(f"  ⚠️  Invalid JSON on line {line_num}: {e}")
                    continue
        
        if not records:
            print("  ❌ No valid records found")
            return
        
        print(f"  📈 Total Records: {len(records)}")
        
        # Analyze record types
        types = {}
        categories = {}
        age_groups = {}
        
        for record in records:
            # Record types
            record_type = record.get('type', 'unknown')
            types[record_type] = types.get(record_type, 0) + 1
            
            # Medical categories
            category = record.get('medical_category') or record.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
            
            # Age groups
            age_group = record.get('age_group', 'unknown')
            age_groups[age_group] = age_groups.get(age_group, 0) + 1
        
        print(f"  📋 Record Types:")
        for rtype, count in sorted(types.items()):
            print(f"    - {rtype}: {count}")
        
        print(f"  🏥 Top Medical Categories:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    - {category}: {count}")
        
        print(f"  👶 Age Groups:")
        for age_group, count in sorted(age_groups.items()):
            if age_group != 'unknown':
                print(f"    - {age_group}: {count}")
        
        # Sample record
        print(f"  📄 Sample Record Structure:")
        sample = records[0]
        for key in sorted(sample.keys()):
            value_type = type(sample[key]).__name__
            if key == 'embedding':
                print(f"    - {key}: {value_type} (length: {len(sample[key])})")
            elif isinstance(sample[key], str) and len(sample[key]) > 50:
                print(f"    - {key}: {value_type} (length: {len(sample[key])})")
            else:
                print(f"    - {key}: {value_type}")
    
    except Exception as e:
        print(f"  ❌ Error analyzing {filename}: {e}")

def main():
    """Main function to create all JSONL datasets."""
    
    print("🏥 Nelson Textbook - JSONL Dataset Creation")
    print("=" * 60)
    
    # Create individual JSONL files
    nelson_count = create_nelson_textbook_jsonl()
    resources_count = create_pediatric_resources_jsonl()
    
    # Create combined dataset
    combined_count = create_combined_jsonl()
    
    # Create training format
    training_count = create_training_format_jsonl()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 JSONL Dataset Creation Summary:")
    print(f"✅ Nelson Textbook JSONL: {nelson_count} records")
    print(f"✅ Pediatric Resources JSONL: {resources_count} records")
    print(f"✅ Combined Dataset JSONL: {combined_count} records")
    print(f"✅ Training Format JSONL: {training_count} examples")
    
    # Analyze datasets
    if nelson_count > 0:
        analyze_jsonl_dataset("nelson_textbook_dataset.jsonl")
    
    if resources_count > 0:
        analyze_jsonl_dataset("pediatric_medical_resources.jsonl")
    
    if training_count > 0:
        analyze_jsonl_dataset("nelson_training_dataset.jsonl")
    
    print(f"\n🎯 JSONL Files Created:")
    print("📚 nelson_textbook_dataset.jsonl - Main medical content")
    print("🏥 pediatric_medical_resources.jsonl - Clinical protocols")
    print("🔄 nelson_complete_dataset.jsonl - Combined dataset")
    print("🎯 nelson_training_dataset.jsonl - Fine-tuning format")
    
    print(f"\n🚀 Use Cases:")
    print("• Machine Learning model training")
    print("• Fine-tuning language models")
    print("• Data processing pipelines")
    print("• Vector database ingestion")
    print("• Medical AI applications")

if __name__ == "__main__":
    main()

