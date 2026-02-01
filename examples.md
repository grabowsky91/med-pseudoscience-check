# Примеры использования MED-PSEUDOSCIENCE-CHECK

## Пример 1: Интерактивный режим

```bash
python app.py
```

Вводите текст:
```
Наше чудо-средство на основе квантовой энергии 100% гарантирует 
полное очищение организма от токсинов за 3 дня! Врачи в шоке!
```

## Пример 2: Анализ файла

```bash
python app.py --file article.txt
```

## Пример 3: Экспорт в HTML

```bash
python app.py --file article.txt --output report.html --format html
```

## Пример 4: Веб-интерфейс

```bash
python app.py --web
```

Откройте: http://localhost:5000

## Примеры текстов для тестирования

### Текст с высоким риском псевдонауки:
```
Революционное чудо-средство на основе квантовой энергии и древних 
тибетских знаний! 100% гарантия полного излечения от всех болезней 
за 3 дня! Врачи скрывают эту информацию! Полное очищение организма 
от токсинов и шлаков. Тысячи довольных пациентов! Не упустите 
последний шанс спасти свою жизнь!
```

### Текст с низким риском:
```
Согласно рандомизированному контролируемому исследованию, 
опубликованному в рецензируемом журнале, новый препарат показал 
статистически значимое улучшение у 60% пациентов. Исследование 
проводилось с использованием методов доказательной медицины и 
плацебо-контроля.
```

## Программное использование

### Python API:

```python
from analyzer import PseudoscienceAnalyzer

# Создание анализатора
analyzer = PseudoscienceAnalyzer(language='russian')

# Анализ текста
text = "Ваш текст для анализа..."
result = analyzer.analyze_text(text)

# Печать отчёта
print(analyzer.generate_report(result, format='text'))

# Экспорт в файл
analyzer.export_report(result, 'report.html', format='html')
```

### Пакетная обработка:

```python
from analyzer import PseudoscienceAnalyzer
from pathlib import Path

analyzer = PseudoscienceAnalyzer(language='russian')

# Обработка всех .txt файлов в папке
for file_path in Path('articles').glob('*.txt'):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    result = analyzer.analyze_text(text)
    
    # Сохранение отчёта
    output_path = file_path.with_suffix('.html')
    analyzer.export_report(result, output_path, format='html')
    
    print(f"Обработан: {file_path.name} -> {output_path.name}")
```