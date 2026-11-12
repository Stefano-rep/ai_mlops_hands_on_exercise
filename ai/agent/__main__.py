"""Desktop assistant by default; --cli enables the terminal interface."""

import argparse
import os
from pathlib import Path
import sys

from langchain_core.messages import HumanMessage

from .graph import build_agent
from .tools import load_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider', choices=['mock', 'openai'], default=os.getenv('AGENT_PROVIDER', 'mock'))
    parser.add_argument('--cli', action='store_true', help='Use the terminal instead of Tkinter.')
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument('--input', type=Path, help='JSON feature record file.')
    inputs.add_argument('--message', help='Single message, JSON record or /schema.')
    args = parser.parse_args()
    try:
        if not args.cli and not args.input and not args.message and os.getenv('AGENT_INTERFACE') != 'cli':
            from .gui import launch_gui
            launch_gui(args.provider)
            return 0
        load_model()
        agent = build_agent(args.provider)
        messages = []

        def ask(text):
            nonlocal messages
            result = agent.invoke({'messages': [*messages, HumanMessage(content=text)]}, {'recursion_limit': 12})
            messages = result['messages']
            print(messages[-1].content)

        if args.input:
            ask(args.input.read_text(encoding='utf-8-sig'))
        elif args.message:
            ask(args.message)
        else:
            print(f'Census agent ({args.provider}). Enter JSON, /schema, /reset or /quit.')
            while True:
                try:
                    text = input('You> ').strip()
                except EOFError:
                    break
                if text.lower() in ('/quit', 'exit', 'quit'):
                    break
                if text == '/reset':
                    messages.clear()
                    print('Conversation cleared.')
                elif text:
                    try:
                        ask(text)
                    except Exception as exc:
                        print(f'Error: {exc}', file=sys.stderr)
    except KeyboardInterrupt:
        print('\nGoodbye.')
    except Exception as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
