import re
from typing import List, Dict, Tuple
from datetime import datetime

class KeywordDetector:
    def __init__(self, keywords: List[str]):
        self.keywords = [kw.lower() for kw in keywords]  # Convert to lowercase for matching
        self.transcription_buffer = []
        self.buffer_size = 100  # Keep last 100 transcriptions
        
    def add_transcription(self, text: str) -> List[Tuple[str, str]]:
        """
        Add a transcription and check for keywords
        Returns list of (keyword, context) tuples for matched keywords
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {"timestamp": timestamp, "text": text.lower()}
        
        # Add to buffer
        self.transcription_buffer.append(entry)
        
        # Keep buffer size manageable
        if len(self.transcription_buffer) > self.buffer_size:
            self.transcription_buffer.pop(0)
        
        # Check for keywords and return matches with context
        matches = []
        for keyword in self.keywords:
            if keyword in text.lower():
                context = self._get_context(text.lower(), keyword)
                matches.append((keyword, context))
        
        return matches
    
    def _get_context(self, text: str, keyword: str) -> str:
        """
        Get context around the keyword (words before and after)
        """
        words = text.split()
        keyword_words = keyword.split()
        
        # Find the position of the keyword
        for i in range(len(words)):
            # Check for multi-word keywords
            if ' '.join(words[i:i+len(keyword_words)]).lower() == keyword:
                start = max(0, i - 10)  # 10 words before
                end = min(len(words), i + len(keyword_words) + 10)  # 10 words after
                
                context_words = words[start:end]
                context = ' '.join(context_words)
                
                return f"[{start}:{end}] {context}"
        
        # Single word keyword
        for i, word in enumerate(words):
            if word == keyword:
                start = max(0, i - 10)
                end = min(len(words), i + 11)
                
                context_words = words[start:end]
                context = ' '.join(context_words)
                
                return f"[{start}:{end}] {context}"
        
        return text  # Fallback
    
    def get_recent_transcriptions(self, count: int = 10) -> List[Dict]:
        """Get recent transcriptions"""
        return self.transcription_buffer[-count:]
    
    def clear_buffer(self):
        """Clear the transcription buffer"""
        self.transcription_buffer.clear()
    
    def search_keyword_history(self, keyword: str) -> List[Dict]:
        """Search through history for specific keyword"""
        keyword_lower = keyword.lower()
        matches = []
        
        for entry in self.transcription_buffer:
            if keyword_lower in entry["text"]:
                matches.append(entry)
        
        return matches