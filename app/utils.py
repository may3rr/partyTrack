import os
from pathlib import Path

def load_party_docs():
    """加载党建相关文档作为上下文"""
    docs_path = Path(os.path.dirname(__file__)) / 'knowledge'
    context = []
    
    # 读取manual.md文件
    manual_path = docs_path / 'manual.md'
    if manual_path.exists():
        with open(manual_path, 'r', encoding='utf-8') as f:
            context.append(f.read())
    
    # 这里可以添加更多文档的处理
    
    # 合并所有文档内容，限制总长度
    combined_context = ' '.join(context)
    max_length = 8000  # 限制上下文长度
    if len(combined_context) > max_length:
        combined_context = combined_context[:max_length]
    
    return combined_context 