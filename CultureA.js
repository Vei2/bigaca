export function register(apiCore) {
    console.log('🧠 Загружается модуль Культуры А (Dahl)...');

    apiCore.registerAnalysisFunction('detectCultureA', detectCultureA);

    const WORDS = [
        { word: "АВВА", definition: "Религиозная традиция: отец, Создатель; настоятель монастыря." },
        { word: "АВВАКУМОВЩИНА", definition: "Старообрядческий обряд и толк, связанный с расколом русской церкви." },
        { word: "АРТЕЛЬ", definition: "Традиционная форма коллективного труда и взаимопомощи." },
        { word: "АТАМАН", definition: "Культура казачества: выборный предводитель, символ вольности." },
        { word: "АРШИН", definition: "Традиционная русская мера длины, укоренившаяся в обычаях." },
        { word: "АЛТЫН", definition: "Старинная денежная единица, отражающая традиции допетровской Руси." },
        { word: "АМУЛЕТ", definition: "Народная магия и суеверия: оберег, защищающий от несчастий." },
        { word: "АИСТ", definition: "Фольклорный символ семейного счастья и плодородия." },
        { word: "АВОСЬ", definition: "Надежда на случай и удачу, часть национального характера." },
        { word: "АЗБУКА", definition: "Символ просвещения и начало всякого учения в русской традиции." }
    ];

    function detectCultureA(text) {
        const sample = text.toLowerCase();
        const found = WORDS.filter(item => sample.includes(item.word.toLowerCase()));
        
        if (found.length > 0) {
            return {
                type: "Культура А",
                confidence: Math.min(found.length * 0.2, 0.95),
                foundWords: found.map(f => f.word)
            };
        }
        return null;
    }

    console.log('✅ Модуль Культуры А зарегистрирован!');
}
