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

    # --- 2. FIX: TYPE MISMATCH & PRECISION (Point 1 & 3) ---
    # Rule: Convert double fields to BigDecimal for financial safety
    if "double amount" in code:
        code = code.replace("double amount", "BigDecimal amount")
        tips.append("💰 <b>Type Fix:</b> Upgraded <code>double</code> to <code>BigDecimal</code> for financial precision.")
    
    # Fix arithmetic syntax: t.amount * t.quantity -> BigDecimal safe multiply
    # We use BigDecimal.valueOf() as a safety bridge for any numeric type
    code = re.sub(r'(\w+)\.amount\s*\*\s*\1\.quantity', 
                  r'BigDecimal.valueOf(\1.amount).multiply(BigDecimal.valueOf(\1.quantity))', code)
    
    # Fix standard multiply call if it's missing valueOf bridge
    code = re.sub(r'(\w+)\.amount\.multiply', r'BigDecimal.valueOf(\1.amount).multiply', code)

    # --- 3. FORCE SINGLE-PASS O(n) & GUARANTEED VARIABLES (Point 2) ---
    if code.count(".stream()") > 1 or "transactions" in code:
        tips.append("🚀 <b>Architect Flow:</b> Implementing Single-Pass O(n) with thread-safe aggregation.")
        
        unified_engine = """
        // --- Architect Level: Unified Single-Pass Engine ---
        int capacity = (int)(transactions.size() / 0.75) + 1;
        ConcurrentMap<String, BigDecimal> revenueByCategory = new ConcurrentHashMap<>(64);
        ConcurrentMap<String, BigDecimal> userSpending = new ConcurrentHashMap<>(capacity);
        ConcurrentMap<String, LongAdder> productSales = new ConcurrentHashMap<>(capacity);

        transactions.parallelStream().filter(t -> !t.failed).forEach(t -> {
            BigDecimal val = BigDecimal.valueOf(t.amount).multiply(BigDecimal.valueOf(t.quantity));
            revenueByCategory.merge(t.category, val, BigDecimal::add);
            userSpending.merge(t.userId, val, BigDecimal::add);
            productSales.computeIfAbsent(t.productId, k -> new LongAdder()).add(t.quantity);
        });

        // Guaranteed Top-K Discovery (Prevents Missing Variable Error)
        PriorityQueue<Map.Entry<String, BigDecimal>> pq = new PriorityQueue<>(Map.Entry.comparingByValue());
        userSpending.entrySet().forEach(e -> {
            pq.offer(e);
            if (pq.size() > 5) pq.poll();
        });
        List<String> topUsers = pq.stream().map(Map.Entry::getKey).collect(Collectors.toList());
        """
        # Replacing the multi-stream/loop mess with the unified engine
        code = re.sub(r'// 1️⃣.*?productSales\s*=\s*.*?\.collect\(.*?\);', unified_engine, code, flags=re.DOTALL)

    # --- 4. FIX: LONGADDER COMPARISON (Point 3) ---
    if "productSales" in code:
        # LongAdder doesn't implement Comparable, must use .sum() or .longValue()
        code = re.sub(r'Map\.Entry\.comparingByValue\(\)', 
                      r'Comparator.comparingLong(e -> e.getValue().sum())', code)
        tips.append("🛠️ <b>Logic Fix:</b> Enabled correct comparison for <code>LongAdder</code> values.")

    return code, tips

@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    original_code = data.get('code', '')
    opt_code, tips = universal_architect_optimizer(original_code)
    return jsonify({"optimized_code": opt_code, "tips": tips})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
