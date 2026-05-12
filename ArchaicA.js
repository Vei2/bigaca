export function register(apiCore) {
    console.log('🧠 Загружается модуль Книжных слов А (Dahl)...');

    apiCore.registerAnalysisFunction('detectArchaicA', detectArchaicA);

    const WORDS = [
        { word: "АБДИКАЦИЯ", definition: "Сложение с себя власти, прав; отречение от престола." },
        { word: "АВАНПОСТ", definition: "Передовой пост, стража впереди войска." },
        { word: "АДАМАНТ", definition: "Старинное название алмаза; нечто крайне твердое." },
        { word: "АДЪЮНКТ", definition: "Помощник или заместитель в ученых заведениях." },
        { word: "АЗБУКОВНИК", definition: "Старинный рукописный сборник энциклопедического содержания." },
        { word: "АКЦИДЕНЦИЯ", definition: "Случайный доход, побочная прибыль при должности." },
        { word: "АЛКАНИЕ", definition: "Сильное желание, жажда чего-либо; голод." },
        { word: "АМБИЦИЯ", definition: "Честолюбие, гордость, требование почтения." }
    ];

    function detectArchaicA(text) {
        const sample = text.toLowerCase();
        const found = WORDS.filter(item => sample.includes(item.word.toLowerCase()));
        
        if (found.length > 0) {
            return {
                type: "Книжные А",
                confidence: Math.min(found.length * 0.2, 0.95),
                foundWords: found.map(f => f.word)
            };
        }
        return null;
    }

    console.log('✅ Модуль Книжных слов А зарегистрирован!');
}
