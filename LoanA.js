export function register(apiCore) {
    console.log('🧠 Загружается модуль Заимствований А (Dahl)...');

    apiCore.registerAnalysisFunction('detectLoanA', detectLoanA);

    const WORDS = [
        { word: "АВАНГАРД", definition: "Французское: передовая часть войска." },
        { word: "АВАНТЮРА", definition: "Французское: похождение, приключение, сомнительное дело." },
        { word: "АВТОГРАФ", definition: "Греческое: собственноручное письмо или подпись." },
        { word: "АГИТАЦИЯ", definition: "Латинское: возбуждение народа, распространение идей." },
        { word: "АГРЕГАТ", definition: "Латинское: собрание частей в одно целое." },
        { word: "АКАДЕМИЯ", definition: "Греческое: высшее ученое заведение." },
        { word: "АЛЛЕГОРИЯ", definition: "Греческое: иносказание, выражение понятия в образе." },
        { word: "АРХИВ", definition: "Греческое: место хранения старых дел и документов." }
    ];

    function detectLoanA(text) {
        const sample = text.toLowerCase();
        const found = WORDS.filter(item => sample.includes(item.word.toLowerCase()));
        
        if (found.length > 0) {
            return {
                type: "Заимствования А",
                confidence: Math.min(found.length * 0.2, 0.95),
                foundWords: found.map(f => f.word)
            };
        }
        return null;
    }

    console.log('✅ Модуль Заимствований А зарегистрирован!');
}
