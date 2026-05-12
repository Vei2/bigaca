export function register(apiCore) {
    console.log('🧠 Загружается модуль Междометий А (Dahl)...');

    apiCore.registerAnalysisFunction('detectInterjectionsA', detectInterjectionsA);

    const WORDS = [
        { word: "А", definition: "Выражение догадки (А, теперь помню), удивления или угрозы (А, коли так!)." },
        { word: "А ТО", definition: "Угроза: Сказывай, а то худо будет!" },
        { word: "А ВОТ", definition: "Угроза: А вот я тебя, ужо!" },
        { word: "АБЫ", definition: "Междометие (южн., зап.) или союз (чтобы, лишь бы)." },
        { word: "АГА", definition: "Да, так, ладно; междометие торжества или изумления." },
        { word: "АГАТУ", definition: "Междометие изумления (смоленское): а, ах, ба!" },
        { word: "АБО-ЩЕ", definition: "Вот еще, что еще; как бы не так." },
        { word: "АБО-ЩО", definition: "Что-нибудь; хотя и." },
        { word: "АБО-КАК", definition: "Как-нибудь, как попало." },
        { word: "АБЫ-НУ", definition: "Частица, употребляемая для усиления (напр. Абы-ну не плакал)." },
        { word: "АСЬ", definition: "Вопросительная частица: что, чего, что надо?" },
        { word: "АЙ", definition: "Выражение испуга, боли или удивления." }
    ];

    function detectInterjectionsA(text) {
        const sample = text.toLowerCase();
        const found = WORDS.filter(item => sample.includes(item.word.toLowerCase()));
        
        if (found.length > 0) {
            return {
                type: "Междометия А",
                confidence: Math.min(found.length * 0.2, 0.95),
                foundWords: found.map(f => f.word)
            };
        }
        return null;
    }

    console.log('✅ Модуль Междометий А зарегистрирован!');
}
