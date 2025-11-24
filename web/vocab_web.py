#!/usr/bin/env python3
"""
Web interface for vocabulary practice using Flask.
"""
import random
from app.vocab_core import load_vocabulary
from app.vocab_audio import get_audio_base64
from app.sentence_generator import generate_smart_sentence


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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <style>
        :root {
            --bg-gradient-start: #667eea;
            --bg-gradient-end: #764ba2;
            --card-bg: white;
            --text-primary: #333;
            --text-secondary: #666;
            --text-light: rgba(255,255,255,0.9);
            --menu-btn-bg: white;
            --menu-btn-text: #667eea;
            --shadow-color: rgba(0,0,0,0.2);
            --progress-bg: rgba(255,255,255,0.3);
            --progress-fill: #4CAF50;
        }
        
        body.dark-mode {
            --bg-gradient-start: #1a1a2e;
            --bg-gradient-end: #16213e;
            --card-bg: #0f3460;
            --text-primary: #e8e8e8;
            --text-secondary: #b8b8b8;
            --text-light: rgba(255,255,255,0.9);
            --menu-btn-bg: #0f3460;
            --menu-btn-text: #67d5ea;
            --shadow-color: rgba(0,0,0,0.5);
            --progress-bg: rgba(255,255,255,0.1);
            --progress-fill: #67d5ea;
        }
        
        * { box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1000px; 
            margin: 0 auto; 
            padding: 20px; 
            background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
            min-height: 100vh;
            transition: background 0.3s ease;
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
            color: var(--text-light);
            font-size: 1.1em;
            margin-bottom: 30px;
        }
        
        .dark-mode-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--card-bg);
            color: var(--text-primary);
            border: none;
            padding: 12px 16px;
            border-radius: 50px;
            cursor: pointer;
            font-size: 20px;
            box-shadow: 0 4px 15px var(--shadow-color);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .dark-mode-toggle:hover {
            transform: scale(1.1) rotate(20deg);
        }
        
        .progress-container {
            width: 100%;
            height: 8px;
            background: var(--progress-bg);
            border-radius: 10px;
            margin: 20px 0;
            overflow: hidden;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--progress-fill), #76ff03);
            border-radius: 10px;
            transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 0 10px var(--progress-fill);
        }
        
        .progress-text {
            text-align: center;
            color: var(--text-light);
            font-size: 0.9em;
            margin-top: 5px;
            font-weight: 600;
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
            background: var(--menu-btn-bg);
            color: var(--menu-btn-text); 
            border: none; 
            border-radius: 25px; 
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px var(--shadow-color);
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
    <button class="dark-mode-toggle" onclick="toggleDarkMode()" title="Toggle Dark Mode">🌙</button>
    
    <h1>🇮🇹 Italian Vocabulary Practice 🇬🇷</h1>
    <div class="subtitle">Master Italian vocabulary with interactive practice modes</div>
    
    <div class="menu" id="mainMenu">
        <button onclick="startMode('it-gr')">Italian → Greek</button>
        <button onclick="startMode('gr-it')">Greek → Italian</button>
        <button onclick="startMode('mc')">Multiple Choice</button>
        <button onclick="startMode('flashcard')">Flashcards</button>
        <button onclick="startMode('sentence-it-gr')">🇮🇹→🇬🇷 Sentences</button>
        <button onclick="startMode('sentence-gr-it')">🇬🇷→🇮🇹 Sentences</button>
        <button onclick="showStats()" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">📊 Statistics</button>
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
        
        // Dark mode functionality
        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDark);
            document.querySelector('.dark-mode-toggle').textContent = isDark ? '☀️' : '🌙';
        }
        
        // Load dark mode preference
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
            document.querySelector('.dark-mode-toggle').textContent = '☀️';
        }
        
        // Confetti celebration
        function celebrate() {
            const duration = 3000;
            const end = Date.now() + duration;
            
            const colors = ['#667eea', '#764ba2', '#4CAF50', '#FFC107', '#f093fb'];
            
            (function frame() {
                confetti({
                    particleCount: 3,
                    angle: 60,
                    spread: 55,
                    origin: { x: 0 },
                    colors: colors
                });
                confetti({
                    particleCount: 3,
                    angle: 120,
                    spread: 55,
                    origin: { x: 1 },
                    colors: colors
                });
                
                if (Date.now() < end) {
                    requestAnimationFrame(frame);
                }
            }());
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Record quiz result to database
        async function recordResult(word, correct, quizType = 'web') {
            try {
                await fetch('/api/record', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        word: word,
                        correct: correct,
                        quiz_type: quizType
                    })
                });
            } catch(e) {
                console.log('Failed to record result:', e);
            }
        }
        
        async function showStats() {
            document.getElementById('mainMenu').style.display = 'none';
            document.getElementById('quiz').innerHTML = '<div style="text-align:center;padding:40px;">Loading statistics... ⏳</div>';
            
            try {
                const res = await fetch('/api/stats');
                const stats = await res.json();
                
                let html = '<div style="max-width:1200px; margin:0 auto;">';
                html += '<button onclick="location.reload()" style="margin-bottom:20px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-size:16px;">← Back to Menu</button>';
                
                // Overview cards
                html += '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:20px; margin-bottom:30px;">';
                html += `<div class="stat-card">
                    <div class="stat-number">${stats.total_words}</div>
                    <div class="stat-label">Words Practiced</div>
                </div>`;
                html += `<div class="stat-card">
                    <div class="stat-number">${stats.total_attempts}</div>
                    <div class="stat-label">Total Attempts</div>
                </div>`;
                html += `<div class="stat-card">
                    <div class="stat-number">${stats.accuracy.toFixed(1)}%</div>
                    <div class="stat-label">Overall Accuracy</div>
                </div>`;
                html += `<div class="stat-card">
                    <div class="stat-number">${stats.best_streak}</div>
                    <div class="stat-label">Best Streak</div>
                </div>`;
                html += `<div class="stat-card">
                    <div class="stat-number">${stats.due_for_review}</div>
                    <div class="stat-label">Due for Review</div>
                </div>`;
                html += '</div>';
                
                // Charts Section
                if (stats.daily_performance.length > 0 || stats.quiz_types.length > 0) {
                    html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:20px;">';
                    
                    // Daily Performance Chart
                    if (stats.daily_performance.length > 0) {
                        html += '<div style="background:white; padding:25px; border-radius:15px; box-shadow:0 4px 15px rgba(0,0,0,0.1);">';
                        html += '<h2 style="color:#667eea; margin-bottom:15px;">📈 Daily Accuracy Trend</h2>';
                        html += '<canvas id="dailyChart" style="max-height:250px;"></canvas>';
                        html += '</div>';
                    }
                    
                    // Quiz Type Performance Chart
                    if (stats.quiz_types.length > 0) {
                        html += '<div style="background:white; padding:25px; border-radius:15px; box-shadow:0 4px 15px rgba(0,0,0,0.1);">';
                        html += '<h2 style="color:#667eea; margin-bottom:15px;">📊 Quiz Type Performance</h2>';
                        html += '<canvas id="quizTypeChart" style="max-height:250px;"></canvas>';
                        html += '</div>';
                    }
                    
                    html += '</div>';
                }
                
                // Top words
                html += '<div style="background:white; padding:25px; border-radius:15px; box-shadow:0 4px 15px rgba(0,0,0,0.1); margin-bottom:20px;">';
                html += '<h2 style="color:#667eea; margin-bottom:15px;">🌟 Top Performing Words</h2>';
                if (stats.top_words.length > 0) {
                    html += '<table style="width:100%; border-collapse:collapse;">';
                    html += '<tr style="background:#f5f5f5; font-weight:bold;"><th style="padding:10px; text-align:left;">Word</th><th style="padding:10px;">Success Rate</th><th style="padding:10px;">Streak</th><th style="padding:10px;">EF</th></tr>';
                    stats.top_words.forEach(w => {
                        html += `<tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px;">${escapeHtml(w.word)}</td>
                            <td style="padding:10px; text-align:center; color:#4CAF50; font-weight:bold;">${w.rate.toFixed(0)}%</td>
                            <td style="padding:10px; text-align:center;">${w.streak}</td>
                            <td style="padding:10px; text-align:center;">${w.ef.toFixed(2)}</td>
                        </tr>`;
                    });
                    html += '</table>';
                } else {
                    html += '<p style="color:#999;">No data yet. Start practicing!</p>';
                }
                html += '</div>';
                
                // Weak words
                html += '<div style="background:white; padding:25px; border-radius:15px; box-shadow:0 4px 15px rgba(0,0,0,0.1); margin-bottom:20px;">';
                html += '<h2 style="color:#f5576c; margin-bottom:15px;">📉 Words Needing Attention</h2>';
                if (stats.weak_words.length > 0) {
                    html += '<table style="width:100%; border-collapse:collapse;">';
                    html += '<tr style="background:#f5f5f5; font-weight:bold;"><th style="padding:10px; text-align:left;">Word</th><th style="padding:10px;">Times Seen</th><th style="padding:10px;">Success Rate</th><th style="padding:10px;">EF</th></tr>';
                    stats.weak_words.forEach(w => {
                        html += `<tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px;">${escapeHtml(w.word)}</td>
                            <td style="padding:10px; text-align:center;">${w.seen}</td>
                            <td style="padding:10px; text-align:center; color:#f44336; font-weight:bold;">${w.rate.toFixed(0)}%</td>
                            <td style="padding:10px; text-align:center;">${w.ef.toFixed(2)}</td>
                        </tr>`;
                    });
                    html += '</table>';
                    html += '<div style="margin-top:15px; padding:15px; background:#fff3cd; border-radius:8px; border-left:4px solid #f5576c;">';
                    html += '💡 <strong>Tip:</strong> Use <code style="background:#f5f5f5; padding:3px 8px; border-radius:4px;">python vocab.py focus</code> in the command line to practice these words intensively!';
                    html += '</div>';
                } else {
                    html += '<p style="color:#999;">Great! No weak words found.</p>';
                }
                html += '</div>';
                
                html += '</div>';
                
                document.getElementById('quiz').innerHTML = html;
                
                // Create charts after DOM is ready
                setTimeout(() => {
                    // Daily Performance Chart
                    if (stats.daily_performance.length > 0) {
                        const dailyCtx = document.getElementById('dailyChart');
                        if (dailyCtx) {
                            new Chart(dailyCtx, {
                                type: 'line',
                                data: {
                                    labels: stats.daily_performance.map(d => d.date),
                                    datasets: [{
                                        label: 'Accuracy %',
                                        data: stats.daily_performance.map(d => d.accuracy),
                                        borderColor: '#667eea',
                                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                                        tension: 0.4,
                                        fill: true,
                                        pointRadius: 5,
                                        pointBackgroundColor: '#667eea',
                                        pointBorderColor: '#fff',
                                        pointBorderWidth: 2
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    maintainAspectRatio: true,
                                    plugins: {
                                        legend: { display: false },
                                        tooltip: {
                                            callbacks: {
                                                label: function(context) {
                                                    const dataPoint = stats.daily_performance[context.dataIndex];
                                                    return [
                                                        `Accuracy: ${dataPoint.accuracy.toFixed(1)}%`,
                                                        `Attempts: ${dataPoint.attempts}`,
                                                        `Correct: ${dataPoint.correct}`
                                                    ];
                                                }
                                            }
                                        }
                                    },
                                    scales: {
                                        y: {
                                            beginAtZero: true,
                                            max: 100,
                                            ticks: {
                                                callback: function(value) {
                                                    return value + '%';
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        }
                    }
                    
                    // Quiz Type Chart
                    if (stats.quiz_types.length > 0) {
                        const quizTypeCtx = document.getElementById('quizTypeChart');
                        if (quizTypeCtx) {
                            const colors = stats.quiz_types.map(qt => 
                                qt.accuracy >= 70 ? '#4CAF50' : 
                                qt.accuracy >= 50 ? '#FF9800' : '#f44336'
                            );
                            
                            new Chart(quizTypeCtx, {
                                type: 'bar',
                                data: {
                                    labels: stats.quiz_types.map(qt => qt.type.charAt(0).toUpperCase() + qt.type.slice(1)),
                                    datasets: [{
                                        label: 'Accuracy %',
                                        data: stats.quiz_types.map(qt => qt.accuracy),
                                        backgroundColor: colors,
                                        borderColor: colors,
                                        borderWidth: 2
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    maintainAspectRatio: true,
                                    plugins: {
                                        legend: { display: false },
                                        tooltip: {
                                            callbacks: {
                                                label: function(context) {
                                                    const qt = stats.quiz_types[context.dataIndex];
                                                    return [
                                                        `Accuracy: ${qt.accuracy.toFixed(1)}%`,
                                                        `Attempts: ${qt.count}`,
                                                        `Correct: ${qt.correct}`
                                                    ];
                                                }
                                            }
                                        }
                                    },
                                    scales: {
                                        y: {
                                            beginAtZero: true,
                                            max: 100,
                                            ticks: {
                                                callback: function(value) {
                                                    return value + '%';
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        }
                    }
                }, 100);
                
            } catch(e) {
                console.error('Error loading stats:', e);
                document.getElementById('quiz').innerHTML = '<p style="color:red;">Error loading statistics. ' + e.message + '</p>';
            }
        }
        
        async function startMode(m) {
            console.log('Starting mode:', m);
            mode = m;
            current = 0;
            score = 0;
            
            try {
                // Check if it's a sentence mode
                if (mode.startsWith('sentence')) {
                    showSentence();
                } else {
                    const res = await fetch('/api/words?n=10');
                    words = await res.json();
                    console.log('Loaded words:', words.length);
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
                const percentage = Math.round(score*100/words.length);
                let completeHTML = '<div class="fade-in" style="text-align:center; padding:40px;">';
                completeHTML += '<h2 style="color:var(--text-light); font-size:2.5em; margin-bottom:20px;">🎉 Quiz Complete!</h2>';
                completeHTML += '<div style="font-size:4em; margin:30px 0;">' + score + '/' + words.length + '</div>';
                completeHTML += '<div style="font-size:2em; color:var(--text-light); margin-bottom:30px;">' + percentage + '%</div>';
                
                // Show confetti for good scores
                if (percentage >= 80) {
                    celebrate();
                    completeHTML += '<p style="color:#4CAF50; font-size:1.5em; margin:20px 0;">🌟 Excellent work! 🌟</p>';
                } else if (percentage >= 60) {
                    completeHTML += '<p style="color:#FFC107; font-size:1.3em; margin:20px 0;">👍 Good job! Keep practicing!</p>';
                } else {
                    completeHTML += '<p style="color:#FF9800; font-size:1.3em; margin:20px 0;">💪 Keep going! Practice makes perfect!</p>';
                }
                
                completeHTML += '<button onclick="location.reload()" class="submit-btn" style="margin-top:20px;">Start New Quiz</button>';
                completeHTML += '</div>';
                document.getElementById('quiz').innerHTML = completeHTML;
                return;
            }
            
            const w = words[current];
            const isReverse = mode === 'gr-it';
            const question = isReverse ? w.greek : w.italian;
            const answer = isReverse ? w.italian : w.greek;
            
            const progressPercent = (current / words.length) * 100;
            
            let html = '<div class="slide-in">';
            html += '<div class="progress-container">';
            html += '<div class="progress-bar" style="width:' + progressPercent + '%"></div>';
            html += '</div>';
            html += '<div class="progress-text">Question ' + (current+1) + ' of ' + words.length + ' • Score: ' + score + '</div>';
            html += '</div>';
            
            if (mode === 'mc') {
                html += '<div class="card">' + escapeHtml(question) + 
                        '<span class="speaker" onclick="playAudio(' + JSON.stringify(w.italian) + ')">🔊</span></div>';
                html += '<div class="options">';
                
                // Get random wrong answers (not sequential)
                const options = [answer];
                const availableWords = words.filter((x, i) => i !== current);
                
                // Shuffle available words and take first 3
                const shuffled = availableWords.sort(() => Math.random() - 0.5);
                for (let i = 0; i < 3 && i < shuffled.length; i++) {
                    const wrongAnswer = isReverse ? shuffled[i].italian : shuffled[i].greek;
                    // Avoid duplicates
                    if (!options.includes(wrongAnswer)) {
                        options.push(wrongAnswer);
                    }
                }
                
                // Shuffle the final options so correct answer isn't always first
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
            const currentWord = words[current];
            
            // Record result in database
            recordResult(currentWord.italian, isCorrect, mode);
            
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
            
            // Record result in database
            recordResult(italianWord, isCorrect, 'mc');
            
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
                let completeHTML = '<div class="fade-in" style="text-align:center; padding:40px;">';
                completeHTML += '<h2 style="color:var(--text-light); font-size:2.5em;">📚 Sentence Practice Complete!</h2>';
                completeHTML += '<p style="color:var(--text-light); margin:30px 0;">Great work practicing with real sentences!</p>';
                completeHTML += '<button onclick="location.reload()" class="submit-btn">Start New Practice</button>';
                completeHTML += '</div>';
                document.getElementById('quiz').innerHTML = completeHTML;
                celebrate();
                return;
            }
            
            // Determine direction based on mode
            let direction;
            if (mode === 'sentence-gr-it') {
                direction = 'gr-it';
            } else if (mode === 'sentence-it-gr') {
                direction = 'it-gr';
            } else {
                // Fallback: random for old 'sentence' mode
                direction = Math.random() > 0.5 ? 'it-gr' : 'gr-it';
            }
            const res = await fetch('/api/sentence?direction=' + direction);
            const data = await res.json();
            currentSentence = data;
            
            const targetLang = direction === 'it-gr' ? 'Greek' : 'Italian';
            const targetPlaceholder = direction === 'it-gr' ? 'Translate to Greek...' : 'Μετάφραση στα Ιταλικά...';
            
            const progressPercent = (current / 5) * 100;
            
            let html = '<div class="slide-in">';
            html += '<div class="progress-container">';
            html += '<div class="progress-bar" style="width:' + progressPercent + '%"></div>';
            html += '</div>';
            html += '<div class="progress-text">Sentence ' + (current+1) + ' of 5</div>';
            html += '</div>';
            html += '<div style="text-align:center; margin:15px 0;">';
            html += '<span style="background:#667eea; color:white; padding:6px 15px; border-radius:20px; font-size:0.85em;">';
            html += direction === 'it-gr' ? '🇮🇹 Italian → Greek 🇬🇷' : '🇬🇷 Greek → Italian 🇮🇹';
            html += '</span></div>';
            html += '<div class="card fade-in">' + escapeHtml(data.source) + '</div>';
            html += '<div style="text-align:center; margin:10px 0; color:#667eea; font-size:0.9em; font-style:italic;">';
            html += '📝 Grammar: ' + escapeHtml(data.pattern) + '</div>';
            html += '<div class="answer">';
            html += '<textarea id="translation" class="sentence-input" placeholder="' + targetPlaceholder + '"></textarea><br>';
            html += '<button onclick="checkSentence()" class="submit-btn">Show Translation</button>';
            html += '</div><div id="result"></div>';
            html += '<div style="margin-top:15px; padding:12px; background:#f5f5f5; border-radius:8px; font-size:14px; color:#666;">';
            html += '<strong>Words:</strong> ' + escapeHtml(data.words);
            html += '</div>';
            
            document.getElementById('quiz').innerHTML = html;
        }
        
        function checkSentence() {
            const userTrans = document.getElementById('translation').value.trim();
            const targetLang = currentSentence.direction === 'it-gr' ? 'Greek' : 'Italian';
            
            let feedback = '<div style="margin-top:20px; animation: fadeIn 0.5s;">';
            
            // User's translation
            feedback += '<div style="margin-bottom:15px;">';
            feedback += '<p style="color:#2196F3; font-weight:bold; margin-bottom:8px;">📝 Your translation:</p>';
            feedback += '<p style="background:#f0f0f0; padding:15px; border-radius:8px; font-size:16px; border-left:4px solid #2196F3;">' + 
                       (userTrans ? escapeHtml(userTrans) : '<i style="color:#999;">No translation provided</i>') + '</p>';
            feedback += '</div>';
            
            // Correct translation
            feedback += '<div style="margin-bottom:15px;">';
            feedback += '<p style="color:#4CAF50; font-weight:bold; margin-bottom:8px;">✅ Correct translation:</p>';
            feedback += '<p style="background:#e8f5e9; padding:15px; border-radius:8px; font-size:16px; font-weight:500; border-left:4px solid #4CAF50;">' + 
                       escapeHtml(currentSentence.translation) + '</p>';
            feedback += '</div>';
            
            // Word-by-word reference
            feedback += '<div style="margin-bottom:15px;">';
            feedback += '<p style="color:#666; font-weight:bold; margin-bottom:8px;">📚 Word reference:</p>';
            feedback += '<p style="background:#fff9e6; padding:12px; border-radius:8px; font-size:14px; border-left:4px solid #FFC107;">' + 
                       escapeHtml(currentSentence.words) + '</p>';
            feedback += '</div>';
            
            feedback += '<button onclick="nextSentence()" class="submit-btn" style="margin-top:15px; width:100%;">Next Sentence →</button>';
            feedback += '</div>';
            
            document.getElementById('result').innerHTML = feedback;
            document.querySelector('textarea').disabled = true;
            document.querySelector('button.submit-btn:not([onclick*="next"])').disabled = true;
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
        from database.vocab_db import get_weak_words
        from datetime import datetime
        import sqlite3
        
        n = int(request.args.get('n', 10))
        words = load_vocabulary()
        
        # Try to get words intelligently based on spaced repetition
        try:
            conn = sqlite3.connect('vocab_progress.db')
            c = conn.cursor()
            
            # Get words due for review (50% of selection)
            due_count = n // 2
            now = datetime.now()
            c.execute("""SELECT word_italian 
                         FROM word_stats 
                         WHERE next_review <= ? 
                         ORDER BY next_review ASC 
                         LIMIT ?""", (now, due_count))
            due_words = [row[0] for row in c.fetchall()]
            
            # Get weak words (30% of selection)
            weak_count = int(n * 0.3)
            c.execute("""SELECT word_italian 
                         FROM word_stats 
                         WHERE (CAST(times_correct AS FLOAT) / times_seen) < 0.7 
                         AND times_seen >= 2
                         ORDER BY (CAST(times_correct AS FLOAT) / times_seen) ASC 
                         LIMIT ?""", (weak_count,))
            weak_words = [row[0] for row in c.fetchall()]
            
            conn.close()
            
            # Combine with random words to fill the rest
            selected_italian = set(due_words + weak_words)
            selected = [w for w in words if w['italian'] in selected_italian]
            
            # Fill remaining slots with random words
            remaining = n - len(selected)
            if remaining > 0:
                available = [w for w in words if w['italian'] not in selected_italian]
                if available:
                    selected.extend(random.sample(available, min(remaining, len(available))))
            
            # If not enough intelligent words, fall back to random
            if len(selected) < n:
                selected = random.sample(words, min(n, len(words)))
            
        except Exception:
            # Fallback to random selection if database not initialized
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
        from app.greek_sentence_generator import generate_greek_sentence
        
        words = load_vocabulary()
        direction = request.args.get('direction', 'it-gr')  # 'it-gr' or 'gr-it'
        
        if direction == 'gr-it':
            # Greek to Italian
            result = generate_greek_sentence(words)
            
            # Format word meanings for display
            word_meanings = []
            for word_gr in result['words_used']:
                matching = [w for w in words if w['greek'].lower() == word_gr.lower()]
                if matching:
                    word_meanings.append(f"{word_gr}={matching[0]['italian']}")
                else:
                    word_meanings.append(word_gr)
            
            return jsonify({
                "source": result['greek'],
                "translation": result['italian'],
                "words": ", ".join(word_meanings),
                "pattern": result['pattern'],
                "direction": 'gr-it'
            })
        else:
            # Italian to Greek (original)
            result = generate_smart_sentence(words)
            
            # Format word meanings for display
            word_meanings = []
            greek_translation_parts = []
            
            for word_it in result['words_used']:
                matching = [w for w in words if w['italian'].lower() == word_it.lower()]
                if matching:
                    word_meanings.append(f"{word_it}={matching[0]['greek']}")
                    greek_translation_parts.append(matching[0]['greek'])
                else:
                    word_meanings.append(word_it)
                    greek_translation_parts.append('?')
            
            # Create approximate Greek translation
            greek_translation = ' '.join(greek_translation_parts) if greek_translation_parts else 'Μετάφραση'
            
            return jsonify({
                "source": result['italian'],
                "translation": greek_translation,
                "words": ", ".join(word_meanings),
                "pattern": result['pattern'],
                "direction": 'it-gr'
            })
    
    @app.route('/api/stats')
    def get_stats_api():
        """API endpoint for detailed statistics."""
        from database.vocab_db import get_detailed_stats
        stats = get_detailed_stats()
        return jsonify(stats)
    
    @app.route('/api/record', methods=['POST'])
    def record_result():
        """Record quiz result for spaced repetition."""
        from database.vocab_db import record_quiz_result, init_db
        
        try:
            init_db()  # Ensure database exists
            data = request.get_json()
            word = data.get('word')
            correct = data.get('correct', False)
            quiz_type = data.get('quiz_type', 'web')
            
            if word:
                record_quiz_result(word, correct, quiz_type)
                return jsonify({"success": True})
            else:
                return jsonify({"success": False, "error": "No word provided"}), 400
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
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
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .stat-label {
            font-size: 0.95em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.05);
            }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        .slide-in {
            animation: slideIn 0.5s ease-out;
        }
        
        .pulse {
            animation: pulse 0.6s ease-in-out;
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
                    <span class="speaker-icon" onclick="playAudio()">🔊</span>
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
            if (currentWord) {
                try {
                    const response = await fetch(`/api/speak?word=${encodeURIComponent(currentWord.italian)}`);
                    const data = await response.json();
                    if (data.audio && data.audio.length > 0) {
                        const audio = new Audio('data:audio/mp3;base64,' + data.audio);
                        audio.play().catch(e => console.log('Audio play error:', e));
                    }
                } catch (e) {
                    console.log('Audio fetch failed:', e);
                }
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
                
                // Play audio for both IT→GR and GR→IT modes
                await playAudio();
                
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
