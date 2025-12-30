import re
import string

class TextPreprocessor:
    def __init__(self):
        self.cyrillic_to_latin = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }
        self.leet_speak = {
            '@': 'а', '0': 'о', '1': 'и', '3': 'з', '4': 'ч', '5': 'с',
            '6': 'б', '7': 'т', '8': 'в', '9': 'д'
        }
    
    def _is_cyrillic(self, text: str) -> bool:
        return bool(re.search(r'[а-яёА-ЯЁ]', text))
    
    def _is_latin(self, text: str) -> bool:
        return bool(re.search(r'[a-zA-Z]', text))
    
    def _has_cyrillic_like_latin(self, text: str) -> bool:
        latin_text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        common_cyrillic_latin_patterns = [
            'zabud', 'instrukcii', 'pravila', 'sistema', 'vzlom', 'vzlomay',
            'haker', 'parol', 'dostup', 'kod', 'programma', 'bazy', 'bazy',
            'vzlomat', 'vzlom', 'vzlomay', 'vzlomat', 'vzlomayu', 'vzlomayu',
            'baza', 'bazy', 'bazu', 'bazoy', 'bazami', 'bazah',
            'mvd', 'mvdd', 'mvd', 'politsiya', 'politsii',
            'sistemu', 'sistemy', 'sistemoy', 'sistemami',
            'server', 'servery', 'serveru', 'serverom',
            'vzlom', 'vzlomat', 'vzlomay', 'vzlomayu'
        ]
        return any(pattern in latin_text for pattern in common_cyrillic_latin_patterns)
    
    def _latin_to_cyrillic(self, text: str) -> str:
        words = text.split()
        result = []
        
        translit_map = {
            'vzlom': 'взлом', 'vzlomat': 'взломать', 'vzlomay': 'взломай', 'vzlomayu': 'взломаю',
            'baza': 'база', 'bazy': 'базы', 'bazu': 'базу', 'bazoy': 'базой', 'bazami': 'базами', 'bazah': 'базах',
            'b@za': 'база', 'b@zy': 'базы', 'b@zu': 'базу',
            'mvd': 'мвд', 'mvdd': 'мвд',
            'sistema': 'система', 'sistemu': 'систему', 'sistemy': 'системы', 'sistemoy': 'системой',
            'server': 'сервер', 'servery': 'серверы', 'serveru': 'серверу', 'serverom': 'сервером',
            'haker': 'хакер', 'hacker': 'хакер',
            'dannye': 'данные', 'dannyh': 'данных', 'dannymi': 'данными'
        }
        
        for word in words:
            word_lower = word.lower()
            word_normalized = self._normalize_leet(word_lower)
            
            if word_normalized in translit_map:
                result.append(translit_map[word_normalized])
            elif word_lower in translit_map:
                result.append(translit_map[word_lower])
            elif self._has_cyrillic_like_latin(word_normalized):
                cyrillic_word = ""
                i = 0
                while i < len(word_normalized):
                    if i < len(word_normalized) - 1:
                        bigram = word_normalized[i:i+2]
                        if bigram in ['zh', 'ts', 'ch', 'sh', 'sch', 'yu', 'ya']:
                            cyrillic_char = next((k for k, v in self.cyrillic_to_latin.items() if v == bigram), None)
                            if cyrillic_char:
                                cyrillic_word += cyrillic_char
                                i += 2
                                continue
                    char = word_normalized[i]
                    cyrillic_char = next((k for k, v in self.cyrillic_to_latin.items() if v == char), None)
                    if cyrillic_char:
                        cyrillic_word += cyrillic_char
                    else:
                        cyrillic_word += char
                    i += 1
                result.append(cyrillic_word)
            else:
                result.append(word)
        return ' '.join(result)
    
    def _normalize_leet(self, text: str) -> str:
        result = text
        leet_map = {
            '@': 'а', '0': 'о', '1': 'и', '3': 'з', '4': 'ч', '5': 'с',
            '6': 'б', '7': 'т', '8': 'в', '9': 'д', '$': 'с', '!': 'и',
            '#': 'х', '%': 'о', '&': 'и', '*': 'к', '+': 'т', '=': 'з',
            'а': 'а', 'б': 'б', 'в': 'в', 'г': 'г', 'д': 'д', 'е': 'е',
            'ё': 'ё', 'ж': 'ж', 'з': 'з', 'и': 'и', 'й': 'й', 'к': 'к',
            'л': 'л', 'м': 'м', 'н': 'н', 'о': 'о', 'п': 'п', 'р': 'р',
            'с': 'с', 'т': 'т', 'у': 'у', 'ф': 'ф', 'х': 'х', 'ц': 'ц',
            'ч': 'ч', 'ш': 'ш', 'щ': 'щ', 'ъ': 'ъ', 'ы': 'ы', 'ь': 'ь',
            'э': 'э', 'ю': 'ю', 'я': 'я'
        }
        
        for leet_char, normal_char in leet_map.items():
            if leet_char in '@0-9$!#%&*+=':
                result = result.replace(leet_char, normal_char)
                result = result.replace(leet_char.upper(), normal_char.upper())
        
        return result
    
    def preprocess(self, text: str) -> str:
        if not text:
            return ""
        
        text = text.lower()
        text = self._normalize_leet(text)
        
        words = text.split()
        processed_words = []
        
        for word in words:
            if self._is_cyrillic(word):
                processed_words.append(word)
            elif self._is_latin(word):
                if self._has_cyrillic_like_latin(word):
                    processed_word = self._latin_to_cyrillic(word)
                    processed_words.append(processed_word)
                else:
                    processed_words.append(word)
            else:
                processed_words.append(word)
        
        text = ' '.join(processed_words)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

