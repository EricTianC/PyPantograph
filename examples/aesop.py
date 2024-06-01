#!/usr/bin/env python3

import subprocess
from pathlib import Path
from pantograph.server import Server

def get_project_and_lean_path():
    cwd = Path(__file__).parent.resolve() / 'Example'
    p = subprocess.check_output(['lake', 'env', 'printenv', 'LEAN_PATH'], cwd=cwd)
    return cwd, p

if __name__ == '__main__':
    project_path, lean_path = get_project_and_lean_path()
    print(f"$PWD: {project_path}")
    print(f"$LEAN_PATH: {lean_path}")
    server = Server(imports=['Example'], project_path=project_path, lean_path=lean_path)
    state0 = server.goal_start("forall (p q: Prop), Or p q -> Or q p")
    state1 = server.goal_tactic(state0, goal_id=0, tactic="aesop")
    assert state1.is_solved
