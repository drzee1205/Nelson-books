-- Nelson Pediatrics Supabase Database Setup
-- This script sets up the complete database schema and functions for semantic search

-- 1. Enable pgvector extension (required for embeddings)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the documents table if it doesn't exist
CREATE TABLE IF NOT EXISTS documents (
  id BIGSERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}',
  embedding VECTOR(1024),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create the semantic search function
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding VECTOR(1024),
  match_threshold FLOAT DEFAULT 0.5,
  match_count INT DEFAULT 5
)
RETURNS TABLE(
  id BIGINT,
  content TEXT,
  metadata JSONB,
  similarity FLOAT
)
LANGUAGE SQL STABLE AS $$
  SELECT
    documents.id,
    documents.content,
    documents.metadata,
    1 - (documents.embedding <=> query_embedding) AS similarity
  FROM documents
  WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
$$;

-- 4. Create function to search by chapter
CREATE OR REPLACE FUNCTION search_by_chapter(
  chapter_name TEXT,
  query_embedding VECTOR(1024),
  match_threshold FLOAT DEFAULT 0.3,
  match_count INT DEFAULT 10
)
RETURNS TABLE(
  id BIGINT,
  content TEXT,
  metadata JSONB,
  similarity FLOAT
)
LANGUAGE SQL STABLE AS $$
  SELECT
    documents.id,
    documents.content,
    documents.metadata,
    1 - (documents.embedding <=> query_embedding) AS similarity
  FROM documents
  WHERE 
    documents.metadata->>'chapter' = chapter_name
    AND 1 - (documents.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
$$;

-- 5. Create function to get random sample documents
CREATE OR REPLACE FUNCTION get_sample_documents(sample_count INT DEFAULT 5)
RETURNS TABLE(
  id BIGINT,
  content TEXT,
  metadata JSONB
)
LANGUAGE SQL STABLE AS $$
  SELECT
    documents.id,
    documents.content,
    documents.metadata
  FROM documents
  ORDER BY RANDOM()
  LIMIT sample_count;
$$;

-- 6. Ensure the embedding column exists and is the right type
ALTER TABLE documents
  ALTER COLUMN embedding TYPE VECTOR(1024);

-- 7. Create indexes for performance
CREATE INDEX IF NOT EXISTS documents_embedding_idx 
ON documents 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS documents_metadata_chapter_idx 
ON documents 
USING GIN ((metadata->>'chapter'));

CREATE INDEX IF NOT EXISTS documents_created_at_idx 
ON documents (created_at DESC);

-- 8. Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_documents_updated_at 
    BEFORE UPDATE ON documents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 9. Insert sample content from Nelson Textbook (only if table is empty)
INSERT INTO documents (content, metadata, embedding)
SELECT * FROM (
  VALUES
  (
    'Kawasaki Disease: A systemic vasculitis affecting medium-sized arteries, most commonly seen in children under 5 years of age. Clinical criteria include fever for at least 5 days plus at least 4 of the following: bilateral conjunctival injection, oral mucosal changes, cervical lymphadenopathy, extremity changes, and polymorphous rash. Coronary artery aneurysms are the most serious complication. Treatment includes high-dose IVIG and aspirin therapy.',
    '{"title": "Kawasaki Disease", "source": "Nelson Textbook of Pediatrics", "chapter": "Rheumatic Diseases", "content_type": "clinical_summary", "id": 1}'::jsonb,
    (SELECT array_agg(random() - 0.5) FROM generate_series(1, 1024))::vector
  ),
  (
    'Fever Management in Children: Fever is a natural immune response and temperatures up to 38.5°C (101.3°F) may not require treatment in otherwise healthy children. Acetaminophen (10-15 mg/kg every 4-6 hours) or ibuprofen (5-10 mg/kg every 6-8 hours) can be used for comfort. Never use aspirin in children due to Reye syndrome risk. Seek immediate medical attention for fever in infants under 3 months.',
    '{"title": "Fever Management", "source": "Nelson Textbook of Pediatrics", "chapter": "Infectious Diseases", "content_type": "clinical_guideline", "id": 2}'::jsonb,
    (SELECT array_agg(random() - 0.5) FROM generate_series(1, 1024))::vector
  ),
  (
    'Asthma in Children: Most common chronic disease in childhood. Characterized by airway inflammation, bronchospasm, and mucus production. Symptoms include wheezing, cough (especially at night), shortness of breath, and chest tightness. Triggers include allergens, respiratory infections, exercise, and environmental irritants. Management includes controller medications (inhaled corticosteroids) and rescue medications (short-acting beta-agonists).',
    '{"title": "Pediatric Asthma", "source": "Nelson Textbook of Pediatrics", "chapter": "Allergic Disorders", "content_type": "disease_overview", "id": 3}'::jsonb,
    (SELECT array_agg(random() - 0.5) FROM generate_series(1, 1024))::vector
  ),
  (
    'Pneumonia in Children: Community-acquired pneumonia is common in pediatric patients. Viral causes predominate in younger children, while bacterial causes (especially Streptococcus pneumoniae) are more common in older children. Symptoms include fever, cough, difficulty breathing, and chest pain. Chest X-ray may show infiltrates. Treatment depends on age and severity, ranging from outpatient oral antibiotics to hospitalization with IV therapy.',
    '{"title": "Pediatric Pneumonia", "source": "Nelson Textbook of Pediatrics", "chapter": "Respiratory Disorders", "content_type": "disease_overview", "id": 4}'::jsonb,
    (SELECT array_agg(random() - 0.5) FROM generate_series(1, 1024))::vector
  ),
  (
    'Developmental Milestones: 6-month milestones include sitting with support, transferring objects between hands, responding to own name, and stranger anxiety beginning. 12-month milestones include walking with assistance, saying first words, playing peek-a-boo, and showing separation anxiety. 18-month milestones include walking independently, vocabulary of 10-25 words, and following simple commands.',
    '{"title": "Developmental Milestones", "source": "Nelson Textbook of Pediatrics", "chapter": "Growth, Development, and Behavior", "content_type": "developmental_guide", "id": 5}'::jsonb,
    (SELECT array_agg(random() - 0.5) FROM generate_series(1, 1024))::vector
  )
) AS v(content, metadata, embedding)
WHERE NOT EXISTS (SELECT 1 FROM documents LIMIT 1);

-- 10. Create view for easy querying
CREATE OR REPLACE VIEW documents_summary AS
SELECT 
  id,
  LEFT(content, 100) || '...' as content_preview,
  metadata->>'title' as title,
  metadata->>'chapter' as chapter,
  metadata->>'content_type' as content_type,
  created_at
FROM documents
ORDER BY created_at DESC;

-- 11. Create function to get chapter statistics
CREATE OR REPLACE FUNCTION get_chapter_stats()
RETURNS TABLE(
  chapter TEXT,
  document_count BIGINT,
  avg_content_length NUMERIC
)
LANGUAGE SQL STABLE AS $$
  SELECT
    metadata->>'chapter' as chapter,
    COUNT(*) as document_count,
    ROUND(AVG(LENGTH(content)), 2) as avg_content_length
  FROM documents
  WHERE metadata->>'chapter' IS NOT NULL
  GROUP BY metadata->>'chapter'
  ORDER BY document_count DESC;
$$;

-- 12. Verify setup and show statistics
SELECT
  'Nelson Pediatrics Database Setup Complete! ✅' AS status,
  COUNT(*) AS total_documents,
  COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) AS documents_with_embeddings,
  ROUND(AVG(LENGTH(content)), 2) AS avg_content_length
FROM documents;

-- Show chapter breakdown
SELECT * FROM get_chapter_stats();

COMMENT ON TABLE documents IS 'Contains Nelson Textbook of Pediatrics content for semantic search';
COMMENT ON FUNCTION match_documents IS 'Performs semantic similarity search using vector embeddings';
COMMENT ON FUNCTION search_by_chapter IS 'Searches within a specific medical chapter/specialty';
COMMENT ON FUNCTION get_chapter_stats IS 'Returns statistics about content distribution by chapter';

