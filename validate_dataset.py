#!/usr/bin/env python3
"""
Dataset Validation Script for Nelson Pediatrics Supabase Dataset
Validates the CSV format, content quality, and metadata structure.
"""

import csv
import json
import sys
from collections import Counter

def validate_dataset(csv_file):
    """Validate the dataset and return statistics."""
    
    print(f"🔍 Validating dataset: {csv_file}")
    print("=" * 50)
    
    # Statistics
    total_records = 0
    content_lengths = []
    chapters = []
    metadata_errors = []
    content_errors = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, 1):
                total_records += 1
                
                # Validate content
                content = row.get('content', '')
                if not content or len(content.strip()) < 50:
                    content_errors.append(f"Row {row_num}: Content too short or empty")
                else:
                    content_lengths.append(len(content))
                
                # Validate metadata
                metadata_str = row.get('metadata', '')
                try:
                    metadata = json.loads(metadata_str)
                    
                    # Check required fields
                    required_fields = ['title', 'source', 'chapter', 'content_type', 'id']
                    for field in required_fields:
                        if field not in metadata:
                            metadata_errors.append(f"Row {row_num}: Missing {field} in metadata")
                    
                    if 'chapter' in metadata:
                        chapters.append(metadata['chapter'])
                        
                except json.JSONDecodeError:
                    metadata_errors.append(f"Row {row_num}: Invalid JSON in metadata")
    
    except FileNotFoundError:
        print(f"❌ Error: File {csv_file} not found")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Print results
    print(f"📊 DATASET STATISTICS")
    print(f"Total Records: {total_records}")
    print(f"Average Content Length: {sum(content_lengths) / len(content_lengths):.0f} characters")
    print(f"Min Content Length: {min(content_lengths) if content_lengths else 0}")
    print(f"Max Content Length: {max(content_lengths) if content_lengths else 0}")
    print()
    
    print(f"📚 CHAPTER DISTRIBUTION")
    chapter_counts = Counter(chapters)
    for chapter, count in chapter_counts.most_common():
        print(f"  {chapter}: {count} records")
    print()
    
    # Error reporting
    if content_errors:
        print(f"⚠️  CONTENT ERRORS ({len(content_errors)})")
        for error in content_errors[:5]:  # Show first 5
            print(f"  {error}")
        if len(content_errors) > 5:
            print(f"  ... and {len(content_errors) - 5} more")
        print()
    
    if metadata_errors:
        print(f"⚠️  METADATA ERRORS ({len(metadata_errors)})")
        for error in metadata_errors[:5]:  # Show first 5
            print(f"  {error}")
        if len(metadata_errors) > 5:
            print(f"  ... and {len(metadata_errors) - 5} more")
        print()
    
    # Overall validation
    total_errors = len(content_errors) + len(metadata_errors)
    if total_errors == 0:
        print("✅ VALIDATION PASSED - Dataset is ready for Supabase!")
        print(f"📈 Quality Score: 100% ({total_records} valid records)")
    else:
        error_rate = (total_errors / total_records) * 100
        print(f"⚠️  VALIDATION COMPLETED WITH WARNINGS")
        print(f"📈 Quality Score: {100 - error_rate:.1f}% ({total_records - total_errors} valid records)")
    
    print()
    print("🚀 NEXT STEPS:")
    print("1. Run supabase_setup.sql in your Supabase database")
    print("2. Import the CSV data")
    print("3. Generate embeddings for each record")
    print("4. Test semantic search functionality")
    
    return total_errors == 0

if __name__ == "__main__":
    csv_file = "nelson_pediatrics_supabase_dataset.csv"
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    validate_dataset(csv_file)

