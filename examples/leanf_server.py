#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
import secrets

app = FastAPI()

import subprocess
from pathlib import Path
from pantograph.expr import GoalState
from pantograph.server import Server



def get_project_and_lean_path():
    cwd = Path(__file__).parent.resolve() / 'Example'
    p = subprocess.check_output(['lake', 'env', 'printenv', 'LEAN_PATH'], cwd=cwd)
    return cwd, p

def state2json(state: GoalState, session: str):
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
        "session": session,
    }



project_path, lean_path = get_project_and_lean_path()
print(f"$PWD: {project_path}")
print(f"$LEAN_PATH: {lean_path}")
server = Server(imports=['Example'], project_path=project_path, lean_path=lean_path)

# check if the server is working
state0 = server.goal_start("forall (p q: Prop), Or p q -> Or q p")
state1 = server.goal_tactic(state0, goal_id=0, tactic="aesop")
assert state1.is_solved

session_pool = {}

@app.get("/goal_start")
async def goal_start(prop: str):
    session = secrets.token_urlsafe(16)
    try:
        state0 = server.goal_start(prop)
        session_pool[session] = state0
        return state2json(state0, session=session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/goal_tactic")
async def goal_tactic(session: str, goal_id: int, tactic: str):
    try:
        new_state = server.goal_tactic(session_pool[session], goal_id, tactic)
        session_pool[session] = new_state
        return state2json(new_state, session=session)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/close_session")
async def close_session(session: str):
    try:
        del session_pool[session]
        return {"status": "ok"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/check_session_pool")
async def check_session_pool():
    return session_pool

@app.route("/")
async def test():
   return {"hello": "world"}