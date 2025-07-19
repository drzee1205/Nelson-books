#!/usr/bin/env python3
"""
Generate Real Embeddings for Supabase Dataset
This script generates actual OpenAI embeddings for the uploaded records.
"""

import os
import time
from typing import List
from supabase import create_client, Client
import openai

# Supabase Configuration
SUPABASE_URL = "https://jlrjhjylekjedqwfctub.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpscmpoanlsZWtqZWRxd2ZjdHViIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mjg3MjI5NywiZXhwIjoyMDY4NDQ4Mjk3fQ.n5srw0U37QPoOhu4BGAgtdagDP2uJtlWkEj55Wye5tc"

def create_supabase_client() -> Client:
    """Create and return Supabase client."""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_openai_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """
    Generate OpenAI embedding for text.
    Using text-embedding-3-small for cost efficiency.
    """
    try:
        # Clean text for embedding
        text = text.replace("\n", " ").strip()
        if len(text) > 8000:  # Truncate if too long
            text = text[:8000]
        
        response = openai.embeddings.create(
            input=text,
            model=model
        )
        
        return response.data[0].embedding
    
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        return None

def update_embeddings_batch():
    """Update embeddings for all records in the database."""
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OpenAI API key not found!")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print("\nFor now, I'll create a demo script you can run when ready.")
        return create_demo_script()
    
    supabase = create_supabase_client()
    
    print("🔄 Generating real OpenAI embeddings...")
    print("=" * 50)
    
    try:
        # Get all records without proper embeddings
        result = supabase.table('documents').select('id, content, metadata').execute()
        records = result.data
        
        print(f"📊 Found {len(records)} records to process")
        
        successful_updates = 0
        failed_updates = 0
        
        for i, record in enumerate(records, 1):
            record_id = record['id']
            content = record['content']
            title = record.get('metadata', {}).get('title', f'Record {record_id}')
            
            print(f"🔄 Processing {i}/{len(records)}: {title[:50]}...")
            
            # Generate embedding
            embedding = get_openai_embedding(content)
            
            if embedding:
                try:
                    # Update record with new embedding
                    update_result = supabase.table('documents').update({
                        'embedding': embedding
                    }).eq('id', record_id).execute()
                    
                    if update_result.data:
                        successful_updates += 1
                        print(f"✅ Updated record {record_id}")
                    else:
                        failed_updates += 1
                        print(f"⚠️  Failed to update record {record_id}")
                
                except Exception as e:
                    failed_updates += 1
                    print(f"❌ Error updating record {record_id}: {e}")
            else:
                failed_updates += 1
                print(f"❌ Failed to generate embedding for record {record_id}")
            
            # Rate limiting - OpenAI has limits
            if i % 10 == 0:
                print(f"⏸️  Pausing for rate limiting...")
                time.sleep(2)
        
        print("=" * 50)
        print(f"🎉 Embedding generation completed!")
        print(f"✅ Successful updates: {successful_updates}")
        print(f"❌ Failed updates: {failed_updates}")
        print(f"📊 Success rate: {(successful_updates / len(records)) * 100:.1f}%")
        
        # Test semantic search
        if successful_updates > 0:
            test_semantic_search(supabase)
    
    except Exception as e:
        print(f"❌ Error processing embeddings: {e}")

def test_semantic_search(supabase: Client):
    """Test semantic search with real embeddings."""
    print("\n🔍 Testing semantic search with real embeddings...")
    
    try:
        # Generate embedding for test query
        test_query = "fever management in pediatric patients"
        query_embedding = get_openai_embedding(test_query)
        
        if query_embedding:
            # Test the match_documents function
            search_result = supabase.rpc('match_documents', {
                'query_embedding': query_embedding,
                'match_threshold': 0.3,
                'match_count': 5
            }).execute()
            
            if search_result.data:
                print(f"✅ Found {len(search_result.data)} relevant matches for '{test_query}':")
                for i, match in enumerate(search_result.data, 1):
                    title = match.get('metadata', {}).get('title', 'No title')
                    chapter = match.get('metadata', {}).get('chapter', 'No chapter')
                    similarity = match.get('similarity', 0)
                    content_preview = match.get('content', '')[:100] + '...'
                    
                    print(f"  {i}. {title}")
                    print(f"     Chapter: {chapter}")
                    print(f"     Similarity: {similarity:.3f}")
                    print(f"     Content: {content_preview}")
                    print()
            else:
                print("⚠️  No matches found - try lowering the threshold")
        
    except Exception as e:
        print(f"❌ Error testing semantic search: {e}")

def create_demo_script():
    """Create a demo script for when OpenAI API key is available."""
    
    demo_script = '''#!/usr/bin/env python3
"""
Demo: Generate Real Embeddings with OpenAI API
Run this script when you have your OpenAI API key ready.
"""

import os
import openai
from supabase import create_client

# Set your OpenAI API key
# openai.api_key = "your-openai-api-key-here"
# Or set environment variable: export OPENAI_API_KEY="your-key"

# Supabase config
SUPABASE_URL = "https://jlrjhjylekjedqwfctub.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpscmpoanlsZWtqZWRxd2ZjdHViIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mjg3MjI5NywiZXhwIjoyMDY4NDQ4Mjk3fQ.n5srw0U37QPoOhu4BGAgtdagDP2uJtlWkEj55Wye5tc"

def generate_embeddings():
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # Get sample record to test
    result = supabase.table('documents').select('*').limit(1).execute()
    if result.data:
        record = result.data[0]
        print(f"Testing with: {record['metadata'].get('title', 'No title')}")
        
        # Generate embedding
        response = openai.embeddings.create(
            input=record['content'],
            model="text-embedding-3-small"
        )
        
        embedding = response.data[0].embedding
        print(f"Generated embedding with {len(embedding)} dimensions")
        
        # Update record
        supabase.table('documents').update({
            'embedding': embedding
        }).eq('id', record['id']).execute()
        
        print("✅ Successfully updated record with real embedding!")
        
        # Test search
        search_result = supabase.rpc('match_documents', {
            'query_embedding': embedding,
            'match_threshold': 0.5,
            'match_count': 3
        }).execute()
        
        print(f"🔍 Search test found {len(search_result.data)} matches")

if __name__ == "__main__":
    if not os.getenv('OPENAI_API_KEY'):
        print("Please set OPENAI_API_KEY environment variable")
    else:
        generate_embeddings()
'''
    
    with open('demo_embeddings.py', 'w') as f:
        f.write(demo_script)
    
    print("📝 Created demo_embeddings.py script")
    print("🔑 To use real embeddings:")
    print("1. Get OpenAI API key from https://platform.openai.com/api-keys")
    print("2. Set environment variable: export OPENAI_API_KEY='your-key'")
    print("3. Run: python3 demo_embeddings.py")

def main():
    """Main function."""
    print("🏥 Nelson Pediatrics - Real Embeddings Generator")
    print("=" * 60)
    
    update_embeddings_batch()

if __name__ == "__main__":
    main()

