export function register(apiCore) {
    console.log('🧠 Загружается модуль Существительных А (Dahl)...');

    apiCore.registerAnalysisFunction('detectNounsA', detectNounsA);
    apiCore.registerUtilityFunction('isKnownNounA', isKnownNounA);

    const WORDS = [
        { word: "АЗ", definition: "Первая буква русской азбуки. Писать азы (буквы), сидеть на азах (начинать науку)." },
        { word: "АБАКА", definition: "Зодческий термин: верхняя плита на капители колонны." },
        { word: "АБРИС", definition: "Контур, очерк, обвод, наброска, очертание." },
        { word: "АББАТ", definition: "Настоятель римско-католического монастыря." },
        { word: "АВВА", definition: "Церковное слово. Отец; Создатель, Бог; архимандрит, настоятель." },
        { word: "АДВОКАТ", definition: "Присяжный поверенный, правовед, берущий на себя ведение тяжб." },
        { word: "АДЕНОЛОГИЯ", definition: "Анатомическая наука о железах в животном теле." },
        { word: "АДЕПТ", definition: "Вновь принятый в братство, в тайное учение или общество." },
        { word: "АВГИТ", definition: "Ископаемое из рода пироксена." },
        { word: "АВГУСТ", definition: "Восьмой месяц года." },
        { word: "АВОСЬ", definition: "Надежда на удачу, случай." },
        { word: "АЛМАЗ", definition: "Драгоценный камень, чистый углерод." },
        { word: "АЛТАРЬ", definition: "Жертвенник, место приношения жертвы." },
        { word: "АМБАР", definition: "Холодное строение для хранения хлеба в зерне." },
        { word: "АНГЕЛ", definition: "Бесплотная сила, вестник Божий." },
        { word: "АПТЕКА", definition: "Место хранения и продажи лекарств." },
        { word: "АРТЕЛЬ", definition: "Товарищество, община для совместной работы." },
        { word: "АТАМАН", definition: "Предводитель, начальник вольницы или казаков." }
    ];

    function detectNounsA(text) {
        const sample = text.toLowerCase();
        const found = WORDS.filter(item => sample.includes(item.word.toLowerCase()));
        
        if (found.length > 0) {
            return {
                type: "Существительные А",
                confidence: Math.min(found.length * 0.2, 0.95),
                foundWords: found.map(f => f.word)
            };
        }
        return null;
    }

    function isKnownNounA(word) {
        return WORDS.some(item => item.word.toLowerCase() === word.toLowerCase());
    }

    console.log('✅ Модуль Существительных А зарегистрирован!');
}
