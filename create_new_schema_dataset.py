#!/usr/bin/env python3
"""
Create Nelson Textbook Dataset for New Schema
Transforms existing content to match the new nelson_textbook table structure.
"""

import csv
import json
import re
import random
from pathlib import Path
from typing import List, Dict, Any

def extract_keywords(content: str) -> List[str]:
    """Extract medical keywords from content."""
    
    # Common medical terms and patterns
    medical_patterns = [
        r'\b(?:mg/kg|mcg/kg|units/kg)\b',  # Dosing patterns
        r'\b\d+(?:-\d+)?\s*(?:mg|mcg|units|ml|cc)\b',  # Medication amounts
        r'\b(?:amoxicillin|ibuprofen|acetaminophen|prednisone|albuterol|azithromycin)\b',  # Common meds
        r'\b(?:fever|temperature|°C|°F)\b',  # Temperature related
        r'\b(?:asthma|pneumonia|bronchitis|otitis|dermatitis|eczema)\b',  # Common conditions
        r'\b(?:infant|child|pediatric|neonatal|adolescent)\b',  # Age groups
        r'\b(?:treatment|therapy|management|diagnosis|symptoms)\b',  # Clinical terms
    ]
    
    keywords = []
    content_lower = content.lower()
    
    # Extract pattern-based keywords
    for pattern in medical_patterns:
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        keywords.extend(matches)
    
    # Extract important medical terms (simple approach)
    medical_terms = [
        'fever', 'infection', 'antibiotic', 'treatment', 'diagnosis', 'symptoms',
        'pediatric', 'child', 'infant', 'adolescent', 'dosage', 'medication',
        'therapy', 'management', 'clinical', 'patient', 'disease', 'disorder',
        'syndrome', 'condition', 'acute', 'chronic', 'severe', 'mild'
    ]
    
    for term in medical_terms:
        if term in content_lower:
            keywords.append(term)
    
    # Remove duplicates and return unique keywords
    return list(set(keywords))[:10]  # Limit to 10 keywords

def categorize_content(chapter: str, content: str) -> tuple:
    """Categorize content and determine age group."""
    
    # Medical category mapping
    category_mapping = {
        'allergic': 'Allergy and Immunology',
        'cardiovascular': 'Cardiology',
        'respiratory': 'Pulmonology',
        'nervous': 'Neurology',
        'endocrine': 'Endocrinology',
        'digestive': 'Gastroenterology',
        'blood': 'Hematology',
        'skin': 'Dermatology',
        'bone': 'Orthopedics',
        'ear': 'Otolaryngology',
        'fluid': 'Nephrology',
        'growth': 'Developmental Pediatrics',
        'metabolic': 'Metabolism',
        'immunology': 'Immunology',
        'cancer': 'Oncology',
        'urology': 'Urology',
        'gynecologic': 'Gynecology',
        'rehabilitation': 'Rehabilitation Medicine',
        'rheumatic': 'Rheumatology',
        'behavioral': 'Psychiatry',
        'learning': 'Developmental Pediatrics'
    }
    
    # Determine category
    chapter_lower = chapter.lower()
    medical_category = 'General Pediatrics'  # Default
    
    for key, category in category_mapping.items():
        if key in chapter_lower:
            medical_category = category
            break
    
    # Determine age group based on content
    content_lower = content.lower()
    age_group = 'Pediatric'  # Default
    
    if any(term in content_lower for term in ['newborn', 'neonate', 'birth']):
        age_group = 'Neonatal'
    elif any(term in content_lower for term in ['infant', 'baby', '0-2 years']):
        age_group = 'Infant'
    elif any(term in content_lower for term in ['toddler', '2-5 years']):
        age_group = 'Toddler'
    elif any(term in content_lower for term in ['school', '6-12 years']):
        age_group = 'School Age'
    elif any(term in content_lower for term in ['adolescent', 'teenager', '13-18 years']):
        age_group = 'Adolescent'
    
    return medical_category, age_group

def extract_section_from_content(content: str) -> str:
    """Extract a meaningful section title from content."""
    
    # Look for section headers or create from first sentence
    sentences = content.split('.')
    if sentences:
        first_sentence = sentences[0].strip()
        
        # If first sentence is too long, try to extract key terms
        if len(first_sentence) > 100:
            # Look for disease/condition names
            words = first_sentence.split()[:10]  # First 10 words
            section = ' '.join(words)
        else:
            section = first_sentence
        
        # Clean up the section title
        section = re.sub(r'^(Chapter \d+:?\s*)', '', section)
        section = section.replace('\n', ' ').strip()
        
        return section[:500]  # Limit to 500 chars
    
    return "General Information"

def generate_page_number() -> int:
    """Generate a realistic page number."""
    return random.randint(50, 2500)

