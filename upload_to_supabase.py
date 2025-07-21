#!/usr/bin/env python3
"""
Upload Nelson Pediatrics Dataset to Supabase
This script uploads the CSV dataset to your Supabase database with embeddings.
"""

import csv
import json
import time
import openai
from supabase import create_client, Client
from typing import List, Dict, Any
import os

# Supabase Configuration
SUPABASE_URL = "https://jlrjhjylekjedqwfctub.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpscmpoanlsZWtqZWRxd2ZjdHViIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mjg3MjI5NywiZXhwIjoyMDY4NDQ4Mjk3fQ.n5srw0U37QPoOhu4BGAgtdagDP2uJtlWkEj55Wye5tc"

def create_supabase_client() -> Client:
    """Create and return Supabase client."""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def generate_mock_embedding(text: str) -> List[float]:
    """
    Generate a mock embedding vector for testing purposes.
    In production, replace this with actual embedding generation.
    """
    import hashlib
    import random
    
    # Use text hash as seed for consistent embeddings
    seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    # Generate 1024-dimensional vector
    embedding = [random.uniform(-1, 1) for _ in range(1024)]
    
    # Normalize the vector
    magnitude = sum(x**2 for x in embedding) ** 0.5
    embedding = [x / magnitude for x in embedding]
    
    return embedding

def load_dataset(csv_file: str) -> List[Dict[str, Any]]:
    """Load dataset from CSV file."""
    print(f"📁 Loading dataset from {csv_file}...")
    
    records = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                metadata = json.loads(row['metadata'])
                records.append({
                    'content': row['content'],
                    'metadata': metadata
                })
            except json.JSONDecodeError as e:
                print(f"⚠️  Skipping row due to invalid JSON: {e}")
                continue
    
    print(f"✅ Loaded {len(records)} records")
    return records

def upload_to_supabase(records: List[Dict[str, Any]], batch_size: int = 50):
    """Upload records to Supabase with embeddings."""
    
    supabase = create_supabase_client()
    
    print(f"🚀 Starting upload to Supabase...")
    print(f"📊 Total records: {len(records)}")
    print(f"📦 Batch size: {batch_size}")
    print("-" * 50)
    
    successful_uploads = 0
    failed_uploads = 0
    
    # Process in batches
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(records) + batch_size - 1) // batch_size
        
        print(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} records)...")
        
        # Prepare batch data with embeddings
        batch_data = []
        for record in batch:
            try:
                # Generate embedding (replace with actual embedding service)
                embedding = generate_mock_embedding(record['content'])
                
                batch_data.append({
                    'content': record['content'],
                    'metadata': record['metadata'],
                    'embedding': embedding
                })
                
            except Exception as e:
                print(f"⚠️  Error processing record: {e}")
                failed_uploads += 1
                continue
        
        # Upload batch to Supabase
        try:
            result = supabase.table('documents').insert(batch_data).execute()
            
            if result.data:
                successful_uploads += len(result.data)
                print(f"✅ Batch {batch_num} uploaded successfully ({len(result.data)} records)")
            else:
                print(f"⚠️  Batch {batch_num} upload returned no data")
                failed_uploads += len(batch_data)
                
        except Exception as e:
            print(f"❌ Error uploading batch {batch_num}: {e}")
            failed_uploads += len(batch_data)
            continue
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    print("-" * 50)
    print(f"🎉 Upload completed!")
    print(f"✅ Successful uploads: {successful_uploads}")
    print(f"❌ Failed uploads: {failed_uploads}")
    print(f"📊 Success rate: {(successful_uploads / len(records)) * 100:.1f}%")
    
    return successful_uploads, failed_uploads

def verify_upload(supabase: Client):
    """Verify the upload by checking record count and sample data."""
    print("\n🔍 Verifying upload...")
    
    try:
        # Get total count
        result = supabase.table('documents').select('id', count='exact').execute()
        total_count = result.count if hasattr(result, 'count') else len(result.data)
        print(f"📊 Total records in database: {total_count}")
        
        # Get sample records
        sample_result = supabase.table('documents').select('*').limit(3).execute()
        
        if sample_result.data:
            print(f"📋 Sample records:")
            for i, record in enumerate(sample_result.data[:3], 1):
                title = record.get('metadata', {}).get('title', 'No title')
                chapter = record.get('metadata', {}).get('chapter', 'No chapter')
                content_preview = record.get('content', '')[:100] + '...'
                has_embedding = 'embedding' in record and record['embedding'] is not None
                
                print(f"  {i}. {title}")
                print(f"     Chapter: {chapter}")
                print(f"     Content: {content_preview}")
                print(f"     Has embedding: {'✅' if has_embedding else '❌'}")
                print()
        
        # Test semantic search function
        print("🔍 Testing semantic search function...")
        try:
            # Generate a test embedding
            test_embedding = generate_mock_embedding("fever in children")
            
            # Call the match_documents function
            search_result = supabase.rpc('match_documents', {
                'query_embedding': test_embedding,
                'match_threshold': 0.1,
                'match_count': 3
            }).execute()
            
            if search_result.data:
                print(f"✅ Semantic search working! Found {len(search_result.data)} matches")
                for match in search_result.data[:2]:
                    title = match.get('metadata', {}).get('title', 'No title')
                    similarity = match.get('similarity', 0)
                    print(f"  - {title} (similarity: {similarity:.3f})")
            else:
                print("⚠️  Semantic search returned no results")
                
        except Exception as e:
            print(f"❌ Error testing semantic search: {e}")
    
    except Exception as e:
        print(f"❌ Error verifying upload: {e}")

def main():
    """Main function to upload dataset."""
    
    print("🏥 Nelson Pediatrics Dataset Upload to Supabase")
    print("=" * 60)
    
    csv_file = "nelson_pediatrics_supabase_dataset.csv"
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"❌ Error: {csv_file} not found!")
        print("Please make sure the dataset file is in the current directory.")
        return
    
    try:
        # Load dataset
        records = load_dataset(csv_file)
        
        if not records:
            print("❌ No records to upload!")
            return
        
        # Upload to Supabase
        successful, failed = upload_to_supabase(records, batch_size=25)
        
        # Verify upload
        if successful > 0:
            supabase = create_supabase_client()
            verify_upload(supabase)
        
        print("\n🎯 Next Steps:")
        print("1. ✅ Dataset uploaded to Supabase")
        print("2. 🔄 Replace mock embeddings with real ones (OpenAI, Cohere, etc.)")
        print("3. 🔍 Test semantic search in your application")
        print("4. 📊 Monitor performance and optimize as needed")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

