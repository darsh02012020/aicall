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

    # --- 2. DYNAMIC CONTEXT DISCOVERY ---
    list_match = re.search(r'(\w+)\.(?:parallelStream|stream)\(\)', code)
    list_name = list_match.group(1) if list_match else "transactions"
    
    item_match = re.search(r'(\w+)\s*->', code) # Simplified regex to avoid (a, b) error
    item_name = item_match.group(1).strip() if item_match else "t"

    map_declarations = re.findall(r'(?:Map|ConcurrentMap)<.*?>\s+(\w+)\s*=', code)
    
    # --- 3. MEMORY OPTIMIZATION: Initial Capacity ---
    if f"{list_name}.size()" in code and "capacity =" not in code:
        capacity_logic = f"\n        int capacity = (int)({list_name}.size() / 0.75) + 1;"
        code = re.sub(r'(Map<.*?>\s+\w+\s*=)', capacity_logic + r'\n        \1', code, count=1)
        tips.append("🧠 <b>Memory:</b> Added Initial Capacity to prevent Map resizing.")

    # --- 4. DYNAMIC TRANSFORMATION ENGINE (Single-Pass with Resilience) ---
    if (".stream()" in code or ".parallelStream()" in code) and map_declarations:
        tips.append(f"🚀 <b>Architect Flow:</b> Unified Single-Pass O(n) Engine with Resilience.")
        
        merge_logics = []
        for m_name in map_declarations:
            if any(x in m_name.lower() for x in ["rev", "sum", "total", "spend"]):
                key = f"{item_name}.category" if "cat" in m_name.lower() else f"{item_name}.userId"
                merge_logics.append(f"{m_name}.merge({key}, val, BigDecimal::add);")
            elif any(x in m_name.lower() for x in ["sales", "count", "prod"]):
                merge_logics.append(f"{m_name}.computeIfAbsent({item_name}.productId, k -> new LongAdder()).add({item_name}.quantity);")

        is_bd = "BigDecimal" in code
        calc = f"{item_name}.amount" if is_bd else f"BigDecimal.valueOf({item_name}.amount)"
        
        # Adding Logging and Try-Catch for production-grade resilience
        optimized_block = f"""
        // --- Architect Level: Unified Single-Pass Engine (Resilient) ---
        long startTime = System.nanoTime();
        LongAdder errorCount = new LongAdder();

        {list_name}.parallelStream().filter({item_name} -> !{item_name}.failed).forEach({item_name} -> {{
            try {{
                BigDecimal val = {calc}.multiply(BigDecimal.valueOf({item_name}.quantity));
                {" ".join(merge_logics)}
            }} catch (Exception e) {{
                errorCount.increment();
            }}
        }});
        long endTime = System.nanoTime();
        System.out.printf("Processed in: %.2f ms | Errors: %d%n", (endTime - startTime) / 1e6, errorCount.sum());
        """
        
        code = re.sub(r'// 1️⃣.*?\.collect\(.*?\);.*?// 3️⃣.*?\.collect\(.*?\);', optimized_block, code, flags=re.DOTALL)

    # --- 5. TOP-K HEALER ---
    if "topUsers" in code and "PriorityQueue" not in code:
        pq_logic = """
        PriorityQueue<Map.Entry<String, BigDecimal>> pq = new PriorityQueue<>(Map.Entry.comparingByValue());
        userSpending.entrySet().forEach(e -> {
            pq.offer(e);
            if (pq.size() > 5) pq.poll();
        });
        List<String> topUsers = pq.stream().sorted(Map.Entry.<String, BigDecimal>comparingByValue().reversed())
                                  .map(Map.Entry::getKey).collect(Collectors.toList());
        """
        code = re.sub(r'List<String> topUsers =.*?\.collect\(.*?\);', pq_logic, code, flags=re.DOTALL)
        tips.append("📊 <b>Performance:</b> Replaced full sort with Min-Heap for Top-K.")

    # --- 6. LONGADDER HEALER ---
    for m_name in map_declarations:
        pattern = rf'{m_name}\.entrySet\(\)\.stream\(\)\.max\(Map\.Entry\.comparingByValue\(\)\)'
        if re.search(pattern, code):
            code = re.sub(pattern, f'{m_name}.entrySet().stream().max(Comparator.comparingLong(e -> e.getValue().sum()))', code)
            tips.append(f"🛠️ <b>Healed:</b> Fixed <code>LongAdder</code> comparison.")

    return code, tips

@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    opt_code, tips = universal_architect_optimizer(data.get('code', ''))
    return jsonify({"optimized_code": opt_code, "tips": tips})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
