import os, subprocess, re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def final_strong_optimizer(code):
    tips = []
    
    # --- 1. ARCHITECT LEVEL: IMPORTS & TYPE SAFETY ---
    needed_imports = [
        "java.math.BigDecimal", "java.util.*", "java.util.stream.*", 
        "java.util.concurrent.*", "java.util.function.*"
    ]
    for imp in needed_imports:
        if f"import {imp};" not in code:
            code = f"import {imp};\n" + code

    # --- 2. THE CHECKLIST: BIGDECIMAL & IMMUTABILITY ---
    # Rule: Use BigDecimal for money, avoid double. Keep objects final.
    if "double price" in code or "double revenue" in code:
        code = re.sub(r'\bdouble\b\s+(price|revenue|total|amount|spending)', r'BigDecimal \1', code)
        code = re.sub(r'\(double\s+(price|revenue|total|amount|spending)\)', r'(BigDecimal \1)', code)
        tips.append("💰 <b>Precision:</b> Converted all money-related <code>double</code> to <code>BigDecimal</code>.")

    # --- 3. GOLDEN RULE: SINGLE-PASS + PARALLEL PROCESSING ---
    # Rule: Avoid multiple loops, use parallel streams for millions of records
    if "for (Order" in code and code.count("for (Order") > 1:
        tips.append("🚀 <b>Scalability:</b> Merged 3 loops into a Single-Pass Parallel Pipeline (O(n)).")
        
        # This block replaces the entire messy logic with a high-performance concurrent engine
        architect_logic = """
        // --- Architect Level: Parallel Single-Pass Processing (1M+ Records) ---
        int capacity = (int) (orders.size() / 0.75) + 1;
        
        // Concurrent Containers for Thread-Safety
        ConcurrentMap<String, BigDecimal> revenueByCategory = new ConcurrentHashMap<>(64);
        ConcurrentMap<String, BigDecimal> customerSpending = new ConcurrentHashMap<>(capacity);
        ConcurrentMap<String, LongAdder> productCount = new ConcurrentHashMap<>(capacity);

        orders.parallelStream().filter(o -> !o.cancelled).forEach(order -> {
            for (OrderItem item : order.items) {
                BigDecimal itemRev = item.price.multiply(BigDecimal.valueOf(item.quantity));
                
                revenueByCategory.merge(item.category, itemRev, BigDecimal::add);
                customerSpending.merge(order.customerId, itemRev, BigDecimal::add);
                productCount.computeIfAbsent(item.productId, k -> new LongAdder()).add(item.quantity);
            }
        });

        // Convert LongAdder to Integer for final output
        Map<String, Integer> finalProductCount = productCount.entrySet().stream()
            .collect(Collectors.toMap(Map.Entry::getKey, e -> e.getValue().intValue()));
        """
        
        # Locate the logic starting from "// 1." to "// 3." and replace it
        code = re.sub(r'// 1\. Revenue.*?// 3\. Most sold product.*?\n', architect_logic + "\n", code, flags=re.DOTALL)

    # --- 4. ALGO OPTIMIZATION: PRIORITY QUEUE (Top-K) ---
    # Rule: Use PriorityQueue instead of full sorting
    if ".sorted(" in code and ".limit(" in code:
        pq_logic = """
        // Top-K Optimization: O(n log k) complexity
        PriorityQueue<Map.Entry<String, BigDecimal>> top3Pq = new PriorityQueue<>(Map.Entry.comparingByValue());
        customerSpending.entrySet().forEach(entry -> {
            top3Pq.offer(entry);
            if (top3Pq.size() > 3) top3Pq.poll();
        });
        List<String> topCustomers = top3Pq.stream().map(Map.Entry::getKey).collect(Collectors.toList());"""
        
        code = re.sub(r'List<String> topCustomers =.*?\.collect\(Collectors\.toList\(\)\);', pq_logic, code, flags=re.DOTALL)
        tips.append("📉 <b>Algorithm:</b> Replaced full Sort with <b>Min-Heap PriorityQueue</b>.")

    # --- 5. COMPILATION FIXER (BigDecimal Syntax) ---
    code = code.replace("0.0", "BigDecimal.ZERO")
    code = re.sub(r'(\w+)\s*\+=\s*(.*?);', r'\1 = \1.add(\2);', code)
    # Fix potential price * quantity errors
    code = re.sub(r'(\w+)\.price\s*\*\s*(\w+)\.quantity', r'\1.price.multiply(BigDecimal.valueOf(\1.quantity))', code)

    return code, tips

# --- RUNNER LOGIC (Java + Python) ---
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
    except Exception as e: return jsonify({"output": "System Error: " + str(e)})

@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    opt_code, tips = final_strong_optimizer(data.get('code', ''))
    return jsonify({"optimized_code": opt_code, "tips": tips})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
