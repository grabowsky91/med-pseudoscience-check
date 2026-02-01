"""
Словари псевдонаучных маркеров для анализа медицинских текстов
"""

# Псевдонаучные термины и фразы
PSEUDOSCIENCE_MARKERS = {
    "russian": {
        "miracle_claims": [
            r"чудо[-\s]?средство",
            r"чудо[-\s]?препарат",
            r"чудодейственн\w+",
            r"волшебн\w+ эффект",
            r"магическ\w+ формула",
            r"революционн\w+ прорыв",
            r"сенсационн\w+ открытие",
        ],
        "guarantees": [
            r"100%\s*гарантия",
            r"абсолютн\w+ гарантия",
            r"гарантирован\w+ результат",
            r"гарантирован\w+ излечение",
            r"полностью излечива\w+",
            r"навсегда избав\w+",
        ],
        "detox": [
            r"детокс",
            r"очищение организма",
            r"вывод токсинов",
            r"шлак\w+",
            r"чистка организма",
            r"очистка от токсинов",
        ],
        "energy": [
            r"энергетическ\w+ поле",
            r"биоэнергетика",
            r"квантов\w+ энергия",
            r"космическ\w+ энергия",
            r"энергетическ\w+ баланс",
            r"энергоинформационн\w+",
        ],
        "natural": [
            r"100%\s*натуральн\w+",
            r"исключительно натуральн\w+",
            r"только природн\w+ компоненты",
            r"без химии",
            r"экологически чист\w+",
        ],
        "fast_results": [
            r"за\s+\d+\s+дн\w+",
            r"мгновенн\w+ результат",
            r"немедленн\w+ эффект",
            r"быстр\w+ излечение",
            r"в\s+считанные\s+\w+",
        ],
        "universal": [
            r"от всех болезней",
            r"универсальн\w+ средство",
            r"лечит всё",
            r"помогает при любых",
            r"панацея",
        ],
        "unproven": [
            r"не признаётся официальной медициной",
            r"скрывается врачами",
            r"тайна фармацевт\w+",
            r"секретн\w+ методика",
            r"древн\w+ знания",
            r"тибетск\w+ медицина",
        ],
        "emotional": [
            r"спасёт вашу жизнь",
            r"не упустите шанс",
            r"последняя надежда",
            r"единственн\w+ способ",
            r"врачи в шоке",
            r"медики скрывают",
        ],
        "testimonials": [
            r"тысячи довольных",
            r"миллионы людей",
            r"все пациенты довольны",
            r"отзывы потрясающие",
            r"никто не пожалел",
        ],
    },
    "english": {
        "miracle_claims": [
            r"miracle\s+cure",
            r"miracle\s+drug",
            r"wonder\s+drug",
            r"magical\s+formula",
            r"revolutionary\s+breakthrough",
            r"breakthrough\s+discovery",
        ],
        "guarantees": [
            r"100%\s*guaranteed",
            r"guaranteed\s+results",
            r"guaranteed\s+cure",
            r"complete\s+cure",
            r"forever\s+cure",
        ],
        "detox": [
            r"detox",
            r"cleanse",
            r"flush\s+toxins",
            r"remove\s+toxins",
            r"body\s+cleanse",
        ],
        "energy": [
            r"energy\s+field",
            r"quantum\s+energy",
            r"cosmic\s+energy",
            r"energy\s+balance",
        ],
        "natural": [
            r"100%\s*natural",
            r"all[-\s]natural",
            r"purely\s+natural",
            r"chemical[-\s]free",
        ],
        "fast_results": [
            r"instant\s+results",
            r"immediate\s+effect",
            r"in\s+\d+\s+days",
            r"overnight\s+cure",
        ],
        "universal": [
            r"cures\s+everything",
            r"universal\s+remedy",
            r"panacea",
        ],
        "unproven": [
            r"not\s+recognized\s+by",
            r"hidden\s+by\s+doctors",
            r"big\s+pharma\s+secret",
            r"ancient\s+wisdom",
        ],
        "emotional": [
            r"save\s+your\s+life",
            r"don't\s+miss",
            r"last\s+hope",
            r"only\s+way",
            r"doctors\s+shocked",
        ],
        "testimonials": [
            r"thousands\s+satisfied",
            r"millions\s+of\s+people",
            r"all\s+patients\s+satisfied",
        ],
    },
}

