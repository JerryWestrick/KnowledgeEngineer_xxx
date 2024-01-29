OpenAI_API_Costs = {

    # GPT4 Turbo
    'gpt-4-1106-preview': {'model': 'gpt-4-1106-preview', 'input': 0.0100, 'output': 0.0300, 'context': 128000},
    'gpt-4-0125-preview': {'model': 'gpt-4-0125-preview', 'input': 0.0100, 'output': 0.0300, 'context': 128000},

    # GPT4
    'gpt-4': {'model': 'gpt-4', 'input': 0.0300, 'output': 0.0600, 'context': 8000},
    'gpt-4-32k': {'model': 'gpt-4-32k', 'input': 0.0600, 'output': 0.1200, 'context': 32000},

    # GPT3
    'gpt-3.5-turbo-1106': {'model': 'gpt-3.5-turbo-1106', 'input': 0.0010, 'output': 0.0020, 'context': 16000},
    'gpt-3.5-turbo-instruct': {'model': 'gpt-3.5-turbo-instruct', 'input': 0.0015, 'output': 0.0020, 'context': 4000},
}
