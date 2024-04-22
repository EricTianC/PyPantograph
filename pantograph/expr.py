"""
Data structuers for expressions and goals
"""
from dataclasses import dataclass
from typing import Optional, Self, Union

Expr = str

def parse_expr(payload: dict) -> Expr:
    return payload["pp"]

@dataclass(frozen=True)
class Variable:
    t: Expr
    v: Optional[Expr] = None
    name: Optional[str] = None

    @staticmethod
    def _parse(payload: dict) -> Self:
        name = payload.get("userName")
        t = parse_expr(payload["type"])
        v = payload.get("value")
        if v:
            v = parse_expr(v)
        return Variable(t, v, name)

    def __str__(self):
        result = self.name if self.name else "_"
        result += f" : {self.t}"
        if self.v:
            result += f" = {self.v}"
        return result

@dataclass(frozen=True)
class Goal:
    variables: list[Variable]
    target: Expr
    name: Optional[str] = None

    @staticmethod
    def sentence(target: Expr) -> Self:
        return Goal(variables=[], target=target)

    @staticmethod
    def _parse(payload: dict) -> Self:
        name = payload.get("userName")
        variables = [Variable._parse(v) for v in payload["vars"]]
        target = parse_expr(payload["target"])
        return Goal(variables, target, name)

    def __str__(self):
        return "\n".join(str(v) for v in self.variables) + \
            f"\n⊢ {self.target}"

@dataclass(frozen=True)
class GoalState:
    state_id: int
    goals: list[Goal]

    @property
    def is_solved(self) -> bool:
        return not self.goals

@dataclass(frozen=True)
class TacticNormal:
    payload: str
@dataclass(frozen=True)
class TacticHave:
    branch: str

Tactic = Union[TacticNormal, TacticHave]
