# app.py
from flask import Flask, request, jsonify
from src.run import load_json_and_test
import asyncio
import json

app = Flask(__name__)

@app.route('/llm', methods=['POST'])
def test_json():
  try:
      if 'calendar_json' not in request.files or \
         'task_json' not in request.files:
          return jsonify({'error': 'Missing required files'}), 400

      # profile_file = request.files['profile_json']
      calendar_file = request.files['calendar_json']
      task_file = request.files['task_json']


      with open("src/database/profile.json", 'r', encoding='utf-8') as f:
        profile_json = f.read()
      # profile_json = json.loads(profile_file.read().decode('utf-8'))
      calendar_json = json.loads(calendar_file.read().decode('utf-8'))
      task_json = json.loads(task_file.read().decode('utf-8'))

      # แปลงเป็น JSON string
      profile_str = json.dumps(profile_json)
      calendar_str = json.dumps(calendar_json)
      task_str = json.dumps(task_json)
      
      # เรียกใช้ฟังก์ชัน test ด้วย asyncio.run
      result = asyncio.run(load_json_and_test(profile_str, calendar_str, task_str))
      
      return jsonify({'result': result})
  
  except json.JSONDecodeError:
      return jsonify({'error': 'Invalid JSON file'}), 400
  except Exception as e:
      return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
  app.run(debug=True, port=5000)