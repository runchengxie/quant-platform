"""Safe, strategy-agnostic factor formula expressions."""

from __future__ import annotations

import ast
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pandas as pd

_BinaryEvaluator = Callable[[Any, Any], Any]
_OperatorEvaluator = Callable[[list[Any], pd.DataFrame, list[ast.AST]], Any]


@dataclass(frozen=True)
class _Operator:
    arity: int
    lookback: Callable[[list[ast.AST]], int]
    evaluate: _OperatorEvaluator
    requires_symbol_date_index: bool = False


def _constant_window(args: list[ast.AST], position: int) -> int:
    node = args[position]
    if not isinstance(node, ast.Constant) or isinstance(node.value, bool):
        raise ValueError("window must be a positive integer constant")
    if not isinstance(node.value, int) or node.value <= 0:
        raise ValueError("window must be a positive integer constant")
    return node.value


def _no_lookback(args: list[ast.AST]) -> int:
    return 0


def _window_lookback(position: int) -> Callable[[list[ast.AST]], int]:
    return lambda args: _constant_window(args, position)


def _rank(values: list[Any], frame: pd.DataFrame, args: list[ast.AST]) -> pd.Series:
    return values[0].groupby(level="date", sort=False).rank(method="average", pct=True)


def _delay(values: list[Any], frame: pd.DataFrame, args: list[ast.AST]) -> pd.Series:
    return values[0].groupby(level="symbol", sort=False).shift(_constant_window(args, 1))


def _returns(values: list[Any], frame: pd.DataFrame, args: list[ast.AST]) -> pd.Series:
    window = _constant_window(args, 1)
    delayed = values[0].groupby(level="symbol", sort=False).shift(window)
    return values[0] / delayed - 1


def _rolling_std(values: list[Any], frame: pd.DataFrame, args: list[ast.AST]) -> pd.Series:
    window = _constant_window(args, 1)
    return _grouped_rolling(values[0], window, lambda series: series.std(ddof=1))


def _rolling_corr(values: list[Any], frame: pd.DataFrame, args: list[ast.AST]) -> pd.Series:
    window = _constant_window(args, 2)
    pair = pd.concat(values[:2], axis=1)
    result = pd.Series(index=pair.index, dtype="float64")
    for _, group in pair.groupby(level="symbol", sort=False):
        result.loc[group.index] = group.iloc[:, 0].rolling(window).corr(group.iloc[:, 1]).to_numpy()
    return result


def _grouped_rolling(
    series: pd.Series, window: int, operation: Callable[[pd.Series], pd.Series]
) -> pd.Series:
    result = pd.Series(index=series.index, dtype="float64")
    for _, group in series.groupby(level="symbol", sort=False):
        result.loc[group.index] = operation(group.rolling(window)).to_numpy()
    return result


def _default_operators() -> dict[str, _Operator]:
    return {
        "RANK": _Operator(1, _no_lookback, _rank, True),
        "DELAY": _Operator(2, _window_lookback(1), _delay, True),
        "RETURNS": _Operator(2, _window_lookback(1), _returns, True),
        "STDDEV": _Operator(2, _window_lookback(1), _rolling_std, True),
        "CORRELATION": _Operator(3, _window_lookback(2), _rolling_corr, True),
    }


