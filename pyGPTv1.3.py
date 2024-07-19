import sys
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QPushButton, QWidget, QLineEdit, QLabel, QHBoxLayout, QComboBox, QListWidget, QListWidgetItem, QMessageBox

# Load environment variables from a .env file
load_dotenv()

# Retrieve API key from environment variable
api_key = os.getenv('API_KEY')
if not api_key:
    raise ValueError("API key not found. Please set the API_KEY environment variable.")

client = OpenAI(
    api_key=api_key
)

CONVERSATIONS_FILE = "conversations.json"

class ChatGPTClient(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Chat GPT Client')
        self.setGeometry(100, 100, 800, 600)
        
        self.init_ui()
        self.conversations = []
        self.current_conversation_index = None
        
        self.load_conversations()
    
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.sidebar = QListWidget(self)
        self.sidebar.setMaximumWidth(250)
        self.sidebar.itemClicked.connect(self.load_conversation)
        
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        
        self.model_label = QLabel("Select Model:", self)
        self.model_dropdown = QComboBox(self)
        self.model_dropdown.addItems([
            "gpt-4o-mini-2024-07-18", "gpt-4o-mini", "gpt-4o-2024-05-13", "gpt-4o", 
            "gpt-4-turbo-preview", "gpt-4-turbo-2024-04-09", "gpt-4-turbo", 
            "gpt-4-1106-preview", "gpt-4-0613", "gpt-4-0125-preview", "gpt-4", 
            "gpt-3.5-turbo-16k", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-0125", "gpt-3.5-turbo"
        ])
        
        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Message ChatGPT")
        self.send_button = QPushButton('Send', self)
        self.send_button.clicked.connect(self.send_message)
        
        self.new_conversation_button = QPushButton('New Conversation', self)
        self.new_conversation_button.clicked.connect(self.create_new_conversation)

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.sidebar)
        
        self.chat_layout = QVBoxLayout()
        self.chat_layout.addWidget(self.chat_display)
        
        self.input_layout = QHBoxLayout()
        self.input_layout.addWidget(self.text_input)
        self.input_layout.addWidget(self.send_button)
        
        self.model_layout = QHBoxLayout()
        self.model_layout.addWidget(self.model_label)
        self.model_layout.addWidget(self.model_dropdown)
        
        self.chat_layout.addLayout(self.model_layout)
        self.chat_layout.addLayout(self.input_layout)
        self.main_layout.addLayout(self.chat_layout)
        
        self.layout.addLayout(self.main_layout)
        self.layout.addWidget(self.new_conversation_button)  # Add the new conversation button to the main layout
        
    def send_message(self):
        user_message = self.text_input.text().strip()
        if user_message:
            if self.current_conversation_index is None:
                self.create_new_conversation()
            
            self.chat_display.append(f"You: {user_message}")
            self.text_input.clear()
            
            # Add the user message to the conversation before sending it to the API
            self.conversations[self.current_conversation_index]['messages'].append({"role": "user", "content": user_message})
            
            response = self.get_gpt_response()
            self.chat_display.append(f"GPT: {response}")
            
            # Add the assistant's response to the conversation
            self.conversations[self.current_conversation_index]['messages'].append({"role": "assistant", "content": response})
            self.update_conversation_list()
            self.save_conversations()
    
    def get_gpt_response(self):
        selected_model = self.model_dropdown.currentText()
        try:
            response = client.chat.completions.create(
                model=selected_model,
                messages=self.conversations[self.current_conversation_index]['messages']
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
            return f"Error: {str(e)}"
    
    def create_new_conversation(self):
        self.conversations.append({
            "title": f"Conversation {len(self.conversations) + 1}",
            "messages": [{"role": "system", "content": "You are a helpful assistant."}]
        })
        self.current_conversation_index = len(self.conversations) - 1
        self.update_conversation_list()
        self.chat_display.clear()
        self.save_conversations()
    
    def update_conversation_list(self):
        self.sidebar.clear()
        for conv in self.conversations:
            item = QListWidgetItem(conv['title'])
            self.sidebar.addItem(item)
    
    def load_conversation(self, item):
        self.current_conversation_index = self.sidebar.row(item)
        self.chat_display.clear()
        conversation = self.conversations[self.current_conversation_index]
        for msg in conversation['messages']:
            role = "You" if msg['role'] == "user" else "GPT"
            self.chat_display.append(f"{role}: {msg['content']}")
    
    def save_conversations(self):
        with open(CONVERSATIONS_FILE, 'w') as file:
            json.dump(self.conversations, file, indent=4)
    
    def load_conversations(self):
        if os.path.exists(CONVERSATIONS_FILE):
            with open(CONVERSATIONS_FILE, 'r') as file:
                self.conversations = json.load(file)
            self.update_conversation_list()

def main():
    app = QApplication(sys.argv)
    main_window = ChatGPTClient()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
