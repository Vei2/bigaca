export function register(apiCore) {
    console.log('🧠 Загружается модуль Природы А (Dahl)...');

    apiCore.registerAnalysisFunction('detectNatureA', detectNatureA);

    const WORDS = [
        { word: "АИСТ", definition: "Крупная перелетная птица; символ семейного счастья." },
        { word: "АЙВА", definition: "Дерево и плод Cydonia; садовое дерево с терпкими плодами." },
        { word: "АКАЦИЯ", definition: "Дерево или кустарник из семейства бобовых с душистыми цветами." },
        { word: "АЛОЭ", definition: "Столетник, горькое лекарственное растение из жарких стран." },
        { word: "АМБРА", definition: "Благовонное вещество, находимое на берегах морей." },
        { word: "АНЧАР", definition: "Ядовитое дерево, растущее в жарких странах." },
        { word: "АРБУЗ", definition: "Крупный, сладкий плод ползучего растения из семейства тыквенных." },
        { word: "АСПИД", definition: "Ядовитая змея; также вид черного мрамора или сланца." }
    ];

    function detectNatureA(text) {
        const sample = text.toLowerCase();
        const found = WORDS.filter(item => sample.includes(item.word.toLowerCase()));
        
        if (found.length > 0) {
            return {
                type: "Природа А",
                confidence: Math.min(found.length * 0.2, 0.95),
                foundWords: found.map(f => f.word)
            };
        }
        return null;
    }

    console.log('✅ Модуль Природы А зарегистрирован!');
}
