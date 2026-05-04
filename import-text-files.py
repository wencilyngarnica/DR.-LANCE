import os
import random
from pathlib import Path

def create_sample_text_files(count=1000):
    """Create sample text files for testing"""
    
    # Sample content templates
    templates = {
        'personal': [
            "My father is {name}. He is a {profession}.",
            "I was created on {date}. My purpose is to help students learn.",
            "My favorite subject is {subject}. I love teaching it to students."
        ],
        'science': [
            "The Earth revolves around the Sun. This takes 365.25 days.",
            "Water freezes at 0°C (32°F) and boils at 100°C (212°F).",
            "Photosynthesis is the process by which plants convert sunlight into energy."
        ],
        'programming': [
            "Python variables store data. Example: x = 5",
            "A for loop repeats code: for i in range(10): print(i)",
            "Functions organize code: def hello(): print('Hello')"
        ],
        'history': [
            "World War II ended in 1945.",
            "The first computer was invented in 1945 (ENIAC).",
            "The internet was created in the 1960s as ARPANET."
        ]
    }
    
    names = ['Alan Turing', 'Ada Lovelace', 'John McCarthy', 'Grace Hopper']
    professions = ['computer scientist', 'mathematician', 'physicist', 'engineer']
    subjects = ['Computer Science', 'Mathematics', 'Physics', 'Chemistry']
    dates = ['January 15, 2020', 'March 22, 2019', 'June 10, 2021']
    
    base_path = Path("knowledge-base")
    base_path.mkdir(exist_ok=True)
    
    print(f"Creating {count} sample text files...")
    
    for i in range(count):
        # Choose random category
        category = random.choice(list(templates.keys()))
        category_path = base_path / category
        category_path.mkdir(exist_ok=True)
        
        # Create filename
        filename = f"doc_{i:04d}.txt"
        filepath = category_path / filename
        
        # Generate content
        template = random.choice(templates[category])
        content = template.format(
            name=random.choice(names),
            profession=random.choice(professions),
            subject=random.choice(subjects),
            date=random.choice(dates)
        )
        
        # Add some variety
        if i % 3 == 0:
            content = f"Q: What is this?\nA: {content}"
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if (i + 1) % 100 == 0:
            print(f"  Created {i+1} files...")
    
    print(f"✅ Created {count} text files in 'knowledge-base/' folder")

# To import YOUR actual text files:
def import_your_files(source_folder, target_folder="knowledge-base"):
    """Import your existing text files"""
    source_path = Path(source_folder)
    target_path = Path(target_folder)
    
    if not source_path.exists():
        print(f"Source folder '{source_folder}' not found!")
        return
    
    txt_files = list(source_path.rglob("*.txt"))
    print(f"Found {len(txt_files)} text files to import")
    
    for file in txt_files:
        # Copy with category based on source folder
        category = file.parent.name
        target_category = target_path / category
        target_category.mkdir(exist_ok=True)
        
        target_file = target_category / file.name
        target_file.write_bytes(file.read_bytes())
    
    print(f"✅ Imported {len(txt_files)} files to {target_path}")

if __name__ == "__main__":
    print("📚 Text File Import Tool")
    print("=" * 40)
    print("1. Create 1000 sample files (for testing)")
    print("2. Import my existing text files")
    
    choice = input("\nChoose (1 or 2): ").strip()
    
    if choice == '1':
        create_sample_text_files(1000)
    elif choice == '2':
        source = input("Enter source folder path: ")
        import_your_files(source)
    else:
        print("Invalid choice")