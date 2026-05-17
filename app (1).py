from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

ENGLISH_FREQ = {
    'a':8.2,'b':1.5,'c':2.8,'d':4.3,'e':12.7,'f':2.2,'g':2.0,
    'h':6.1,'i':7.0,'j':0.15,'k':0.77,'l':4.0,'m':2.4,'n':6.7,
    'o':7.5,'p':1.9,'q':0.10,'r':6.0,'s':6.3,'t':9.1,'u':2.8,
    'v':0.98,'w':2.4,'x':0.15,'y':2.0,'z':0.07
}

COMMON_WORDS = [
    "the","and","that","have","for","not","with","you",
    "this","but","his","from","they","she","what","there",
    "been","one","all","were","when","your","said","each"
]

def caesar_encrypt(text, shift):
    result = ""
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result += chr((ord(ch) - base + shift) % 26 + base)
        else:
            result += ch
    return result

def caesar_decrypt(text, shift):
    return caesar_encrypt(text, 26 - shift)

def vigenere_encrypt(text, key):
    key = ''.join(c for c in key.lower() if c.isalpha())
    if not key: return text
    result, ki = "", 0
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            shift = ord(key[ki % len(key)]) - ord('a')
            result += chr((ord(ch) - base + shift) % 26 + base)
            ki += 1
        else:
            result += ch
    return result

def vigenere_decrypt(text, key):
    key = ''.join(c for c in key.lower() if c.isalpha())
    if not key: return text
    result, ki = "", 0
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            shift = ord(key[ki % len(key)]) - ord('a')
            result += chr((ord(ch) - base - shift) % 26 + base)
            ki += 1
        else:
            result += ch
    return result

def score_text(text):
    lower = text.lower()
    score = 0
    for word in COMMON_WORDS:
        score += lower.count(word) * len(word) * 3
    letters = [c for c in lower if c.isalpha()]
    if not letters: return 0
    freq = {}
    for c in letters:
        freq[c] = freq.get(c, 0) + 1
    for c, count in freq.items():
        observed = (count / len(letters)) * 100
        expected = ENGLISH_FREQ.get(c, 0)
        score -= abs(observed - expected)
    return score

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/caesar", methods=["POST"])
def caesar():
    d = request.get_json()
    text, shift, mode = d.get("text",""), int(d.get("shift",3)), d.get("mode","encrypt")
    result = caesar_encrypt(text, shift) if mode == "encrypt" else caesar_decrypt(text, shift)
    return jsonify({"result": result, "shift": shift, "mode": mode})

@app.route("/vigenere", methods=["POST"])
def vigenere():
    d = request.get_json()
    text, key, mode = d.get("text",""), d.get("key",""), d.get("mode","encrypt")
    result = vigenere_encrypt(text, key) if mode == "encrypt" else vigenere_decrypt(text, key)
    return jsonify({"result": result, "key": key, "mode": mode})

@app.route("/brute", methods=["POST"])
def brute():
    d = request.get_json()
    ciphertext = d.get("text","")
    results = []
    for shift in range(1, 26):
        decrypted = caesar_decrypt(ciphertext, shift)
        results.append({"shift": shift, "text": decrypted, "score": round(score_text(decrypted), 2)})
    results.sort(key=lambda x: x["score"], reverse=True)
    return jsonify({"results": results[:10]})

@app.route("/frequency", methods=["POST"])
def frequency():
    d = request.get_json()
    text = d.get("text","")
    letters = [c.lower() for c in text if c.isalpha()]
    if not letters:
        return jsonify({"error": "No letters found"})
    total = len(letters)
    freq = {}
    for c in letters:
        freq[c] = freq.get(c, 0) + 1
    data = sorted([{"letter": k.upper(), "count": v, "percent": round((v/total)*100, 1), "english": ENGLISH_FREQ.get(k,0)} for k,v in freq.items()], key=lambda x: x["count"], reverse=True)
    top = data[0]["letter"].lower()
    likely_shift = (ord(top) - ord('e')) % 26
    suggested = caesar_decrypt(text, likely_shift)
    return jsonify({"data": data, "likely_shift": likely_shift, "suggested": suggested, "total": total})

if __name__ == "__main__":
    print("\n  Classical Cipher Toolkit — Flask Server")
    print("  Open browser: http://localhost:5000\n")
    app.run(debug=True, port=5001)
