"""
Основной модуль анализа медицинских текстов на псевдонаучные утверждения
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Предупреждение: spaCy не установлен. Некоторые функции будут недоступны.")

try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("Предупреждение: NLTK не установлен. Некоторые функции будут недоступны.")

from markets import (
    PSEUDOSCIENCE_MARKERS, RISK_CATEGORIES, LEGITIMATE_MEDICAL_TERMS,
    AMPLIFIERS, get_all_patterns, get_risk_level
)
from textloader import TextLoader, TextHighlighter


class PseudoscienceAnalyzer:
    """Анализатор псевдонаучных утверждений в медицинских текстах"""
    
    def __init__(self, language: str = 'russian', use_spacy: bool = True, 
                 use_nltk: bool = True):
        """
        Инициализация анализатора
        
        Args:
            language: Язык анализа ('russian' или 'english')
            use_spacy: Использовать spaCy для анализа
            use_nltk: Использовать NLTK для анализа
        """
        self.language = language
        self.text_loader = TextLoader()
        self.highlighter = TextHighlighter(use_colors=True)
        
        # Загрузка моделей spaCy
        self.nlp = None
        if use_spacy and SPACY_AVAILABLE:
            try:
                model_name = 'ru_core_news_sm' if language == 'russian' else 'en_core_web_sm'
                self.nlp = spacy.load(model_name)
            except OSError:
                print(f"Модель {model_name} не найдена. Используйте: python -m spacy download {model_name}")
        
        # Проверка NLTK
        self.use_nltk = use_nltk and NLTK_AVAILABLE
        if self.use_nltk:
            try:
                # Попытка загрузить необходимые данные
                stopwords.words('russian' if language == 'russian' else 'english')
            except LookupError:
                print("Загрузка данных NLTK...")
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
        
        # Компиляция регулярных выражений для производительности
        self.compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """
        Компиляция всех регулярных выражений
        
        Returns:
            Словарь скомпилированных паттернов по категориям
        """
        patterns = get_all_patterns(self.language)
        compiled = {}
        
        for category, pattern_list in patterns.items():
            compiled[category] = [
                re.compile(pattern, re.IGNORECASE | re.UNICODE)
                for pattern in pattern_list
            ]
        
        return compiled
    
    def analyze_text(self, text: str, detailed: bool = True) -> Dict:
        """
        Полный анализ текста
        
        Args:
            text: Текст для анализа
            detailed: Включить детальную информацию
        
        Returns:
            Словарь с результатами анализа
        """
        # Предварительная обработка
        processed_text = self.text_loader.preprocess_text(text)
        detected_language = self.text_loader.detect_language(processed_text)
        
        # Если язык текста отличается от настроенного, предупреждаем
        language_warning = None
        if detected_language != self.language and detected_language != 'unknown':
            language_warning = (
                f"Внимание: обнаружен язык '{detected_language}', "
                f"но анализатор настроен на '{self.language}'"
            )
        
        # Поиск псевдонаучных маркеров
        markers_found = self._find_markers(processed_text)
        
        # Поиск легитимных медицинских терминов
        legitimate_terms = self._find_legitimate_terms(processed_text)
        
        # Анализ амплификаторов
        amplifiers_found = self._find_amplifiers(processed_text)
        
        # Подсчёт по категориям
        category_counts = {}
        for marker in markers_found:
            category = marker['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Определение уровня риска
        risk_level = get_risk_level(category_counts)
        
        # Статистика текста
        text_stats = self.text_loader.get_text_stats(processed_text)
        
        # Формирование результата
        result = {
            'timestamp': datetime.now().isoformat(),
            'language_detected': detected_language,
            'language_warning': language_warning,
            'text_stats': text_stats,
            'risk_level': risk_level,
            'markers_count': len(markers_found),
            'category_counts': category_counts,
            'legitimate_terms_count': len(legitimate_terms),
            'amplifiers_count': len(amplifiers_found),
        }
        
        if detailed:
            result['markers'] = markers_found
            result['legitimate_terms'] = legitimate_terms
            result['amplifiers'] = amplifiers_found
            result['highlighted_text'] = self.highlighter.highlight_text(
                processed_text, markers_found
            )
        
        return result
    
    def _find_markers(self, text: str) -> List[Dict]:
        """
        Поиск псевдонаучных маркеров в тексте
        
        Args:
            text: Текст для анализа
        
        Returns:
            Список найденных маркеров
        """
        markers = []
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    marker = {
                        'category': category,
                        'text': match.group(0),
                        'start': match.start(),
                        'end': match.end(),
                        'severity': RISK_CATEGORIES[category]['severity'],
                        'description_ru': RISK_CATEGORIES[category]['description_ru'],
                        'description_en': RISK_CATEGORIES[category]['description_en'],
                    }
                    markers.append(marker)
        
        return markers
    
    def _find_legitimate_terms(self, text: str) -> List[Dict]:
        """
        Поиск легитимных медицинских терминов
        
        Args:
            text: Текст для анализа
        
        Returns:
            Список найденных терминов
        """
        terms = []
        patterns = LEGITIMATE_MEDICAL_TERMS.get(self.language, [])
        
        for pattern_str in patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE | re.UNICODE)
            for match in pattern.finditer(text):
                term = {
                    'text': match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                }
                terms.append(term)
        
        return terms
    
    def _find_amplifiers(self, text: str) -> List[Dict]:
        """
        Поиск слов-амплификаторов
        
        Args:
            text: Текст для анализа
        
        Returns:
            Список найденных амплификаторов
        """
        amplifiers = []
        words = AMPLIFIERS.get(self.language, [])
        
        for word in words:
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', 
                               re.IGNORECASE | re.UNICODE)
            for match in pattern.finditer(text):
                amplifier = {
                    'text': match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                }
                amplifiers.append(amplifier)
        
        return amplifiers
    
    def generate_report(self, analysis_result: Dict, format: str = 'text') -> str:
        """
        Генерация отчёта по результатам анализа
        
        Args:
            analysis_result: Результат анализа
            format: Формат отчёта ('text', 'json', 'html')
        
        Returns:
            Отчёт в выбранном формате
        """
        if format == 'json':
            return json.dumps(analysis_result, ensure_ascii=False, indent=2)
        elif format == 'html':
            return self._generate_html_report(analysis_result)
        else:
            return self._generate_text_report(analysis_result)
    
    def _generate_text_report(self, result: Dict) -> str:
        """Генерация текстового отчёта"""
        lines = []
        lines.append("=" * 70)
        lines.append("ОТЧЁТ АНАЛИЗА МЕДИЦИНСКОГО ТЕКСТА НА ПСЕВДОНАУКУ")
        lines.append("=" * 70)
        lines.append("")
        
        # Метаданные
        lines.append(f"Время анализа: {result['timestamp']}")
        lines.append(f"Обнаруженный язык: {result['language_detected']}")
        if result.get('language_warning'):
            lines.append(f"⚠️  {result['language_warning']}")
        lines.append("")
        
        # Статистика текста
        lines.append("СТАТИСТИКА ТЕКСТА:")
        stats = result['text_stats']
        lines.append(f"  • Символов: {stats['chars']}")
        lines.append(f"  • Слов: {stats['words']}")
        lines.append(f"  • Предложений: {stats['sentences']}")
        lines.append(f"  • Средняя длина предложения: {stats['avg_sentence_length']:.1f} слов")
        lines.append("")
        
        # Уровень риска
        risk_level = result['risk_level']
        risk_icons = {
            'low': '✅',
            'medium': '⚠️',
            'high': '⚠️⚠️',
            'critical': '🚨'
        }
        risk_names = {
            'low': 'НИЗКИЙ',
            'medium': 'СРЕДНИЙ',
            'high': 'ВЫСОКИЙ',
            'critical': 'КРИТИЧЕСКИЙ'
        }
        
        lines.append(f"УРОВЕНЬ РИСКА: {risk_icons.get(risk_level, '?')} {risk_names.get(risk_level, risk_level.upper())}")
        lines.append("")
        
        # Найденные маркеры
        lines.append(f"НАЙДЕНО ПСЕВДОНАУЧНЫХ МАРКЕРОВ: {result['markers_count']}")
        
        if result['category_counts']:
            lines.append("")
            lines.append("По категориям:")
            for category, count in sorted(result['category_counts'].items(), 
                                        key=lambda x: x[1], reverse=True):
                cat_info = RISK_CATEGORIES.get(category, {})
                name = cat_info.get('name_ru', category)
                severity = cat_info.get('severity', 'unknown')
                lines.append(f"  • {name}: {count} (серьёзность: {severity})")
        
        lines.append("")
        lines.append(f"Легитимных медицинских терминов: {result['legitimate_terms_count']}")
        lines.append(f"Слов-амплификаторов: {result['amplifiers_count']}")
        lines.append("")
        
        # Детальная информация
        if 'markers' in result and result['markers']:
            lines.append("=" * 70)
            lines.append("ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О НАЙДЕННЫХ МАРКЕРАХ:")
            lines.append("=" * 70)
            lines.append("")
            
            for i, marker in enumerate(result['markers'], 1):
                cat_info = RISK_CATEGORIES.get(marker['category'], {})
                lines.append(f"{i}. «{marker['text']}»")
                lines.append(f"   Категория: {cat_info.get('name_ru', marker['category'])}")
                lines.append(f"   Серьёзность: {marker['severity']}")
                lines.append(f"   Описание: {marker['description_ru']}")
                lines.append("")
        
        # Рекомендации
        lines.append("=" * 70)
        lines.append("РЕКОМЕНДАЦИИ:")
        lines.append("=" * 70)
        lines.append("")
        
        if risk_level in ['high', 'critical']:
            lines.append("⚠️  ВНИМАНИЕ! Текст содержит множество признаков псевдонаучной информации.")
            lines.append("Рекомендуется:")
            lines.append("  • Проверить источники информации")
            lines.append("  • Обратиться к квалифицированным специалистам")
            lines.append("  • Искать подтверждения в рецензируемых исследованиях")
        elif risk_level == 'medium':
            lines.append("⚠️  Текст содержит некоторые признаки псевдонаучной информации.")
            lines.append("Рекомендуется проявить критическое мышление и проверить факты.")
        else:
            lines.append("✅ Текст не содержит значительных признаков псевдонауки.")
            lines.append("Однако всегда полезно проверять источники информации.")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _generate_html_report(self, result: Dict) -> str:
        """Генерация HTML отчёта"""
        risk_colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'critical': '#dc3545'
        }
        
        risk_color = risk_colors.get(result['risk_level'], '#6c757d')
        
        html = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Отчёт анализа медицинского текста</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    border-bottom: 3px solid {risk_color};
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #555;
                    margin-top: 30px;
                }}
                .risk-level {{
                    font-size: 24px;
                    font-weight: bold;
                    color: {risk_color};
                    padding: 15px;
                    background: {risk_color}22;
                    border-left: 5px solid {risk_color};
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .stat-card {{
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 5px;
                    border-left: 3px solid #007bff;
                }}
                .stat-value {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #007bff;
                }}
                .stat-label {{
                    color: #666;
                    font-size: 14px;
                }}
                .category-list {{
                    list-style: none;
                    padding: 0;
                }}
                .category-item {{
                    padding: 10px;
                    margin: 5px 0;
                    background: #f8f9fa;
                    border-radius: 5px;
                }}
                .severity-high {{ border-left: 4px solid #dc3545; }}
                .severity-medium {{ border-left: 4px solid #ffc107; }}
                .severity-low {{ border-left: 4px solid #28a745; }}
                .marker {{
                    margin: 10px 0;
                    padding: 10px;
                    background: #fff3cd;
                    border-radius: 5px;
                }}
                .recommendations {{
                    background: #e7f3ff;
                    padding: 20px;
                    border-radius: 5px;
                    border-left: 5px solid #007bff;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Отчёт анализа медицинского текста</h1>
                
                <div class="risk-level">
                    Уровень риска: {result['risk_level'].upper()}
                </div>
                
                <h2>📈 Статистика</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">{result['markers_count']}</div>
                        <div class="stat-label">Псевдонаучных маркеров</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{result['text_stats']['words']}</div>
                        <div class="stat-label">Слов в тексте</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{result['legitimate_terms_count']}</div>
                        <div class="stat-label">Легитимных терминов</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{result['amplifiers_count']}</div>
                        <div class="stat-label">Слов-амплификаторов</div>
                    </div>
                </div>
                
                <h2>📋 Категории найденных маркеров</h2>
                <ul class="category-list">
        """
        
        for category, count in sorted(result['category_counts'].items(), 
                                     key=lambda x: x[1], reverse=True):
            cat_info = RISK_CATEGORIES.get(category, {})
            name = cat_info.get('name_ru', category)
            severity = cat_info.get('severity', 'medium')
            html += f"""
                    <li class="category-item severity-{severity}">
                        <strong>{name}</strong>: {count}
                        <br><small>{cat_info.get('description_ru', '')}</small>
                    </li>
            """
        
        html += """
                </ul>
                
                <div class="recommendations">
                    <h2>💡 Рекомендации</h2>
        """
        
        if result['risk_level'] in ['high', 'critical']:
            html += """
                    <p>⚠️ <strong>ВНИМАНИЕ!</strong> Текст содержит множество признаков псевдонаучной информации.</p>
                    <ul>
                        <li>Проверьте источники информации</li>
                        <li>Обратитесь к квалифицированным специалистам</li>
                        <li>Ищите подтверждения в рецензируемых исследованиях</li>
                    </ul>
            """
        elif result['risk_level'] == 'medium':
            html += """
                    <p>⚠️ Текст содержит некоторые признаки псевдонаучной информации.</p>
                    <p>Рекомендуется проявить критическое мышление и проверить факты.</p>
            """
        else:
            html += """
                    <p>✅ Текст не содержит значительных признаков псевдонауки.</p>
                    <p>Однако всегда полезно проверять источники информации.</p>
            """
        
        html += """
                </div>
                
                <p style="text-align: center; color: #999; margin-top: 40px;">
                    <small>Время анализа: {}</small>
                </p>
            </div>
        </body>
        </html>
        """.format(result['timestamp'])
        
        return html
    
    def export_report(self, analysis_result: Dict, filepath: str, 
                     format: str = 'text') -> None:
        """
        Экспорт отчёта в файл
        
        Args:
            analysis_result: Результат анализа
            filepath: Путь к файлу для сохранения
            format: Формат ('text', 'json', 'html')
        """
        report = self.generate_report(analysis_result, format)
        self.text_loader.save_to_file(report, filepath)