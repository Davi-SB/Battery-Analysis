from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import pandas as pd

app = Flask(__name__)
CORS(app)

cells = []
try:
    with open('src/lithium_cells.txt', 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            cells.append({
                'Battery Name': parts[0],
                'Nominal Voltage (V)': float(parts[1]),
                'Continuous Discharge Current (A)': float(parts[2]),
                'Capacity (mAh)': float(parts[3]),
            })
except FileNotFoundError:
    print("Error: lithium_cells.txt not found!")

df_cells = pd.DataFrame(cells)


@app.route('/api/cells', methods=['GET'])
def get_cells():
    """Returns available battery cells from the file"""
    return jsonify(cells)


@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Performs battery calculations"""
    data = request.json
    cell_name = data.get('cell_type')
    input_type = data.get('input_type')

    v_bat = data.get('v_bat')
    i_bat = data.get('i_bat')
    t_bat = data.get('t_bat')
    C_bat = data.get('capacity')

    try:
        v_bat = float(v_bat)
        if input_type == "capacity" and C_bat:
            C_bat = float(C_bat)
        elif i_bat and t_bat:
            i_bat = float(i_bat)
            t_bat = float(t_bat)
            C_bat = i_bat * t_bat
        else:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input"}), 400

    selected_cell = next((cell for cell in cells if cell['Battery Name'] == cell_name), None)
    if not selected_cell:
        return jsonify({"error": "Cell not found"}), 404

    n_series = math.ceil(v_bat / selected_cell['Nominal Voltage (V)'])
    n_parallel = math.ceil(C_bat / (selected_cell['Capacity (mAh)'] * 1e-3))
    total = n_series * n_parallel

    bat_summary = {
        'v_bat': v_bat,
        'i_bat': i_bat,
        't_bat': t_bat,
        'C_bat': C_bat,
        'n_series': n_series,
        'n_parallel': n_parallel,
        'total': total,
    }

    return jsonify(bat_summary)


if __name__ == '__main__':
    app.run(debug=True)
