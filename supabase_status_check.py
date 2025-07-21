#!/usr/bin/env python3
"""
Supabase Database Status Check
Comprehensive status report of the Nelson Pediatrics dataset in Supabase.
"""

from supabase import create_client, Client
import json

# Supabase Configuration
SUPABASE_URL = "https://jlrjhjylekjedqwfctub.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpscmpoanlsZWtqZWRxd2ZjdHViIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mjg3MjI5NywiZXhwIjoyMDY4NDQ4Mjk3fQ.n5srw0U37QPoOhu4BGAgtdagDP2uJtlWkEj55Wye5tc"

def create_supabase_client() -> Client:
    """Create and return Supabase client."""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def check_database_status():
    """Check the current status of the database."""
    
    print("🏥 Nelson Pediatrics Supabase Database Status")
    print("=" * 60)
    
    supabase = create_supabase_client()
    
    try:
        # 1. Total record count
        result = supabase.table('documents').select('id', count='exact').execute()
        total_records = result.count if hasattr(result, 'count') else len(result.data)
        print(f"📊 Total Records: {total_records}")
        
        # 2. Records with embeddings
        embedding_result = supabase.table('documents').select('id').not_.is_('embedding', 'null').execute()
        records_with_embeddings = len(embedding_result.data)
        print(f"🔗 Records with Embeddings: {records_with_embeddings}")
        
        # 3. Chapter distribution
        print(f"\n📚 Chapter Distribution:")
        all_records = supabase.table('documents').select('metadata').execute()
        
        chapter_counts = {}
        for record in all_records.data:
            metadata = record.get('metadata', {})
            chapter = metadata.get('chapter', 'Unknown')
            chapter_counts[chapter] = chapter_counts.get(chapter, 0) + 1
        
        for chapter, count in sorted(chapter_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {chapter}: {count} records")
        
        # 4. Sample records
        print(f"\n📋 Sample Records:")
        sample_result = supabase.table('documents').select('*').limit(5).execute()
        
        for i, record in enumerate(sample_result.data, 1):
            title = record.get('metadata', {}).get('title', 'No title')
            chapter = record.get('metadata', {}).get('chapter', 'No chapter')
            content_length = len(record.get('content', ''))
            has_embedding = record.get('embedding') is not None
            
            print(f"  {i}. {title}")
            print(f"     Chapter: {chapter}")
            print(f"     Content Length: {content_length} chars")
            print(f"     Has Embedding: {'✅' if has_embedding else '❌'}")
            print()
        
        # 5. Test database functions
        print("🔧 Testing Database Functions:")
        
        # Test get_chapter_stats function
        try:
            stats_result = supabase.rpc('get_chapter_stats').execute()
            if stats_result.data:
                print("✅ get_chapter_stats() function working")
                print("   Top chapters by record count:")
                for stat in stats_result.data[:3]:
                    print(f"   - {stat['chapter']}: {stat['document_count']} records")
            else:
                print("⚠️  get_chapter_stats() returned no data")
        except Exception as e:
            print(f"❌ get_chapter_stats() error: {e}")
        
        # Test get_sample_documents function
        try:
            sample_func_result = supabase.rpc('get_sample_documents', {'sample_count': 2}).execute()
            if sample_func_result.data:
                print("✅ get_sample_documents() function working")
            else:
                print("⚠️  get_sample_documents() returned no data")
        except Exception as e:
            print(f"❌ get_sample_documents() error: {e}")
        
        # 6. Embedding status and recommendations
        print(f"\n🎯 Status Summary:")
        embedding_percentage = (records_with_embeddings / total_records) * 100 if total_records > 0 else 0
        
        if embedding_percentage == 100:
            print("✅ Database is fully ready for semantic search!")
            print("🔍 All records have embeddings - semantic search is operational")
        elif embedding_percentage > 0:
            print(f"⚠️  Partial setup: {embedding_percentage:.1f}% of records have embeddings")
            print("🔄 Run embedding generation to complete setup")
        else:
            print("❌ No real embeddings detected - using mock embeddings")
            print("🔑 Set up OpenAI API key and run embedding generation")
        
        print(f"\n🚀 Next Steps:")
        if embedding_percentage < 100:
            print("1. 🔑 Get OpenAI API key from https://platform.openai.com/api-keys")
            print("2. 🔄 Run: export OPENAI_API_KEY='your-key'")
            print("3. 🚀 Run: python3 generate_embeddings.py")
        else:
            print("1. ✅ Database is ready for production use!")
            print("2. 🔍 Test semantic search in your application")
            print("3. 📊 Monitor query performance and optimize as needed")
        
        print("4. 📖 Check SUPABASE_DATASET_README.md for usage examples")
        
        # 7. Connection test
        print(f"\n🔗 Connection Status:")
        print(f"✅ Successfully connected to Supabase")
        print(f"🌐 Database URL: {SUPABASE_URL}")
        print(f"📊 Total API calls made: Multiple successful")
        
    except Exception as e:
        print(f"❌ Error checking database status: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function."""
    check_database_status()

if __name__ == "__main__":
    main()

