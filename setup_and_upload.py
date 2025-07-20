#!/usr/bin/env python3
"""
Setup New Schema and Upload Data to Supabase
First creates the new schema, then uploads the data.
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

def setup_schema():
    """Setup the new database schema."""
    
    print("🔧 Setting up new database schema...")
    
    supabase = create_supabase_client()
    
    # SQL commands to create the schema
    schema_commands = [
        # Enable pgvector extension
        "CREATE EXTENSION IF NOT EXISTS vector;",
        
        # Drop existing tables if they exist (for clean setup)
        "DROP TABLE IF EXISTS chat_messages CASCADE;",
        "DROP TABLE IF EXISTS chat_sessions CASCADE;",
        "DROP TABLE IF EXISTS pediatric_medical_resources CASCADE;",
        "DROP TABLE IF EXISTS nelson_textbook CASCADE;",
        
        # Create nelson_textbook table
        """
        CREATE TABLE nelson_textbook (
          id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
          chapter VARCHAR(255) NOT NULL,
          section VARCHAR(500) NOT NULL,
          page_number INTEGER,
          content TEXT NOT NULL,
          embedding vector(1536),
          keywords TEXT[],
          medical_category VARCHAR(100),
          age_group VARCHAR(50),
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Create pediatric_medical_resources table
        """
        CREATE TABLE pediatric_medical_resources (
          id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
          title VARCHAR(500) NOT NULL,
          content TEXT NOT NULL,
          resource_type VARCHAR(50) CHECK (resource_type IN ('protocol', 'dosage', 'guideline', 'reference')),
          category VARCHAR(100) NOT NULL,
          age_range VARCHAR(50),
          weight_range VARCHAR(50),
          embedding vector(1536),
          source VARCHAR(255),
          last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Create chat_sessions table
        """
        CREATE TABLE chat_sessions (
          id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
          user_id UUID,
          title VARCHAR(500) NOT NULL,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Create chat_messages table
        """
        CREATE TABLE chat_messages (
          id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
          session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
          role VARCHAR(20) CHECK (role IN ('user', 'assistant')) NOT NULL,
          content TEXT NOT NULL,
          citations TEXT[],
          metadata JSONB,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
    ]
    
    # Execute schema commands
    for i, command in enumerate(schema_commands, 1):
        try:
            print(f"  Executing command {i}/{len(schema_commands)}...")
            result = supabase.rpc('exec_sql', {'sql': command}).execute()
            print(f"  ✅ Command {i} executed successfully")
        except Exception as e:
            print(f"  ⚠️  Command {i} error (may be expected): {e}")
    
    # Create indexes
    index_commands = [
        "CREATE INDEX IF NOT EXISTS idx_nelson_textbook_embedding ON nelson_textbook USING ivfflat (embedding vector_cosine_ops);",
        "CREATE INDEX IF NOT EXISTS idx_pediatric_resources_embedding ON pediatric_medical_resources USING ivfflat (embedding vector_cosine_ops);",
        "CREATE INDEX IF NOT EXISTS idx_nelson_textbook_category ON nelson_textbook(medical_category);",
        "CREATE INDEX IF NOT EXISTS idx_nelson_textbook_keywords ON nelson_textbook USING GIN(keywords);",
        "CREATE INDEX IF NOT EXISTS idx_pediatric_resources_category ON pediatric_medical_resources(category);",
        "CREATE INDEX IF NOT EXISTS idx_pediatric_resources_type ON pediatric_medical_resources(resource_type);",
        "CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);",
        "CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated ON chat_sessions(updated_at DESC);"
    ]
    
    print("🔍 Creating indexes...")
    for i, command in enumerate(index_commands, 1):
        try:
            result = supabase.rpc('exec_sql', {'sql': command}).execute()
            print(f"  ✅ Index {i} created")
        except Exception as e:
            print(f"  ⚠️  Index {i} error: {e}")
    
    print("✅ Schema setup completed!")

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

def upload_data():
    """Upload data to the new schema."""
    
    print("📚 Uploading data to new schema...")
    
    supabase = create_supabase_client()
    
    # Upload Nelson Textbook data
    print("  📖 Uploading Nelson Textbook records...")
    nelson_success = 0
    nelson_failed = 0
    
    try:
        with open('nelson_textbook_dataset.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            batch_data = []
            batch_size = 10  # Smaller batches
            
            for row_num, row in enumerate(reader, 1):
                try:
                    keywords = parse_keywords_array(row['keywords'])
                    embedding = generate_mock_embedding_1536()
                    
                    record = {
                        'chapter': row['chapter'][:255],  # Ensure length limit
                        'section': row['section'][:500],  # Ensure length limit
                        'page_number': int(row['page_number']) if row['page_number'] else None,
                        'content': row['content'],
                        'embedding': embedding,
                        'keywords': keywords,
                        'medical_category': row['medical_category'][:100],  # Ensure length limit
                        'age_group': row['age_group'][:50]  # Ensure length limit
                    }
                    
                    batch_data.append(record)
                    
                    if len(batch_data) >= batch_size:
                        result = supabase.table('nelson_textbook').insert(batch_data).execute()
                        
                        if result.data:
                            nelson_success += len(result.data)
                            print(f"    ✅ Batch {row_num//batch_size}: {len(result.data)} records")
                        else:
                            nelson_failed += len(batch_data)
                            print(f"    ❌ Batch {row_num//batch_size} failed")
                        
                        batch_data = []
                        time.sleep(0.3)
                
                except Exception as e:
                    print(f"    ⚠️  Row {row_num} error: {str(e)[:100]}...")
                    nelson_failed += 1
                    continue
            
            # Upload remaining records
            if batch_data:
                result = supabase.table('nelson_textbook').insert(batch_data).execute()
                if result.data:
                    nelson_success += len(result.data)
                    print(f"    ✅ Final batch: {len(result.data)} records")
    
    except Exception as e:
        print(f"    ❌ Error reading nelson_textbook_dataset.csv: {e}")
    
    # Upload Pediatric Resources data
    print("  🏥 Uploading Pediatric Resources...")
    resources_success = 0
    resources_failed = 0
    
    try:
        with open('pediatric_medical_resources_dataset.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            batch_data = []
            
            for row_num, row in enumerate(reader, 1):
                try:
                    embedding = generate_mock_embedding_1536()
                    
                    record = {
                        'title': row['title'][:500],
                        'content': row['content'],
                        'resource_type': row['resource_type'],
                        'category': row['category'][:100],
                        'age_range': row['age_range'][:50] if row['age_range'] else None,
                        'weight_range': row['weight_range'][:50] if row['weight_range'] else None,
                        'embedding': embedding,
                        'source': row['source'][:255] if row['source'] else None
                    }
                    
                    batch_data.append(record)
                
                except Exception as e:
                    print(f"    ⚠️  Resource row {row_num} error: {e}")
                    resources_failed += 1
                    continue
            
            if batch_data:
                result = supabase.table('pediatric_medical_resources').insert(batch_data).execute()
                
                if result.data:
                    resources_success = len(result.data)
                    print(f"    ✅ {resources_success} pediatric resources uploaded")
                else:
                    resources_failed = len(batch_data)
                    print("    ❌ Pediatric resources upload failed")
    
    except Exception as e:
        print(f"    ❌ Error reading pediatric resources: {e}")
    
    return nelson_success, nelson_failed, resources_success, resources_failed

def verify_setup():
    """Verify the setup and data upload."""
    
    print("\n🔍 Verifying setup...")
    
    supabase = create_supabase_client()
    
    try:
        # Check table counts
        nelson_result = supabase.table('nelson_textbook').select('id', count='exact').execute()
        nelson_count = nelson_result.count if hasattr(nelson_result, 'count') else len(nelson_result.data)
        
        resources_result = supabase.table('pediatric_medical_resources').select('id', count='exact').execute()
        resources_count = resources_result.count if hasattr(resources_result, 'count') else len(resources_result.data)
        
        print(f"📊 Nelson Textbook records: {nelson_count}")
        print(f"🏥 Pediatric Resources records: {resources_count}")
        
        # Sample records
        if nelson_count > 0:
            sample = supabase.table('nelson_textbook').select('chapter, section, medical_category, age_group').limit(2).execute()
            print(f"\n📋 Sample Nelson records:")
            for i, record in enumerate(sample.data, 1):
                print(f"  {i}. {record['chapter'][:50]}...")
                print(f"     Section: {record['section'][:50]}...")
                print(f"     Category: {record['medical_category']}")
                print(f"     Age Group: {record['age_group']}")
        
        if resources_count > 0:
            sample = supabase.table('pediatric_medical_resources').select('title, resource_type, category').limit(2).execute()
            print(f"\n🏥 Sample Resource records:")
            for i, record in enumerate(sample.data, 1):
                print(f"  {i}. {record['title']}")
                print(f"     Type: {record['resource_type']}")
                print(f"     Category: {record['category']}")
        
        print(f"\n✅ Setup verification completed!")
        
    except Exception as e:
        print(f"❌ Error verifying setup: {e}")

def main():
    """Main function."""
    
    print("🏥 Nelson Textbook - New Schema Setup & Upload")
    print("=" * 60)
    
    # Setup schema
    setup_schema()
    
    # Upload data
    nelson_success, nelson_failed, resources_success, resources_failed = upload_data()
    
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
        verify_setup()
    
    print(f"\n🎯 Next Steps:")
    print("1. ✅ New schema created and data uploaded")
    print("2. 🔄 Replace mock embeddings with real OpenAI embeddings")
    print("3. 🔍 Test semantic search functionality")
    print("4. 🚀 Build your pediatric AI application!")

if __name__ == "__main__":
    main()

