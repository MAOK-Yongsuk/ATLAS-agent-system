import json
from src.config import NeMoLLaMa
from src.agents.data_manager import DataManager
import os
from langchain_core.messages import HumanMessage
from src.graph import create_agents_graph
# from IPython.display import Image, display
import re
# from google.colab import files

async def run_all_system(profile_json: str, calendar_json: str, task_json: str):
    try:
        llm = NeMoLLaMa(os.environ["NEMOTRON_4_340B_INSTRUCT_KEY"])
        dm = DataManager()
        dm.load_data(profile_json, calendar_json, task_json)

        user_input = str(input("Input : "))

        state = {
            "messages": [HumanMessage(content=user_input)],
            "profile": dm.get_student_profile("student_123"),
            "calendar": {"events": dm.get_upcoming_events()},
            "tasks": {"tasks": dm.get_active_tasks()},
            "results": {}
        }

        graph = create_agents_graph(llm)
        async for step in graph.astream(state):
            output_graph = step
            print(f"\nStep: {json.dumps(step, indent=2, default=str)}")
        final_state = graph.invoke(state)
        print("eieieiei",final_state)

        # Model Output
        plan_value = output_graph["execute"]["results"]["agent_outputs"]["planner"]["plan"]

        # display(Image(graph.get_graph().draw_mermaid_png()))
        return plan_value
    
    except Exception as e:
        print(f"System error: {e}")

class JsonCleaner:
  @staticmethod
  def clean_json_content(content: str) -> str:
      """Clean JSON content by removing comments and fixing common issues"""
      # Remove single-line comments (// style)
      content = re.sub(r'\s*//.*$', '', content, flags=re.MULTILINE)

      # Remove multi-line comments (/* ... */ style)
      content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

      # Fix trailing commas
      content = re.sub(r',(\s*[}$])', r'\1', content)

      return content

async def load_json_and_test(profile_json: str, calendar_json: str, task_json: str):
  """Load, clean, and validate JSON strings"""
  try:
      json_contents = {}
      cleaner = JsonCleaner()
      
      # Process each JSON string
      json_inputs = {
          'profile': profile_json,
          'calendar': calendar_json,
          'task': task_json
      }

      for file_type, content in json_inputs.items():
          print(f"\nProcessing {file_type} JSON...")
          
          # Clean the content
          print("Cleaning JSON content...")
          cleaned_content = cleaner.clean_json_content(content)
          
          try:
              # Parse JSON string to Python object
              parsed_json = json.loads(cleaned_content)
              json_contents[file_type] = parsed_json
              print(f"✓ Valid JSON for {file_type}")
              
          except json.JSONDecodeError as e:
              print(f"Validation failed for {file_type}!")
              lines = cleaned_content.split('\n')
              line_no = e.lineno - 1
              start = max(0, line_no - 3)
              end = min(len(lines), line_no + 4)
              context_lines = lines[start:end]
              error_context = "\n".join([
                  f"{i+start+1}{' >' if i+start == line_no else '  '} {line}"
                  for i, line in enumerate(context_lines)
              ])
              print(f"\nError: {str(e)}")
              print(f"\nContext:\n{error_context}")
              return

      print("\nAll JSON content processed successfully!")

      # ตรวจสอบและแก้ไขโครงสร้าง profile
      profile_data = json_contents['profile']  # ตอนนี้เป็น dict แล้ว
      
      if isinstance(profile_data, dict):  # เช็คว่าเป็น dict
          if 'profiles' in profile_data and len(profile_data['profiles']) > 0:
              if 'productivity_tools' in profile_data['profiles'][0]:
                  calendar_obj = profile_data['profiles'][0]['productivity_tools']['calendar']
                  if 'default_reminder' in calendar_obj:
                      calendar_obj['default_reminder'] = 24

      # แปลงกลับเป็น JSON string สำหรับส่งต่อ
      profile_str = json.dumps(profile_data)
      calendar_str = json.dumps(json_contents['calendar'])
      task_str = json.dumps(json_contents['task'])

      print("\nStarting test workflow...")
      output = await run_all_system(
          profile_str,
          calendar_str,
          task_str
      )
      return output

  except Exception as e:
      print(f"\nError processing JSON: {str(e)}")
      import traceback
      print("\nDetailed error information:")
      print(traceback.format_exc())

# FIXED_CALENDAR_STRUCTURE = {
#   "platform": "Google Calendar",
#   "sync_status": True,
#   "default_reminder": 24
# }

print("Academic Assistant Test Setup")
print("-" * 50)