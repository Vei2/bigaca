export function register(apiCore) {
    console.log('🧠 Загружается модуль Наречий А (Dahl)...');

    apiCore.registerAnalysisFunction('detectAdverbsA', detectAdverbsA);

    const WORDS = [
        { word: "АГА", definition: "Выражение догадки, торжества или согласия." },
        { word: "АБСОЛЮТНО", definition: "Совершенно, вполне, безусловно." },
        { word: "АВОСЬ", definition: "Может быть, станется, сбудется (в значении наречия надежды)." },
        { word: "АЖ", definition: "Даже, так что, до того что (усилительное)." },
        { word: "АККУРАТНО", definition: "Точно, исправно, опрятно." },
        { word: "АЛЧНО", definition: "Жадно, с большой страстью." },
        { word: "АЛЫМ-АЛО", definition: "Совершенно ало, очень красно." },
        { word: "АМИНЬ", definition: "Истинно, верно; конец, запечатано." },
        { word: "АН", definition: "А вот, а вместо того, напротив." },
        { word: "АПАТИЧНО", definition: "Бесчувственно, равнодушно." },
        { word: "АРТЕЛЬНО", definition: "Сообща, всей артелью." },
        { word: "АХ", definition: "Восклицание удивления, испуга, боли." }
    ];

    function detectAdverbsA(text) {
        const sample = text.toLowerCase();
        const found = WORDS.filter(item => sample.includes(item.word.toLowerCase()));
        
        if (found.length > 0) {
            return {
                type: "Наречия А",
                confidence: Math.min(found.length * 0.2, 0.95),
                foundWords: found.map(f => f.word)
            };
        }
        return null;
    }

    console.log('✅ Модуль Наречий А зарегистрирован!');
}
