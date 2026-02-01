#!/usr/bin/env python3
"""
MED-PSEUDOSCIENCE-CHECK
Приложение для анализа медицинских текстов на псевдонаучные утверждения
"""

import sys
import argparse
from pathlib import Path

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

from analyzer import PseudoscienceAnalyzer
from textloader import TextLoader


def print_header():
    """Вывод заголовка приложения"""
    if COLORAMA_AVAILABLE:
        print(Fore.CYAN + Style.BRIGHT + """
╔═══════════════════════════════════════════════════════════════╗
║           MED-PSEUDOSCIENCE-CHECK v1.0                       ║
║   Анализатор медицинских текстов на псевдонауку             ║
╚═══════════════════════════════════════════════════════════════╝
        """ + Style.RESET_ALL)
    else:
        print("""
===============================================================
          MED-PSEUDOSCIENCE-CHECK v1.0
  Анализатор медицинских текстов на псевдонауку
===============================================================
        """)


def analyze_text_interactive():
    """Интерактивный режим анализа текста"""
    print("\n📝 РЕЖИМ АНАЛИЗА ТЕКСТА")
    print("=" * 60)
    
    # Выбор языка
    print("\nВыберите язык текста:")
    print("1. Русский")
    print("2. English")
    
    lang_choice = input("\nВаш выбор (1/2): ").strip()
    language = 'russian' if lang_choice == '1' else 'english'
    
    # Ввод текста
    print("\n" + "=" * 60)
    print("Введите или вставьте текст для анализа.")
    print("Для завершения ввода введите пустую строку и нажмите Enter.")
    print("=" * 60 + "\n")
    
    lines = []
    while True:
        try:
            line = input()
            if not line:
                break
            lines.append(line)
        except EOFError:
            break
    
    text = '\n'.join(lines)
    
    if not text.strip():
        print("\n❌ Текст не может быть пустым!")
        return
    
    # Анализ
    print("\n⏳ Анализирую текст...\n")
    
    analyzer = PseudoscienceAnalyzer(language=language)
    result = analyzer.analyze_text(text, detailed=True)
    
    # Вывод результата
    report = analyzer.generate_report(result, format='text')
    print(report)
    
    # Предложение сохранить отчёт
    save = input("\n💾 Сохранить отчёт в файл? (y/n): ").strip().lower()
    if save == 'y':
        format_choice = input("Выберите формат (text/html/json): ").strip().lower()
        if format_choice not in ['text', 'html', 'json']:
            format_choice = 'text'
        
        ext = 'txt' if format_choice == 'text' else format_choice
        filename = f"report_{result['timestamp'].replace(':', '-').split('.')[0]}.{ext}"
        
        analyzer.export_report(result, filename, format=format_choice)
        print(f"✅ Отчёт сохранён: {filename}")


def analyze_file(filepath: str, output: str = None, format: str = 'text'):
    """
    Анализ текста из файла
    
    Args:
        filepath: Путь к файлу
        output: Путь для сохранения отчёта (опционально)
        format: Формат отчёта
    """
    print(f"\n📄 Анализ файла: {filepath}")
    print("=" * 60)
    
    loader = TextLoader()
    
    try:
        text = loader.load_from_file(filepath)
    except Exception as e:
        print(f"❌ Ошибка загрузки файла: {e}")
        return
    
    # Автоопределение языка
    detected_lang = loader.detect_language(text)
    language = detected_lang if detected_lang != 'unknown' else 'russian'
    
    print(f"📊 Обнаружен язык: {detected_lang}")
    print(f"⏳ Анализирую текст...\n")
    
    analyzer = PseudoscienceAnalyzer(language=language)
    result = analyzer.analyze_text(text, detailed=True)
    
    # Вывод результата
    report = analyzer.generate_report(result, format='text')
    print(report)
    
    # Сохранение отчёта
    if output:
        analyzer.export_report(result, output, format=format)
        print(f"\n✅ Отчёт сохранён: {output}")
    else:
        # Автоматическое сохранение рядом с исходным файлом
        input_path = Path(filepath)
        ext = 'txt' if format == 'text' else format
        output_path = input_path.parent / f"{input_path.stem}_report.{ext}"
        
        analyzer.export_report(result, str(output_path), format=format)
        print(f"\n✅ Отчёт сохранён: {output_path}")


