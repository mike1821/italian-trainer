#!/usr/bin/env python3
"""
Web interface for vocabulary practice using Flask.
"""
import random
from vocab_core import load_vocabulary
from vocab_audio import get_audio_base64
from sentence_generator import generate_smart_sentence


def launch_web():
    """Launch Flask web interface."""
    try:
        from flask import Flask, render_template_string, request, jsonify
        import json
    except ImportError:
        print("Flask not installed. Run: pip install flask")
        return
    
    app = Flask(__name__)
    
    HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Italian Vocabulary Practice</title>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1000px; 
            margin: 0 auto; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        h1 { 
            text-align: center; 
            color: white; 
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .subtitle {
            text-align: center;
            color: rgba(255,255,255,0.9);
            font-size: 1.1em;
            margin-bottom: 30px;
        }
        .menu { 
            display: flex; 
            flex-wrap: wrap; 
            gap: 12px; 
            justify-content: center; 
            margin: 30px 0; 
        }
        .menu button { 
            font-size: 16px; 
            padding: 15px 30px; 
            background: white;
            color: #667eea; 
            border: none; 
            border-radius: 25px; 
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .menu button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            background: #f0f0f0;
        }
        .menu button.active { 
            background: #4CAF50;
            color: white;
        }
        #quiz { 
            background: white; 
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.3); 
            min-height: 400px;
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .card { 
            border: 3px solid #667eea; 
            padding: 50px; 
            text-align: center; 
            font-size: 32px; 
            margin: 20px 0; 
            background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
            border-radius: 15px;
            font-weight: 500;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .flashcard { 
            cursor: pointer; 
            user-select: none;
            transition: transform 0.3s ease;
        }
        .flashcard:hover {
            transform: scale(1.02);
        }
        .answer { 
            margin: 30px 0; 
            text-align: center; 
        }
        input { 
            font-size: 20px; 
            padding: 15px 20px; 
            width: 400px; 
            max-width: 100%;
            border: 2px solid #667eea; 
            border-radius: 10px;
            outline: none;
            transition: border-color 0.3s ease;
        }
        input:focus {
            border-color: #4CAF50;
            box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
        }
        button { 
            font-size: 16px; 
            padding: 12px 28px; 
            margin: 5px; 
            border: none; 
            border-radius: 10px; 
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .submit-btn { 
            background: #4CAF50; 
            color: white;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }
        .submit-btn:hover { 
            background: #45a049;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        }
        .correct { 
            color: #4CAF50; 
            font-weight: bold; 
            font-size: 1.3em;
            animation: bounceIn 0.5s ease;
        }
        .wrong { 
            color: #f44336; 
            font-weight: bold; 
            font-size: 1.2em;
        }
        @keyframes bounceIn {
            0% { transform: scale(0.5); opacity: 0; }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); opacity: 1; }
        }
        .options { 
            display: flex; 
            flex-direction: column; 
            gap: 12px; 
            max-width: 500px; 
            margin: 20px auto; 
        }
        .option-btn { 
            padding: 18px; 
            font-size: 18px; 
            background: #f5f5f5;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            transition: all 0.3s ease;
        }
        .option-btn:hover { 
            background: #667eea;
            color: white;
            border-color: #667eea;
            transform: translateX(5px);
        }
        .speaker { 
            cursor: pointer; 
            font-size: 28px; 
            margin-left: 15px;
            transition: transform 0.2s ease;
            display: inline-block;
        }
        .speaker:hover {
            transform: scale(1.2);
        }
        .speaker:active {
            transform: scale(0.9);
        }
        .controls { 
            text-align: center; 
            margin: 20px 0; 
        }
        .progress { 
            text-align: center; 
            color: #667eea; 
            margin: 10px 0; 
            font-weight: 600;
            font-size: 1.1em;
        }
        .sentence-input { 
            width: 90%; 
            min-height: 80px; 
            font-size: 17px; 
            padding: 15px;
            border: 2px solid #667eea;
            border-radius: 10px;
            font-family: inherit;
            resize: vertical;
        }
        .sentence-input:focus {
            outline: none;
            border-color: #4CAF50;
            box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
        }
        footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>🇮🇹 Italian Vocabulary Practice 🇬🇷</h1>
    <div class="subtitle">Master Italian vocabulary with interactive practice modes</div>
    
    <div class="menu">
        <button onclick="startMode('it-gr')">Italian → Greek</button>
        <button onclick="startMode('gr-it')">Greek → Italian</button>
        <button onclick="startMode('mc')">Multiple Choice</button>
        <button onclick="startMode('flashcard')">Flashcards</button>
        <button onclick="startMode('sentence')">Sentences</button>
    </div>
    
    <div id="quiz"></div>
    
    <footer>
        Practice makes perfect! 💪 Keep learning every day 📚
    </footer>
    
    <script>
        let words = [];
        let current = 0;
        let score = 0;
        let mode = '';
        let flipped = false;
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        async function startMode(m) {
            console.log('Starting mode:', m);
            mode = m;
            current = 0;
            score = 0;
            
            try {
                const res = await fetch('/api/words?n=10');
                words = await res.json();
                console.log('Loaded words:', words.length);
                
                if (mode === 'sentence') {
                    showSentence();
                } else {
                    showQuestion();
                }
            } catch(e) {
                console.error('Error loading words:', e);
                document.getElementById('quiz').innerHTML = '<p style="color:red;">Error loading vocabulary. Check console.</p>';
            }
        }
        
        async function playAudio(word) {
            try {
                const res = await fetch('/api/speak?word=' + encodeURIComponent(word));
                const data = await res.json();
                if (data.audio) {
                    const audio = new Audio('data:audio/mp3;base64,' + data.audio);
                    audio.play();
                }
            } catch(e) {
                console.log('Audio unavailable:', e);
            }
        }
        
        function showQuestion() {
            if (current >= words.length) {
                document.getElementById('quiz').innerHTML = 
                    '<h2>🎉 Quiz Complete!</h2><p>Score: ' + score + '/' + words.length + 
                    ' (' + Math.round(score*100/words.length) + '%)</p>' +
                    '<button onclick="location.reload()" class="submit-btn">Start New Quiz</button>';
                return;
            }
            
            const w = words[current];
            const isReverse = mode === 'gr-it';
            const question = isReverse ? w.greek : w.italian;
            const answer = isReverse ? w.italian : w.greek;
            
            let html = '<div class="progress">Question ' + (current+1) + ' of ' + words.length + '</div>';
            
            if (mode === 'mc') {
                html += '<div class="card">' + escapeHtml(question) + 
                        '<span class="speaker" onclick="playAudio(' + JSON.stringify(w.italian) + ')">🔊</span></div>';
                html += '<div class="options">';
                
                const options = [answer];
                const otherWords = words.filter((x, i) => i !== current);
                for (let i = 0; i < 3 && i < otherWords.length; i++) {
                    options.push(isReverse ? otherWords[i].italian : otherWords[i].greek);
                }
                options.sort(() => Math.random() - 0.5);
                
                options.forEach((opt, idx) => {
                    html += '<button class="option-btn" data-opt="' + escapeHtml(opt) + 
                            '" data-correct="' + escapeHtml(answer) + 
                            '" data-italian="' + escapeHtml(w.italian) + '">' + escapeHtml(opt) + '</button>';
                });
                html += '</div>';
                
                // Attach event listeners after DOM update
                setTimeout(() => {
                    document.querySelectorAll('.option-btn').forEach(btn => {
                        btn.onclick = function() {
                            checkMC(this.dataset.opt, this.dataset.correct, this.dataset.italian);
                        };
                    });
                }, 10);
            } else if (mode === 'flashcard') {
                if (!flipped) {
                    html += '<div class="card flashcard" onclick="flipCard()">' + escapeHtml(question) +
                            '<span class="speaker" onclick="event.stopPropagation(); playAudio(' + JSON.stringify(w.italian) + ')">🔊</span>' +
                            '<p style="font-size:14px; color:#999; margin-top:20px;">Click to flip</p></div>';
                } else {
                    html += '<div class="card">' + escapeHtml(question) + 
                            '<span class="speaker" onclick="playAudio(' + JSON.stringify(w.italian) + ')">🔊</span></div>';
                    html += '<div class="card" style="background:#e8f5e9;">→ ' + escapeHtml(answer) + '</div>';
                    html += '<div class="controls">' +
                            '<button onclick="markCard(true)" class="submit-btn" style="background:#4CAF50;">✓ Know it</button>' +
                            '<button onclick="markCard(false)" class="submit-btn" style="background:#f44336;">✗ Need review</button>' +
                            '</div>';
                }
            } else {
                html += '<div class="card">' + escapeHtml(question) + 
                        '<span class="speaker" onclick="playAudio(' + JSON.stringify(w.italian) + ')">🔊</span></div>';
                html += '<div class="answer">' +
                        '<input type="text" id="answer" placeholder="Your answer" autofocus data-correct=' + JSON.stringify(answer) + ' />' +
                        '<button onclick="checkAnswerBtn()" class="submit-btn">Submit</button>' +
                        '</div><div id="result"></div>';
                
                setTimeout(() => {
                    const inp = document.getElementById('answer');
                    if (inp) {
                        inp.focus();
                        inp.addEventListener('keypress', function(e) {
                            if (e.key === 'Enter') checkAnswerBtn();
                        });
                    }
                }, 100);
            }
            
            document.getElementById('quiz').innerHTML = html;
        }
        
        function flipCard() {
            flipped = true;
            showQuestion();
        }
        
        function markCard(correct) {
            if (correct) score++;
            flipped = false;
            current++;
            showQuestion();
        }
        
        function checkAnswerBtn() {
            const inp = document.getElementById('answer');
            const ans = inp.value.trim();
            const correct = inp.dataset.correct;
            checkAnswer(ans, correct);
        }
        
        function checkAnswer(userAnswer, correct) {
            const isCorrect = userAnswer.toLowerCase() === correct.toLowerCase();
            
            if (isCorrect) {
                score++;
                document.getElementById('result').innerHTML = '<p class="correct">✓ Correct!</p>';
            } else {
                document.getElementById('result').innerHTML = 
                    '<p class="wrong">✗ Wrong. Answer: ' + escapeHtml(correct) + '</p>';
            }
            
            playAudio(words[current].italian);
            
            current++;
            setTimeout(showQuestion, 2000);
        }
        
        function checkMC(selected, correct, italianWord) {
            const isCorrect = selected === correct;
            if (isCorrect) score++;
            
            const res = isCorrect ? 
                '<p class="correct">✓ Correct!</p>' : 
                '<p class="wrong">✗ Wrong. Answer: ' + escapeHtml(correct) + '</p>';
            
            document.getElementById('quiz').innerHTML += '<div>' + res + '</div>';
            
            // Play audio with the word passed as parameter
            playAudio(italianWord);
            
            current++;
            setTimeout(showQuestion, 2000);
        }
        
        let currentSentence = null;
        
        async function showSentence() {
            if (current >= 5) {
                document.getElementById('quiz').innerHTML = 
                    '<h2>Sentence Practice Complete!</h2>' +
                    '<button onclick="location.reload()" class="submit-btn">Start New</button>';
                return;
            }
            
            const res = await fetch('/api/sentence');
            const data = await res.json();
            currentSentence = data;
            
            let html = '<div class="progress">Sentence ' + (current+1) + ' of 5</div>';
            html += '<div class="card">' + escapeHtml(data.italian) + '</div>';
            html += '<div style="text-align:center; margin:10px 0; color:#667eea; font-size:0.9em; font-style:italic;">';
            html += '📝 Grammar: ' + escapeHtml(data.pattern) + '</div>';
            html += '<div class="answer">';
            html += '<textarea id="translation" class="sentence-input" placeholder="Translate to Greek..."></textarea><br>';
            html += '<button onclick="checkSentence()" class="submit-btn">Show Translation</button>';
            html += '</div><div id="result"></div>';
            html += '<div style="margin-top:20px; color:#666; font-size:14px;">Words used: ' + escapeHtml(data.words) + '</div>';
            
            document.getElementById('quiz').innerHTML = html;
        }
        
        function checkSentence() {
            const userTrans = document.getElementById('translation').value.trim();
            
            let feedback = '<div style="margin-top:20px;">';
            feedback += '<p style="color:#2196F3; font-weight:bold;">Your translation:</p>';
            feedback += '<p style="background:#f0f0f0; padding:10px; border-radius:5px;">' + 
                       (userTrans || '<i>No translation provided</i>') + '</p>';
            feedback += '<p style="color:#666; font-weight:bold; margin-top:15px;">Reference (word-by-word):</p>';
            feedback += '<p style="background:#e8f5e9; padding:10px; border-radius:5px;">' + 
                       escapeHtml(currentSentence.words) + '</p>';
            feedback += '<p style="font-size:14px; color:#999; margin-top:10px;">💡 Tip: Compare your translation with the word meanings above.</p>';
            feedback += '<button onclick="nextSentence()" class="submit-btn" style="margin-top:15px;">Next Sentence →</button>';
            feedback += '</div>';
            
            document.getElementById('result').innerHTML = feedback;
        }
        
        function nextSentence() {
            current++;
            showSentence();
        }
        
        window.onload = () => {
            console.log('Page loaded, auto-starting Italian→Greek mode');
            startMode('it-gr');
        };
    </script>
</body>
</html>
    '''
    
    @app.route('/')
    def index():
        return render_template_string(HTML)
    
    @app.route('/api/words')
    def get_words():
        n = int(request.args.get('n', 10))
        words = load_vocabulary()
        selected = random.sample(words, min(n, len(words)))
        return jsonify([{"italian": w["italian"], "greek": w["greek"]} for w in selected])
    
    @app.route('/api/speak')
    def speak():
        word = request.args.get('word', '')
        audio_b64 = get_audio_base64(word)
        if audio_b64:
            return jsonify({"audio": audio_b64})
        else:
            return jsonify({"error": "Audio generation failed"}), 500
    
    @app.route('/api/sentence')
    def get_sentence():
        words = load_vocabulary()
        result = generate_smart_sentence(words)
        
        # Format word meanings for display
        word_meanings = []
        for word_it in result['words_used']:
            # Find the Greek translation
            matching = [w for w in words if w['italian'].lower() == word_it.lower()]
            if matching:
                word_meanings.append(f"{word_it}={matching[0]['greek']}")
            else:
                word_meanings.append(word_it)
        
        return jsonify({
            "italian": result['italian'],
            "words": ", ".join(word_meanings),
            "pattern": result['pattern']
        })
    
    print("\n🌐 Starting web interface at http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    app.run(debug=True, port=5000, host='0.0.0.0')


# WSGI entry point for PythonAnywhere/production deployment
# This allows the Flask app to be imported by WSGI servers
application = None

def create_wsgi_app():
    """Create Flask app for WSGI deployment without app.run()."""
    from flask import Flask, render_template_string, request, jsonify
    import json
    
    app = Flask(__name__)
    vocabulary = load_vocabulary()
    
    HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Italian Vocabulary Practice</title>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes bounceIn {
            0% { transform: scale(0.3); opacity: 0; }
            50% { transform: scale(1.05); }
            70% { transform: scale(0.9); }
            100% { transform: scale(1); opacity: 1; }
        }
        
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            font-size: 2.5em;
        }
        
        .mode-selector {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            margin-bottom: 20px;
        }
        
        .mode-selector h2 {
            color: #667eea;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .mode-buttons {
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
        }
        
        .mode-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 20px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .mode-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        .mode-btn:active {
            transform: translateY(-1px);
        }
        
        .quiz-container {
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-width: 700px;
            width: 100%;
            min-height: 300px;
            display: none;
        }
        
        .quiz-container.active {
            display: block;
            animation: bounceIn 0.6s ease-out;
        }
        
        .word-display {
            text-align: center;
            margin: 30px 0;
        }
        
        .word {
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .speaker-icon {
            font-size: 2em;
            cursor: pointer;
            display: inline-block;
            transition: transform 0.2s;
        }
        
        .speaker-icon:hover {
            transform: scale(1.2);
        }
        
        input[type="text"] {
            width: 100%;
            padding: 15px;
            font-size: 18px;
            border: 3px solid #667eea;
            border-radius: 10px;
            margin-bottom: 20px;
            transition: all 0.3s;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #764ba2;
            box-shadow: 0 0 15px rgba(118, 75, 162, 0.3);
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .back-btn {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            margin-right: 10px;
        }
        
        .feedback {
            text-align: center;
            font-size: 1.5em;
            margin: 20px 0;
            min-height: 40px;
            font-weight: bold;
        }
        
        .correct {
            color: #4CAF50;
            animation: bounceIn 0.5s ease-out;
        }
        
        .wrong {
            color: #f44336;
        }
        
        .score {
            text-align: center;
            font-size: 1.2em;
            color: #666;
            margin-top: 20px;
        }
        
        .options {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 30px 0;
        }
        
        .option-btn {
            background: white;
            border: 3px solid #667eea;
            color: #667eea;
            padding: 20px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .option-btn:hover {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .option-btn.correct {
            background: #4CAF50;
            border-color: #4CAF50;
            color: white;
        }
        
        .option-btn.wrong {
            background: #f44336;
            border-color: #f44336;
            color: white;
        }
        
        .flashcard {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 40px;
            border-radius: 15px;
            text-align: center;
            min-height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: transform 0.3s ease;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .flashcard:hover {
            transform: scale(1.02);
        }
        
        .flashcard-text {
            font-size: 3em;
            font-weight: bold;
        }
        
        .flashcard-controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 30px;
        }
        
        .sentence-info {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        
        .sentence-info h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .sentence-info p {
            margin: 10px 0;
            font-size: 1.1em;
            line-height: 1.6;
        }
        
        .pattern-badge {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <h1>🇮🇹 Italian Vocabulary Practice 🇬🇷</h1>
    
    <div class="mode-selector" id="modeSelector">
        <h2>Choose Practice Mode</h2>
        <div class="mode-buttons">
            <button class="mode-btn" onclick="startMode('it-gr')">Italian → Greek Translation</button>
            <button class="mode-btn" onclick="startMode('gr-it')">Greek → Italian Translation</button>
            <button class="mode-btn" onclick="startMode('mc')">Multiple Choice Quiz</button>
            <button class="mode-btn" onclick="startMode('flashcard')">Flashcards</button>
            <button class="mode-btn" onclick="startMode('sentence')">Practice with Sentences</button>
        </div>
    </div>
    
    <div class="quiz-container" id="quizContainer">
        <button class="btn back-btn" onclick="backToMenu()">← Back to Menu</button>
        <div id="quizContent"></div>
    </div>

    <script>
        let currentMode = '';
        let words = [];
        let currentIndex = 0;
        let score = 0;
        let total = 0;
        let currentWord = null;
        let flashcardRevealed = false;

        function backToMenu() {
            document.getElementById('modeSelector').style.display = 'block';
            document.getElementById('quizContainer').classList.remove('active');
            currentMode = '';
            words = [];
            currentIndex = 0;
            score = 0;
            total = 0;
        }

        async function startMode(mode) {
            currentMode = mode;
            currentIndex = 0;
            score = 0;
            total = 0;
            
            document.getElementById('modeSelector').style.display = 'none';
            document.getElementById('quizContainer').classList.add('active');
            
            if (mode === 'sentence') {
                showSentence();
            } else {
                const response = await fetch('/api/words?n=10');
                words = await response.json();
                
                if (mode === 'it-gr' || mode === 'gr-it') {
                    showTranslationQuiz();
                } else if (mode === 'mc') {
                    showMultipleChoice();
                } else if (mode === 'flashcard') {
                    showFlashcard();
                }
            }
        }

        function showTranslationQuiz() {
            if (currentIndex >= words.length) {
                showFinalScore();
                return;
            }
            
            currentWord = words[currentIndex];
            const question = currentMode === 'it-gr' ? currentWord.italian : currentWord.greek;
            
            const html = `
                <div class="word-display">
                    <div class="word">${question}</div>
                    ${currentMode === 'it-gr' ? '<span class="speaker-icon" onclick="playAudio()">🔊</span>' : ''}
                </div>
                <input type="text" id="answer" placeholder="Type your answer..." onkeypress="handleEnter(event)">
                <button class="btn" onclick="checkAnswer()">Check Answer</button>
                <div class="feedback" id="feedback"></div>
                <div class="score">Score: ${score}/${total}</div>
            `;
            
            document.getElementById('quizContent').innerHTML = html;
            document.getElementById('answer').focus();
        }

        async function playAudio() {
            if (currentWord && currentMode === 'it-gr') {
                const response = await fetch(`/api/speak?word=${encodeURIComponent(currentWord.italian)}`);
                const data = await response.json();
                const audio = new Audio('data:audio/mp3;base64,' + data.audio);
                audio.play();
            }
        }

        function handleEnter(event) {
            if (event.key === 'Enter') {
                checkAnswer();
            }
        }

        async function checkAnswer() {
            const userAnswer = document.getElementById('answer').value.trim().toLowerCase();
            const correctAnswer = currentMode === 'it-gr' ? currentWord.greek.toLowerCase() : currentWord.italian.toLowerCase();
            const feedback = document.getElementById('feedback');
            
            total++;
            
            if (userAnswer === correctAnswer) {
                score++;
                feedback.innerHTML = '✓ Correct!';
                feedback.className = 'feedback correct';
                
                if (currentMode === 'it-gr') {
                    await playAudio();
                }
                
                setTimeout(() => {
                    currentIndex++;
                    showTranslationQuiz();
                }, 1500);
            } else {
                feedback.innerHTML = `✗ Wrong! Correct answer: ${currentMode === 'it-gr' ? currentWord.greek : currentWord.italian}`;
                feedback.className = 'feedback wrong';
                
                setTimeout(() => {
                    currentIndex++;
                    showTranslationQuiz();
                }, 3000);
            }
        }

        async function showMultipleChoice() {
            if (currentIndex >= words.length) {
                showFinalScore();
                return;
            }
            
            currentWord = words[currentIndex];
            const others = words.filter(w => w !== currentWord).slice(0, 3);
            const options = [currentWord, ...others].sort(() => Math.random() - 0.5);
            
            const html = `
                <div class="word-display">
                    <div class="word">${currentWord.italian}</div>
                    <span class="speaker-icon" onclick="playAudio()">🔊</span>
                </div>
                <div class="options" id="options">
                    ${options.map(opt => `
                        <button class="option-btn" 
                                data-opt="${opt.greek}" 
                                data-correct="${currentWord.greek}"
                                data-italian="${currentWord.italian}">
                            ${opt.greek}
                        </button>
                    `).join('')}
                </div>
                <div class="feedback" id="feedback"></div>
                <div class="score">Score: ${score}/${total}</div>
            `;
            
            document.getElementById('quizContent').innerHTML = html;
            
            setTimeout(() => {
                document.querySelectorAll('.option-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        checkMC(this.dataset.opt, this.dataset.correct, this.dataset.italian);
                    });
                });
            }, 10);
        }

        async function checkMC(selected, correct, italian) {
            total++;
            const buttons = document.querySelectorAll('.option-btn');
            const feedback = document.getElementById('feedback');
            
            buttons.forEach(btn => btn.disabled = true);
            
            if (selected === correct) {
                score++;
                feedback.innerHTML = '✓ Correct!';
                feedback.className = 'feedback correct';
                buttons.forEach(btn => {
                    if (btn.dataset.opt === correct) {
                        btn.classList.add('correct');
                    }
                });
                
                const response = await fetch(`/api/speak?word=${encodeURIComponent(italian)}`);
                const data = await response.json();
                const audio = new Audio('data:audio/mp3;base64,' + data.audio);
                audio.play();
            } else {
                feedback.innerHTML = `✗ Wrong! Correct answer: ${correct}`;
                feedback.className = 'feedback wrong';
                buttons.forEach(btn => {
                    if (btn.dataset.opt === selected) {
                        btn.classList.add('wrong');
                    }
                    if (btn.dataset.opt === correct) {
                        btn.classList.add('correct');
                    }
                });
            }
            
            setTimeout(() => {
                currentIndex++;
                showMultipleChoice();
            }, 2000);
        }

        async function showFlashcard() {
            if (currentIndex >= words.length) {
                showFinalScore();
                return;
            }
            
            currentWord = words[currentIndex];
            flashcardRevealed = false;
            
            const html = `
                <div class="flashcard" onclick="revealFlashcard()">
                    <div class="flashcard-text">${currentWord.italian}</div>
                </div>
                <div class="flashcard-controls">
                    <button class="btn" onclick="markFlashcard(false)" id="wrongBtn" disabled>Wrong</button>
                    <button class="btn" onclick="markFlashcard(true)" id="correctBtn" disabled>Correct</button>
                </div>
                <div class="score">Score: ${score}/${total}</div>
            `;
            
            document.getElementById('quizContent').innerHTML = html;
            await playAudio();
        }

        function revealFlashcard() {
            if (flashcardRevealed) return;
            
            flashcardRevealed = true;
            document.querySelector('.flashcard-text').textContent = currentWord.greek;
            document.getElementById('wrongBtn').disabled = false;
            document.getElementById('correctBtn').disabled = false;
        }

        function markFlashcard(correct) {
            total++;
            if (correct) score++;
            
            currentIndex++;
            showFlashcard();
        }

        async function showSentence() {
            const response = await fetch('/api/sentence');
            const data = await response.json();
            
            const html = `
                <div class="word-display">
                    <div class="word">${data.italian}</div>
                </div>
                <input type="text" id="translation" placeholder="Translate to Greek..." onkeypress="handleSentenceEnter(event)">
                <button class="btn" onclick="checkSentence()">Check Translation</button>
                <div class="feedback" id="sentenceFeedback"></div>
                <div class="sentence-info" id="sentenceInfo" style="display:none;"></div>
                <button class="btn" onclick="nextSentence()" id="nextBtn" style="display:none;">Next Sentence →</button>
            `;
            
            document.getElementById('quizContent').innerHTML = html;
            document.getElementById('translation').focus();
            
            window.currentSentenceData = data;
        }

        function handleSentenceEnter(event) {
            if (event.key === 'Enter') {
                checkSentence();
            }
        }

        function checkSentence() {
            const data = window.currentSentenceData;
            const feedback = document.getElementById('sentenceFeedback');
            const info = document.getElementById('sentenceInfo');
            
            feedback.innerHTML = `
                <span class="pattern-badge">${data.pattern}</span>
            `;
            feedback.className = 'feedback';
            
            info.innerHTML = `
                <h3>Word Meanings:</h3>
                <p>${data.words}</p>
            `;
            info.style.display = 'block';
            
            document.getElementById('nextBtn').style.display = 'inline-block';
            document.querySelector('input').disabled = true;
            document.querySelector('button.btn:not(#nextBtn)').disabled = true;
        }

        function nextSentence() {
            showSentence();
        }

        function showFinalScore() {
            const percentage = total > 0 ? Math.round((score / total) * 100) : 0;
            const html = `
                <div style="text-align: center;">
                    <h2 style="color: #667eea; margin-bottom: 20px;">Quiz Complete!</h2>
                    <div style="font-size: 3em; margin: 30px 0;">
                        ${score}/${total}
                    </div>
                    <div style="font-size: 2em; color: #764ba2; margin-bottom: 30px;">
                        ${percentage}%
                    </div>
                    <button class="btn" onclick="startMode(currentMode)">Try Again</button>
                    <button class="btn back-btn" onclick="backToMenu()">Back to Menu</button>
                </div>
            `;
            document.getElementById('quizContent').innerHTML = html;
        }
    </script>
</body>
</html>
'''
    
    @app.route('/')
    def index():
        return render_template_string(HTML)
    
    @app.route('/api/words')
    def get_words():
        n = int(request.args.get('n', 10))
        selected = random.sample(vocabulary, min(n, len(vocabulary)))
        return jsonify(selected)
    
    @app.route('/api/speak')
    def speak():
        word = request.args.get('word', '')
        audio_base64 = get_audio_base64(word)
        return jsonify({"audio": audio_base64})
    
    @app.route('/api/sentence')
    def sentence():
        result = generate_smart_sentence(vocabulary)
        word_meanings = []
        for word_it in result['words_used']:
            matching = [w for w in vocabulary if w['italian'].lower() == word_it.lower()]
            if matching:
                word_meanings.append(f"{word_it}={matching[0]['greek']}")
            else:
                word_meanings.append(word_it)
        
        return jsonify({
            "italian": result['italian'],
            "words": ", ".join(word_meanings),
            "pattern": result['pattern']
        })
    
    return app


# Create the application instance for WSGI
application = create_wsgi_app()
