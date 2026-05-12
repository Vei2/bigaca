export function register(apiCore) {
    console.log('🧠 Загружается модуль Прилагательных А (Dahl)...');

    apiCore.registerAnalysisFunction('detectAdjectivesA', detectAdjectivesA);

    const WORDS = [
        { word: "АБСОЛЮТНЫЙ", definition: "Отрешенный, безграничный, безусловный, безотносительный, непременный." },
        { word: "АБСТРАКТНЫЙ", definition: "Отвлеченный, мысленный, не вещественный." },
        { word: "АЛЫЙ", definition: "Ярко-красный, цвета крови, зари." },
        { word: "АВСТРАЛЬНЫЙ", definition: "Южный, к южному полюсу относящийся." },
        { word: "АЗОВЫЙ", definition: "К букве 'аз' относящийся." },
        { word: "АЗБУЧНЫЙ", definition: "К азбуке относящийся; начальный, простой." },
        { word: "АЙВОВЫЙ", definition: "Из айвы приготовленный." },
        { word: "АКВАМАРИНОВЫЙ", definition: "Цвета морской воды, зеленовато-голубой." },
        { word: "АЛМАЗНЫЙ", definition: "Из алмаза состоящий; блестящий, твердый." },
        { word: "АЛТАРНЫЙ", definition: "К алтарю относящийся." },
        { word: "АЛЧНЫЙ", definition: "Жадный, корыстный, страстно желающий чего-либо." },
        { word: "АМБАРНЫЙ", definition: "К амбару относящийся." },
        { word: "АНГЕЛЬСКИЙ", definition: "Свойственный ангелу; чистый, кроткий." },
        { word: "АПРЕЛЬСКИЙ", definition: "К апрелю месяцу относящийся." },
        { word: "АПТЕЧНЫЙ", definition: "К аптеке относящийся." },
        { word: "АРТЕЛЬНЫЙ", definition: "К артели принадлежащий." },
        { word: "АРХИЕРЕЙСКИЙ", definition: "К архиерею относящийся." }
    ];

    function detectAdjectivesA(text) {
        const sample = text.toLowerCase();
        const found = WORDS.filter(item => sample.includes(item.word.toLowerCase()));
        
        if (found.length > 0) {
            return {
                type: "Прилагательные А",
                confidence: Math.min(found.length * 0.2, 0.95),
                foundWords: found.map(f => f.word)
            };
        }
        return null;
    }

    console.log('✅ Модуль Прилагательных А зарегистрирован!');
}
