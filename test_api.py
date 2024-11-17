import requests
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

files = {
  'profile_json': open(os.path.join(current_dir, "src","database", "profile.json"), 'rb'),
  'calendar_json': open(os.path.join(current_dir, "src","database", "calendar.json"), 'rb'),
  'task_json': open(os.path.join(current_dir, "src","database", "task.json"), 'rb')
}

try:
  response = requests.post('http://localhost:5000/llm', files=files)
  
  print("Status Code:", response.status_code)
  print("Response Headers:", response.headers)
  print("Response Text:", response.text)
  
  if response.headers.get('content-type') == 'application/json':
      print("Response JSON:", response.json())

except Exception as e:
  print(f"Error: {str(e)}")

finally:
  # ปิดไฟล์ทั้งหมด
  for file in files.values():
      file.close()