class OperatorRegistry:
    """Whitelist of formula operators available to :func:`parse_factor`."""

    def __init__(self) -> None:
        self._operators = _default_operators()

    def get(self, name: str) -> _Operator:
        try:
            return self._operators[name]
        except KeyError as exc:
            raise ValueError(f"unknown factor operator: {name}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._operators)


@dataclass(frozen=True)
class FactorExpression:
    """A validated formula that can be interpreted against a DataFrame."""

    _tree: ast.Expression
    _required: tuple[str, ...]
    _lookback: int
    _operators: tuple[str, ...]
    _registry: OperatorRegistry

    def required_columns(self) -> tuple[str, ...]:
        return self._required

    def lookback(self) -> int:
        return self._lookback

    def normalized(self) -> str:
        return ast.unparse(self._tree.body)

    def operators(self) -> tuple[str, ...]:
        return self._operators

    def evaluate(self, frame: pd.DataFrame) -> pd.Series:
        if not isinstance(frame, pd.DataFrame):
            raise TypeError("frame must be a pandas DataFrame")
        value = _evaluate_node(self._tree.body, frame, self._registry)
        if not isinstance(value, pd.Series):
            value = pd.Series(value, index=frame.index)
        return value.rename("factor")


def parse_factor(source: str, *, registry: OperatorRegistry | None = None) -> FactorExpression:
    """Parse and validate one safe factor expression."""

    if not isinstance(source, str) or not source.strip():
        raise ValueError("factor expression must be a non-empty string")
    try:
        tree = ast.parse(source, mode="eval")
    except SyntaxError as exc:
        raise ValueError("factor expression must contain one expression") from exc

    registry = registry or OperatorRegistry()
    required: list[str] = []
    operators: list[str] = []
    lookback = _validate_node(tree.body, registry, required, operators)
    return FactorExpression(
        tree,
        tuple(required),
        lookback,
        tuple(operators),
        registry,
    )


def _validate_node(  # noqa: C901
    node: ast.AST,
    registry: OperatorRegistry,
    required: list[str],
    operators: list[str],
) -> int:
    if isinstance(node, ast.Name):
        if node.id.startswith("__"):
            raise ValueError("dunder names are not allowed")
        if node.id not in required:
            required.append(node.id)
        return 0
    if (
        isinstance(node, ast.Constant)
        and isinstance(node.value, (int, float))
        and not isinstance(node.value, bool)
    ):
        return 0
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        return _validate_node(node.operand, registry, required, operators)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
        return max(
            _validate_node(node.left, registry, required, operators),
            _validate_node(node.right, registry, required, operators),
        )
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.keywords or len(node.args) == 0:
            raise ValueError("factor operators do not accept keyword arguments")
        operator = registry.get(node.func.id)
        if len(node.args) != operator.arity:
            raise ValueError(f"{node.func.id} expects {operator.arity} arguments")
        if node.func.id not in operators:
            operators.append(node.func.id)
        child_lookback = max(
            (_validate_node(argument, registry, required, operators) for argument in node.args),
            default=0,
        )
        return max(child_lookback, operator.lookback(node.args))
    raise ValueError(f"unsupported factor expression syntax: {type(node).__name__}")


def _validate_index(frame: pd.DataFrame) -> None:
    if not isinstance(frame.index, pd.MultiIndex) or not {"symbol", "date"}.issubset(
        frame.index.names
    ):
        raise ValueError("time-series factor operators require a symbol/date MultiIndex")


def _evaluate_node(node: ast.AST, frame: pd.DataFrame, registry: OperatorRegistry) -> Any:
    if isinstance(node, ast.Name):
        return frame[node.id]
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.UnaryOp):
        value = _evaluate_node(node.operand, frame, registry)
        if isinstance(node.op, ast.USub):
            return -value
        return +value
    if isinstance(node, ast.BinOp):
        left = _evaluate_node(node.left, frame, registry)
        right = _evaluate_node(node.right, frame, registry)
        operations: dict[type[ast.operator], _BinaryEvaluator] = {
            ast.Add: lambda a, b: a + b,
            ast.Sub: lambda a, b: a - b,
            ast.Mult: lambda a, b: a * b,
            ast.Div: lambda a, b: a / b,
        }
        return operations[type(node.op)](left, right)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        operator = registry.get(node.func.id)
        if operator.requires_symbol_date_index:
            _validate_index(frame)
        values = [_evaluate_node(argument, frame, registry) for argument in node.args]
        return operator.evaluate(values, frame, node.args)
    raise ValueError(f"unsupported factor expression syntax: {type(node).__name__}")
