#!/usr/bin/env python3
import os
import re
import json
from pathlib import Path
from collections import defaultdict

def find_all_source_files(root_dir):
    """Find all source files in the project"""
    source_extensions = {'.vue', '.ts', '.js', '.jsx', '.tsx', '.json'}
    exclude_dirs = {'node_modules', '.output', 'dist', 'venv', '.git', 'dumps', 'backend', 'cloudRun'}
    
    source_files = []
    for root, dirs, files in os.walk(root_dir):
        # Remove excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in source_extensions):
                source_files.append(os.path.join(root, file))
    
    return source_files

def extract_component_name(file_path):
    """Extract component name from file path"""
    # Get the base name without extension
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    return base_name

def check_file_usage(file_to_check, all_files):
    """Check if a file is imported or used anywhere"""
    component_name = extract_component_name(file_to_check)
    file_relative = os.path.relpath(file_to_check).replace('\\', '/')
    
    # Various import patterns to check
    import_patterns = [
        rf"import\s+.*\s+from\s+['\"].*{component_name}['\"]",
        rf"import\s+\{{\s*{component_name}\s*\}}\s+from",
        rf"import\s+{component_name}\s+from",
        rf"const\s+.*=\s*import\(['\"].*{component_name}['\"]",
        rf"defineAsyncComponent\(\(\)\s*=>\s*import\(['\"].*{component_name}['\"]",
        # Direct path imports
        rf"from\s+['\"].*{file_relative}['\"]",
        rf"import\(['\"].*{file_relative}['\"]",
    ]
    
    # Component usage patterns in Vue templates
    kebab_case = re.sub(r'([A-Z])', r'-\1', component_name).lower().lstrip('-')
    usage_patterns = [
        rf"<{component_name}[\s/>]",  # Vue component usage
        rf"<{kebab_case}[\s/>]",  # kebab-case
        rf"components:\s*\{{[^}}]*{component_name}[^}}]*\}}",  # Component registration
        rf"'{component_name}':|{component_name}:",  # Object property
    ]
    
    usages = []
    
    for source_file in all_files:
        if source_file == file_to_check:
            continue
            
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check import patterns
            for pattern in import_patterns:
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    usages.append({
                        'file': source_file,
                        'type': 'import',
                        'pattern': pattern
                    })
                    
            # Check usage patterns
            for pattern in usage_patterns:
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    usages.append({
                        'file': source_file,
                        'type': 'usage',
                        'pattern': pattern
                    })
                    
        except Exception as e:
            print(f"Error reading {source_file}: {e}")
            
    return usages

def analyze_directory(root_dir, target_dirs):
    """Analyze specified directories for unused files"""
    all_source_files = find_all_source_files(root_dir)
    results = defaultdict(list)
    
    for target_dir in target_dirs:
        dir_path = os.path.join(root_dir, target_dir)
        if not os.path.exists(dir_path):
            continue
            
        # Find all files in target directory
        target_files = []
        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if d not in {'node_modules', '.output', 'dist', 'venv'}]
            for file in files:
                if file.endswith(('.vue', '.ts', '.js', '.jsx', '.tsx')) and not file.endswith('.spec.test.ts'):
                    target_files.append(os.path.join(root, file))
        
        # Check each file
        for file_path in target_files:
            usages = check_file_usage(file_path, all_source_files)
            if not usages:
                results[target_dir].append(file_path)
                
    return results

def main():
    root_dir = '/Users/osapiii/Documents/GitHub/knockai'
    target_dirs = ['components', 'pages', 'stores', 'utils', 'composables', 'types']
    
    print("Analyzing unused files...")
    unused_files = analyze_directory(root_dir, target_dirs)
    
    # Print results
    total_unused = 0
    for directory, files in unused_files.items():
        if files:
            print(f"\n## Unused files in {directory}/:")
            for file in sorted(files):
                print(f"  - {os.path.relpath(file, root_dir)}")
            total_unused += len(files)
    
    print(f"\n## Summary: Found {total_unused} potentially unused files")
    
    # Save detailed results to JSON
    with open('unused_files_report.json', 'w') as f:
        json.dump({
            'unused_files': {k: [os.path.relpath(f, root_dir) for f in v] 
                           for k, v in unused_files.items()},
            'total_count': total_unused
        }, f, indent=2)
    print("\nDetailed report saved to unused_files_report.json")

if __name__ == "__main__":
    main()