def process_existing_dataset():
    """Process the existing dataset and create new schema format."""
    
    print("🔄 Processing existing dataset for new schema...")
    
    # Load existing dataset
    existing_file = "nelson_pediatrics_supabase_dataset.csv"
    if not Path(existing_file).exists():
        print(f"❌ {existing_file} not found!")
        return []
    
    records = []
    
    with open(existing_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                metadata = json.loads(row['metadata'])
                content = row['content']
                chapter = metadata.get('chapter', 'Unknown Chapter')
                
                # Extract information for new schema
                section = extract_section_from_content(content)
                keywords = extract_keywords(content)
                medical_category, age_group = categorize_content(chapter, content)
                page_number = generate_page_number()
                
                record = {
                    'chapter': f"Chapter: {chapter}",
                    'section': section,
                    'page_number': page_number,
                    'content': content,
                    'keywords': keywords,
                    'medical_category': medical_category,
                    'age_group': age_group
                }
                
                records.append(record)
                
            except Exception as e:
                print(f"⚠️  Error processing row: {e}")
                continue
    
    print(f"✅ Processed {len(records)} records")
    return records

def create_pediatric_resources():
    """Create pediatric medical resources data."""
    
    resources = [
        {
            'title': 'Pediatric Fever Management Protocol',
            'content': 'For children 3 months to 3 years: Acetaminophen 10-15 mg/kg every 4-6 hours (max 5 doses/24h) OR Ibuprofen 5-10 mg/kg every 6-8 hours (>6 months old). Seek immediate care if fever >38°C in infants <3 months, or >39°C with concerning symptoms.',
            'resource_type': 'protocol',
            'category': 'Emergency Medicine',
            'age_range': '3 months - 3 years',
            'weight_range': '5-15 kg',
            'source': 'AAP Clinical Guidelines'
        },
        {
            'title': 'Pediatric Asthma Medication Dosing',
            'content': 'Albuterol MDI: 2-4 puffs every 4-6 hours as needed. Severe exacerbation: 4-8 puffs every 20 minutes x3, then every 1-4 hours. Prednisolone: 1-2 mg/kg/day (max 60mg) for 3-5 days for moderate-severe exacerbations.',
            'resource_type': 'dosage',
            'category': 'Pulmonology',
            'age_range': '2-18 years',
            'weight_range': '10-70 kg',
            'source': 'NHLBI Guidelines'
        },
        {
            'title': 'Pediatric Dehydration Assessment',
            'content': 'Mild (3-5% loss): Slightly dry mucous membranes, normal vital signs. Moderate (6-9% loss): Dry mucous membranes, decreased skin turgor, tachycardia. Severe (>10% loss): Very dry mucous membranes, poor skin turgor, altered mental status, hypotension.',
            'resource_type': 'guideline',
            'category': 'Emergency Medicine',
            'age_range': '1 month - 18 years',
            'weight_range': '3-70 kg',
            'source': 'AAP Practice Guidelines'
        },
        {
            'title': 'Pediatric Antibiotic Dosing Reference',
            'content': 'Amoxicillin: 80-90 mg/kg/day divided BID for otitis media, 45 mg/kg/day divided BID for mild infections. Azithromycin: 10 mg/kg day 1, then 5 mg/kg days 2-5. Cephalexin: 25-50 mg/kg/day divided QID.',
            'resource_type': 'reference',
            'category': 'Infectious Diseases',
            'age_range': '1 month - 18 years',
            'weight_range': '3-70 kg',
            'source': 'Pediatric Dosing Handbook'
        },
        {
            'title': 'Newborn Screening Protocol',
            'content': 'Collect blood sample on filter paper between 24-48 hours of life, ideally before discharge. Screen for PKU, hypothyroidism, galactosemia, sickle cell disease, and other metabolic disorders. Repeat if collected <24 hours of age.',
            'resource_type': 'protocol',
            'category': 'Neonatology',
            'age_range': '24-48 hours',
            'weight_range': '2-5 kg',
            'source': 'State Health Department'
        }
    ]
    
    return resources

def create_csv_files(nelson_records: List[Dict], resource_records: List[Dict]):
    """Create CSV files for both tables."""
    
    # Nelson Textbook CSV
    nelson_csv = 'nelson_textbook_dataset.csv'
    with open(nelson_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['chapter', 'section', 'page_number', 'content', 'keywords', 'medical_category', 'age_group']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for record in nelson_records:
            # Convert keywords list to PostgreSQL array format
            keywords_str = '{' + ','.join(f'"{k}"' for k in record['keywords']) + '}'
            
            writer.writerow({
                'chapter': record['chapter'],
                'section': record['section'],
                'page_number': record['page_number'],
                'content': record['content'],
                'keywords': keywords_str,
                'medical_category': record['medical_category'],
                'age_group': record['age_group']
            })
    
    # Pediatric Resources CSV
    resources_csv = 'pediatric_medical_resources_dataset.csv'
    with open(resources_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['title', 'content', 'resource_type', 'category', 'age_range', 'weight_range', 'source']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for record in resource_records:
            writer.writerow(record)
    
    print(f"✅ Created {nelson_csv} with {len(nelson_records)} records")
    print(f"✅ Created {resources_csv} with {len(resource_records)} records")
    
    return nelson_csv, resources_csv

def main():
    """Main function to create datasets."""
    
    print("🏥 Creating Nelson Textbook Dataset for New Schema")
    print("=" * 60)
    
    # Process existing data
    nelson_records = process_existing_dataset()
    
    if not nelson_records:
        print("❌ No records to process!")
        return
    
    # Create pediatric resources
    resource_records = create_pediatric_resources()
    
    # Create CSV files
    nelson_csv, resources_csv = create_csv_files(nelson_records, resource_records)
    
    # Show statistics
    print(f"\n📊 Dataset Statistics:")
    print(f"Nelson Textbook Records: {len(nelson_records)}")
    print(f"Pediatric Resources: {len(resource_records)}")
    
    # Show category distribution
    categories = {}
    for record in nelson_records:
        cat = record['medical_category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n📚 Medical Categories:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count} records")
    
    print(f"\n🎯 Files Ready for Upload:")
    print(f"1. {nelson_csv}")
    print(f"2. {resources_csv}")
    print(f"3. new_schema_setup.sql")

if __name__ == "__main__":
    main()

