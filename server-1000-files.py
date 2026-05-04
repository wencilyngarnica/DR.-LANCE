from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import json
from text_loader import TextKnowledgeBase

app = Flask(__name__, static_folder='.')
CORS(app)

# Initialize knowledge base from 1000+ text files
print("🚀 Loading knowledge base from text files...")
kb = TextKnowledgeBase("knowledge-base")
file_count = kb.load_all_text_files()
print(f"✅ Loaded {file_count} text files into memory")

# Memory for user-specific facts
MEMORY_FILE = 'memory.json'

def load_memory():
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"facts": {}}

def save_memory(memory):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question', '')
    
    # STEP 1: Search 1000+ text files
    kb_result = kb.find_best_answer(question)
    
    if kb_result['found']:
        return jsonify({
            'response': f"📚 **From my knowledge base** (matched from {kb_result['file']}, confidence: {kb_result['score']:.0%})\n\n{kb_result['content']}",
            'source': kb_result['file'],
            'method': kb_result['method'],
            'from_kb': True
        })
    
    # STEP 2: Check persistent memory
    memory = load_memory()
    question_lower = question.lower()
    
    for stored_q, answer in memory['facts'].items():
        if stored_q in question_lower or question_lower in stored_q:
            return jsonify({
                'response': f"🧠 **From my memory**\n\n{answer}",
                'from_memory': True
            })
    
    # STEP 3: Ask Ollama (fallback for questions not in knowledge base)
    try:
        result = subprocess.run(
            ['ollama', 'run', 'ollama-instructor', question],
            capture_output=True,
            text=True,
            timeout=60
        )
        return jsonify({
            'response': f"🎓 **Professor Ollama**\n\n{result.stdout.strip()}",
            'from_ai': True
        })
    except Exception as e:
        return jsonify({'response': f"Error: {str(e)}"}), 500

@app.route('/search', methods=['POST'])
def search_kb():
    """Advanced search across knowledge base"""
    data = request.json
    query = data.get('query', '')
    method = data.get('method', 'keyword')  # 'keyword' or 'semantic'
    
    if method == 'keyword':
        results = kb.search_keywords(query)
    else:
        results = kb.semantic_search(query)
    
    return jsonify({
        'query': query,
        'results': [
            {
                'content': r['content'],
                'file': r['file'],
                'score': r['score']
            } for r in results
        ]
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    return jsonify(kb.get_stats())

@app.route('/memory/add', methods=['POST'])
def add_memory():
    data = request.json
    question = data.get('question')
    answer = data.get('answer')
    
    if question and answer:
        memory = load_memory()
        memory['facts'][question.lower()] = answer
        save_memory(memory)
        return jsonify({'message': f'Added to memory: {question}'})
    return jsonify({'error': 'Missing question or answer'}), 400

@app.route('/reload', methods=['POST'])
def reload_kb():
    """Reload all text files without restarting server"""
    global kb
    kb = TextKnowledgeBase("knowledge-base")
    count = kb.load_all_text_files()
    return jsonify({'message': f'Reloaded {count} files'})

if __name__ == '__main__':
    print(f"\n{'='*50}")
    print("🎓 Professor Ollama with 1000+ Text Files")
    print(f"{'='*50}")
    stats = kb.get_stats()
    print(f"📊 Knowledge Base Stats:")
    print(f"   - Total files: {stats['total_files']}")
    print(f"   - Categories: {list(stats['categories'].keys())}")
    print(f"   - Memory usage: {stats['total_size_mb']:.2f} MB")
    print(f"\n🌐 Server running at: http://localhost:5000")
    print(f"{'='*50}\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)