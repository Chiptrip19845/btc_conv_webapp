import os
from flask import Flask, request, jsonify, session, send_from_directory, render_template_string
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# HTML Template als String
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bitcoin Umrechner</title>
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
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            width: 100%;
            text-align: center;
        }

        .bitcoin-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
            font-weight: 300;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }

        .last-input {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 30px;
            border: 1px solid #e9ecef;
        }

        .last-input h3 {
            color: #495057;
            margin-bottom: 10px;
            font-size: 1em;
        }

        .last-input-display {
            color: #6c757d;
            font-weight: 500;
            margin-bottom: 10px;
        }

        .reuse-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            transition: background-color 0.3s;
        }

        .reuse-btn:hover {
            background: #218838;
        }

        .form-group {
            margin-bottom: 25px;
            text-align: left;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }

        input, select {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s, box-shadow 0.3s;
        }

        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .convert-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 18px 40px;
            border-radius: 50px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
            margin-top: 10px;
        }

        .convert-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .convert-btn:active {
            transform: translateY(0);
        }

        .result {
            margin-top: 30px;
            padding: 25px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            border: 1px solid #dee2e6;
        }

        .result-amount {
            font-size: 2.5em;
            font-weight: 700;
            color: #333;
            margin-bottom: 10px;
        }

        .result-description {
            color: #6c757d;
            font-size: 1.1em;
        }

        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .loading {
            opacity: 0.7;
            pointer-events: none;
        }

        @media (max-width: 600px) {
            .container {
                padding: 30px 20px;
            }
            
            h1 {
                font-size: 2em;
            }
            
            .result-amount {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="bitcoin-icon">₿</div>
        <h1>Bitcoin Umrechner</h1>
        <p class="subtitle">Rechnen Sie Bitcoin in USD oder EUR um</p>
        
        <div class="last-input" id="lastInputSection" style="display: none;">
            <h3>Letzte Eingabe:</h3>
            <div class="last-input-display" id="lastInputDisplay"></div>
            <button class="reuse-btn" onclick="reuseLastInput()">Wiederverwenden</button>
        </div>

        <form id="converterForm">
            <div class="form-group">
                <label for="amount">Betrag:</label>
                <input type="number" id="amount" step="any" placeholder="z.B. 1.5" required>
            </div>

            <div class="form-group">
                <label for="fromCurrency">Von:</label>
                <select id="fromCurrency" required>
                    <option value="BTC">Bitcoin (BTC)</option>
                </select>
            </div>

            <div class="form-group">
                <label for="toCurrency">Zu:</label>
                <select id="toCurrency" required>
                    <option value="USD">US-Dollar (USD)</option>
                    <option value="EUR">Euro (EUR)</option>
                </select>
            </div>

            <button type="submit" class="convert-btn">Umrechnen</button>
        </form>

        <div id="result" style="display: none;"></div>
    </div>

    <script>
        // Load last input on page load
        window.addEventListener('load', loadLastInput);

        async function loadLastInput() {
            try {
                const response = await fetch('/api/last_input');
                const data = await response.json();
                
                if (data.last_amount && data.last_from_currency && data.last_to_currency) {
                    const lastInputSection = document.getElementById('lastInputSection');
                    const lastInputDisplay = document.getElementById('lastInputDisplay');
                    
                    lastInputDisplay.textContent = `${data.last_amount} ${data.last_from_currency} → ${data.last_to_currency}`;
                    lastInputSection.style.display = 'block';
                }
            } catch (error) {
                console.error('Error loading last input:', error);
            }
        }

        function reuseLastInput() {
            fetch('/api/last_input')
                .then(response => response.json())
                .then(data => {
                    if (data.last_amount && data.last_from_currency && data.last_to_currency) {
                        document.getElementById('amount').value = data.last_amount;
                        document.getElementById('fromCurrency').value = data.last_from_currency;
                        document.getElementById('toCurrency').value = data.last_to_currency;
                    }
                })
                .catch(error => {
                    console.error('Error reusing last input:', error);
                });
        }

        document.getElementById('converterForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const amount = document.getElementById('amount').value;
            const fromCurrency = document.getElementById('fromCurrency').value;
            const toCurrency = document.getElementById('toCurrency').value;
            const resultDiv = document.getElementById('result');
            const convertBtn = document.querySelector('.convert-btn');
            
            // Show loading state
            convertBtn.textContent = 'Wird umgerechnet...';
            convertBtn.classList.add('loading');
            resultDiv.style.display = 'none';
            
            try {
                const response = await fetch('/api/convert', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        amount: parseFloat(amount),
                        from_currency: fromCurrency,
                        to_currency: toCurrency
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    const formattedResult = new Intl.NumberFormat('de-DE', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    }).format(data.result);
                    
                    resultDiv.innerHTML = `
                        <div class="result-amount">${formattedResult} ${toCurrency}</div>
                        <div class="result-description">${amount} ${fromCurrency} entspricht ${formattedResult} ${toCurrency}</div>
                    `;
                    resultDiv.className = 'result';
                    
                    // Reload last input section
                    loadLastInput();
                } else {
                    resultDiv.innerHTML = `
                        <div class="result-amount">Fehler</div>
                        <div class="result-description">${data.error}</div>
                    `;
                    resultDiv.className = 'result error';
                }
                
                resultDiv.style.display = 'block';
                
            } catch (error) {
                resultDiv.innerHTML = `
                    <div class="result-amount">Fehler</div>
                    <div class="result-description">Netzwerkfehler: ${error.message}</div>
                `;
                resultDiv.className = 'result error';
                resultDiv.style.display = 'block';
            } finally {
                // Reset button state
                convertBtn.textContent = 'Umrechnen';
                convertBtn.classList.remove('loading');
            }
        });
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/convert', methods=['POST'])
def convert():
    data = request.get_json()
    amount = data.get('amount')
    from_currency = data.get('from_currency')
    to_currency = data.get('to_currency')

    if not all([amount, from_currency, to_currency]):
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400

    # Store the last input in the session
    session['last_amount'] = amount
    session['last_from_currency'] = from_currency
    session['last_to_currency'] = to_currency

    # Try multiple APIs for Bitcoin rates
    try:
        # First try: Alternative.me API
        if to_currency == 'USD':
            url = "https://api.alternative.me/v2/ticker/bitcoin/?convert=USD"
        elif to_currency == 'EUR':
            url = "https://api.alternative.me/v2/ticker/bitcoin/?convert=EUR"
        else:
            return jsonify({'error': 'Unsupported currency'}), 400
            
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'data' in data and '1' in data['data']:
            bitcoin_data = data['data']['1']
            if to_currency in bitcoin_data['quotes']:
                price = bitcoin_data['quotes'][to_currency]['price']
                result = amount * price
                return jsonify({'result': result})
        
        # Fallback: Try CoinGecko API
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,eur"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'bitcoin' in data:
            btc_usd = data['bitcoin']['usd']
            btc_eur = data['bitcoin']['eur']
            
            if to_currency == 'USD':
                result = amount * btc_usd
            elif to_currency == 'EUR':
                result = amount * btc_eur
            else:
                return jsonify({'error': 'Unsupported currency'}), 400
                
            return jsonify({'result': result})
        
        # Second fallback: Try CoinDesk API (USD only)
        if to_currency == 'USD':
            url = "https://api.coindesk.com/v1/bpi/currentprice.json"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if 'bpi' in data and 'USD' in data['bpi']:
                price_str = data['bpi']['USD']['rate'].replace(',', '').replace('$', '')
                price = float(price_str)
                result = amount * price
                return jsonify({'result': result})
        
        return jsonify({'error': 'Failed to get Bitcoin price from all sources'}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Network error: Unable to fetch Bitcoin price'}), 500
    except Exception as e:
        return jsonify({'error': 'API request failed'}), 500

@app.route('/api/last_input', methods=['GET'])
def get_last_input():
    last_amount = session.get('last_amount')
    last_from_currency = session.get('last_from_currency')
    last_to_currency = session.get('last_to_currency')
    return jsonify({
        'last_amount': last_amount,
        'last_from_currency': last_from_currency,
        'last_to_currency': last_to_currency
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'Bitcoin Converter is running'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

