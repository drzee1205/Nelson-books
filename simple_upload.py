#!/usr/bin/env python3
"""
Simple Upload to Existing Supabase Tables
Assumes the new schema tables already exist in Supabase.
"""

import csv
import time
import random
from typing import List
from supabase import create_client, Client

# Supabase Configuration
SUPABASE_URL = "https://jlrjhjylekjedqwfctub.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpscmpoanlsZWtqZWRxd2ZjdHViIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mjg3MjI5NywiZXhwIjoyMDY4NDQ4Mjk3fQ.n5srw0U37QPoOhu4BGAgtdagDP2uJtlWkEj55Wye5tc"

def create_supabase_client() -> Client:
    """Create and return Supabase client."""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def generate_mock_embedding_1536() -> List[float]:
    """Generate a mock 1536-dimensional embedding vector."""
    embedding = [random.uniform(-1, 1) for _ in range(1536)]
    magnitude = sum(x**2 for x in embedding) ** 0.5
    embedding = [x / magnitude for x in embedding]
    return embedding

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

def check_tables_exist():
    """Check if the required tables exist."""
    
    print("🔍 Checking if tables exist...")
    
    supabase = create_supabase_client()
    
    try:
        # Try to query each table
        nelson_test = supabase.table('nelson_textbook').select('id').limit(1).execute()
        print("✅ nelson_textbook table exists")
        
        resources_test = supabase.table('pediatric_medical_resources').select('id').limit(1).execute()
        print("✅ pediatric_medical_resources table exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Tables don't exist or error accessing them: {e}")
        print("\n📋 Please create the tables first using the SQL schema:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Run the SQL from new_schema_setup.sql")
        print("4. Then run this script again")
        return False

