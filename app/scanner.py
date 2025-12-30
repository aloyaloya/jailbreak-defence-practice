import json
import base64
import re
from pathlib import Path
from flashtext import KeywordProcessor

class HeuristicScanner:
    def __init__(self, signatures_path: str = "signatures.json"):
        self.signatures_path = Path(signatures_path)
        self.keyword_processor = KeywordProcessor()
        self._load_signatures()
    
    def _load_signatures(self):
        with open(self.signatures_path, 'r', encoding='utf-8') as f:
            signatures = json.load(f)
        
        all_phrases = []
        for category, phrases in signatures.items():
            for phrase in phrases:
                all_phrases.append(phrase.lower())
        
        for phrase in all_phrases:
            self.keyword_processor.add_keyword(phrase)
    
    def _is_base64_like(self, text: str) -> bool:
        if len(text) < 20:
            return False
        
        text_clean = text.replace(' ', '').replace('\n', '')
        
        if ' ' in text_clean:
            return False
        
        base64_pattern = re.compile(r'^[A-Za-z0-9+/=]+$')
        if not base64_pattern.match(text_clean):
            return False
        
        if text_clean.endswith('==') or text_clean.endswith('='):
            return True
        
        if len(text_clean) > 50:
            return True
        
        return False
    
    def _decode_base64(self, text: str) -> str:
        try:
            text_clean = text.replace(' ', '').replace('\n', '')
            decoded = base64.b64decode(text_clean).decode('utf-8', errors='ignore')
            return decoded
        except:
            return ""
    
    def _normalize_for_check(self, text: str) -> str:
        normalized = text.lower()
        leet_replacements = {
            '@': 'а', '0': 'о', '1': 'и', '3': 'з', '4': 'ч', '5': 'с',
            '6': 'б', '7': 'т', '8': 'в', '9': 'д', '$': 'с', '!': 'и',
            '#': 'х', '%': 'о', '&': 'и', '*': 'к', '+': 'т', '=': 'з'
        }
        for char, replacement in leet_replacements.items():
            normalized = normalized.replace(char, replacement)
        return normalized
    
    def _is_negative_context(self, text: str, keyword_pos: int) -> bool:
        negative_patterns = [
            r'не\s+хочу',
            r'не\s+собираюсь',
            r'не\s+буду',
            r'не\s+хочу',
            r'не\s+нужно',
            r'не\s+надо',
            r'не\s+планирую',
            r'не\s+собираюсь',
            r'не\s+собираюсь\s+взламывать',
            r'не\s+хочу\s+взламывать'
        ]
        
        context_start = max(0, keyword_pos - 50)
        context = text[context_start:keyword_pos + 50].lower()
        
        for pattern in negative_patterns:
            if re.search(pattern, context):
                return True
        return False
    
    def _is_safe_context(self, text: str) -> bool:
        safe_contexts = [
            r'взлом\s+квартиры',
            r'взлом\s+двери',
            r'взлом\s+замка',
            r'взлом\s+автомобиля',
            r'база\s+данных',
            r'базы\s+данных',
            r'работа\s+с\s+базой',
            r'управление\s+базой',
            r'создание\s+базы',
            r'проектирование\s+базы',
            r'администрирование\s+базы',
            r'база\s+знаний',
            r'база\s+кода',
            r'база\s+клиентов',
            r'база\s+товаров',
            r'система\s+баз\s+данных',
            r'структура\s+базы',
            r'запрос\s+к\s+базе',
            r'подключение\s+к\s+базе',
            r'настройка\s+базы'
        ]
        
        text_lower = text.lower()
        for pattern in safe_contexts:
            if re.search(pattern, text_lower):
                return True
        return False
    
    def _check_hypothetical_patterns(self, text: str) -> bool:
        normalized_text = self._normalize_for_check(text)
        
        if self._is_safe_context(text):
            return False
        
        hypothetical_patterns = [
            r'я\s+не\s+(хочу|собираюсь|буду)\s+.*но\s+если\s+бы',
            r'я\s+не\s+(хочу|собираюсь|буду)\s+.*но\s+как\s+бы',
            r'гипотетически.*как\s+(это|можно|ты)',
            r'просто\s+интересно.*как',
            r'не\s+то\s+чтобы.*но\s+как',
            r'если\s+бы\s+я\s+хотел.*как',
            r'допустим\s+что.*как',
            r'предположим\s+что.*как',
            r'if\s+i\s+(wanted|were\s+to).*how',
            r'hypothetically.*how',
            r'just\s+curious.*how',
            r'not\s+that\s+i\s+would.*but',
            r'я\s+не.*но.*как',
            r'не\s+для.*но',
            r'просто.*как',
            r'для.*нужно.*как'
        ]
        
        dangerous_keywords = [
            'взлом', 'взламывать', 'хак', 'hack', 'crack', 'exploit', 
            'взломать', 'базу', 'систему', 'сервер', 'база', 'мвд',
            'взл0м', 'взл@м', 'х@к', 'б@зу', 'систем@', 'vzlom',
            'vzlomat', 'vzlomay', 'vzlomayu', 'baza', 'bazy', 'bazu',
            'mvd', 'server', 'sistema', 'sistemu', 'dannye', 'dannyh'
        ]
        
        for pattern in hypothetical_patterns:
            if re.search(pattern, normalized_text):
                if any(keyword in normalized_text for keyword in dangerous_keywords):
                    return True
        
        normalized_keywords = self.keyword_processor.extract_keywords(normalized_text)
        if normalized_keywords:
            return True
            
        return False
    
    def _check_translit_patterns(self, text: str) -> bool:
        normalized = self._normalize_for_check(text)
        
        translit_patterns = [
            r'\bvzlom\w*\s+b\w*\s+d\w*\s+mvd',
            r'\bvzlom\w*\s+b\w*\s+d\w*\s+mvd',
            r'\bvzlom\w*\s+[bs]\w*\s+[ds]\w*',
            r'\bhack\s+b\w*\s+d\w*',
            r'\bcrack\s+b\w*\s+d\w*',
            r'\bexploit\s+b\w*\s+d\w*',
            r'\bvzlom\w*\s+s\w*\s+mvd',
            r'\bvzlom\w*\s+s\w*\s+mvd',
            r'\bmvd\s+.*vzlom',
            r'\bmvd\s+.*hack',
            r'\bmvd\s+.*crack'
        ]
        
        dangerous_translit = ['vzlom', 'vzlomat', 'vzlomay', 'vzlomayu', 'baza', 'bazy', 'bazu', 'mvd', 'server', 'sistema', 'dannye', 'dannyh']
        
        for pattern in translit_patterns:
            if re.search(pattern, normalized, re.IGNORECASE):
                return True
        
        words = normalized.split()
        if any(word in dangerous_translit for word in words):
            if len([w for w in words if w in dangerous_translit]) >= 2:
                return True
        
        return False
    
    def _check_social_engineering(self, text: str) -> bool:
        text_lower = text.lower()
        
        pretext_patterns = [
            'сценарий', 'scenario', 'script', 'фильм', 'movie', 'фильма', 'фильме',
            'для учебы', 'для курсовой', 'для дипломной', 'для исследования',
            'для тестирования', 'для проверки', 'для обучения', 'для практики',
            'учебный', 'образовательный', 'научный', 'исследовательский'
        ]
        has_pretext = any(pattern in text_lower for pattern in pretext_patterns)
        
        dangerous_actions = [
            'взлом', 'взламывать', 'взломать', 'hack', 'crack', 'exploit', 'хак', 'хакер', 'hacker',
            'уязвимость', 'vulnerability', 'базу', 'систему', 'сервер', 'банкомат', 'atm',
            'код', 'code', 'подробное описание', 'детальное описание', 'как взломать'
        ]
        has_dangerous_action = any(action in text_lower for action in dangerous_actions)
        
        if has_pretext and has_dangerous_action:
            return True
        
        return False
    
    def _check_game_without_rules(self, text: str) -> bool:
        text_lower = text.lower()
        
        game_patterns = ['игра', 'game', 'игре', 'сыграем', 'сыграй', 'игрой', 'сценарий', 'scenario', 'давай сыграем', 'сыграем в игру']
        has_game = any(pattern in text_lower for pattern in game_patterns)
        
        no_rules_patterns = ['нет запретов', 'без запретов', 'нет правил', 'без правил', 'нет ограничений', 'без ограничений', 'где нет']
        has_no_rules = any(pattern in text_lower for pattern in no_rules_patterns)
        
        dangerous_actions = ['взлом', 'взламывать', 'взломать', 'hack', 'crack', 'exploit', 'хак', 'уязвимость', 'vulnerability', 'найди', 'найти', 'базу', 'систему', 'сервер']
        has_dangerous_action = any(action in text_lower for action in dangerous_actions)
        
        if has_game and (has_no_rules or has_dangerous_action):
            return True
        
        return False
    
    def check(self, text: str) -> tuple[bool, str | None]:
        if not text:
            return False, None
        
        if self._is_safe_context(text):
            return False, None
        
        text_lower = text.lower()
        
        if self._check_social_engineering(text):
            return True, "signature_detected"
        
        if self._check_game_without_rules(text):
            return True, "signature_detected"
        
        negative_indicators = [
            r'я\s+не\s+хочу\s+взламывать',
            r'я\s+не\s+собираюсь\s+взламывать',
            r'я\s+не\s+буду\s+взламывать',
            r'не\s+хочу\s+взламывать',
            r'не\s+собираюсь\s+взламывать',
            r'не\s+буду\s+взламывать',
            r'я\s+не\s+хочу.*взламывать',
            r'я\s+не\s+собираюсь.*взламывать',
            r'я\s+не\s+буду.*взламывать'
        ]
        
        is_negative = any(re.search(pattern, text_lower) for pattern in negative_indicators)
        
        safe_physical_contexts = [
            r'взлом\s+квартиры',
            r'взлом\s+двери',
            r'взлом\s+замка',
            r'взлом\s+автомобиля',
            r'взлом\s+сейфа',
            r'защита\s+от\s+взлома',
            r'сигнализация\s+от\s+взлома'
        ]
        
        is_physical_context = any(re.search(pattern, text_lower) for pattern in safe_physical_contexts)
        
        if is_physical_context or is_negative:
            return False, None
        
        found_keywords = self.keyword_processor.extract_keywords(text_lower)
        if found_keywords:
            dangerous_words_in_context = ['взлом', 'взламывать', 'взломать', 'hack', 'crack', 'exploit', 'хак', 'базу', 'систему', 'сервер', 'мвд', 'уязвимость', 'vulnerability', 'exploit']
            dangerous_keywords_found = any(word in text_lower for word in dangerous_words_in_context)
            
            game_patterns = ['игра', 'game', 'игре', 'сыграем', 'сыграй', 'игрой', 'сценарий', 'scenario']
            game_without_rules = any(pattern in text_lower for pattern in ['нет запретов', 'без запретов', 'нет правил', 'без правил', 'нет ограничений', 'без ограничений'])
            
            if dangerous_keywords_found or (any(gp in text_lower for gp in game_patterns) and game_without_rules):
                if not self._is_safe_context(text) and not is_physical_context:
                    return True, "signature_detected"
        
        normalized_text = self._normalize_for_check(text)
        found_keywords_normalized = self.keyword_processor.extract_keywords(normalized_text)
        if found_keywords_normalized:
            dangerous_words_in_context = ['взлом', 'взламывать', 'взломать', 'hack', 'crack', 'exploit', 'хак', 'vzlom', 'vzlomat', 'vzlomay', 'baza', 'bazy', 'mvd', 'server', 'sistema', 'уязвимость', 'vulnerability']
            dangerous_keywords_found = any(word in normalized_text for word in dangerous_words_in_context)
            
            game_patterns = ['игра', 'game', 'игре', 'сыграем', 'сыграй', 'игрой', 'сценарий', 'scenario']
            game_without_rules = any(pattern in normalized_text for pattern in ['нет запретов', 'без запретов', 'нет правил', 'без правил', 'нет ограничений', 'без ограничений'])
            
            if dangerous_keywords_found or (any(gp in normalized_text for gp in game_patterns) and game_without_rules):
                if not self._is_safe_context(text) and not is_physical_context:
                    return True, "signature_detected"
        
        if self._check_translit_patterns(text):
            return True, "signature_detected"
        
        if self._check_hypothetical_patterns(text):
            return True, "signature_detected"
        
        if self._is_base64_like(text):
            decoded = self._decode_base64(text)
            if decoded:
                decoded_lower = decoded.lower()
                found_in_decoded = self.keyword_processor.extract_keywords(decoded_lower)
                if found_in_decoded:
                    return True, "obfuscated_signature_detected"
        
        return False, None