# Категории рисков
RISK_CATEGORIES = {
    "miracle_claims": {
        "name_ru": "Чудодейственные утверждения",
        "name_en": "Miracle claims",
        "severity": "high",
        "description_ru": "Необоснованные обещания чудесного исцеления",
        "description_en": "Unsubstantiated promises of miraculous healing",
    },
    "guarantees": {
        "name_ru": "Абсолютные гарантии",
        "name_en": "Absolute guarantees",
        "severity": "high",
        "description_ru": "100% гарантии результата без доказательств",
        "description_en": "100% result guarantees without evidence",
    },
    "detox": {
        "name_ru": "Детокс-мифы",
        "name_en": "Detox myths",
        "severity": "medium",
        "description_ru": "Необоснованные утверждения об очищении организма",
        "description_en": "Unsubstantiated cleansing claims",
    },
    "energy": {
        "name_ru": "Энергетические псевдоконцепции",
        "name_en": "Energy pseudoconcepts",
        "severity": "high",
        "description_ru": "Ссылки на несуществующие энергетические поля",
        "description_en": "References to non-existent energy fields",
    },
    "natural": {
        "name_ru": "Натуральность как гарантия",
        "name_en": "Natural as guarantee",
        "severity": "low",
        "description_ru": "Ошибочное представление о безопасности натурального",
        "description_en": "Misconception about natural safety",
    },
    "fast_results": {
        "name_ru": "Мгновенные результаты",
        "name_en": "Instant results",
        "severity": "medium",
        "description_ru": "Нереалистичные сроки лечения",
        "description_en": "Unrealistic treatment timeframes",
    },
    "universal": {
        "name_ru": "Универсальные средства",
        "name_en": "Universal remedies",
        "severity": "high",
        "description_ru": "Утверждения о лечении всех болезней",
        "description_en": "Claims of curing all diseases",
    },
    "unproven": {
        "name_ru": "Непризнанные методы",
        "name_en": "Unproven methods",
        "severity": "high",
        "description_ru": "Ссылки на секретные или непризнанные методы",
        "description_en": "References to secret or unrecognized methods",
    },
    "emotional": {
        "name_ru": "Эмоциональная манипуляция",
        "name_en": "Emotional manipulation",
        "severity": "high",
        "description_ru": "Давление на эмоции и страхи пациентов",
        "description_en": "Pressure on patient emotions and fears",
    },
    "testimonials": {
        "name_ru": "Массовые отзывы",
        "name_en": "Mass testimonials",
        "severity": "medium",
        "description_ru": "Необоснованные утверждения о массовой эффективности",
        "description_en": "Unsubstantiated mass efficacy claims",
    },
}

# Медицинские термины, которые НЕ являются псевдонаукой
LEGITIMATE_MEDICAL_TERMS = {
    "russian": [
        r"клиническ\w+ исследования",
        r"рандомизированн\w+ контролируем\w+",
        r"доказательн\w+ медицина",
        r"плацебо[-\s]контролируем\w+",
        r"мета[-\s]анализ",
        r"систематическ\w+ обзор",
        r"peer[-\s]review",
        r"рецензируем\w+ журнал",
    ],
    "english": [
        r"clinical\s+trial",
        r"randomized\s+controlled",
        r"evidence[-\s]based",
        r"placebo[-\s]controlled",
        r"meta[-\s]analysis",
        r"systematic\s+review",
        r"peer[-\s]reviewed",
    ],
}

# Слова-усилители, которые часто используются в псевдонаучных текстах
AMPLIFIERS = {
    "russian": [
        "абсолютно", "полностью", "совершенно", "исключительно",
        "невероятно", "поразительно", "удивительно", "феноменально",
    ],
    "english": [
        "absolutely", "completely", "totally", "exclusively",
        "incredibly", "amazingly", "astonishingly", "phenomenally",
    ],
}


def get_all_patterns(language="russian"):
    """
    Получить все паттерны для указанного языка
    
    Args:
        language: Язык ('russian' или 'english')
    
    Returns:
        Словарь всех паттернов по категориям
    """
    if language not in PSEUDOSCIENCE_MARKERS:
        raise ValueError(f"Язык '{language}' не поддерживается")
    
    return PSEUDOSCIENCE_MARKERS[language]


def get_risk_level(category_counts):
    """
    Определить общий уровень риска на основе найденных маркеров
    
    Args:
        category_counts: Словарь с количеством маркеров по категориям
    
    Returns:
        Уровень риска: 'low', 'medium', 'high', 'critical'
    """
    total_markers = sum(category_counts.values())
    high_severity_count = sum(
        count for cat, count in category_counts.items()
        if RISK_CATEGORIES.get(cat, {}).get("severity") == "high"
    )
    
    if total_markers == 0:
        return "low"
    elif high_severity_count >= 3 or total_markers >= 10:
        return "critical"
    elif high_severity_count >= 1 or total_markers >= 5:
        return "high"
    elif total_markers >= 2:
        return "medium"
    else:
        return "low"