#!/usr/bin/env python3
"""
Web interface for vocabulary practice using Flask.
"""
import random
from app.vocab_core import load_vocabulary
from app.vocab_audio import get_audio_base64
from app.grammar_loader import get_exercises, check_answer as grammar_check_answer, GRAMMAR_CATEGORIES


def launch_web():
    """Launch Flask web interface."""
    try:
        from flask import Flask, request, jsonify, send_from_directory
        import json
        import os
    except ImportError:
        print("Flask not installed. Run: pip install flask")
        return
    
    app = Flask(__name__)
    WEB_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(WEB_DIR)
    
    HTML_REMOVED = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Italian Vocabulary Practice</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js" defer></script>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js" defer></script>
    <style>
        :root {
            --bg: #f5f2ed;
            --bg-accent: #e8e2d9;
            --card: #ffffff;
            --text: #1c1917;
            --text-muted: #57534e;
            --primary: #b45309;
            --primary-hover: #92400e;
            --success: #15803d;
            --success-bg: #dcfce7;
            --error: #b91c1c;
            --error-bg: #fee2e2;
            --border: rgba(0,0,0,0.08);
            --shadow: 0 1px 3px rgba(0,0,0,0.06);
            --shadow-lg: 0 10px 40px -10px rgba(0,0,0,0.12);
            --radius: 14px;
            --radius-sm: 10px;
        }
        body.dark-mode {
            --bg: #1c1917;
            --bg-accent: #292524;
            --card: #292524;
            --text: #fafaf9;
            --text-muted: #a8a29e;
            --primary: #f59e0b;
            --primary-hover: #fbbf24;
            --success: #4ade80;
            --success-bg: rgba(74, 222, 128, 0.15);
            --error: #f87171;
            --error-bg: rgba(248, 113, 113, 0.15);
            --border: rgba(255,255,255,0.08);
            --shadow: 0 1px 3px rgba(0,0,0,0.3);
            --shadow-lg: 0 10px 40px -10px rgba(0,0,0,0.4);
        }
        * { box-sizing: border-box; }
        body {
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            max-width: 640px;
            margin: 0 auto;
            padding: 24px 20px 48px;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            line-height: 1.5;
            transition: background 0.25s ease, color 0.25s ease;
        }
        h1 {
            font-size: 1.75rem;
            font-weight: 700;
            text-align: center;
            color: var(--text);
            margin: 0 0 6px;
            letter-spacing: -0.02em;
        }
        .subtitle {
            text-align: center;
            color: var(--text-muted);
            font-size: 0.95rem;
            font-weight: 500;
            margin-bottom: 32px;
        }
        .dark-mode-toggle {
            position: fixed;
            top: 16px;
            right: 16px;
            width: 44px;
            height: 44px;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: var(--card);
            color: var(--text);
            cursor: pointer;
            font-size: 1.25rem;
            box-shadow: var(--shadow);
            transition: transform 0.2s, box-shadow 0.2s;
            z-index: 1000;
        }
        .dark-mode-toggle:hover {
            transform: scale(1.05);
            box-shadow: var(--shadow-lg);
        }
        .menu {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin-bottom: 24px;
        }
        .menu button {
            font-family: inherit;
            font-size: 0.9rem;
            font-weight: 600;
            padding: 12px 20px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
            background: var(--card);
            color: var(--text);
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: var(--shadow);
        }
        .menu button:hover {
            background: var(--primary);
            color: #fff;
            border-color: var(--primary);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(180, 83, 9, 0.25);
        }
        body.dark-mode .menu button:hover {
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        }
        .menu button.stats-btn {
            background: var(--text-muted);
            color: var(--card);
            border-color: transparent;
        }
        .menu button.stats-btn:hover {
            background: var(--text);
            color: var(--card);
        }
        #quiz {
            background: var(--card);
            padding: 28px 24px;
            border-radius: var(--radius);
            box-shadow: var(--shadow-lg);
            min-height: 360px;
            border: 1px solid var(--border);
            animation: fadeIn 0.35s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .progress-container {
            height: 6px;
            background: var(--bg-accent);
            border-radius: 999px;
            margin: 0 0 12px;
            overflow: hidden;
        }
        .progress-bar {
            height: 100%;
            background: var(--primary);
            border-radius: 999px;
            transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .progress-text {
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 16px;
        }
        .card {
            padding: 32px 24px;
            text-align: center;
            font-size: 1.75rem;
            font-weight: 600;
            margin: 16px 0;
            background: var(--bg-accent);
            border-radius: var(--radius);
            border: 1px solid var(--border);
            letter-spacing: -0.01em;
        }
        .flashcard {
            cursor: pointer;
            user-select: none;
            transition: transform 0.2s ease;
        }
        .flashcard:hover {
            transform: scale(1.01);
        }
        .answer { margin: 24px 0; text-align: center; }
        input {
            font-family: inherit;
            font-size: 1.1rem;
            padding: 14px 18px;
            width: 100%;
            max-width: 360px;
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            background: var(--card);
            color: var(--text);
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(180, 83, 9, 0.15);
        }
        body.dark-mode input:focus {
            box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
        }
        button {
            font-family: inherit;
            font-size: 0.9rem;
            font-weight: 600;
            padding: 12px 24px;
            margin: 6px;
            border-radius: var(--radius-sm);
            border: none;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .submit-btn {
            background: var(--success);
            color: #fff;
        }
        .submit-btn:hover {
            filter: brightness(1.08);
            transform: translateY(-1px);
        }
        .correct {
            color: var(--success);
            font-weight: 700;
            font-size: 1.15rem;
            animation: bounceIn 0.4s ease;
        }
        .wrong {
            color: var(--error);
            font-weight: 700;
            font-size: 1.1rem;
        }
        @keyframes bounceIn {
            0% { transform: scale(0.9); opacity: 0; }
            60% { transform: scale(1.03); }
            100% { transform: scale(1); opacity: 1; }
        }
        .options {
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 480px;
            margin: 20px auto;
        }
        .option-btn {
            font-family: inherit;
            padding: 16px 20px;
            font-size: 1rem;
            font-weight: 500;
            text-align: left;
            background: var(--bg-accent);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            color: var(--text);
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .option-btn:hover {
            background: var(--primary);
            color: #fff;
            border-color: var(--primary);
            transform: translateX(4px);
        }
        .speaker {
            cursor: pointer;
            font-size: 1.4rem;
            margin-left: 10px;
            opacity: 0.85;
            transition: transform 0.2s, opacity 0.2s;
            display: inline-block;
        }
        .speaker:hover { opacity: 1; transform: scale(1.15); }
        .speaker:active { transform: scale(0.95); }
        .controls { text-align: center; margin: 20px 0; }
        .sentence-input {
            width: 100%;
            min-height: 88px;
            font-family: inherit;
            font-size: 1rem;
            padding: 14px 18px;
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            background: var(--card);
            color: var(--text);
            resize: vertical;
        }
        .sentence-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(180, 83, 9, 0.15);
        }
        footer {
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-top: 32px;
        }
        .stat-card {
            background: var(--card);
            padding: 20px;
            border-radius: var(--radius);
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
            text-align: center;
        }
        .stat-number { font-size: 1.75rem; font-weight: 700; color: var(--primary); }
        .stat-label { font-size: 0.8rem; color: var(--text-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.04em; margin-top: 4px; }
        .panel {
            background: var(--card);
            padding: 24px;
            border-radius: var(--radius);
            border: 1px solid var(--border);
            margin-bottom: 20px;
        }
        .charts-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 20px;
        }
        .charts-grid .panel {
            min-width: 0;
            overflow: hidden;
        }
        .chart-wrapper {
            position: relative;
            width: 100%;
            height: 220px;
            min-width: 0;
            min-height: 0;
            overflow: hidden;
        }
        .chart-wrapper canvas {
            max-width: 100% !important;
            max-height: 100% !important;
            display: block;
        }
        @media (max-width: 520px) {
            .charts-grid { grid-template-columns: 1fr; }
        }
        .home-logo { display: block; max-width: 200px; height: auto; margin: 0 auto 20px; border-radius: var(--radius); box-shadow: var(--shadow-lg); }
        .section-title { font-size: 1rem; font-weight: 700; color: var(--text); margin-bottom: 12px; }
        .panel table { width: 100%; border-collapse: collapse; }
        .panel th, .panel td { padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); }
        .panel th { font-size: 0.75rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }
        .panel td { font-size: 0.9rem; }
    </style>
</head>
<body>
    <script>
    (function() {
        "use strict";
        window.goVocab = function() {
            var h = document.getElementById("homeMenu"), g = document.getElementById("grammarSubMenu"), v = document.getElementById("vocabSubMenu"), q = document.getElementById("quiz");
            if (h) h.style.display = "none"; if (g) g.style.display = "none"; if (v) v.style.display = "flex"; if (q) q.innerHTML = "";
        };
        window.goGrammar = function() {
            var h = document.getElementById("homeMenu"), g = document.getElementById("vocabSubMenu"), v = document.getElementById("grammarSubMenu"), q = document.getElementById("quiz");
            if (h) h.style.display = "none"; if (g) g.style.display = "none"; if (v) v.style.display = "flex"; if (q) q.innerHTML = "";
        };
        window.goBack = function() {
            var h = document.getElementById("homeMenu"), g = document.getElementById("grammarSubMenu"), v = document.getElementById("vocabSubMenu"), q = document.getElementById("quiz");
            if (h) h.style.display = "flex"; if (g) g.style.display = "none"; if (v) v.style.display = "none"; if (q) q.innerHTML = "";
        };
        window.goStats = function() {
            var h = document.getElementById("homeMenu"), g = document.getElementById("grammarSubMenu"), v = document.getElementById("vocabSubMenu"), q = document.getElementById("quiz");
            if (h) h.style.display = "none"; if (g) g.style.display = "none"; if (v) v.style.display = "none";
            if (q) q.innerHTML = "<div style=\"text-align:center;padding:40px;\">Loading statistics...</div>";
            fetch("/api/stats").then(function(r) { return r.json(); }).then(function(stats) {
                var acc = stats.accuracy != null ? Number(stats.accuracy) * 100 : 0;
                var html = "<div style=\"max-width:1200px;margin:0 auto;\"><button onclick=\"window.goBack()\" class=\"submit-btn\" style=\"margin-bottom:20px;\">Back to Home</button>";
                html += "<div style=\"display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:24px;\">";
                html += "<div class=\"stat-card\"><div class=\"stat-number\">" + (stats.total_words || 0) + "</div><div class=\"stat-label\">Words Practiced</div></div>";
                html += "<div class=\"stat-card\"><div class=\"stat-number\">" + (stats.total_attempts || 0) + "</div><div class=\"stat-label\">Total Attempts</div></div>";
                html += "<div class=\"stat-card\"><div class=\"stat-number\">" + acc.toFixed(1) + "%</div><div class=\"stat-label\">Accuracy</div></div></div></div>";
                if (q) q.innerHTML = html;
            }).catch(function() { if (q) q.innerHTML = "<p>Error loading stats.</p><button onclick=\"window.goBack()\">Back to Home</button>"; });
        };
        if (typeof console !== "undefined" && console.log) console.log("Home menu ready");
    })();
    </script>
    <button class="dark-mode-toggle" onclick="toggleDarkMode()" title="Toggle dark mode" aria-label="Toggle dark mode">🌙</button>
    <img src="/italian.webp" alt="Italian" class="home-logo" />
    <h1>Italian Trainer</h1>
    <p class="subtitle">Choose practice type</p>
    <div class="menu" id="homeMenu">
        <button type="button" onclick="window.goVocab()">Vocabulary</button>
        <button type="button" onclick="window.goGrammar()">Grammar</button>
        <button type="button" class="stats-btn" onclick="window.goStats()">Statistics</button>
    </div>
    <div class="menu" id="vocabSubMenu" style="display:none;">
        <button onclick="startMode('it-gr')">Italian → Greek</button>
        <button onclick="startMode('gr-it')">Greek → Italian</button>
        <button onclick="startMode('mc')">Multiple choice (IT→GR)</button>
        <button onclick="startMode('mc-gr-it')">Multiple choice (GR→IT)</button>
        <button onclick="window.goBack()" style="background:var(--text-muted); color:var(--card);">← Back to Home</button>
    </div>
    <div class="menu" id="grammarSubMenu" style="display:none;">
        <button onclick="startGrammarCategory('verbs_present')">Ρήματα ενεστώτας (όλα τα πρόσωπα)</button>
        <button onclick="startGrammarCategory('articles')">Άρθρα οριστικά και αόριστα</button>
        <button onclick="startGrammarCategory('avercela_avere_essere_esserci')">avercela, avere, essere, esserci</button>
        <button onclick="startGrammarCategory('irregular_nouns')">Ανώμαλα ουσιαστικά</button>
        <button onclick="window.goBack()" style="background:var(--text-muted); color:var(--card);">← Back to Home</button>
    </div>
    <div id="quiz"></div>
    <footer>Practice a little every day.</footer>
    
    <script>
        let words = [];
        let current = 0;
        let score = 0;
        let mode = '';
        
        function showVocabMenu() { if (window.goVocab) window.goVocab(); }
        function showGrammarMenu() { if (window.goGrammar) window.goGrammar(); }
        function backToHome() { if (window.goBack) window.goBack(); }
        
        // Dark mode functionality
        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDark);
            document.querySelector('.dark-mode-toggle').textContent = isDark ? '☀️' : '🌙';
        }
        
        // Load dark mode preference
        try {
            if (localStorage.getItem('darkMode') === 'true') {
                document.body.classList.add('dark-mode');
                var t = document.querySelector('.dark-mode-toggle');
                if (t) t.textContent = '\u2600\uFE0F';
            }
        } catch (e) { console.log('Dark mode init:', e); }
        
        // Confetti celebration
        function celebrate() {
            const duration = 3000;
            const end = Date.now() + duration;
            
            const colors = ['#b45309', '#15803d', '#1c1917', '#f59e0b', '#92400e'];
            
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
        
        function showVocabMenu() {
            document.getElementById('homeMenu').style.display = 'none';
            document.getElementById('grammarSubMenu').style.display = 'none';
            document.getElementById('vocabSubMenu').style.display = 'flex';
            document.getElementById('quiz').innerHTML = '';
        }
        function showGrammarMenu() {
            document.getElementById('homeMenu').style.display = 'none';
            document.getElementById('vocabSubMenu').style.display = 'none';
            document.getElementById('grammarSubMenu').style.display = 'flex';
            document.getElementById('quiz').innerHTML = '';
        }
        function backToHome() {
            document.getElementById('homeMenu').style.display = 'flex';
            document.getElementById('vocabSubMenu').style.display = 'none';
            document.getElementById('grammarSubMenu').style.display = 'none';
            document.getElementById('quiz').innerHTML = '';
        }
        async function showStats() {
            document.getElementById('homeMenu').style.display = 'none';
            document.getElementById('vocabSubMenu').style.display = 'none';
            document.getElementById('grammarSubMenu').style.display = 'none';
            document.getElementById('quiz').innerHTML = '<div style="text-align:center;padding:40px;">Loading statistics... ⏳</div>';
            
            try {
                const res = await fetch('/api/stats');
                const stats = await res.json();
                
                let html = '<div style="max-width:1200px; margin:0 auto;">';
                html += '<button onclick="backToHome()" class="submit-btn" style="margin-bottom:20px; background:var(--text); color:var(--card);">← Back to Home</button>';
                const safe = (v, d) => (v != null && v !== '') ? v : (d != null ? d : 0);
                html += '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:16px; margin-bottom:24px;">';
                html += `<div class="stat-card">
                    <div class="stat-number">${safe(stats.total_words, 0)}</div>
                    <div class="stat-label">Words Practiced</div>
                </div>`;
                html += `<div class="stat-card">
                    <div class="stat-number">${safe(stats.total_attempts, 0)}</div>
                    <div class="stat-label">Total Attempts</div>
                </div>`;
                html += `<div class="stat-card">
                    <div class="stat-number">${(stats.accuracy != null ? Number(stats.accuracy) : 0).toFixed(1)}%</div>
                    <div class="stat-label">Overall Accuracy</div>
                </div>`;
                html += `<div class="stat-card">
                    <div class="stat-number">${safe(stats.best_streak, 0)}</div>
                    <div class="stat-label">Best Streak</div>
                </div>`;
                html += `<div class="stat-card">
                    <div class="stat-number">${safe(stats.due_for_review, 0)}</div>
                    <div class="stat-label">Due for Review</div>
                </div>`;
                html += '</div>';
                
                // Charts Section
                if (stats.daily_performance.length > 0 || stats.quiz_types.length > 0) {
                    html += '<div class="charts-grid">';
                    if (stats.daily_performance.length > 0) {
                        html += '<div class="panel"><h2 class="section-title">Daily accuracy</h2><div class="chart-wrapper"><canvas id="dailyChart"></canvas></div></div>';
                    }
                    if (stats.quiz_types.length > 0) {
                        html += '<div class="panel"><h2 class="section-title">By quiz type</h2><div class="chart-wrapper"><canvas id="quizTypeChart"></canvas></div></div>';
                    }
                    html += '</div>';
                }
                html += '<div class="panel"><h2 class="section-title">Top words</h2>';
                if (stats.top_words.length > 0) {
                    html += '<table><tr><th>Word</th><th>Success</th><th>Streak</th><th>EF</th></tr>';
                    stats.top_words.forEach(w => {
                        const rate = w.rate != null ? Number(w.rate) : 0;
                        const ef = w.ef != null ? Number(w.ef) : 0;
                        html += `<tr><td>${escapeHtml(w.word)}</td><td style="text-align:center; color:var(--success); font-weight:600;">${rate.toFixed(0)}%</td><td style="text-align:center;">${w.streak ?? ''}</td><td style="text-align:center;">${ef.toFixed(2)}</td></tr>`;
                    });
                    html += '</table>';
                } else {
                    html += '<p style="color:var(--text-muted);">No data yet. Start practicing!</p>';
                }
                html += '</div>';
                html += '<div class="panel"><h2 class="section-title">Words to review</h2>';
                if (stats.weak_words.length > 0) {
                    html += '<table><tr><th>Word</th><th>Seen</th><th>Rate</th><th>EF</th></tr>';
                    stats.weak_words.forEach(w => {
                        const rate = w.rate != null ? Number(w.rate) : 0;
                        const ef = w.ef != null ? Number(w.ef) : 0;
                        html += `<tr><td>${escapeHtml(w.word)}</td><td style="text-align:center;">${w.seen ?? ''}</td><td style="text-align:center; color:var(--error); font-weight:600;">${rate.toFixed(0)}%</td><td style="text-align:center;">${ef.toFixed(2)}</td></tr>`;
                    });
                    html += '</table><p style="margin-top:12px; padding:12px; background:var(--success-bg); border-radius:var(--radius-sm); font-size:0.9rem;">Tip: run <code style="background:var(--bg-accent); padding:2px 6px; border-radius:4px;">python vocab.py focus</code> to practice these words.</p>';
                } else {
                    html += '<p style="color:var(--text-muted);">No weak words — nice!</p>';
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
                                        data: stats.daily_performance.map(d => d.accuracy != null ? Number(d.accuracy) : 0),
                                        borderColor: '#b45309',
                                        backgroundColor: 'rgba(180, 83, 9, 0.12)',
                                        tension: 0.4,
                                        fill: true,
                                        pointRadius: 5,
                                        pointBackgroundColor: '#b45309',
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
                                                    const acc = dataPoint && dataPoint.accuracy != null ? Number(dataPoint.accuracy) : 0;
                                                    return [
                                                        `Accuracy: ${acc.toFixed(1)}%`,
                                                        `Attempts: ${dataPoint ? dataPoint.attempts : 0}`,
                                                        `Correct: ${dataPoint ? dataPoint.correct : 0}`
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
                            const colors = stats.quiz_types.map(qt => {
                                const a = qt.accuracy != null ? Number(qt.accuracy) : 0;
                                return a >= 70 ? '#15803d' : a >= 50 ? '#b45309' : '#b91c1c';
                            });
                            new Chart(quizTypeCtx, {
                                type: 'bar',
                                data: {
                                    labels: stats.quiz_types.map(qt => (qt.type || '').charAt(0).toUpperCase() + (qt.type || '').slice(1)),
                                    datasets: [{
                                        label: 'Accuracy %',
                                        data: stats.quiz_types.map(qt => qt.accuracy != null ? Number(qt.accuracy) : 0),
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
                                                    const acc = qt && qt.accuracy != null ? Number(qt.accuracy) : 0;
                                                    return [
                                                        `Accuracy: ${acc.toFixed(1)}%`,
                                                        `Attempts: ${qt ? qt.count : 0}`,
                                                        `Correct: ${qt ? qt.correct : 0}`
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
        window.showVocabMenu = showVocabMenu;
        window.showGrammarMenu = showGrammarMenu;
        window.showStats = showStats;
        (function bindHomeNow() {
            var vocab = document.getElementById('btnVocab');
            var gram = document.getElementById('btnGrammar');
            var stats = document.getElementById('btnStats');
            if (vocab) vocab.onclick = showVocabMenu;
            if (gram) gram.onclick = showGrammarMenu;
            if (stats) stats.onclick = showStats;
        })();
        
        async function startMode(m) {
            console.log('Starting mode:', m);
            mode = m;
            current = 0;
            score = 0;
            totalAnswered = 0;
            document.getElementById('vocabSubMenu').style.display = 'none';
            try {
                const n = (mode === 'mc' || mode === 'mc-gr-it') ? 300 : 10;
                const res = await fetch('/api/words?n=' + n);
                words = await res.json();
                console.log('Loaded words:', words.length);
                showQuestion();
            } catch(e) {
                console.error('Error loading words:', e);
                document.getElementById('quiz').innerHTML = '<p style="color:red;">Error loading vocabulary. Check console.</p>';
            }
        }
        
        let totalAnswered = 0;
        
        async function playAudio(word) {
            try {
                const res = await fetch('/api/speak?word=' + encodeURIComponent(word));
                const data = await res.json();
                if (res.ok && data.audio && data.audio.length > 0) {
                    const audio = new Audio('data:audio/mp3;base64,' + data.audio);
                    audio.play().catch(() => fallbackSpeak(word));
                } else {
                    fallbackSpeak(word);
                }
            } catch(e) {
                fallbackSpeak(word);
            }
        }
        
        function fallbackSpeak(word) {
            if (!window.speechSynthesis) return;
            const u = new SpeechSynthesisUtterance(word);
            u.lang = 'it-IT';
            u.rate = 0.9;
            window.speechSynthesis.speak(u);
        }
        
        async function showQuestion() {
            const isMC = mode === 'mc' || mode === 'mc-gr-it';
            
            if (current >= words.length) {
                if (isMC && totalAnswered > 0) {
                    const percentage = Math.round(score*100/totalAnswered);
                    let completeHTML = '<div style="text-align:center; padding:32px 24px;">';
                    completeHTML += '<h2 style="color:var(--text); font-size:1.5rem; margin-bottom:16px;">Session done</h2>';
                    completeHTML += '<div style="font-size:3rem; font-weight:700; color:var(--primary); margin:20px 0;">' + score + '/' + totalAnswered + '</div>';
                    completeHTML += '<p style="color:var(--text-muted); margin-bottom:24px;">' + percentage + '% correct</p>';
                    completeHTML += '<button onclick="loadMoreWords()" class="submit-btn" style="margin:8px;">More words</button>';
                    completeHTML += '<button onclick="location.reload()" style="margin:8px; background:var(--text); color:#fff;" class="submit-btn">Menu</button>';
                    completeHTML += '</div>';
                    document.getElementById('quiz').innerHTML = completeHTML;
                    return;
                }
                const percentage = words.length ? Math.round(score*100/words.length) : 0;
                let completeHTML = '<div style="text-align:center; padding:32px 24px;">';
                completeHTML += '<h2 style="color:var(--text); font-size:1.5rem; margin-bottom:16px;">Quiz complete</h2>';
                completeHTML += '<div style="font-size:3rem; font-weight:700; color:var(--primary); margin:20px 0;">' + score + '/' + words.length + '</div>';
                completeHTML += '<p style="color:var(--text-muted); margin-bottom:20px;">' + percentage + '%</p>';
                if (percentage >= 80) {
                    celebrate();
                    completeHTML += '<p style="color:var(--success); font-weight:600; margin:16px 0;">Well done!</p>';
                } else if (percentage >= 60) {
                    completeHTML += '<p style="color:var(--text-muted); margin:16px 0;">Good — keep practicing.</p>';
                } else {
                    completeHTML += '<p style="color:var(--text-muted); margin:16px 0;">Every round helps.</p>';
                }
                completeHTML += '<button onclick="location.reload()" class="submit-btn" style="margin-top:16px;">New quiz</button>';
                completeHTML += '</div>';
                document.getElementById('quiz').innerHTML = completeHTML;
                return;
            }
            
            const w = words[current];
            const isReverse = mode === 'gr-it' || mode === 'mc-gr-it';
            const question = isReverse ? w.greek : w.italian;
            const answer = isReverse ? w.italian : w.greek;
            
            const progressPercent = words.length ? (current / words.length) * 100 : 0;
            
            let html = '<div class="slide-in">';
            html += '<div class="progress-container">';
            html += '<div class="progress-bar" style="width:' + progressPercent + '%"></div>';
            html += '</div>';
            html += '<div class="progress-text">Question ' + (current+1) + (words.length ? ' of ' + words.length : '') + ' • Score: ' + score + '</div>';
            html += '<button onclick="location.reload()" style="margin-left:12px; padding:8px 16px; background:var(--bg-accent); color:var(--text); border:1px solid var(--border); border-radius:var(--radius-sm); cursor:pointer; font-weight:600; font-size:0.85rem;">Stop</button>';
            html += '</div>';
            
            if (isMC) {
                const lang = isReverse ? 'italian' : 'greek';
                const category = (w.category || '').trim();
                let options = [answer];
                try {
                    let url = '/api/mc-options?correct=' + encodeURIComponent(answer) + '&lang=' + lang + '&count=3';
                    if (category) url += '&category=' + encodeURIComponent(category);
                    const optRes = await fetch(url);
                    if (optRes.ok) {
                        const wrongOpts = await optRes.json();
                        if (Array.isArray(wrongOpts)) {
                            wrongOpts.forEach(function(x) {
                                if (x && options.indexOf(x) === -1) options.push(x);
                            });
                        }
                    }
                } catch(e) {
                    console.warn('MC options fetch failed, using batch fallback:', e);
                }
                if (options.length < 4) {
                    const availableWords = words.filter((x, i) => i !== current);
                    for (let i = 0; i < availableWords.length && options.length < 4; i++) {
                        const wrongAnswer = isReverse ? availableWords[i].italian : availableWords[i].greek;
                        if (wrongAnswer && options.indexOf(wrongAnswer) === -1) options.push(wrongAnswer);
                    }
                }
                options.sort(() => Math.random() - 0.5);
                
                html += '<div class="card">' + escapeHtml(question) + 
                        '<span class="speaker" onclick="playAudio(' + JSON.stringify(w.italian) + ')">🔊</span></div>';
                html += '<div class="options">';
                options.forEach((opt) => {
                    html += '<button class="option-btn" data-opt="' + escapeHtml(opt) + 
                            '" data-correct="' + escapeHtml(answer) + 
                            '" data-italian="' + escapeHtml(w.italian) + '">' + escapeHtml(opt) + '</button>';
                });
                html += '</div>';
                document.getElementById('quiz').innerHTML = html;
                document.querySelectorAll('.option-btn').forEach(btn => {
                    btn.onclick = function() {
                        checkMC(this.dataset.opt, this.dataset.correct, this.dataset.italian);
                    };
                });
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
            
            if (!isMC) {
                document.getElementById('quiz').innerHTML = html;
            }
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
            totalAnswered++;
            recordResult(italianWord, isCorrect, 'mc');
            if (isCorrect) score++;
            
            const res = isCorrect ? 
                '<p class="correct">✓ Correct!</p>' : 
                '<p class="wrong">✗ Wrong. Answer: ' + escapeHtml(correct) + '</p>';
            
            document.getElementById('quiz').innerHTML += '<div>' + res + '</div>';
            playAudio(italianWord);
            
            current++;
            setTimeout(showQuestion, 2000);
        }
        
        async function loadMoreWords() {
            try {
                const res = await fetch('/api/words?n=300');
                const more = await res.json();
                words = more;
                current = 0;
                score = 0;
                totalAnswered = 0;
                showQuestion();
            } catch(e) {
                console.error('Load more failed:', e);
            }
        }
        
        // Grammar exercise state
        let grammarExercises = [];
        let grammarIndex = 0;
        let grammarScore = 0;
        let grammarCategory = '';
        
        async function startGrammarCategory(cat) {
            grammarCategory = cat;
            grammarIndex = 0;
            grammarScore = 0;
            document.getElementById('grammarSubMenu').style.display = 'none';
            document.getElementById('quiz').innerHTML = '<div style="text-align:center;padding:24px;">Loading exercises...</div>';
            try {
                const res = await fetch('/api/grammar/exercises?category=' + encodeURIComponent(cat) + '&n=20');
                grammarExercises = await res.json();
                if (!grammarExercises.length) {
                    document.getElementById('quiz').innerHTML = '<p style="color:var(--error);">No exercises for this category.</p><button onclick="backToHome()" class="submit-btn">Back to Home</button>';
                    return;
                }
                showGrammarQuestion();
            } catch(e) {
                document.getElementById('quiz').innerHTML = '<p style="color:var(--error);">Error loading exercises.</p><button onclick="backToHome()" class="submit-btn">Back to Home</button>';
            }
        }
        
        function showGrammarQuestion() {
            if (grammarIndex >= grammarExercises.length) {
                const pct = grammarExercises.length ? Math.round(grammarScore * 100 / grammarExercises.length) : 0;
                let html = '<div style="text-align:center; padding:32px 24px;">';
                html += '<h2 style="color:var(--text); font-size:1.5rem; margin-bottom:16px;">Grammar session done</h2>';
                html += '<div style="font-size:3rem; font-weight:700; color:var(--primary); margin:20px 0;">' + grammarScore + '/' + grammarExercises.length + '</div>';
                html += '<p style="color:var(--text-muted); margin-bottom:24px;">' + pct + '% correct</p>';
                if (pct >= 80) celebrate();
                html += '<button onclick="document.getElementById(\'grammarSubMenu\').style.display=\'flex\'; document.getElementById(\'quiz\').innerHTML=\'\';" class="submit-btn" style="margin:8px;">Back to categories</button>';
                html += '<button onclick="backToHome()" style="margin:8px; background:var(--text); color:var(--card);" class="submit-btn">Back to Home</button>';
                html += '</div>';
                document.getElementById('quiz').innerHTML = html;
                return;
            }
            const ex = grammarExercises[grammarIndex];
            const progressPercent = grammarExercises.length ? (grammarIndex / grammarExercises.length) * 100 : 0;
            let html = '<div class="slide-in">';
            html += '<div class="progress-container"><div class="progress-bar" style="width:' + progressPercent + '%"></div></div>';
            html += '<div class="progress-text">Question ' + (grammarIndex + 1) + ' of ' + grammarExercises.length + ' • Score: ' + grammarScore + '</div>';
            html += '<button onclick="backToHome()" style="margin-left:12px; padding:8px 16px; background:var(--bg-accent); color:var(--text); border:1px solid var(--border); border-radius:var(--radius-sm); cursor:pointer; font-weight:600; font-size:0.85rem;">Stop</button>';
            html += '</div>';
            html += '<div class="card">' + escapeHtml(ex.prompt) + '</div>';
            html += '<div class="answer"><input type="text" id="grammarAnswer" placeholder="Your answer" autofocus />';
            html += '<button onclick="checkGrammarAnswer()" class="submit-btn">Submit</button></div><div id="grammarResult"></div>';
            document.getElementById('quiz').innerHTML = html;
            const inp = document.getElementById('grammarAnswer');
            if (inp) {
                inp.focus();
                inp.addEventListener('keypress', function(e) { if (e.key === 'Enter') checkGrammarAnswer(); });
            }
        }
        
        async function checkGrammarAnswer() {
            const inp = document.getElementById('grammarAnswer');
            if (!inp) return;
            const userAnswer = inp.value.trim();
            const ex = grammarExercises[grammarIndex];
            if (!ex) return;
            try {
                const res = await fetch('/api/grammar/check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ category: grammarCategory, prompt: ex.prompt, user_answer: userAnswer })
                });
                const data = await res.json();
                const resultEl = document.getElementById('grammarResult');
                if (data.correct) {
                    grammarScore++;
                    resultEl.innerHTML = '<p class="correct">✓ Correct!</p>';
                } else {
                    resultEl.innerHTML = '<p class="wrong">✗ Wrong. Correct: ' + escapeHtml(data.correct_answer || '') + '</p>';
                }
                grammarIndex++;
                setTimeout(showGrammarQuestion, 2000);
            } catch(e) {
                document.getElementById('grammarResult').innerHTML = '<p class="wrong">Error checking answer.</p>';
            }
        }
        
    </script>
</body>
</html>
    '''
    
    @app.route('/')
    def index():
        return send_from_directory(WEB_DIR, 'index.html', mimetype='text/html')
    
    @app.route('/italian.webp')
    def serve_italian_logo():
        return send_from_directory(PROJECT_ROOT, 'italian.webp', mimetype='image/webp')
    
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
        
        return jsonify([{"italian": w["italian"], "greek": w["greek"], "category": w.get("category", "other")} for w in selected])
    
    @app.route('/api/mc-options')
    def mc_options():
        """Return wrong options for multiple choice. If category is given, only same-category words (harder)."""
        correct = request.args.get('correct', '')
        lang = request.args.get('lang', 'greek')  # 'greek' or 'italian'
        count = int(request.args.get('count', 3))
        category = request.args.get('category', '').strip() or None
        words = load_vocabulary()
        key = 'greek' if lang == 'greek' else 'italian'
        pool = words
        if category:
            pool = [w for w in words if w.get('category') == category]
        if len(pool) < 4:
            pool = words
        candidates = list(dict.fromkeys([w[key] for w in pool if w[key] != correct]))
        random.shuffle(candidates)
        return jsonify(candidates[:min(count, len(candidates))])
    
    @app.route('/api/speak')
    def speak():
        word = request.args.get('word', '')
        audio_b64 = get_audio_base64(word)
        if audio_b64:
            return jsonify({"audio": audio_b64})
        else:
            return jsonify({"error": "Audio generation failed"}), 500
    
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
    
    @app.route('/api/grammar/exercises')
    def grammar_exercises():
        """Return list of grammar exercises for a category."""
        category = request.args.get('category', '')
        if category not in GRAMMAR_CATEGORIES:
            return jsonify([]), 400
        n = int(request.args.get('n', 20))
        exercises = get_exercises(category, n)
        return jsonify(exercises)
    
    @app.route('/api/grammar/check', methods=['POST'])
    def grammar_check():
        """Check grammar exercise answer. Body: category, prompt, user_answer."""
        data = request.get_json() or {}
        category = data.get('category', '')
        prompt = data.get('prompt', '')
        user_answer = data.get('user_answer', '')
        if category not in GRAMMAR_CATEGORIES:
            return jsonify({"correct": False, "correct_answer": ""}), 400
        correct, correct_answer = grammar_check_answer(category, prompt, user_answer)
        return jsonify({"correct": correct, "correct_answer": correct_answer})
    
    print("\n🌐 Starting web interface at http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    app.run(debug=True, port=5000, host='0.0.0.0')


# WSGI entry point for PythonAnywhere/production deployment
# This allows the Flask app to be imported by WSGI servers
application = None

def create_wsgi_app():
    """Create Flask app for WSGI deployment without app.run()."""
    from flask import Flask, request, jsonify, send_from_directory
    from app.grammar_loader import get_exercises, check_answer as grammar_check_answer, GRAMMAR_CATEGORIES
    import json
    import os
    
    app = Flask(__name__)
    vocabulary = load_vocabulary()
    WSGI_WEB_DIR = os.path.dirname(os.path.abspath(__file__))
    WSGI_PROJECT_ROOT = os.path.dirname(WSGI_WEB_DIR)
    
    WSGI_HTML_REMOVED = '''
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
        
        .home-logo {
            display: block;
            max-width: 200px;
            height: auto;
            margin: 0 auto 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <script>
    (function() {
        window.goVocab = function() {
            var h = document.getElementById("homeMenu"), g = document.getElementById("grammarSubMenu"), v = document.getElementById("vocabSubMenu"), c = document.getElementById("quizContainer"), q = document.getElementById("quizContent");
            if (h) h.style.display = "none"; if (g) g.style.display = "none"; if (v) v.style.display = "block"; if (c) c.classList.remove("active"); if (q) q.innerHTML = "";
        };
        window.goGrammar = function() {
            var h = document.getElementById("homeMenu"), g = document.getElementById("vocabSubMenu"), v = document.getElementById("grammarSubMenu"), c = document.getElementById("quizContainer"), q = document.getElementById("quizContent");
            if (h) h.style.display = "none"; if (g) g.style.display = "none"; if (v) v.style.display = "block"; if (c) c.classList.remove("active"); if (q) q.innerHTML = "";
        };
        window.goBack = function() {
            var h = document.getElementById("homeMenu"), g = document.getElementById("grammarSubMenu"), v = document.getElementById("vocabSubMenu"), c = document.getElementById("quizContainer"), q = document.getElementById("quizContent");
            if (h) h.style.display = "block"; if (g) g.style.display = "none"; if (v) v.style.display = "none"; if (c) c.classList.remove("active"); if (q) q.innerHTML = "";
        };
        window.goStats = function() {
            var h = document.getElementById("homeMenu"), g = document.getElementById("grammarSubMenu"), v = document.getElementById("vocabSubMenu"), c = document.getElementById("quizContainer"), q = document.getElementById("quizContent");
            if (h) h.style.display = "none"; if (g) g.style.display = "none"; if (v) v.style.display = "none"; if (c) c.classList.add("active"); if (q) q.innerHTML = "<p>Loading statistics...</p>";
            fetch("/api/stats").then(function(r) { return r.json(); }).then(function(stats) {
                var acc = stats.accuracy != null ? Number(stats.accuracy) * 100 : 0;
                var html = "<h2>Statistics</h2><p>Words practiced: " + (stats.total_words || 0) + "</p><p>Total attempts: " + (stats.total_attempts || 0) + "</p><p>Accuracy: " + acc.toFixed(1) + "%</p>";
                html += "<button class=\"btn\" onclick=\"window.goBack()\">Back to Home</button>";
                if (q) q.innerHTML = html;
            }).catch(function() { if (q) q.innerHTML = "<p>Error loading stats.</p><button class=\"btn\" onclick=\"window.goBack()\">Back to Home</button>"; });
        };
    })();
    </script>
    <img src="/italian.webp" alt="Italian" class="home-logo" />
    <h1>🇮🇹 Italian Trainer 🇬🇷</h1>
    
    <div class="mode-selector" id="homeMenu">
        <h2>Choose practice type</h2>
        <div class="mode-buttons">
            <button type="button" class="mode-btn" onclick="window.goVocab()">Vocabulary</button>
            <button type="button" class="mode-btn" onclick="window.goGrammar()">Grammar</button>
            <button type="button" class="mode-btn" onclick="window.goStats()">Statistics</button>
        </div>
    </div>
    
    <div class="mode-selector" id="vocabSubMenu" style="display:none;">
        <h2>Vocabulary</h2>
        <div class="mode-buttons">
            <button class="mode-btn" onclick="startMode('it-gr')">Italian → Greek</button>
            <button class="mode-btn" onclick="startMode('gr-it')">Greek → Italian</button>
            <button class="mode-btn" onclick="startMode('mc')">Multiple choice (IT→GR)</button>
            <button class="mode-btn" onclick="startMode('mc-gr-it')">Multiple choice (GR→IT)</button>
            <button class="btn back-btn" onclick="window.goBack()">← Back to Home</button>
        </div>
    </div>
    
    <div class="mode-selector" id="grammarSubMenu" style="display:none;">
        <h2>Grammar</h2>
        <div class="mode-buttons">
            <button class="mode-btn" onclick="startGrammarCategory('verbs_present')">Ρήματα ενεστώτας</button>
            <button class="mode-btn" onclick="startGrammarCategory('articles')">Άρθρα οριστικά και αόριστα</button>
            <button class="mode-btn" onclick="startGrammarCategory('avercela_avere_essere_esserci')">avercela, avere, essere, esserci</button>
            <button class="mode-btn" onclick="startGrammarCategory('irregular_nouns')">Ανώμαλα ουσιαστικά</button>
            <button class="btn back-btn" onclick="window.goBack()">← Back to Home</button>
        </div>
    </div>
    
    <div class="quiz-container" id="quizContainer">
        <button class="btn back-btn" onclick="window.goBack()">← Back to Home</button>
        <div id="quizContent"></div>
    </div>

    <script>
        let currentMode = '';
        let words = [];
        let currentIndex = 0;
        let score = 0;
        let total = 0;
        let currentWord = null;

        function showVocabMenu() { if (window.goVocab) window.goVocab(); }
        function showGrammarMenu() { if (window.goGrammar) window.goGrammar(); }
        function backToHome() { if (window.goBack) window.goBack(); }

        async function showStats() {
            document.getElementById('homeMenu').style.display = 'none';
            document.getElementById('vocabSubMenu').style.display = 'none';
            document.getElementById('grammarSubMenu').style.display = 'none';
            document.getElementById('quizContainer').classList.add('active');
            document.getElementById('quizContent').innerHTML = '<p>Loading statistics...</p>';
            try {
                const res = await fetch('/api/stats');
                const stats = await res.json();
                let html = '<h2>Statistics</h2><p>Words practiced: ' + (stats.total_words || 0) + '</p><p>Total attempts: ' + (stats.total_attempts || 0) + '</p><p>Accuracy: ' + ((stats.accuracy != null ? Number(stats.accuracy) : 0) * 100).toFixed(1) + '%</p>';
                html += '<button class="btn" onclick="backToHome()">Back to Home</button>';
                document.getElementById('quizContent').innerHTML = html;
            } catch (e) {
                document.getElementById('quizContent').innerHTML = '<p>Error loading stats.</p><button class="btn" onclick="backToHome()">Back to Home</button>';
            }
        }

        async function startMode(mode) {
            currentMode = mode;
            currentIndex = 0;
            score = 0;
            total = 0;
            document.getElementById('vocabSubMenu').style.display = 'none';
            document.getElementById('quizContainer').classList.add('active');
            const n = (mode === 'mc' || mode === 'mc-gr-it') ? 50 : 10;
            const response = await fetch('/api/words?n=' + n);
            words = await response.json();
            if (mode === 'it-gr' || mode === 'gr-it') {
                showTranslationQuiz();
            } else if (mode === 'mc' || mode === 'mc-gr-it') {
                showMultipleChoice();
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
            const isReverse = currentMode === 'mc-gr-it';
            const question = isReverse ? currentWord.greek : currentWord.italian;
            const correctAnswer = isReverse ? currentWord.italian : currentWord.greek;
            const others = words.filter((w, i) => words.indexOf(w) !== currentIndex).slice(0, 3);
            const options = [currentWord, ...others].sort(() => Math.random() - 0.5);
            const html = `
                <div class="word-display">
                    <div class="word">${question}</div>
                    ${!isReverse ? '<span class="speaker-icon" onclick="playAudio()">🔊</span>' : ''}
                </div>
                <div class="options" id="options">
                    ${options.map(opt => {
                        const optVal = isReverse ? opt.italian : opt.greek;
                        return `<button class="option-btn" data-opt="${optVal.replace(/"/g, '&quot;')}" data-correct="${correctAnswer.replace(/"/g, '&quot;')}" data-italian="${currentWord.italian.replace(/"/g, '&quot;')}">${optVal}</button>`;
                    }).join('')}
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

        let grammarExercises = [];
        let grammarIndex = 0;
        let grammarScore = 0;
        let grammarCategory = '';

        async function startGrammarCategory(cat) {
            grammarCategory = cat;
            grammarIndex = 0;
            grammarScore = 0;
            document.getElementById('grammarSubMenu').style.display = 'none';
            document.getElementById('quizContainer').classList.add('active');
            document.getElementById('quizContent').innerHTML = '<p>Loading exercises...</p>';
            try {
                const res = await fetch('/api/grammar/exercises?category=' + encodeURIComponent(cat) + '&n=20');
                grammarExercises = await res.json();
                if (!grammarExercises.length) {
                    document.getElementById('quizContent').innerHTML = '<p>No exercises for this category.</p><button class="btn" onclick="backToHome()">Back to Home</button>';
                    return;
                }
                showGrammarQuestion();
            } catch (e) {
                document.getElementById('quizContent').innerHTML = '<p>Error loading exercises.</p><button class="btn" onclick="backToHome()">Back to Home</button>';
            }
        }

        function showGrammarQuestion() {
            if (grammarIndex >= grammarExercises.length) {
                const pct = grammarExercises.length ? Math.round(grammarScore * 100 / grammarExercises.length) : 0;
                let html = '<h2>Grammar session done</h2><div class="score">' + grammarScore + '/' + grammarExercises.length + ' (' + pct + '%)</div>';
                html += '<button class="btn" onclick="document.getElementById(\'grammarSubMenu\').style.display=\'block\'; document.getElementById(\'quizContent\').innerHTML=\'\'; document.getElementById(\'quizContainer\').classList.remove(\'active\');">Back to categories</button> ';
                html += '<button class="btn back-btn" onclick="backToHome()">Back to Home</button>';
                document.getElementById('quizContent').innerHTML = html;
                return;
            }
            const ex = grammarExercises[grammarIndex];
            let html = '<p>Question ' + (grammarIndex + 1) + ' of ' + grammarExercises.length + ' | Score: ' + grammarScore + '</p>';
            html += '<div class="word">' + ex.prompt.replace(/</g, '&lt;') + '</div>';
            html += '<input type="text" id="grammarAnswer" placeholder="Your answer">';
            html += '<button class="btn" onclick="checkGrammarAnswer()">Submit</button>';
            html += '<div class="feedback" id="grammarResult"></div>';
            document.getElementById('quizContent').innerHTML = html;
            document.getElementById('grammarAnswer').focus();
            document.getElementById('grammarAnswer').onkeypress = function(e) { if (e.key === 'Enter') checkGrammarAnswer(); };
        }

        async function checkGrammarAnswer() {
            const inp = document.getElementById('grammarAnswer');
            if (!inp) return;
            const userAnswer = inp.value.trim();
            const ex = grammarExercises[grammarIndex];
            if (!ex) return;
            try {
                const res = await fetch('/api/grammar/check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ category: grammarCategory, prompt: ex.prompt, user_answer: userAnswer })
                });
                const data = await res.json();
                const resultEl = document.getElementById('grammarResult');
                if (data.correct) {
                    grammarScore++;
                    resultEl.innerHTML = '<span class="correct">✓ Correct!</span>';
                } else {
                    resultEl.innerHTML = '<span class="wrong">✗ Wrong. Correct: ' + (data.correct_answer || '').replace(/</g, '&lt;') + '</span>';
                }
                resultEl.className = 'feedback ' + (data.correct ? 'correct' : 'wrong');
                grammarIndex++;
                setTimeout(showGrammarQuestion, 2000);
            } catch (e) {
                document.getElementById('grammarResult').innerHTML = 'Error checking answer.';
            }
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
                    <button class="btn back-btn" onclick="backToHome()">Back to Home</button>
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
        return send_from_directory(WSGI_WEB_DIR, 'index.html', mimetype='text/html')
    
    @app.route('/italian.webp')
    def serve_italian_logo_wsgi():
        return send_from_directory(WSGI_PROJECT_ROOT, 'italian.webp', mimetype='image/webp')
    
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
    
    @app.route('/api/stats')
    def get_stats_wsgi():
        try:
            from database.vocab_db import get_detailed_stats
            return jsonify(get_detailed_stats())
        except Exception:
            return jsonify({"total_words": 0, "total_attempts": 0, "accuracy": 0})
    
    @app.route('/api/grammar/exercises')
    def grammar_exercises_wsgi():
        category = request.args.get('category', '')
        if category not in GRAMMAR_CATEGORIES:
            return jsonify([]), 400
        n = int(request.args.get('n', 20))
        return jsonify(get_exercises(category, n))
    
    @app.route('/api/grammar/check', methods=['POST'])
    def grammar_check_wsgi():
        data = request.get_json() or {}
        category = data.get('category', '')
        prompt = data.get('prompt', '')
        user_answer = data.get('user_answer', '')
        if category not in GRAMMAR_CATEGORIES:
            return jsonify({"correct": False, "correct_answer": ""}), 400
        correct, correct_answer = grammar_check_answer(category, prompt, user_answer)
        return jsonify({"correct": correct, "correct_answer": correct_answer})
    
    return app


# Create the application instance for WSGI
application = create_wsgi_app()
