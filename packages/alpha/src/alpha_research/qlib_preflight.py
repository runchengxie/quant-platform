"""Bounded admission using actual Qlib operators, without eval or data access."""

from __future__ import annotations

import ast
import hashlib
import json
import math
import operator
import re
from importlib import import_module, metadata

CONTEXT_KEYS = {
    "data_revision",
    "universe_revision",
    "calendar_revision",
    "execution_policy_revision",
    "frequency",
    "dependency_lock_sha256",
}
VOCABULARY = ("Feature", "Ref", "Mean", "Std", "Sum", "Min", "Max", "Rank", "Corr", "Abs", "Log")
WINDOWED = {"Ref", "Mean", "Std", "Sum", "Min", "Max", "Rank", "Corr"}
ARITHMETIC = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def _runtime():
    ops = import_module("qlib.data.ops")
    return {
        "parse": import_module("qlib.utils").parse_field,
        "operators": {name: getattr(ops, name) for name in VOCABULARY},
        "expression_type": ops.Expression,
        "version": metadata.version("pyqlib"),
    }


def _context(allowed_fields, context, role, label_lookahead):
    if (
        not isinstance(context, dict)
        or set(context) != CONTEXT_KEYS
        or any(not isinstance(value, str) or not value.strip() for value in context.values())
    ):
        raise ValueError("explicit revision, frequency and dependency-lock context required")
    if re.fullmatch(r"[0-9a-f]{64}", context["dependency_lock_sha256"]) is None:
        raise ValueError("dependency_lock_sha256 must be a SHA-256")
    if (
        not isinstance(role, str)
        or role not in {"signal", "label"}
        or type(label_lookahead) is not int
    ):
        raise ValueError("explicit signal/label role and integer horizon required")
    if not 0 <= label_lookahead <= 4096 or (role == "signal" and label_lookahead):
        raise ValueError("only labels may have a bounded positive lookahead")
    if (
        not isinstance(allowed_fields, (list, tuple))
        or not allowed_fields
        or any(
            not isinstance(value, str) or re.fullmatch(r"[A-Za-z_]\w*", value) is None
            for value in allowed_fields
        )
    ):
        raise ValueError("an explicit field allowlist is required")


def _call(node, runtime, fields, dependencies):
    if (
        not isinstance(node.func, ast.Attribute)
        or not isinstance(node.func.value, ast.Name)
        or node.func.value.id != "Operators"
        or node.func.attr not in VOCABULARY
        or node.keywords
    ):
        raise ValueError("operator is outside the registered vocabulary")
    name = node.func.attr
    if name == "Feature":
        if (
            len(node.args) != 1
            or not isinstance(node.args[0], ast.Constant)
            or not isinstance(node.args[0].value, str)
            or node.args[0].value not in fields
        ):
            raise ValueError("feature is outside the field allowlist")
        dependencies.add(node.args[0].value)
        return runtime["operators"][name](node.args[0].value)
    args = [_construct(value, runtime, fields, dependencies) for value in node.args]
    if name in WINDOWED:
        count = 3 if name == "Corr" else 2
        if len(args) != count or type(args[-1]) is not int or not 1 <= abs(args[-1]) <= 4096:
            raise ValueError("registered operators require bounded integer windows")
        if name != "Ref" and args[-1] < 0:
            raise ValueError("rolling windows must be positive")
    if any(
        not isinstance(value, runtime["expression_type"])
        for value in (args[:-1] if name in WINDOWED else args)
    ):
        raise ValueError("operator inputs must be Qlib expressions")
    return runtime["operators"][name](*args)


def _construct(node, runtime, fields, dependencies):
    if isinstance(node, ast.Call):
        return _call(node, runtime, fields, dependencies)
    if isinstance(node, ast.BinOp) and type(node.op) in ARITHMETIC:
        return ARITHMETIC[type(node.op)](
            _construct(node.left, runtime, fields, dependencies),
            _construct(node.right, runtime, fields, dependencies),
        )
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _construct(node.operand, runtime, fields, dependencies)
        return value if isinstance(node.op, ast.UAdd) else -value
    if (
        isinstance(node, ast.Constant)
        and type(node.value) in {int, float}
        and math.isfinite(node.value)
        and abs(node.value) <= 1e12
    ):
        return node.value
    raise ValueError("unsupported expression syntax")


def preflight_qlib_expression(
    expression: str, *, allowed_fields, context, role="signal", label_lookahead=0
) -> dict:
    """Return a JSON receipt, not executable code or a full PIT certificate.

    All numeric operators/window metadata are Qlib-owned. This adapter limits
    syntax and binds context; it neither evaluates market data nor certifies
    processor fitting, field publication times or a complete QBX graph.
    """
    result = {
        "schema_version": "alpha_research.qlib-preflight.v1",
        "backend": "qlib",
        "expression": expression if isinstance(expression, str) else None,
        "role": role if isinstance(role, str) else None,
        "pit_verified": False,
    }
    try:
        _context(allowed_fields, context, role, label_lookahead)
    except ValueError as exc:
        return {
            **result,
            "status": "rejected",
            "diagnostic": {"code": "invalid_context", "message": str(exc)},
        }
    try:
        runtime = _runtime()
    except ImportError:
        return {
            **result,
            "status": "unavailable",
            "diagnostic": {"code": "optional_dependency_missing"},
        }
    result["backend_version"] = runtime["version"]
    try:
        if not isinstance(expression, str) or not expression.strip() or len(expression) > 4096:
            raise ValueError("expression must be nonempty and at most 4096 characters")
        tree = ast.parse(runtime["parse"](expression.strip()), mode="eval")
        if sum(1 for _ in ast.walk(tree)) > 256:
            raise ValueError("expression exceeds the registered node budget")
        dependencies = set()
        value = _construct(tree.body, runtime, set(allowed_fields), dependencies)
        if not isinstance(value, runtime["expression_type"]):
            raise ValueError("the root must be a Qlib expression")
        left, right = value.get_extended_window_size()
        if any(not math.isfinite(n) or n < 0 or n > 65536 or int(n) != n for n in (left, right)):
            raise ValueError("unsupported extended window")
    except (
        SyntaxError,
        ValueError,
        TypeError,
        OverflowError,
        ZeroDivisionError,
        RecursionError,
    ) as exc:
        return {
            **result,
            "status": "rejected",
            "diagnostic": {"code": "invalid_expression", "message": str(exc)},
        }
    if right > label_lookahead:
        return {
            **result,
            "status": "rejected",
            "diagnostic": {"code": "future_reference"},
            "right_window": int(right),
        }
    identity = {
        "schema_version": result["schema_version"],
        "backend_version": runtime["version"],
        "syntax": ast.dump(tree, include_attributes=False),
        "fields": sorted(set(allowed_fields)),
        "context": dict(context),
        "role": role,
        "label_lookahead": label_lookahead,
    }
    result.update(
        status="admitted",
        context=dict(context),
        dependencies=sorted(dependencies),
        left_window=int(left),
        right_window=int(right),
        root_sha256=hashlib.sha256(
            json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    )
    return result
