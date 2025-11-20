#!/usr/bin/env python3
"""
Web interface for vocabulary practice using Flask.
"""
import random
from vocab_core import load_vocabulary
from vocab_audio import get_audio_base64


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
        body { font-family: Arial; max-width: 900px; margin: 30px auto; padding: 20px; background: #f5f5f5; }
        h1 { text-align: center; color: #333; }
        .menu { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin: 30px 0; }
        .menu button { font-size: 16px; padding: 15px 25px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .menu button:hover { background: #45a049; }
        .menu button.active { background: #2196F3; }
        #quiz { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); min-height: 300px; }
        .card { border: 2px solid #333; padding: 40px; text-align: center; font-size: 28px; margin: 20px 0; background: #fafafa; border-radius: 8px; }
        .flashcard { cursor: pointer; user-select: none; }
        .answer { margin: 20px 0; text-align: center; }
        input { font-size: 18px; padding: 12px; width: 350px; border: 2px solid #ddd; border-radius: 5px; }
        button { font-size: 16px; padding: 12px 24px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
        .submit-btn { background: #4CAF50; color: white; }
        .submit-btn:hover { background: #45a049; }
        .correct { color: #4CAF50; font-weight: bold; }
        .wrong { color: #f44336; font-weight: bold; }
        .options { display: flex; flex-direction: column; gap: 10px; max-width: 400px; margin: 20px auto; }
        .option-btn { padding: 15px; font-size: 18px; background: #e0e0e0; }
        .option-btn:hover { background: #d0d0d0; }
        .speaker { cursor: pointer; font-size: 24px; margin-left: 10px; }
        .controls { text-align: center; margin: 20px 0; }
        .progress { text-align: center; color: #666; margin: 10px 0; }
        .sentence-input { width: 80%; min-height: 60px; font-size: 16px; padding: 10px; }
    </style>
</head>
<body>
    <h1>🇮🇹 Italian Vocabulary Practice 🇬🇷</h1>
    
    <div class="menu">
        <button onclick="startMode('it-gr')">Italian → Greek</button>
        <button onclick="startMode('gr-it')">Greek → Italian</button>
        <button onclick="startMode('mc')">Multiple Choice</button>
        <button onclick="startMode('flashcard')">Flashcards</button>
        <button onclick="startMode('sentence')">Sentences</button>
    </div>
    
    <div id="quiz"></div>
    
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
        selected = random.sample(words, min(3, len(words)))
        
        templates = [
            lambda w: f"{w[0]['italian'].capitalize()} è {w[1]['italian']}.",
            lambda w: f"Ho visto {w[0]['italian']} nel {w[1]['italian']}.",
            lambda w: f"Mi piace {w[0]['italian']} e {w[1]['italian']}.",
            lambda w: f"Domani vado al {w[0]['italian']} con {w[1]['italian']}.",
        ]
        
        template = random.choice(templates)
        sentence = template(selected)
        words_used = ", ".join([f"{w['italian']}={w['greek']}" for w in selected[:2]])
        
        return jsonify({"italian": sentence, "words": words_used})
    
    print("\n🌐 Starting web interface at http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    app.run(debug=True, port=5000, host='0.0.0.0')