def run_web_interface():
    """Запуск веб-интерфейса"""
    try:
        from flask import Flask, render_template_string, request, jsonify
    except ImportError:
        print("❌ Flask не установлен. Установите: pip install flask")
        return
    
    app = Flask(__name__)
    
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MED-PSEUDOSCIENCE-CHECK</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 30px;
                text-align: center;
            }
            h1 {
                color: #667eea;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                font-size: 16px;
            }
            .main-content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
            .card {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .card h2 {
                color: #667eea;
                margin-bottom: 15px;
            }
            textarea {
                width: 100%;
                min-height: 300px;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 14px;
                font-family: 'Courier New', monospace;
                resize: vertical;
            }
            textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            .controls {
                display: flex;
                gap: 10px;
                margin-top: 15px;
            }
            select, button {
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.3s;
            }
            select {
                background: #f5f5f5;
                flex: 1;
            }
            button {
                background: #667eea;
                color: white;
                font-weight: bold;
                flex: 2;
            }
            button:hover {
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }
            .result {
                margin-top: 20px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                border-left: 5px solid #667eea;
            }
            .risk-indicator {
                display: inline-block;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                margin: 10px 0;
            }
            .risk-low { background: #d4edda; color: #155724; }
            .risk-medium { background: #fff3cd; color: #856404; }
            .risk-high { background: #f8d7da; color: #721c24; }
            .risk-critical { background: #dc3545; color: white; }
            .stats {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
                margin-top: 15px;
            }
            .stat-item {
                background: white;
                padding: 10px;
                border-radius: 8px;
                text-align: center;
            }
            .stat-value {
                font-size: 24px;
                font-weight: bold;
                color: #667eea;
            }
            .stat-label {
                font-size: 12px;
                color: #666;
            }
            .loading {
                display: none;
                text-align: center;
                margin: 20px 0;
            }
            .loading.active {
                display: block;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            @media (max-width: 768px) {
                .main-content {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔬 MED-PSEUDOSCIENCE-CHECK</h1>
                <p class="subtitle">Анализатор медицинских текстов на псевдонаучные утверждения</p>
            </div>
            
            <div class="main-content">
                <div class="card">
                    <h2>📝 Введите текст</h2>
                    <textarea id="inputText" placeholder="Вставьте текст медицинской статьи или поста для анализа..."></textarea>
                    <div class="controls">
                        <select id="language">
                            <option value="russian">🇷🇺 Русский</option>
                            <option value="english">🇬🇧 English</option>
                        </select>
                        <button id="analyzeBtn" onclick="analyzeText()">Анализировать</button>
                    </div>
                </div>
                
                <div class="card">
                    <h2>📊 Результаты анализа</h2>
                    <div id="results">
                        <p style="color: #999; text-align: center; padding: 50px 0;">
                            Введите текст и нажмите "Анализировать"
                        </p>
                    </div>
                    <div class="loading" id="loading">
                        <div class="spinner"></div>
                        <p style="margin-top: 10px; color: #666;">Анализируем текст...</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            async function analyzeText() {
                const text = document.getElementById('inputText').value;
                const language = document.getElementById('language').value;
                const resultsDiv = document.getElementById('results');
                const loadingDiv = document.getElementById('loading');
                const analyzeBtn = document.getElementById('analyzeBtn');
                
                if (!text.trim()) {
                    alert('Пожалуйста, введите текст для анализа');
                    return;
                }
                
                analyzeBtn.disabled = true;
                loadingDiv.classList.add('active');
                resultsDiv.innerHTML = '';
                
                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ text, language })
                    });
                    
                    const result = await response.json();
                    
                    if (result.error) {
                        resultsDiv.innerHTML = `<p style="color: red;">❌ Ошибка: ${result.error}</p>`;
                    } else {
                        displayResults(result);
                    }
                } catch (error) {
                    resultsDiv.innerHTML = `<p style="color: red;">❌ Ошибка: ${error.message}</p>`;
                } finally {
                    analyzeBtn.disabled = false;
                    loadingDiv.classList.remove('active');
                }
            }
            
            function displayResults(result) {
                const resultsDiv = document.getElementById('results');
                
                const riskClasses = {
                    'low': 'risk-low',
                    'medium': 'risk-medium',
                    'high': 'risk-high',
                    'critical': 'risk-critical'
                };
                
                const riskNames = {
                    'low': 'НИЗКИЙ',
                    'medium': 'СРЕДНИЙ',
                    'high': 'ВЫСОКИЙ',
                    'critical': 'КРИТИЧЕСКИЙ'
                };
                
                let html = `
                    <div class="result">
                        <h3>Уровень риска</h3>
                        <div class="risk-indicator ${riskClasses[result.risk_level]}">
                            ${riskNames[result.risk_level]}
                        </div>
                        
                        <div class="stats">
                            <div class="stat-item">
                                <div class="stat-value">${result.markers_count}</div>
                                <div class="stat-label">Маркеров найдено</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${result.text_stats.words}</div>
                                <div class="stat-label">Слов в тексте</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${result.legitimate_terms_count}</div>
                                <div class="stat-label">Легитимных терминов</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${result.amplifiers_count}</div>
                                <div class="stat-label">Амплификаторов</div>
                            </div>
                        </div>
                        
                        ${result.language_warning ? `<p style="color: orange; margin-top: 10px;">⚠️ ${result.language_warning}</p>` : ''}
                    </div>
                `;
                
                if (Object.keys(result.category_counts).length > 0) {
                    html += '<div class="result"><h3>Категории маркеров</h3><ul>';
                    for (const [category, count] of Object.entries(result.category_counts)) {
                        html += `<li><strong>${category}</strong>: ${count}</li>`;
                    }
                    html += '</ul></div>';
                }
                
                resultsDiv.innerHTML = html;
            }
        </script>
    </body>
    </html>
    """
    
    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/analyze', methods=['POST'])
    def analyze():
        try:
            data = request.json
            text = data.get('text', '')
            language = data.get('language', 'russian')
            
            if not text:
                return jsonify({'error': 'Текст не может быть пустым'}), 400
            
            analyzer = PseudoscienceAnalyzer(language=language)
            result = analyzer.analyze_text(text, detailed=False)
            
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    print("\n🌐 Запуск веб-сервера...")
    print("📱 Откройте браузер: http://localhost:5000")
    print("⚠️  Нажмите Ctrl+C для остановки\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)


def main():
    """Главная функция приложения"""
    parser = argparse.ArgumentParser(
        description='MED-PSEUDOSCIENCE-CHECK - Анализатор медицинских текстов на псевдонауку'
    )
    parser.add_argument('--file', type=str, help='Путь к файлу для анализа')
    parser.add_argument('--output', type=str, help='Путь для сохранения отчёта')
    parser.add_argument('--format', choices=['text', 'html', 'json'], 
                       default='text', help='Формат отчёта')
    parser.add_argument('--web', action='store_true', help='Запустить веб-интерфейс')
    
    args = parser.parse_args()
    
    print_header()
    
    if args.web:
        run_web_interface()
    elif args.file:
        analyze_file(args.file, args.output, args.format)
    else:
        # Интерактивный режим
        analyze_text_interactive()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Работа завершена. До встречи!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)