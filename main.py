import os, subprocess, re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def universal_architect_optimizer(code):
    tips = []
    
    # 1. ARCHITECT LEVEL IMPORTS
    needed_imports = ["java.math.*", "java.util.*", "java.util.concurrent.*", "java.util.concurrent.atomic.*", "java.util.function.*", "java.util.stream.*"]
    for imp in needed_imports:
        if f"import {imp};" not in code:
            code = f"import {imp};\n" + code

    # 2. DYNAMIC DISCOVERY (Variable Names)
    list_match = re.search(r'(\w+)\.(?:parallelStream|stream)\(\)', code)
    list_name = list_match.group(1) if list_match else "dataList"
    
    item_match = re.search(r'(\w+)\s*->', code)
    item_name = item_match.group(1).strip() if item_match else "obj"

    # Map information extraction (Value Types and Names)
    # Pattern detects: Map<Key, Value> name = ...
    map_info = re.findall(r'(?:Map|ConcurrentMap)<\s*\w+\s*,\s*(\w+)\s*>\s+(\w+)\s*=', code)

    # 3. CLASS FIELD DISCOVERY (Ab kuch bhi static nahi)
    # Hum dhoond rahe hain ki Transaction/Object class mein kaunsi fields hain
    fields = re.findall(r'\b(?:String|double|int|long|BigDecimal)\b\s+(\w+);', code)
    
    # Identify "Quantity" and "Amount" style fields dynamically
    qty_field = next((f for f in fields if any(x in f.lower() for x in ["qty", "quantity", "count", "unit"])), "quantity")
    amt_field = next((f for f in fields if any(x in f.lower() for x in ["amt", "amount", "price", "value"])), "amount")
    key_field = next((f for f in fields if any(x in f.lower() for x in ["id", "key", "name", "category"])), "id")

    # 4. GLOBAL CLEANER
    redundant_pattern = rf'Map<.*?>\s+\w+\s*=\s*{list_name}\.stream\(\).*?\.collect\(.*?\);'
    if len(re.findall(redundant_pattern, code, flags=re.DOTALL)) > 0:
        code = re.sub(redundant_pattern, '', code, flags=re.DOTALL)
        tips.append("🧹 <b>Cleaner:</b> Dynamically flushed all redundant stream scans.")

    # 5. DYNAMIC INITIALIZATION
    init_logic = f"\n        int capacity = (int)({list_name}.size() / 0.75) + 1;"
    for v_type, m_name in map_info:
        # Long/Integer ko LongAdder mein badalna (Concurrency ke liye)
        final_type = "LongAdder" if any(x in v_type for x in ["Integer", "Long", "Int"]) else "BigDecimal"
        init_logic += f"\n        ConcurrentMap<String, {final_type}> {m_name} = new ConcurrentHashMap<>(capacity);"
    
    code = re.sub(rf'({list_name}\.(?:parallelStream|stream))', init_logic + r"\n\n        \1", code, count=1)

    # 6. ZERO-STATIC MERGE ENGINE
    merge_logics = []
    for v_type, m_name in map_info:
        if any(x in v_type for x in ["Double", "BigDecimal", "Float"]):
            # Use discovered fields
            merge_logics.append(f"{m_name}.merge({item_name}.{key_field}, val, BigDecimal::add);")
        else:
            merge_logics.append(f"{m_name}.computeIfAbsent({item_name}.{key_field}, k -> new LongAdder()).add({item_name}.{qty_field});")

    optimized_block = f"""
        // --- Architect Level: Dynamic Unified Engine ---
        long startTime = System.nanoTime();
        LongAdder errorCount = new LongAdder();

        {list_name}.parallelStream().forEach({item_name} -> {{
            try {{
                if ({item_name} == null) return;
                BigDecimal val = BigDecimal.valueOf({item_name}.{amt_field}).multiply(BigDecimal.valueOf({item_name}.{qty_field}));
                {" ".join(merge_logics)}
            }} catch (Exception e) {{
                errorCount.increment();
            }}
        }});
        long endTime = System.nanoTime();
        System.out.printf("Execution: %.2f ms | Faults: %d%n", (endTime - startTime) / 1e6, errorCount.sum());
    """
    
    # Final replacement
    code = re.sub(rf'{list_name}\.(?:parallelStream|stream).*?\.forEach\(.*?\);|// 1️⃣.*?\n.*?(?={list_name})', optimized_block, code, flags=re.DOTALL, count=1)

    # 7. DYNAMIC TOP-K HEALER
    if "top" in code.lower() or "limit" in code:
        # Dhoondte hain konsa map sort ho raha hai
        sort_map_match = re.search(r'(\w+)\.entrySet\(\)\.stream\(\)\.sorted', code)
        sort_map = sort_map_match.group(1) if sort_map_match else (map_info[0][1] if map_info else "results")
        
        pq_logic = f"""
        List<String> topResults = {sort_map}.entrySet().stream()
                .sorted(Map.Entry.<String, BigDecimal>comparingByValue().reversed())
                .limit(5).map(Map.Entry::getKey).collect(Collectors.toList());
        """
        code = re.sub(r'List<.*?>\s+\w+\s*=\s*.*?\.sorted\(.*?\)\.limit\(.*?\).*?\.collect\(.*?\);', pq_logic, code, flags=re.DOTALL)

    return code, tips

@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    opt_code, tips = universal_architect_optimizer(data.get('code', ''))
    return jsonify({"optimized_code": opt_code, "tips": tips})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
