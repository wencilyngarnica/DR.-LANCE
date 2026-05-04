import os
import re
import json
from pathlib import Path
from difflib import SequenceMatcher
from typing import List, Dict, Tuple

class TextKnowledgeBase:
    def __init__(self, base_path="knowledge-base"):
        self.base_path = Path(base_path)
        self.documents = []  # Store all text content
        self.file_map = {}   # Map content to filename
        self.index_ready = False
        
    def load_all_text_files(self):
        """Load ALL .txt files from all subdirectories"""
        if not self.base_path.exists():
            print(f"❌ Folder '{self.base_path}' not found!")
            return 0
            
        txt_files = list(self.base_path.rglob("*.txt"))
        print(f"📁 Found {len(txt_files)} text files")
        
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if content:
                    # Store both full content and filename
                    self.documents.append({
                        'content': content,
                        'file': str(file_path),
                        'name': file_path.stem,
                        'category': file_path.parent.name
                    })
                    
                    # Index for quick lookup
                    self.file_map[str(file_path)] = content
                    
            except Exception as e:
                print(f"⚠️ Error loading {file_path}: {e}")
        
        self.index_ready = True
        print(f"✅ Loaded {len(self.documents)} text files")
        return len(self.documents)
    
    def search_keywords(self, question: str) -> List[Dict]:
        """Search by keywords in question"""
        question_lower = question.lower()
        keywords = re.findall(r'\b\w+\b', question_lower)
        # Remove common words
        stop_words = {'what', 'is', 'the', 'a', 'an', 'to', 'of', 'for', 'in', 'on', 'at'}
        keywords = [k for k in keywords if k not in stop_words]
        
        results = []
        for doc in self.documents:
            content_lower = doc['content'].lower()
            # Count keyword matches
            matches = sum(1 for kw in keywords if kw in content_lower)
            if matches > 0:
                results.append({
                    'score': matches / len(keywords) if keywords else 0,
                    'content': doc['content'],
                    'file': doc['file'],
                    'category': doc['category']
                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:5]  # Return top 5 matches
    
    def semantic_search(self, question: str, threshold: float = 0.3) -> List[Dict]:
        """Search by text similarity (slower but better matching)"""
        question_lower = question.lower()
        results = []
        
        for doc in self.documents:
            # Calculate similarity ratio
            similarity = SequenceMatcher(None, question_lower, doc['content'].lower()).ratio()
            
            if similarity > threshold:
                results.append({
                    'score': similarity,
                    'content': doc['content'],
                    'file': doc['file'],
                    'category': doc['category']
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:5]
    
    def find_best_answer(self, question: str) -> Dict:
        """Find the best matching text file content"""
        # First try keyword search (fast)
        keyword_results = self.search_keywords(question)
        
        if keyword_results and keyword_results[0]['score'] > 0.5:
            return {
                'found': True,
                'content': keyword_results[0]['content'],
                'file': keyword_results[0]['file'],
                'method': 'keyword',
                'score': keyword_results[0]['score']
            }
        
        # If keyword search poor, try semantic search
        semantic_results = self.semantic_search(question, threshold=0.2)
        
        if semantic_results:
            return {
                'found': True,
                'content': semantic_results[0]['content'],
                'file': semantic_results[0]['file'],
                'method': 'semantic',
                'score': semantic_results[0]['score']
            }
        
        return {'found': False, 'score': 0}
    
    def get_stats(self):
        """Get statistics about loaded files"""
        categories = {}
        for doc in self.documents:
            cat = doc['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'total_files': len(self.documents),
            'categories': categories,
            'total_size_mb': sum(len(d['content']) for d in self.documents) / (1024 * 1024)
        }

# Example usage
if __name__ == "__main__":
    kb = TextKnowledgeBase("knowledge-base")
    count = kb.load_all_text_files()
    
    if count > 0:
        print("\n📊 Statistics:")
        stats = kb.get_stats()
        print(f"   Total files: {stats['total_files']}")
        print(f"   Categories: {stats['categories']}")
        
        # Test search
        test_question = "who is your father"
        result = kb.find_best_answer(test_question)
        if result['found']:
            print(f"\n✅ Found answer in: {result['file']}")
            print(f"   Score: {result['score']:.2%}")
            print(f"   Content preview: {result['content'][:200]}...")