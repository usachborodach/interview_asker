import os
import random
import webbrowser

base_path = os.path.dirname(__file__)
os.chdir(base_path)
file_path = 'list.md'
file = open(file_path)
content = file.read()
file.close()
lines = content.splitlines()
random_line = random.choice(lines)
question = random_line.split('[')[1].split(']')[0]
answer_anchor = random_line.split('(')[1].split(')')[0]
answer_url = f'https://github.com/Swfuse/devops-interview/blob/main/interview.md{answer_anchor}'

print(f'Question: {question}')
input('Press Enter to open the answer in your web browser...')
webbrowser.open(answer_url)