"""
Модуль для загрузки и предварительной обработки текстов
"""

import re
from typing import Dict, List, Optional
import os


class TextLoader:
    """Класс для загрузки и обработки текстов из различных источников"""
    
    def __init__(self):
        self.supported_extensions = ['.txt', '.md', '.text']
    
    def load_from_file(self, filepath: str) -> str:
        """
        Загрузить текст из файла
        
        Args:
            filepath: Путь к файлу
        
        Returns:
            Содержимое файла
        
        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если расширение файла не поддерживается
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Файл не найден: {filepath}")
        
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in self.supported_extensions:
            raise ValueError(
                f"Неподдерживаемое расширение: {ext}. "
                f"Поддерживаются: {', '.join(self.supported_extensions)}"
            )
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            return text
        except UnicodeDecodeError:
            # Попробуем другие кодировки
            for encoding in ['cp1251', 'latin-1', 'iso-8859-1']:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        text = f.read()
                    return text
                except UnicodeDecodeError:
                    continue
            raise ValueError("Не удалось определить кодировку файла")
    
    def load_from_string(self, text: str) -> str:
        """
        Загрузить текст из строки
        
        Args:
            text: Текст для анализа
        
        Returns:
            Очищенный текст
        """
        if not isinstance(text, str):
            raise ValueError("Текст должен быть строкой")
        
        if not text.strip():
            raise ValueError("Текст не может быть пустым")
        
        return text.strip()
    
    def preprocess_text(self, text: str, remove_urls: bool = True, 
                       remove_emails: bool = True) -> str:
        """
        Предварительная обработка текста
        
        Args:
            text: Исходный текст
            remove_urls: Удалить URL-адреса
            remove_emails: Удалить email-адреса
        
        Returns:
            Обработанный текст
        """
        processed = text
        
        # Удаление URL
        if remove_urls:
            url_pattern = r'https?://\S+|www\.\S+'
            processed = re.sub(url_pattern, '[URL]', processed)
        
        # Удаление email
        if remove_emails:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            processed = re.sub(email_pattern, '[EMAIL]', processed)
        
        # Удаление множественных пробелов
        processed = re.sub(r'\s+', ' ', processed)
        
        # Удаление пробелов в начале и конце
        processed = processed.strip()
        
        return processed
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Разбить текст на предложения
        
        Args:
            text: Текст для разбиения
        
        Returns:
            Список предложений
        """
        # Простая эвристика для разбиения на предложения
        # В идеале использовать nltk.sent_tokenize, но это добавим в analyzer
        sentence_pattern = r'[.!?]+\s+'
        sentences = re.split(sentence_pattern, text)
        
        # Удалить пустые предложения
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def get_text_stats(self, text: str) -> Dict[str, int]:
        """
        Получить статистику по тексту
        
        Args:
            text: Текст для анализа
        
        Returns:
            Словарь со статистикой
        """
        sentences = self.split_into_sentences(text)
        words = text.split()
        
        return {
            'chars': len(text),
            'chars_no_spaces': len(text.replace(' ', '')),
            'words': len(words),
            'sentences': len(sentences),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
        }
    
    def extract_quotes(self, text: str) -> List[str]:
        """
        Извлечь цитаты из текста (текст в кавычках)
        
        Args:
            text: Текст для анализа
        
        Returns:
            Список цитат
        """
        # Поиск текста в кавычках (различные типы кавычек)
        quote_patterns = [
            r'"([^"]+)"',  # Английские кавычки
            r'«([^»]+)»',  # Русские кавычки
            r'"([^"]+)"',  # Типографские кавычки
            r''([^']+)'',  # Одинарные типографские кавычки
        ]
        
        quotes = []
        for pattern in quote_patterns:
            quotes.extend(re.findall(pattern, text))
        
        return quotes
    
    def detect_language(self, text: str) -> str:
        """
        Определить язык текста (простая эвристика)
        
        Args:
            text: Текст для анализа
        
        Returns:
            'russian', 'english' или 'unknown'
        """
        # Подсчёт кириллицы и латиницы
        cyrillic_chars = len(re.findall(r'[а-яА-ЯёЁ]', text))
        latin_chars = len(re.findall(r'[a-zA-Z]', text))
        
        total_chars = cyrillic_chars + latin_chars
        
        if total_chars == 0:
            return 'unknown'
        
        if cyrillic_chars / total_chars > 0.6:
            return 'russian'
        elif latin_chars / total_chars > 0.6:
            return 'english'
        else:
            return 'unknown'
    
    def save_to_file(self, text: str, filepath: str) -> None:
        """
        Сохранить текст в файл
        
        Args:
            text: Текст для сохранения
            filepath: Путь к файлу
        """
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)


class TextHighlighter:
    """Класс для подсветки найденных маркеров в тексте"""
    
    def __init__(self, use_colors: bool = True):
        """
        Args:
            use_colors: Использовать цветную подсветку (для консоли)
        """
        self.use_colors = use_colors
        
        # ANSI коды цветов
        self.colors = {
            'high': '\033[91m',      # Красный
            'medium': '\033[93m',    # Жёлтый
            'low': '\033[92m',       # Зелёный
            'reset': '\033[0m',      # Сброс
            'bold': '\033[1m',       # Жирный
        }
    
    def highlight_text(self, text: str, markers: List[Dict], 
                      severity_colors: Optional[Dict[str, str]] = None) -> str:
        """
        Подсветить маркеры в тексте
        
        Args:
            text: Исходный текст
            markers: Список найденных маркеров с позициями
            severity_colors: Соответствие серьёзности и цвета
        
        Returns:
            Текст с подсветкой
        """
        if not markers:
            return text
        
        if severity_colors is None:
            severity_colors = {
                'high': 'high',
                'medium': 'medium',
                'low': 'low',
            }
        
        # Сортируем маркеры по позиции (в обратном порядке)
        sorted_markers = sorted(markers, key=lambda x: x['start'], reverse=True)
        
        highlighted = text
        
        for marker in sorted_markers:
            start = marker['start']
            end = marker['end']
            severity = marker.get('severity', 'medium')
            
            original = highlighted[start:end]
            
            if self.use_colors:
                color = self.colors.get(severity_colors.get(severity, 'medium'), '')
                reset = self.colors['reset']
                bold = self.colors['bold']
                replacement = f"{bold}{color}{original}{reset}"
            else:
                replacement = f"**{original}**"
            
            highlighted = highlighted[:start] + replacement + highlighted[end:]
        
        return highlighted
    
    def generate_html_highlight(self, text: str, markers: List[Dict]) -> str:
        """
        Генерация HTML с подсветкой маркеров
        
        Args:
            text: Исходный текст
            markers: Список найденных маркеров
        
        Returns:
            HTML с подсветкой
        """
        if not markers:
            return f"<pre>{text}</pre>"
        
        # Сортируем маркеры по позиции (в обратном порядке)
        sorted_markers = sorted(markers, key=lambda x: x['start'], reverse=True)
        
        highlighted = text
        
        severity_classes = {
            'high': 'marker-high',
            'medium': 'marker-medium',
            'low': 'marker-low',
        }
        
        for marker in sorted_markers:
            start = marker['start']
            end = marker['end']
            severity = marker.get('severity', 'medium')
            category = marker.get('category', '')
            
            original = highlighted[start:end]
            css_class = severity_classes.get(severity, 'marker-medium')
            
            replacement = (
                f'<span class="{css_class}" '
                f'title="Категория: {category}. Серьёзность: {severity}">'
                f'{original}</span>'
            )
            
            highlighted = highlighted[:start] + replacement + highlighted[end:]
        
        html = f"""
        <style>
            .marker-high {{
                background-color: #ffcccc;
                border-bottom: 2px solid #ff0000;
                font-weight: bold;
            }}
            .marker-medium {{
                background-color: #fff4cc;
                border-bottom: 2px solid #ff9900;
            }}
            .marker-low {{
                background-color: #ccffcc;
                border-bottom: 2px solid #00cc00;
            }}
            pre {{
                white-space: pre-wrap;
                word-wrap: break-word;
                font-family: 'Courier New', monospace;
                line-height: 1.6;
            }}
        </style>
        <pre>{highlighted}</pre>
        """
        
        return html