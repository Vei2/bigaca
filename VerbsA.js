export function register(apiCore) {
    console.log('🧠 Загружается модуль Глаголов А (Dahl)...');

    apiCore.registerAnalysisFunction('detectVerbsA', detectVerbsA);

    const WORDS = [
        { word: "АКАТЬ", definition: "Произносить букву 'а' вместо 'о' без ударения." },
        { word: "АУКАТЬ", definition: "Кричать 'ау', звать кого-либо в лесу." },
        { word: "АХАТЬ", definition: "Издавать восклицание 'ах'; выражать удивление." },
        { word: "АБСТРАГИРОВАТЬ", definition: "Мысленно выделять свойства или признаки предмета." },
        { word: "АДАПТИРОВАТЬ", definition: "Приспосабливать, делать годным для чего-либо." },
        { word: "АДРЕСОВАТЬ", definition: "Направлять письмо, вещь или слова кому-либо." },
        { word: "АККОМПАНИРОВАТЬ", definition: "Сопровождать музыкой пение или игру." },
        { word: "АВАНСИРОВАТЬ", definition: "Давать аванс, деньги вперед." },
        { word: "АГИТИРОВАТЬ", definition: "Побуждать к какой-либо деятельности." },
        { word: "АНАЛИЗИРОВАТЬ", definition: "Разбирать, рассматривать части целого." },
        { word: "АРЕСТОВАТЬ", definition: "Лишать свободы, задерживать по закону." },
        { word: "АТАКОВАТЬ", definition: "Нападать на неприятеля." }
    ];

    function detectVerbsA(text) {
        const sample = text.toLowerCase();
        const found = WORDS.filter(item => sample.includes(item.word.toLowerCase()));
        
        if (found.length > 0) {
            return {
                type: "Глаголы А",
                confidence: Math.min(found.length * 0.2, 0.95),
                foundWords: found.map(f => f.word)
            };
        }
        return null;
    }

    console.log('✅ Модуль Глаголов А зарегистрирован!');
}
