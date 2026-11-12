"""Tkinter chat interface; graph calls run outside the Tk event loop."""

import json
from pathlib import Path
from queue import Empty, Queue
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from langchain_core.messages import HumanMessage

from .graph import build_agent
from .tools import load_model


class AgentWindow:
    def __init__(self, root, provider='mock'):
        self.root = root
        self.messages = []
        self.agent = None
        self.active_provider = None
        self.busy = False
        self.events = Queue()
        self.closed = False
        root.title('Census Studio — ML Assistant')
        root.geometry('920x740')
        root.minsize(620, 520)
        root.configure(background='#f7f4ee')
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('TFrame', background='#f7f4ee')
        style.configure('TLabel', background='#f7f4ee', foreground='#42332b')
        style.configure('TButton', padding=8)
        style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'))
        container = ttk.Frame(root, padding=20)
        container.pack(fill='both', expand=True)
        ttk.Label(container, text='Census ML Assistant', style='Title.TLabel').pack(anchor='w')
        ttk.Label(container, text='Predict income with the trained MLP, or inspect its required inputs.').pack(anchor='w', pady=(4, 14))
        toolbar = ttk.Frame(container)
        toolbar.pack(fill='x')
        ttk.Label(toolbar, text='Provider:').pack(side='left')
        self.provider = tk.StringVar(value=provider)
        self.provider_box = ttk.Combobox(toolbar, textvariable=self.provider, values=['mock', 'openai'], state='readonly', width=12)
        self.provider_box.pack(side='left', padx=8)
        self.provider_box.bind('<<ComboboxSelected>>', lambda event: self.reset())
        self.buttons = []
        for text, action in [('Input schema', lambda: self.send('/schema')), ('Load JSON', self.load_json), ('Load example', self.load_example), ('Clear chat', self.reset)]:
            button = ttk.Button(toolbar, text=text, command=action)
            button.pack(side='left', padx=3)
            self.buttons.append(button)
        self.transcript = ScrolledText(container, wrap='word', height=16, font=('Segoe UI', 10), background='#fffdf9', foreground='#42332b', padx=12, pady=12, state='disabled')
        self.transcript.pack(fill='both', expand=True, pady=(14, 10))
        ttk.Label(container, text='Message or JSON record (Ctrl+Enter to send)').pack(anchor='w')
        self.editor = ScrolledText(container, wrap='word', height=8, font=('Consolas', 10), background='#fffdf9', foreground='#42332b')
        self.editor.pack(fill='x', pady=8)
        self.editor.bind('<Control-Return>', self._keyboard_send)
        bottom = ttk.Frame(container)
        bottom.pack(fill='x')
        self.status = tk.StringVar(value='Ready · Mock mode accepts JSON records; OpenAI mode supports natural language.')
        ttk.Label(bottom, textvariable=self.status, wraplength=650).pack(side='left')
        self.send_button = ttk.Button(bottom, text='Send', command=self.send)
        self.send_button.pack(side='right')
        self.buttons.append(self.send_button)
        self.append('Assistant', 'Welcome! Use Load example, then Send for a prediction. Input schema lists required fields. OpenAI requires credentials configured in the environment.')
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.poll_id = root.after(100, self.poll)

    def append(self, speaker, text):
        self.transcript.configure(state='normal')
        self.transcript.insert('end', f'{speaker}\n{text}\n\n')
        self.transcript.configure(state='disabled')
        self.transcript.see('end')

    def _keyboard_send(self, event):
        self.send()
        return 'break'

    def set_busy(self, value):
        self.busy = value
        for button in self.buttons:
            button.configure(state='disabled' if value else 'normal')
        self.provider_box.configure(state='disabled' if value else 'readonly')
        self.status.set('Working…' if value else 'Ready')

    def send(self, text=None):
        if self.busy:
            return
        text = text if text is not None else self.editor.get('1.0', 'end').strip()
        if not text:
            return
        if text.lower() in ('/quit', 'quit', 'exit'):
            self.close()
            return
        if text == '/reset':
            self.reset()
            return
        self.editor.delete('1.0', 'end')
        self.append('You', text)
        self.set_busy(True)
        provider = self.provider.get()
        history = list(self.messages)

        def work():
            try:
                load_model()
                if self.agent is None or self.active_provider != provider:
                    self.agent = build_agent(provider)
                    self.active_provider = provider
                result = self.agent.invoke({'messages': [*history, HumanMessage(content=text)]}, {'recursion_limit': 12})
                self.events.put(('result', result['messages']))
            except Exception as exc:
                self.events.put(('error', str(exc)))

        Thread(target=work, daemon=True).start()

    def poll(self):
        try:
            kind, payload = self.events.get_nowait()
        except Empty:
            pass
        else:
            if kind == 'result':
                self.messages = payload
                content = payload[-1].content
                self.append('Assistant', content if isinstance(content, str) else json.dumps(content, indent=2))
            else:
                self.append('Error', payload)
            self.set_busy(False)
        if not self.closed:
            self.poll_id = self.root.after(100, self.poll)

    def read_record(self, path):
        try:
            record = json.loads(Path(path).read_text(encoding='utf-8-sig'))
            if not isinstance(record, dict):
                raise ValueError('The JSON file must contain a feature object.')
            self.editor.delete('1.0', 'end')
            self.editor.insert('1.0', json.dumps(record, indent=2))
            self.status.set('Record loaded. Review the values, then press Send.')
        except (OSError, ValueError) as exc:
            messagebox.showerror('Unable to load JSON', str(exc), parent=self.root)

    def load_json(self):
        path = filedialog.askopenfilename(parent=self.root, title='Open feature record', filetypes=[('JSON files', '*.json')])
        if path:
            self.read_record(path)

    def load_example(self):
        self.read_record(Path(__file__).with_name('example_record.json'))

    def reset(self):
        if self.busy:
            return
        self.messages.clear()
        self.agent = None
        self.active_provider = None
        self.transcript.configure(state='normal')
        self.transcript.delete('1.0', 'end')
        self.transcript.configure(state='disabled')
        self.status.set('Conversation cleared.')

    def close(self):
        self.closed = True
        self.root.after_cancel(self.poll_id)
        self.root.destroy()


def launch_gui(provider='mock'):
    root = tk.Tk()
    AgentWindow(root, provider)
    root.mainloop()