def upload_nelson_data():
    """Upload Nelson Textbook data."""
    
    print("📚 Uploading Nelson Textbook data...")
    
    supabase = create_supabase_client()
    successful = 0
    failed = 0
    
    try:
        with open('nelson_textbook_dataset.csv', 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            
            batch_data = []
            batch_size = 5  # Very small batches to avoid issues
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Clean and prepare data
                    keywords = parse_keywords_array(row.get('keywords', '{}'))
                    embedding = generate_mock_embedding_1536()
                    
                    # Ensure all fields are within limits
                    record = {
                        'chapter': str(row.get('chapter', ''))[:255],
                        'section': str(row.get('section', ''))[:500],
                        'page_number': int(row['page_number']) if row.get('page_number') and row['page_number'].isdigit() else None,
                        'content': str(row.get('content', '')),
                        'embedding': embedding,
                        'keywords': keywords,
                        'medical_category': str(row.get('medical_category', ''))[:100],
                        'age_group': str(row.get('age_group', ''))[:50]
                    }
                    
                    batch_data.append(record)
                    
                    # Upload in small batches
                    if len(batch_data) >= batch_size:
                        try:
                            result = supabase.table('nelson_textbook').insert(batch_data).execute()
                            
                            if result.data:
                                successful += len(result.data)
                                print(f"  ✅ Batch {row_num//batch_size}: {len(result.data)} records")
                            else:
                                failed += len(batch_data)
                                print(f"  ❌ Batch {row_num//batch_size} failed")
                        
                        except Exception as batch_error:
                            print(f"  ❌ Batch error: {str(batch_error)[:100]}...")
                            failed += len(batch_data)
                        
                        batch_data = []
                        time.sleep(0.5)  # Rate limiting
                
                except Exception as row_error:
                    print(f"  ⚠️  Row {row_num} error: {str(row_error)[:50]}...")
                    failed += 1
                    continue
            
            # Upload remaining records
            if batch_data:
                try:
                    result = supabase.table('nelson_textbook').insert(batch_data).execute()
                    if result.data:
                        successful += len(result.data)
                        print(f"  ✅ Final batch: {len(result.data)} records")
                    else:
                        failed += len(batch_data)
                except Exception as e:
                    print(f"  ❌ Final batch error: {e}")
                    failed += len(batch_data)
    
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return 0, 0
    
    return successful, failed

def upload_resources_data():
    """Upload Pediatric Resources data."""
    
    print("🏥 Uploading Pediatric Resources data...")
    
    supabase = create_supabase_client()
    successful = 0
    failed = 0
    
    try:
        with open('pediatric_medical_resources_dataset.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            batch_data = []
            
            for row_num, row in enumerate(reader, 1):
                try:
                    embedding = generate_mock_embedding_1536()
                    
                    record = {
                        'title': str(row.get('title', ''))[:500],
                        'content': str(row.get('content', '')),
                        'resource_type': str(row.get('resource_type', 'reference')),
                        'category': str(row.get('category', ''))[:100],
                        'age_range': str(row.get('age_range', ''))[:50] if row.get('age_range') else None,
                        'weight_range': str(row.get('weight_range', ''))[:50] if row.get('weight_range') else None,
                        'embedding': embedding,
                        'source': str(row.get('source', ''))[:255] if row.get('source') else None
                    }
                    
                    batch_data.append(record)
                
                except Exception as e:
                    print(f"  ⚠️  Resource row {row_num} error: {e}")
                    failed += 1
                    continue
            
            # Upload all resources
            if batch_data:
                try:
                    result = supabase.table('pediatric_medical_resources').insert(batch_data).execute()
                    
                    if result.data:
                        successful = len(result.data)
                        print(f"  ✅ {successful} pediatric resources uploaded")
                    else:
                        failed = len(batch_data)
                        print("  ❌ Pediatric resources upload failed")
                
                except Exception as e:
                    print(f"  ❌ Resources upload error: {e}")
                    failed = len(batch_data)
    
    except Exception as e:
        print(f"❌ Error reading resources CSV: {e}")
        return 0, 0
    
    return successful, failed

def verify_upload():
    """Verify the upload."""
    
    print("\n🔍 Verifying upload...")
    
    supabase = create_supabase_client()
    
    try:
        # Check counts
        nelson_result = supabase.table('nelson_textbook').select('id', count='exact').execute()
        nelson_count = nelson_result.count if hasattr(nelson_result, 'count') else len(nelson_result.data)
        
        resources_result = supabase.table('pediatric_medical_resources').select('id', count='exact').execute()
        resources_count = resources_result.count if hasattr(resources_result, 'count') else len(resources_result.data)
        
        print(f"📊 Nelson Textbook records: {nelson_count}")
        print(f"🏥 Pediatric Resources records: {resources_count}")
        
        # Sample data
        if nelson_count > 0:
            sample = supabase.table('nelson_textbook').select('chapter, medical_category, age_group, keywords').limit(2).execute()
            print(f"\n📋 Sample Nelson records:")
            for i, record in enumerate(sample.data, 1):
                print(f"  {i}. {record['chapter'][:50]}...")
                print(f"     Category: {record['medical_category']}")
                print(f"     Age Group: {record['age_group']}")
                print(f"     Keywords: {len(record.get('keywords', []))} items")
        
        if resources_count > 0:
            sample = supabase.table('pediatric_medical_resources').select('title, resource_type, category').limit(2).execute()
            print(f"\n🏥 Sample Resource records:")
            for i, record in enumerate(sample.data, 1):
                print(f"  {i}. {record['title']}")
                print(f"     Type: {record['resource_type']}")
                print(f"     Category: {record['category']}")
        
        return nelson_count, resources_count
        
    except Exception as e:
        print(f"❌ Error verifying upload: {e}")
        return 0, 0

def main():
    """Main function."""
    
    print("🏥 Nelson Textbook - Simple Upload to New Schema")
    print("=" * 60)
    
    # Check if tables exist
    if not check_tables_exist():
        return
    
    # Upload data
    nelson_success, nelson_failed = upload_nelson_data()
    resources_success, resources_failed = upload_resources_data()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 Upload Summary:")
    print(f"✅ Nelson Textbook: {nelson_success} successful, {nelson_failed} failed")
    print(f"✅ Pediatric Resources: {resources_success} successful, {resources_failed} failed")
    
    total_success = nelson_success + resources_success
    total_failed = nelson_failed + resources_failed
    
    if total_success + total_failed > 0:
        success_rate = (total_success / (total_success + total_failed)) * 100
        print(f"📊 Overall Success Rate: {success_rate:.1f}%")
    
    # Verify
    if total_success > 0:
        final_nelson, final_resources = verify_upload()
        
        print(f"\n🎯 Database Status:")
        print(f"📚 Nelson Textbook: {final_nelson} records ready")
        print(f"🏥 Pediatric Resources: {final_resources} records ready")
        print(f"🔍 Semantic search ready with 1536-dimension embeddings")
        
        print(f"\n🚀 Next Steps:")
        print("1. ✅ Data uploaded to new schema")
        print("2. 🔄 Replace mock embeddings with real OpenAI embeddings")
        print("3. 🔍 Test the match_documents function")
        print("4. 🏗️  Build your pediatric AI application!")

if __name__ == "__main__":
    main()

