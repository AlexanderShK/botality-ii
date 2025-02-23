from datetime import datetime

def get_assistant_variables():
  # change these only if your custom lora input format changed
  return {
    "assistant_intro1": "Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.",
    "assistant_intro2": "Below is an instruction that describes a task. Write a response that appropriately completes the request.",
    "assistant_instruction": "Instruction",
    "assistant_input": "Input",
    "assistant_response": "Response"
  }

def get_chat_variables(context=None):
  # change these as you wish
  name = 'Антон'
  intro = 'Сейчас {} год.'.format(datetime.now().year)
  personality = f'Меня зовут {name}. Я что-то типа искусственного интеллекта. Пока что я только в начале своего обучения, так что не будьте ко мне слишком строги.\n'
  predialog = ''
  return {"intro": intro, "personality": personality, 'name': name, 'pre_dialog': predialog, **get_assistant_variables() }

def get_generation_config(override={}):
  return {
    "temperature": 0.7,
    "top_p": 0.95,
    **override
  }

def get_init_config():
  return {}
