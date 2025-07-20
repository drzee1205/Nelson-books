#!/usr/bin/env python3
"""
Upload Nelson Textbook Dataset to New Supabase Schema
Uploads data to the new nelson_textbook and pediatric_medical_resources tables.
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
    # Generate consistent mock embedding
    embedding = [random.uniform(-1, 1) for _ in range(1536)]
    
    # Normalize the vector
    magnitude = sum(x**2 for x in embedding) ** 0.5
    embedding = [x / magnitude for x in embedding]
    
    return embedding

def parse_keywords_array(keywords_str: str) -> List[str]:
    """Parse PostgreSQL array format keywords string."""
    if not keywords_str or keywords_str == '{}':
        return []
    
    # Remove curly braces and split by comma
    keywords_str = keywords_str.strip('{}')
    keywords = []
    
    for keyword in keywords_str.split(','):
        # Remove quotes and whitespace
        keyword = keyword.strip().strip('"').strip("'")
        if keyword:
            keywords.append(keyword)
    
    return keywords

def upload_nelson_textbook_data():
    """Upload nelson_textbook data."""
    
    supabase = create_supabase_client()
    
    print("📚 Uploading Nelson Textbook data...")
    
    successful_uploads = 0
    failed_uploads = 0
    
    try:
        with open('nelson_textbook_dataset.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            batch_data = []
            batch_size = 25
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Parse keywords
                    keywords = parse_keywords_array(row['keywords'])
                    
                    # Generate embedding
                    embedding = generate_mock_embedding_1536()
                    
                    record = {
                        'chapter': row['chapter'],
                        'section': row['section'],
                        'page_number': int(row['page_number']) if row['page_number'] else None,
                        'content': row['content'],
                        'embedding': embedding,
                        'keywords': keywords,
                        'medical_category': row['medical_category'],
                        'age_group': row['age_group']
                    }
                    
                    batch_data.append(record)
                    
                    # Upload in batches
                    if len(batch_data) >= batch_size:
                        result = supabase.table('nelson_textbook').insert(batch_data).execute()
                        
                        if result.data:
                            successful_uploads += len(result.data)
                            print(f"✅ Uploaded batch {row_num//batch_size} ({len(result.data)} records)")
                        else:
                            failed_uploads += len(batch_data)
                            print(f"⚠️  Batch {row_num//batch_size} failed")
                        
                        batch_data = []
                        time.sleep(0.5)  # Rate limiting
                
                except Exception as e:
                    print(f"❌ Error processing row {row_num}: {e}")
                    failed_uploads += 1
                    continue
            
            # Upload remaining records
            if batch_data:
                result = supabase.table('nelson_textbook').insert(batch_data).execute()
                if result.data:
                    successful_uploads += len(result.data)
                    print(f"✅ Uploaded final batch ({len(result.data)} records)")
                else:
                    failed_uploads += len(batch_data)
    
    except Exception as e:
        print(f"❌ Error reading nelson_textbook_dataset.csv: {e}")
        return 0, 0
    
    return successful_uploads, failed_uploads

def upload_pediatric_resources_data():
    """Upload pediatric_medical_resources data."""
    
    supabase = create_supabase_client()
    
    print("🏥 Uploading Pediatric Medical Resources data...")
    
    successful_uploads = 0
    failed_uploads = 0
    
    try:
        with open('pediatric_medical_resources_dataset.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            batch_data = []
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Generate embedding
                    embedding = generate_mock_embedding_1536()
                    
                    record = {
                        'title': row['title'],
                        'content': row['content'],
                        'resource_type': row['resource_type'],
                        'category': row['category'],
                        'age_range': row['age_range'] if row['age_range'] else None,
                        'weight_range': row['weight_range'] if row['weight_range'] else None,
                        'embedding': embedding,
                        'source': row['source']
                    }
                    
                    batch_data.append(record)
                
                except Exception as e:
                    print(f"❌ Error processing resource row {row_num}: {e}")
                    failed_uploads += 1
                    continue
            
            # Upload all resources at once (small dataset)
            if batch_data:
                result = supabase.table('pediatric_medical_resources').insert(batch_data).execute()
                
                if result.data:
                    successful_uploads = len(result.data)
                    print(f"✅ Uploaded {successful_uploads} pediatric resources")
                else:
                    failed_uploads = len(batch_data)
                    print("⚠️  Failed to upload pediatric resources")
    
    except Exception as e:
        print(f"❌ Error reading pediatric_medical_resources_dataset.csv: {e}")
        return 0, 0
    
    return successful_uploads, failed_uploads

def verify_upload():
    """Verify the upload by checking record counts."""
    
    supabase = create_supabase_client()
    
    print("\n🔍 Verifying upload...")
    
    try:
        # Check nelson_textbook table
        nelson_result = supabase.table('nelson_textbook').select('id', count='exact').execute()
        nelson_count = nelson_result.count if hasattr(nelson_result, 'count') else len(nelson_result.data)
        
        # Check pediatric_medical_resources table
        resources_result = supabase.table('pediatric_medical_resources').select('id', count='exact').execute()
        resources_count = resources_result.count if hasattr(resources_result, 'count') else len(resources_result.data)
        
        print(f"📊 Nelson Textbook records: {nelson_count}")
        print(f"🏥 Pediatric Resources records: {resources_count}")
        
        # Get sample records
        print(f"\n📋 Sample Nelson Textbook records:")
        sample_nelson = supabase.table('nelson_textbook').select('*').limit(3).execute()
        
        for i, record in enumerate(sample_nelson.data[:3], 1):
            chapter = record.get('chapter', 'No chapter')[:50]
            section = record.get('section', 'No section')[:50]
            category = record.get('medical_category', 'No category')
            age_group = record.get('age_group', 'No age group')
            has_embedding = record.get('embedding') is not None
            keywords_count = len(record.get('keywords', []))
            
            print(f"  {i}. {chapter}...")
            print(f"     Section: {section}...")
            print(f"     Category: {category}")
            print(f"     Age Group: {age_group}")
            print(f"     Keywords: {keywords_count} items")
            print(f"     Has Embedding: {'✅' if has_embedding else '❌'}")
            print()
        
        print(f"📋 Sample Pediatric Resources:")
        sample_resources = supabase.table('pediatric_medical_resources').select('*').limit(2).execute()
        
        for i, record in enumerate(sample_resources.data[:2], 1):
            title = record.get('title', 'No title')
            resource_type = record.get('resource_type', 'No type')
            category = record.get('category', 'No category')
            age_range = record.get('age_range', 'No age range')
            has_embedding = record.get('embedding') is not None
            
            print(f"  {i}. {title}")
            print(f"     Type: {resource_type}")
            print(f"     Category: {category}")
            print(f"     Age Range: {age_range}")
            print(f"     Has Embedding: {'✅' if has_embedding else '❌'}")
            print()
        
        # Test the new match_documents function
        print("🔍 Testing match_documents function...")
        try:
            test_embedding = generate_mock_embedding_1536()
            
            # Test with nelson_textbook
            search_result = supabase.rpc('match_documents', {
                'query_embedding': test_embedding,
                'match_table': 'nelson_textbook',
                'match_count': 3,
                'similarity_threshold': 0.1
            }).execute()
            
            if search_result.data:
                print(f"✅ Nelson textbook search: Found {len(search_result.data)} matches")
            else:
                print("⚠️  Nelson textbook search returned no results")
            
            # Test with pediatric_medical_resources
            resources_search = supabase.rpc('match_documents', {
                'query_embedding': test_embedding,
                'match_table': 'pediatric_medical_resources',
                'match_count': 2,
                'similarity_threshold': 0.1
            }).execute()
            
            if resources_search.data:
                print(f"✅ Pediatric resources search: Found {len(resources_search.data)} matches")
            else:
                print("⚠️  Pediatric resources search returned no results")
                
        except Exception as e:
            print(f"❌ Error testing search function: {e}")
    
    except Exception as e:
        print(f"❌ Error verifying upload: {e}")

def main():
    """Main function to upload all data."""
    
    print("🏥 Nelson Textbook - New Schema Upload to Supabase")
    print("=" * 60)
    
    # Upload nelson_textbook data
    nelson_success, nelson_failed = upload_nelson_textbook_data()
    
    # Upload pediatric_medical_resources data
    resources_success, resources_failed = upload_pediatric_resources_data()
    
    # Summary
    print("=" * 60)
    print("🎉 Upload Summary:")
    print(f"✅ Nelson Textbook: {nelson_success} successful, {nelson_failed} failed")
    print(f"✅ Pediatric Resources: {resources_success} successful, {resources_failed} failed")
    
    total_success = nelson_success + resources_success
    total_failed = nelson_failed + resources_failed
    total_records = total_success + total_failed
    
    if total_records > 0:
        success_rate = (total_success / total_records) * 100
        print(f"📊 Overall Success Rate: {success_rate:.1f}%")
    
    # Verify upload
    if total_success > 0:
        verify_upload()
    
    print(f"\n🎯 Next Steps:")
    print("1. ✅ Data uploaded to new schema tables")
    print("2. 🔄 Replace mock embeddings with real OpenAI embeddings")
    print("3. 🔍 Test semantic search with match_documents function")
    print("4. 🚀 Build your pediatric AI application!")

if __name__ == "__main__":
    main()

