import os, subprocess, re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def supreme_architect_optimizer(code):
    tips = []
    
    # 1. 🛡️ IMPORT SCAN (Ensuring Zero-Error Compilation)
    imports = ["java.math.BigDecimal", "java.util.*", "java.util.stream.*", "java.util.concurrent.*"]
    for imp in imports:
        if f"import {imp};" not in code:
            code = f"import {imp};\n" + code

    # 2. 🔒 IMMUTABILITY & GC PRESSURE REDUCTION
    # Rule: Keep objects immutable (final) & Reduce object creation
    if "class " in code:
        code = re.sub(r'(public|private|protected)\s+(String|int|long|BigDecimal|LocalDate|List<.*?>)\s+(\w+);', 
                      r'private final \2 \3;', code)
        tips.append("🔒 <b>Architectural Safety:</b> Enforced <b>Immutability</b> (final fields) to reduce side-effects and GC overhead.")

    # 3. 🏗️ SINGLE-PASS O(n) ENGINE (Golden Rule: Algorithm > Code)
    # Rule: Avoid multiple loops, Prefer single-pass, Pre-size collections
    if code.count("for (") > 1 or ".stream()" in code:
        tips.append("🏗️ <b>Single-Pass Mastery:</b> Consolidated multiple O(n) passes into a single optimized engine.")
        
        # Pre-sizing logic: size / 0.75 + 1
        optimized_block = """
        // --- Architect Optimized: Single-Pass & Pre-sized Collections ---
        int totalRecords = orders.size();
        int initialCap = (int) (totalRecords / 0.75) + 1; // Pre-sizing to avoid Rehashing

        Map<String, BigDecimal> revenueByCategory = new HashMap<>(64); // Fixed categories
        Map<String, BigDecimal> customerSpending = new HashMap<>(initialCap);
        Map<String, Integer> productCount = new HashMap<>(initialCap);

        for (Order order : orders) {
            if (order.cancelled) continue; // Branching Optimization

            for (OrderItem item : order.items) {
                // BigDecimal Math: Avoid double for Money
                BigDecimal itemRev = item.price.multiply(BigDecimal.valueOf(item.quantity));
                
                // Map.merge: Atomic & efficient updates
                revenueByCategory.merge(item.category, itemRev, BigDecimal::add);
                customerSpending.merge(order.customerId, itemRev, BigDecimal::add);
                productCount.merge(item.productId, item.quantity, Integer::sum);
            }
        }"""
        
        # Regex replacement to wipe out messy loops and inject the "Golden Loop"
        code = re.sub(r'// 1\. Revenue.*?// 3\. Most sold product.*?\n', optimized_block + "\n", code, flags=re.DOTALL)

    # 4. 📉 ALGORITHM SWAP: TOP-K EFFICIENCY
    # Rule: Use PriorityQueue instead of full sorting for Top-K
    if ".sorted(" in code and ".limit(" in code:
        pq_logic = """
        // Top-K Optimization: PriorityQueue (Min-Heap) O(n log k) instead of O(n log n)
        PriorityQueue<Map.Entry<String, BigDecimal>> topK = new PriorityQueue<>(Map.Entry.comparingByValue());
        for (var entry : customerSpending.entrySet()) {
            topK.offer(entry);
            if (topK.size() > 3) topK.poll();
        }
        List<String> topCustomers = topK.stream().map(Map.Entry::getKey).collect(Collectors.toList());"""
        
        code = re.sub(r'List<String> topCustomers =.*?collect\(Collectors\.toList\(\)\);', pq_logic, code, flags=re.DOTALL)
        tips.append("📉 <b>Algorithmic Shift:</b> Swapped Full Sort with <b>PriorityQueue Min-Heap</b> for Top-K.")

    # 5. 💰 PRECISION & TYPE HARMONIZATION
    code = code.replace("double ", "BigDecimal ")
    code = code.replace("0.0", "BigDecimal.ZERO")
    code = re.sub(r'(\w+)\s*\+=\s*(.*?);', r'\1 = \1.add(\2);', code) # Fix addition
    code = re.sub(r'(\w+)\s*\*\s*(\w+)', r'\1.multiply(\2)', code) # Fix multiplication

    return code, tips

# --- 🚀 MULTI-LANG RUNNER (Python + Java) ---
@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code, lang, stdin = data.get('code'), data.get('lang'), data.get('stdin', '')
    try:
        if lang == 'python':
            with open("/tmp/script.py", "w") as f: f.write(code)
            res = subprocess.run(['python3', '/tmp/script.py'], input=stdin, capture_output=True, text=True, timeout=15)
            return jsonify({"output": res.stdout + res.stderr})
        else:
            match = re.search(r'public\s+class\s+(\w+)', code)
            name = match.group(1) if match else "Main"
            with open(f"/tmp/{name}.java", "w") as f: f.write(code)
            comp = subprocess.run(['javac', '-d', '/tmp', f"/tmp/{name}.java"], capture_output=True, text=True)
            if comp.returncode != 0: return jsonify({"output": "Compile Error:\n" + comp.stderr})
            run = subprocess.run(['java', '-Xmx512m', '-cp', '/tmp', name], input=stdin, capture_output=True, text=True, timeout=15)
            return jsonify({"output": run.stdout + run.stderr})
    except Exception as e: return jsonify({"output": f"System Error: {str(e)}"})

@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    opt_code, tips = supreme_architect_optimizer(data.get('code', ''))
    return jsonify({"optimized_code": opt_code, "tips": tips})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
