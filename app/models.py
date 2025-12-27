import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import threading

class PairManager:
    """管理图片对的数据模型"""
    
    def __init__(self, pairs_file: str):
        self.pairs_file = pairs_file
        self.lock = threading.Lock()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """确保pairs.json文件存在"""
        if not os.path.exists(self.pairs_file):
            with open(self.pairs_file, 'w', encoding='utf-8') as f:
                json.dump({"pairs": []}, f, ensure_ascii=False, indent=2)
    
    def load_pairs(self) -> List[Dict]:
        """加载所有图片对"""
        with self.lock:
            try:
                with open(self.pairs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('pairs', [])
            except (FileNotFoundError, json.JSONDecodeError):
                return []
    
    def save_pair(self, pair_data: Dict) -> str:
        """保存新图片对"""
        with self.lock:
            pairs = self.load_pairs()
            pairs.append(pair_data)
            
            with open(self.pairs_file, 'w', encoding='utf-8') as f:
                json.dump({"pairs": pairs}, f, ensure_ascii=False, indent=2)
            
            return pair_data['pair_id']
    
    def get_pair(self, pair_id: str) -> Optional[Dict]:
        """获取指定图片对"""
        pairs = self.load_pairs()
        for pair in pairs:
            if pair['pair_id'] == pair_id:
                return pair
        return None
    
    def delete_pair(self, pair_id: str) -> bool:
        """删除图片对"""
        with self.lock:
            pairs = self.load_pairs()
            original_count = len(pairs)
            pairs = [p for p in pairs if p['pair_id'] != pair_id]
            
            if len(pairs) < original_count:
                with open(self.pairs_file, 'w', encoding='utf-8') as f:
                    json.dump({"pairs": pairs}, f, ensure_ascii=False, indent=2)
                return True
            return False

