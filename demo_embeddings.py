#!/usr/bin/env python3
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
