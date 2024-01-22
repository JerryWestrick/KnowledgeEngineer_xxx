import os

def get_subdirectories(directory):
    return {name: os.listdir(os.path.join(directory, name, 'Steps')) for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))}

subdirectories = get_subdirectories('./Memory')
print(f"Dictionary with Subdirectories: {subdirectories}")