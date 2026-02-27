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
    # List aur Item detect karna (e.g., transactions, t)
    list_match = re.search(r'(\w+)\.(?:parallelStream|stream)\(\)', code)
    list_name = list_match.group(1) if list_match else "list"
    
    item_match = re.search(r'\(([^)]+)\)\s*->', code) or re.search(r'(\w+)\s*->', code)
    item_name = item_match.group(1).strip() if item_match else "t"

    # Maps Detection: Hum dhundte hain ki user ne kaunse Maps declare kiye hain
    # Pattern: Map name aur uska purpose (revenue, sales, spending)
    map_declarations = re.findall(r'(?:Map|ConcurrentMap)<.*?>\s+(\w+)\s*=', code)
    
    # --- 3. DYNAMIC TRANSFORMATION ENGINE ---
    if ".stream()" in code and map_declarations:
        tips.append(f"🚀 <b>Architect Flow:</b> Performed Context-Aware O(n) Optimization on <code>{list_name}</code>.")
        
        # Build the dynamic forEach block based ONLY on existing maps
        merge_logics = []
        
        # Har map ke liye sahi merge logic generate karna
        for m_name in map_declarations:
            if "rev" in m_name.lower() or "sum" in m_name.lower() or "total" in m_name.lower():
                merge_logics.append(f"{m_name}.merge({item_name}.getCategory(), val, BigDecimal::add);")
            elif "spend" in m_name.lower() or "user" in m_name.lower():
                merge_logics.append(f"{m_name}.merge({item_name}.getUserId(), val, BigDecimal::add);")
            elif "sales" in m_name.lower() or "count" in m_name.lower() or "prod" in m_name.lower():
                merge_logics.append(f"{m_name}.computeIfAbsent({item_name}.getProductId(), k -> new LongAdder()).add({item_name}.getQuantity());")

        # Reconstruct calculation logic
        is_bd = "BigDecimal" in code
        calc = f"{item_name}.getAmount()" if is_bd else f"BigDecimal.valueOf({item_name}.getAmount())"
        
        # Create the optimized block
        optimized_block = f"""
        // --- Optimized Single-Pass Engine ---
        {list_name}.parallelStream().forEach({item_name} -> {{
            BigDecimal val = {calc}.multiply(BigDecimal.valueOf({item_name}.getQuantity()));
            {" ".join(merge_logics)}
        }});
        """
        
        # Replace only the stream/loop part, keeping user's map declarations intact
        code = re.sub(r'// 1️⃣.*?\.collect\(.*?\);', optimized_block, code, flags=re.DOTALL)

    # --- 4. GENERIC LONGADDER HEALER (No Hardcoding) ---
    # Kisi bhi variable par agar max() error hai, toh use theek karo
    for m_name in map_declarations:
        pattern = rf'{m_name}\.entrySet\(\)\.stream\(\)\.max\(Map\.Entry\.comparingByValue\(\)\)'
        if re.search(pattern, code):
            code = re.sub(pattern, 
                          f'{m_name}.entrySet().stream().max(Comparator.comparingLong(e -> e.getValue().sum()))', code)
            tips.append(f"🛠️ <b>Healed:</b> Fixed <code>LongAdder</code> comparison for <code>{m_name}</code>.")

    return code, tips

@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    opt_code, tips = universal_architect_optimizer(data.get('code', ''))
    return jsonify({"optimized_code": opt_code, "tips": tips})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
