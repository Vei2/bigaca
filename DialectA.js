export function register(apiCore) {
    console.log('🧠 Загружается модуль Диалектов А (Dahl)...');

    apiCore.registerAnalysisFunction('detectDialectA', detectDialectA);

    const WORDS = [
        { word: "АБАНАТ", definition: "Псковское: упрямец, своевольник, неуступчивый человек." },
        { word: "АБАТУР", definition: "Рязанское, владимирское: упрямец, неслух; наглец, нахал." },
        { word: "АБНЯ", definition: "Тверское: ловушка на рыбу, плетеный из прутьев сак." },
        { word: "АБО", definition: "Южное, западное: или, либо; а то, иначе." },
        { word: "АБУТОР", definition: "Вологодское: обжора, ненасытный человек." },
        { word: "АВДАН-СЫРЫ", definition: "Оренбургское: беспорядок, суматоха, суета." },
        { word: "АГЛЕНЬ", definition: "Архангельское: ленивый человек, бездельник." },
        { word: "АГОВЕТЬ", definition: "Южное: угомониться, притихнуть, успокоиться." }
    ];

    function detectDialectA(text) {
        const sample = text.toLowerCase();
        const found = WORDS.filter(item => sample.includes(item.word.toLowerCase()));
        
        if (found.length > 0) {
            return {
                type: "Диалекты А",
                confidence: Math.min(found.length * 0.2, 0.95),
                foundWords: found.map(f => f.word)
            };
        }
        return null;
    }

    console.log('✅ Модуль Диалектов А зарегистрирован!');
}
