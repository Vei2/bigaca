export function register(apiCore) {
    console.log('🧠 Загружается модуль Человека А (Dahl)...');

    apiCore.registerAnalysisFunction('detectHumanA', detectHumanA);

    const WORDS = [
        { word: "АБОРДАЖ", definition: "Сцепка кораблей для рукопашного боя." },
        { word: "АВТОР", definition: "Творец, сочинитель, создатель какого-либо произведения." },
        { word: "АГЕНТ", definition: "Уполномоченный, делец, лицо, действующее по поручению." },
        { word: "АКРОБАТ", definition: "Плясун на канате, ловкий гимнаст." },
        { word: "АКТЕР", definition: "Лицедей, представляющий на сцене разные лица." },
        { word: "АКУШЕР", definition: "Врач или помощник при родах." },
        { word: "АПТЕКАРЬ", definition: "Лицо, заведующее аптекой и приготовлением лекарств." },
        { word: "АРХИТЕКТОР", definition: "Зодчий, строитель зданий." }
    ];

    function detectHumanA(text) {
        const sample = text.toLowerCase();
        const found = WORDS.filter(item => sample.includes(item.word.toLowerCase()));
        
        if (found.length > 0) {
            return {
                type: "Человек А",
                confidence: Math.min(found.length * 0.2, 0.95),
                foundWords: found.map(f => f.word)
            };
        }
        return null;
    }

    console.log('✅ Модуль Человека А зарегистрирован!');
}
