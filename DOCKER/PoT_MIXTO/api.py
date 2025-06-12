from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

# Almacenará la configuración actual
current_config = {
    'script': None,
    'params': None
}

# Directorio base para los scripts
SCRIPT_BASE_DIR = "/home/ubuntu/PoT_MIXTO"

@app.route('/run-command', methods=['POST'])
def run_command():
    global current_config
    data = request.get_json()
    script = data.get('script')
    
    if not script or not isinstance(script, str):
        return jsonify({'status': 'error', 'message': 'Script must be provided and must be a string'}), 400

    # Construir la ruta completa del script
    full_script_path = os.path.join(SCRIPT_BASE_DIR, script)
    
    # Diferenciar según el script a ejecutar
    if script == "scenario-generator_nodes.sh":
        number1 = data.get('number1')
        number2 = data.get('number2')
        option = data.get('option')
        
        if not isinstance(number1, int) or not (1 <= number1 <= 10):
            return jsonify({'status': 'error', 'message': 'number1 must be an integer between 1 and 10'}), 400
        if not isinstance(number2, int) or not (0 <= number2 <= 10):
            return jsonify({'status': 'error', 'message': 'number2 must be an integer between 1 and 10'}), 400
        if not option or not isinstance(option, str):
            return jsonify({'status': 'error', 'message': 'Option must be provided and must be a string'}), 400
        
        args = [str(number1), str(number2), option]
    else:
        # Caso por defecto: scenario-generator.sh u otro script que requiera 1 número y 1 opción
        number = data.get('number')
        option = data.get('option')
        
        if not isinstance(number, int) or not (0 <= number <= 10):
            return jsonify({'status': 'error', 'message': 'Number must be an integer between 1 and 10'}), 400
        if not option or not isinstance(option, str):
            return jsonify({'status': 'error', 'message': 'Option must be provided and must be a string'}), 400
        
        args = [str(number), option]

    # Construir el comando completo
    command = " ".join([full_script_path] + args)
    
    # Almacenar la configuración actual
    current_config = {
        'script': full_script_path,
        'params': args
    }

    try:
        # Ejecutar el comando
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return jsonify({
            'STATUS': 'Success',
            'SSSS OUTPUT': result.stdout,
            'CREATED': result.stderr
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/delete-script', methods=['DELETE'])
def delete_script():
    data = request.get_json()
    script = data.get('script')

    if not script or not isinstance(script, str):
        return jsonify({'status': 'error', 'message': 'Script must be provided and must be a string'}), 400

    try:
        full_script_path = os.path.join(SCRIPT_BASE_DIR, script)
        command = f"{full_script_path}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return jsonify({
            'STATUS': 'Success',
            'output': result.stdout,
            'DELETE STATUS': result.stderr
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/get-config', methods=['GET'])
def get_config():
    return jsonify(current_config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
