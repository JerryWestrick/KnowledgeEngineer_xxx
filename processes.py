import jsonpickle as jsonpickle
from step import Step

import os
import shutil
from pathlib import Path
import glob

from logger import Logger


# This class represents a simple database that stores its data as files in a directory hierarchy.


class Processes:
    """A simple key-value store, where keys are filenames and values are file contents."""
    wlog = Logger(namespace='PROCESS', debug=True)

    def __init__(self, path):
        # path is the directory where the data is stored
        self.path = Path(path).absolute()
        self.path.mkdir(parents=True, exist_ok=True)

    def __contains__(self, key):
        return (self.path / key).is_file()

    def __delitem__(self, key: str):
        # Implement the logic to delete the item with the given key
        full_path = self.path / key
        if full_path.is_file():
            os.remove(full_path)
        else:
            shutil.rmtree(f'{full_path}')
        return

    def read(self, key: str):
        k: str = f"{key}.kestep"
        full_path = self.path / k
        if not full_path.is_file():
            self.wlog.error(f"Invalid Memory Item.  \nPath not found: {full_path}")
            raise KeyError(key)
        with full_path.open("r", encoding="utf-8") as f:
            content = f.read()
        step = jsonpickle.decode(content)
        # self.wlog.info(f"Read--> Processes/{key}")
        return step

    def __getitem__(self, key: str) -> Step:
        """Return the contents of the file with the given key."""
        return self.read(key)

    def glob_files(self, search: str) -> [str]:
        """ Return a list of all files in the database that match the search pattern """
        s = self.path / search
        l = len(str(self.path))
        files = []
        for x in glob.glob(str(s), recursive=True):
            files.append(x[l+1:].replace('.kestep', ''))
        files.sort()
        return files

    def get(self, key: str, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def new_process(self, proc_name: str) -> str:
        self.wlog.info(f"New Process: {proc_name}")
        full_path = self.path / f"{proc_name}"
        full_path.mkdir(parents=True, exist_ok=True)
        return proc_name

    def __setitem__(self, proc_name: str, step: Step) -> Step:
        self.wlog.info(f"Save Step: {self.path}/{proc_name}/{step.name}, {step.ai.max_tokens}")
        if isinstance(step, Step):
            full_path = self.path / f"{proc_name}/{step.name}.kestep"
        else:
            full_path = self.path / f"{proc_name}"

        full_path.parent.mkdir(parents=True, exist_ok=True)

        step_json = jsonpickle.encode(step, indent=2)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(step_json)
        return step
