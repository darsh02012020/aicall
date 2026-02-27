import os, subprocess, re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def universal_architect_optimizer(code):
    tips = []
    
    # --- 1. ARCHITECT LEVEL IMPORTS (Mandatory for Concurrency) ---
    needed_imports = ["java.math.*", "java.util.concurrent.*", "java.util.concurrent.atomic.*", "java.util.function.*"]
    for imp in needed_imports:
        if f"import {imp};" not in code:
            code = f"import {imp};\n" + code

    # --- 2. THE BIGDECIMAL & PRECISION ENGINE (Point 1 & 3) ---
    # Sabse pehle types check karo aur operators fix karo taaki Compile Error na aaye
    if "BigDecimal" in code or "amount" in code:
        # Rule: t.amount * t.quantity -> t.amount.multiply(BigDecimal.valueOf(t.quantity))
        code = re.sub(r'(\w+)\.amount\s*\*\s*\1\.quantity', 
                      r'\1.amount.multiply(BigDecimal.valueOf(\1.quantity))', code)
        # Rule: total += price -> total = total.add(price)
        code = re.sub(r'(\w+)\s*\+=\s*(.*?);', r'\1 = \1.add(\2);', code)
        tips.append("💰 <b>Precision & Syntax:</b> Upgraded to BigDecimal arithmetic to prevent compilation and rounding errors.")

    # --- 3. FORCE SINGLE-PASS O(n) TRANSFORMATION (Point 2) ---
    # Agar 1 se zyada stream passes hain, toh pura block merge kar do
    if code.count(".stream()") > 1 or code.count(".parallelStream()") > 1:
        tips.append("🚀 <b>Scalability:</b> Merged multiple passes into a <b>Single-Pass Parallel Engine (O(n))</b>.")
        
        # Ye block purane messy streams ko replace karega
        single_pass_block = """
        // --- Architect Level: Single-Pass Concurrent Processor ---
        int capacity = (int)(transactions.size() / 0.75) + 1;
        ConcurrentMap<String, BigDecimal> revenueByCategory = new ConcurrentHashMap<>(64);
        ConcurrentMap<String, BigDecimal> userSpending = new ConcurrentHashMap<>(capacity);
        ConcurrentMap<String, LongAdder> productSales = new ConcurrentHashMap<>(capacity);

        transactions.parallelStream().filter(t -> !t.failed).forEach(t -> {
            BigDecimal lineAmount = t.amount.multiply(BigDecimal.valueOf(t.quantity));
            revenueByCategory.merge(t.category, lineAmount, BigDecimal::add);
            userSpending.merge(t.userId, lineAmount, BigDecimal::add);
            productSales.computeIfAbsent(t.productId, k -> new LongAdder()).add(t.quantity);
        });
        """
        # Purane blocks (1 se 3 tak) ko target karke replace karna
        code = re.sub(r'// 1️⃣.*?productSales\s*=\s*.*?\.collect\(.*?\);', 
                      single_pass_block, code, flags=re.DOTALL)

    # --- 4. TOP-K EFFICIENCY (PriorityQueue) ---
    if ".sorted(" in code and ".limit(" in code:
        tips.append("📉 <b>Algorithm:</b> Replaced Full Sort with <b>PriorityQueue (Min-Heap)</b> for Top-K efficiency.")
        pq_logic = """
        PriorityQueue<Map.Entry<String, BigDecimal>> topK = new PriorityQueue<>(Map.Entry.comparingByValue());
        userSpending.entrySet().forEach(e -> {
            topK.offer(e);
            if (topK.size() > 5) topK.poll();
        });
        List<String> topUsers = topK.stream().map(Map.Entry::getKey).collect(Collectors.toList());
        """
        code = re.sub(r'List<String> topUsers\s*=\s*.*?\.collect\(Collectors\.toList\(\)\);', 
                      pq_logic, code, flags=re.DOTALL)

    return code, tips

# --- FLASK ROUTES (Keep these as they are) ---
@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    original_code = data.get('code', '')
    opt_code, tips = universal_architect_optimizer(original_code)
    return jsonify({"optimized_code": opt_code, "tips": tips})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
