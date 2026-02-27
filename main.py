import os, subprocess, re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def universal_architect_optimizer(code):
    tips = []
    
    # --- 1. ARCHITECT LEVEL IMPORTS ---
    needed_imports = ["java.math.*", "java.util.*", "java.util.concurrent.*", "java.util.concurrent.atomic.*", "java.util.function.*", "java.util.stream.*"]
    for imp in needed_imports:
        if f"import {imp};" not in code:
            code = f"import {imp};\n" + code

    # --- 2. SMART TYPE & MATH DETECTION ---
    is_big_decimal = "BigDecimal amount" in code
    
    if "double amount" in code:
        code = code.replace("double amount", "BigDecimal amount")
        is_big_decimal = True
        tips.append("💰 <b>Type Fix:</b> Upgraded <code>double</code> to <code>BigDecimal</code> for precision.")

    if is_big_decimal:
        code = re.sub(r'(\w+)\.amount\s*\*\s*\1\.quantity', 
                      r'\1.amount.multiply(BigDecimal.valueOf(\1.quantity))', code)
    else:
        code = re.sub(r'(\w+)\.amount\s*\*\s*\1\.quantity', 
                      r'BigDecimal.valueOf(\1.amount).multiply(BigDecimal.valueOf(\1.quantity))', code)

    # --- 3. DYNAMIC SINGLE-PASS TRANSFORMATION ---
    if ".stream()" in code or "transactions" in code:
        tips.append("🚀 <b>Architect Flow:</b> Implementing Single-Pass O(n) with guaranteed variable safety.")
        
        unified_engine = f"""
        // --- Architect Level: Unified Single-Pass Engine ---
        int capacity = (int)(transactions.size() / 0.75) + 1;
        ConcurrentMap<String, BigDecimal> revenueByCategory = new ConcurrentHashMap<>(64);
        ConcurrentMap<String, BigDecimal> userSpending = new ConcurrentHashMap<>(capacity);
        ConcurrentMap<String, LongAdder> productSales = new ConcurrentHashMap<>(capacity);

        transactions.parallelStream().filter(t -> !t.failed).forEach(t -> {{
            BigDecimal val = {"t.amount" if is_big_decimal else "BigDecimal.valueOf(t.amount)"}.multiply(BigDecimal.valueOf(t.quantity));
            revenueByCategory.merge(t.category, val, BigDecimal::add);
            userSpending.merge(t.userId, val, BigDecimal::add);
            productSales.computeIfAbsent(t.productId, k -> new LongAdder()).add(t.quantity);
        }});

        PriorityQueue<Map.Entry<String, BigDecimal>> pq = new PriorityQueue<>(Map.Entry.comparingByValue());
        for (Map.Entry<String, BigDecimal> entry : userSpending.entrySet()) {{
            pq.offer(entry);
            if (pq.size() > 5) pq.poll();
        }}
        List<String> topUsers = pq.stream()
                .sorted((a, b) -> b.getValue().compareTo(a.getValue()))
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());
        """
        code = re.sub(r'// 1️⃣.*?productSales\s*=\s*.*?\.collect\(.*?\);', unified_engine, code, flags=re.DOTALL)

    # --- 4. FIX: GENERIC LONGADDER COMPARISON (Corrected & Enhanced) ---
    # Rule: LongAdder is NOT Comparable. We must use .sum() in the comparator.
    if "LongAdder" in code:
        # Search for any map entry stream that tries to find max/min using natural order on LongAdder
        # This regex catches: anyMap.entrySet().stream().max(Map.Entry.comparingByValue())
        generic_longadder_pattern = r'(\w+)\.entrySet\(\)\.stream\(\)\.max\(Map\.Entry\.comparingByValue\(\)\)'
        
        if re.search(generic_longadder_pattern, code):
            code = re.sub(generic_longadder_pattern, 
                          r'\1.entrySet().stream().max(Comparator.comparingLong(e -> e.getValue().sum()))', code)
            tips.append("🛠️ <b>Compilation Fix:</b> Fixed <code>LongAdder</code> comparison using <code>.sum()</code>.")

    return code, tips

@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    opt_code, tips = universal_architect_optimizer(data.get('code', ''))
    return jsonify({"optimized_code": opt_code, "tips": tips})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
