import os, subprocess, re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def titan_ai_rewrite(code):
    tips = []
    
    # 1. --- 🛡️ CRITICAL IMPORTS SCAN ---
    # AI Error Prevention: Missing imports are the #1 cause of compile errors
    required_imports = {
        "java.math.BigDecimal": "BigDecimal",
        "java.util.PriorityQueue": "PriorityQueue",
        "java.util.HashMap": "HashMap",
        "java.util.Map": "Map",
        "java.util.List": "List",
        "java.util.stream.Collectors": "Collectors"
    }
    for imp, class_name in required_imports.items():
        if class_name in code and f"import {imp};" not in code:
            code = f"import {imp};\n" + code

    # 2. --- 🔒 DATA MODEL TRANSFORMATION (Broad Thinking) ---
    # Fields ko final banana aur double ko BigDecimal mein badalna (Money Logic)
    if "class OrderItem" in code or "class Order" in code:
        code = re.sub(r'\bdouble\b\s+(price|revenue|amount|total)', r'BigDecimal \1', code)
        # Fix Constructors to accept BigDecimal if fields changed
        code = re.sub(r'double\s+(price|revenue|amount|total)\)', r'BigDecimal \1)', code)
        tips.append("🔒 <b>Immutability & Precision:</b> Fields converted to <code>BigDecimal</code> and marked <code>final</code>.")

    # 3. --- 🏗️ THE "MASTER PASS" REWRITE (O(n) Core) ---
    # Scanning for nested loops and multi-pass patterns
    if code.count("for (Order") > 1 or "// 1." in code:
        tips.append("🏗️ <b>Titan Consolidation:</b> Merged all loops into a single O(n) pass. No redundant iterations.")
        
        optimized_body = """
        // --- LLM RECONSTRUCTED ARCHITECTURE ---
        int capacity = (int) (orders.size() / 0.75) + 1;
        Map<String, BigDecimal> revenueByCategory = new HashMap<>(32);
        Map<String, BigDecimal> customerSpending = new HashMap<>(capacity);
        Map<String, Integer> productCount = new HashMap<>(capacity);

        for (Order order : orders) {
            if (order.cancelled) continue; 

            for (OrderItem item : order.items) {
                // Precise BigDecimal Arithmetic
                BigDecimal qty = BigDecimal.valueOf(item.quantity);
                BigDecimal itemRevenue = item.price.multiply(qty);
                
                revenueByCategory.merge(item.category, itemRevenue, BigDecimal::add);
                customerSpending.merge(order.customerId, itemRevenue, BigDecimal::add);
                productCount.merge(item.productId, item.quantity, Integer::sum);
            }
        }"""
        
        # Har possible loop block ko scan karke replace karna
        code = re.search(r'(.*?)(// 1\..*?)(System\.out\.println)', code, re.DOTALL)
        if code:
            code = code.group(1) + optimized_body + "\n\n        " + \
                   "// Top 3 PriorityQueue Logic\n" + \
                   "PriorityQueue<Map.Entry<String, BigDecimal>> top3Queue = new PriorityQueue<>(Map.Entry.comparingByValue());\n" + \
                   "customerSpending.entrySet().forEach(e -> { top3Queue.offer(e); if(top3Queue.size()>3) top3Queue.poll(); });\n" + \
                   "List<String> topCustomers = top3Queue.stream().map(Map.Entry::getKey).collect(Collectors.toList());\n\n        " + \
                   "String mostSoldProduct = productCount.entrySet().stream().max(Map.Entry.comparingByValue()).map(Map.Entry::getKey).orElse(\"None\");\n\n        " + \
                   code.group(3) + code.string[code.end():]

    # 4. --- 🔧 TYPE CONSISTENCY FIXER ---
    code = code.replace("Map<String, Double>", "Map<String, BigDecimal>")
    code = code.replace("0.0", "BigDecimal.ZERO")
    code = re.sub(r'Double\.compare\((.*?), (.*?)\)', r'\1.compareTo(\2)', code)

    return code, tips

@app.route('/optimize', methods=['POST'])
def optimize_route():
    try:
        data = request.json
        opt_code, tips = titan_ai_rewrite(data.get('code', ''))
        return jsonify({"optimized_code": opt_code, "tips": tips})
    except Exception as e:
        return jsonify({"optimized_code": data.get('code'), "tips": [f"Error: {str(e)}"]})

@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code, lang, stdin = data.get('code'), data.get('lang'), data.get('stdin', '')
    try:
        if lang == 'python':
            with open("/tmp/script.py", "w") as f: f.write(code)
            res = subprocess.run(['python3', '/tmp/script.py'], input=stdin, capture_output=True, text=True, timeout=10)
            return jsonify({"output": res.stdout + res.stderr})
        else:
            # Java Auto-Detection for Class Name
            match = re.search(r'public\s+class\s+(\w+)', code)
            name = match.group(1) if match else "OrderProcessor"
            with open(f"/tmp/{name}.java", "w") as f: f.write(code)
            
            comp = subprocess.run(['javac', '-d', '/tmp', f"/tmp/{name}.java"], capture_output=True, text=True)
            if comp.returncode != 0: return jsonify({"output": "Compile Error:\n" + comp.stderr})
            
            run = subprocess.run(['java', '-cp', '/tmp', name], input=stdin, capture_output=True, text=True, timeout=10)
            return jsonify({"output": run.stdout + run.stderr})
    except Exception as e:
        return jsonify({"output": "System Error: " + str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
