#!/usr/bin/env python3
from fastapi import FastAPI

app = FastAPI()

import subprocess
from pathlib import Path
from pantograph.expr import GoalState
from pantograph.server import Server



def get_project_and_lean_path():
    cwd = Path(__file__).parent.resolve() / 'Example'
    p = subprocess.check_output(['lake', 'env', 'printenv', 'LEAN_PATH'], cwd=cwd)
    return cwd, p

def state2json(state: GoalState):
    return {
        "goals": list(map(lambda goal : 
                          {
                                "variables": list(map(lambda variable: 
                                                      {"t": variable.t,
                                                       "v": variable.v,
                                                       "name": variable.name}, goal.variables)),
                                "target": goal.target,
                                "sibling_dep": goal.sibling_dep,
                                "name": goal.name,
                                "is_conversion": goal.is_conversion,
                            }, state.goals)),
        "is_solved": state.is_solved,
    }



project_path, lean_path = get_project_and_lean_path()
print(f"$PWD: {project_path}")
print(f"$LEAN_PATH: {lean_path}")
server = Server(imports=['Example'], project_path=project_path, lean_path=lean_path)

# check if the server is working
state0 = server.goal_start("forall (p q: Prop), Or p q -> Or q p")
state1 = server.goal_tactic(state0, goal_id=0, tactic="aesop")
assert state1.is_solved

@app.get("goal_start")
async def goal_start(prop: str):
    state0 = server.goal_start(prop)
    return state2json(state0)
    
@app.get("goal_tactic")
async def goal_tactic(state, goal_id: int, tactic: str):
    new_state = server.goal_tactic(state, goal_id, tactic)
    return state2json(new_state)

@app.route("/")
async def test(request):
   return {"hello": "world"}