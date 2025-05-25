import subprocess
from .files import get_extension
from .timeout import TimeoutException, signal
from .env import dev

supported_languages = {
    "py": lambda agent_path: {
        "compile": None,
        "run": ['python3', agent_path]
    },

    "cpp": lambda agent_path: {
        "compile": ['g++', '-std=c++17', agent_path, '-o', f'{agent_path}.out'],
        "run": [f'./{agent_path}.out']
    },

    "java": lambda agent_path: {
        "compile": ['javac', agent_path],
        "run": ['java', agent_path[:-5]]  # assumes agent_path ends in .java
    },

    "js": lambda agent_path: {
        "compile": None,
        "run": ['node', agent_path]
    },

    "c": lambda agent_path: {
        "compile": ['gcc', agent_path, '-o', f'{agent_path}.out'],
        "run": [f'./{agent_path}.out']
    },
    "terminal" : {

    }
}
class Agent:
    def __init__(self,id : str, cmd_path):
        self.path = cmd_path
        self._id = id
        self.terminal_agent = cmd_path == "terminal.terminal"
        self.timeout = 1000 if self.terminal_agent or dev else 2
    def get_id(self):
        return self._id
    id = property(get_id)
    def send_message(self,message :str):
        if self.terminal_agent:
            print(f"To Agent {self.id}: {message}")
            return message
        self.__agent.stdin.write(f"{message}\n")
        self.__agent.stdin.flush()
        return message
    
    def stderror(self):
        r = self.__agent.poll()
        if r is None or r == 0:
            return None
        return self.__agent.stderr.read()

    def __get_action(self):
        signal.alarm(self.timeout)
        try:
            self.send_message("TURN")
            response = input() if self.terminal_agent else str(self.__agent.stdout.readline()).strip()
            if response == "":
                return None
            return response.split()
        finally:
            signal.alarm(0)  # disable alarm
        
    
    def get_action(self):
        try:
            response = self.__get_action()
            if response is None:
                raise Exception(f"Agent {self.id} quit prematurely")
            return response
        except TimeoutException:
            raise Exception(f"Agent {self.id} caused a timeout (2 seconds)")

    def launch(self):
        if self.terminal_agent:
            return
        config = supported_languages[get_extension(self.path)](self.path)
        if config["compile"]:
            subprocess.run(config["compile"], check=True)
        self.__agent = subprocess.Popen(
            config["run"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    def return_code(self):
        if self.terminal_agent:
            return None
        return self.__agent.poll()
    def kill(self):
        if self.terminal_agent:
            return
        self.__agent.kill()

