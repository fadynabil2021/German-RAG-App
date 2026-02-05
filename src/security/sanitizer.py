import re
from typing import List

class PromptSanitizer:
    """
    Sanitizes user input to mitigate prompt injection and abuse.
    """
    
    # Common prompt injection patterns
    INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"system prompt",
        r"disregard all",
        r"you are now an? admin",
        r"reveal your secrets",
        r"stop being",
        r"new instructions:",
    ]

    @staticmethod
    def sanitize(text: str) -> str:
        """
        Cleans user text by removing potentially malicious instructions.
        """
        if not text:
            return ""
        
        # 1. Strip HTML if any (simple regex)
        text = re.sub(r'<[^>]*>', '', text)
        
        # 2. Check for injection patterns (case insensitive)
        for pattern in PromptSanitizer.INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                # We could block the request, but for a tutor, 
                # we just strip the suspicious part or return a sanitized version.
                text = re.sub(pattern, "[PROTECTED]", text, flags=re.IGNORECASE)
        
        # 3. Limit total length to prevent DoS via massive context
        MAX_LEN = 2000
        if len(text) > MAX_LEN:
            text = text[:MAX_LEN] + "... [TRUNCATED]"
            
        return text.strip()
