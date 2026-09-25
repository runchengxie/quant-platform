"""Execution-lifecycle table renderers (reconcile, cancel, traces, retries)."""

from __future__ import annotations

from typing import Any

from ..broker.base import BrokerReconcileReport
from ..diagnostics import diagnose_order_issue, diagnose_warning_message
from ..execution import (
    ExecutionAcceptPartialResult,
    ExecutionBulkCancelResult,
    ExecutionOrderTrace,
    ExecutionReconcileDelta,
    ExecutionRepriceResult,
    ExecutionResumeRemainingResult,
    ExecutionStaleRetryResult,
    ExecutionTrackedOrder,
)
from ._table_helpers import (
    _append_child_selection_lines,
    _append_diagnostic,
    _append_parent_lines,
)


def render_reconcile_summary(
    *,
    report: BrokerReconcileReport,
    state_path: str,
    tracked_orders: int,
    fill_events: int,
    new_fill_events: int,
    refreshed_orders: int,
    changed_orders: list[ExecutionReconcileDelta],
) -> str:
    """Render manual reconcile summary."""

    lines = [
        "Reconcile summary:",
        f"- Broker / Account: {report.broker_name} / {report.account_label}",
        f"- Open orders from broker: {len(report.open_orders)}",
        f"- Tracked broker orders: {tracked_orders}",
        f"- Total fill events in state: {fill_events}",
        f"- New fill events recorded: {new_fill_events}",
        f"- Closed tracked orders refreshed: {refreshed_orders}",
        f"- Changed tracked orders: {len(changed_orders)}",
        f"- State file: {state_path}",
    ]
    if changed_orders:
        lines.append("- Changes:")
        for delta in changed_orders:
            before_status = delta.before_status or "-"
            fill_delta = delta.after_filled_quantity - delta.before_filled_quantity
            lines.append(
                "  * "
                f"{delta.broker_order_id} {delta.symbol}: "
                f"{before_status} -> {delta.after_status}, "
                f"filled {delta.before_filled_quantity:g} -> {delta.after_filled_quantity:g}"
            )
            if delta.new_fill_events > 0 or fill_delta > 0:
                lines.append(
                    f"    new_fill_events={delta.new_fill_events}, filled_delta={fill_delta:g}"
                )
    if report.warnings:
        lines.append("- Warnings:")
        for warning in report.warnings:
            diagnostic = diagnose_warning_message(warning)
            lines.append(f"  * [{diagnostic.code}] {diagnostic.summary}")
            if diagnostic.action_hint:
                lines.append(f"    next: {diagnostic.action_hint}")
    return "\n".join(lines)


def render_cancel_summary(
    *,
    broker_name: str,
    account_label: str,
    order_ref: str,
    broker_order_id: str,
    client_order_id: str | None,
    status: str,
    state_path: str,
    warnings: list[str],
) -> str:
    """Render tracked-order cancel summary."""

    lines = [
        "Cancel summary:",
        f"- Broker / Account: {broker_name} / {account_label}",
        f"- Requested Ref: {order_ref}",
        f"- Broker Order ID: {broker_order_id}",
        f"- Client Order ID: {client_order_id or '-'}",
        f"- Current Status: {status}",
        f"- State file: {state_path}",
    ]
    if warnings:
        lines.append("- Warnings:")
        for warning in warnings:
            diagnostic = diagnose_warning_message(warning)
            lines.append(f"  * [{diagnostic.code}] {diagnostic.summary}")
            if diagnostic.action_hint:
                lines.append(f"    next: {diagnostic.action_hint}")
    return "\n".join(lines)


def render_bulk_cancel_summary(outcome: ExecutionBulkCancelResult) -> str:
    """Render tracked bulk-cancel summary."""

    canceled = sum(1 for result in outcome.results if result.status == "CANCELED")
    pending_cancel = sum(1 for result in outcome.results if result.status == "PENDING_CANCEL")
    other_statuses = len(outcome.results) - canceled - pending_cancel

    lines = [
        "Bulk cancel summary:",
        f"- Broker / Account: {outcome.broker_name} / {outcome.account_label}",
        f"- Tracked open orders targeted: {outcome.targeted_orders}",
        f"- Cancel requests completed: {len(outcome.results)}",
        f"- Final CANCELED: {canceled}",
        f"- Final PENDING_CANCEL: {pending_cancel}",
        f"- Other statuses: {other_statuses}",
        f"- State file: {outcome.state_path}",
    ]
    if outcome.results:
        lines.append("- Orders:")
        for result in outcome.results:
            lines.append(
                f"  * {result.broker_order_id} ({result.client_order_id or '-'}) -> {result.status}"
            )
            for warning in result.warnings:
                diagnostic = diagnose_warning_message(warning)
                lines.append(f"    warning: [{diagnostic.code}] {diagnostic.summary}")
                if diagnostic.action_hint:
                    lines.append(f"    next: {diagnostic.action_hint}")
    if outcome.warnings:
        lines.append("- Warnings:")
        for warning in outcome.warnings:
            diagnostic = diagnose_warning_message(warning)
            lines.append(f"  * [{diagnostic.code}] {diagnostic.summary}")
            if diagnostic.action_hint:
                lines.append(f"    next: {diagnostic.action_hint}")
    if not outcome.results and not outcome.warnings:
        lines.append("- No tracked open orders were found in local execution state")
    return "\n".join(lines)


def render_tracked_order_detail(tracked: ExecutionTrackedOrder) -> str:
    """Render tracked order details from local execution state."""

    lines = [
        "Tracked order detail:",
        f"- Broker / Account: {tracked.broker_name} / {tracked.account_label}",
        f"- Requested Ref: {tracked.order_ref}",
        f"- State file: {tracked.state_path}",
    ]
    _append_tracked_intent_lines(lines, tracked)
    _append_tracked_parent_detail_lines(lines, tracked)
    _append_tracked_child_detail_lines(lines, tracked)
    if tracked.broker_order is not None:
        lines.extend(
            [
                f"- Broker Order ID: {tracked.broker_order.broker_order_id}",
                f"- Broker Status: {tracked.broker_order.status}",
                f"- Client Order ID: {tracked.broker_order.client_order_id or '-'}",
                "- Broker Filled / Remaining: "
                f"{float(tracked.broker_order.filled_quantity or 0.0):g} / "
                f"{float(tracked.broker_order.remaining_quantity or 0.0):g}",
            ]
        )
        diagnostic = diagnose_order_issue(tracked.broker_order)
        _append_diagnostic(lines, diagnostic)
    elif tracked.child is not None:
        diagnostic = diagnose_order_issue(tracked.child)
        _append_diagnostic(lines, diagnostic)
    lines.append(f"- Fill Events: {len(tracked.fill_events)}")
    for fill in tracked.fill_events:
        lines.append(f"  * {fill.fill_id}: {fill.quantity:g} @ {fill.price:g} on {fill.filled_at}")
    return "\n".join(lines)


def _append_tracked_intent_lines(lines: list[str], tracked: ExecutionTrackedOrder) -> None:
    intent = tracked.intent
    if intent is None:
        return
    lines.extend(
        [
            f"- Intent: {intent.intent_id} {intent.side} {intent.quantity:g} {intent.symbol}",
            f"- Intent Order Type: {intent.order_type}",
            f"- Target Source: {intent.target_source or '-'}",
            f"- Target Asof: {intent.target_asof or '-'}",
            f"- Target Input: {intent.target_input_path or '-'}",
        ]
    )
    if str(intent.order_type).upper() == "LIMIT":
        limit_price = intent.limit_price if intent.limit_price is not None else "-"
        lines.append(f"- Intent Limit Price: {limit_price}")
    last_reprice_at = intent.metadata.get("last_reprice_at")
    if last_reprice_at:
        lines.append(f"- Last Reprice At: {last_reprice_at}")
    if "last_reprice_from_limit_price" in intent.metadata:
        lines.append(
            f"- Last Reprice From Limit: {intent.metadata.get('last_reprice_from_limit_price')}"
        )


def _append_tracked_parent_detail_lines(lines: list[str], tracked: ExecutionTrackedOrder) -> None:
    parent = tracked.parent
    if parent is None:
        return
    lines.extend(
        [
            f"- Parent: {parent.parent_order_id}",
            f"- Parent Status: {parent.status}",
            "- Parent Filled / Remaining: "
            f"{parent.filled_quantity:g} / {parent.remaining_quantity:g}",
        ]
    )
    manual_resolution = parent.metadata.get("manual_resolution")
    if manual_resolution:
        lines.append(f"- Manual Resolution: {manual_resolution}")
    if parent.metadata.get("manual_resolution_at"):
        lines.append(f"- Manual Resolution At: {parent.metadata.get('manual_resolution_at')}")


def _append_tracked_child_detail_lines(lines: list[str], tracked: ExecutionTrackedOrder) -> None:
    child = tracked.child
    if child is None:
        return
    lines.extend(
        [
            f"- Child: {child.child_order_id} (attempt {child.attempt})",
            f"- Child Status: {child.status}",
        ]
    )
    if child.message:
        lines.append(f"- Child Message: {child.message}")


def render_order_trace(trace: ExecutionOrderTrace) -> str:
    """Render a merged tracked-state and broker-side trace."""

    lines = [
        "Order trace:",
        f"- Broker / Account: {trace.broker_name} / {trace.account_label}",
        f"- Requested Ref: {trace.order_ref}",
        f"- State file: {trace.state_path}",
    ]
    if trace.intent is not None:
        lines.extend(
            [
                f"- Intent: {trace.intent.intent_id} {trace.intent.side} "
                f"{trace.intent.quantity:g} {trace.intent.symbol}",
                f"- Intent Order Type: {trace.intent.order_type}",
                f"- Intent Run ID: {trace.intent.run_id}",
            ]
        )
        if trace.intent.limit_price is not None:
            lines.append(f"- Intent Limit Price: {trace.intent.limit_price}")
    _append_parent_lines(lines, trace.parent)
    _append_child_selection_lines(lines, trace.child)
    if trace.broker_order is not None:
        lines.append(
            "- Selected Broker Order: "
            f"{trace.broker_order.broker_order_id} ({trace.broker_order.status}, "
            f"filled {float(trace.broker_order.filled_quantity or 0.0):g} / "
            f"remaining {float(trace.broker_order.remaining_quantity or 0.0):g})"
        )
        diagnostic = diagnose_order_issue(trace.broker_order)
        _append_diagnostic(lines, diagnostic)
    _append_trace_children(lines, trace)
    _append_trace_orders(
        lines, "Local Tracked Broker Orders", trace.tracked_broker_orders, show_message=True
    )
    _append_trace_fills(lines, "Local Fill Events", trace.fill_events)
    _append_trace_orders(lines, "Broker-side Order History", trace.broker_history_orders)
    _append_trace_fills(lines, "Broker-side Fill History", trace.broker_history_fills)
    _append_warning_lines(lines, trace.warnings)
    return "\n".join(lines)


def _append_trace_children(lines: list[str], trace: ExecutionOrderTrace) -> None:
    lines.append(f"- Local Child Attempts: {len(trace.child_orders)}")
    for child in trace.child_orders:
        lines.append(
            "  * "
            f"attempt {child.attempt}: {child.child_order_id} -> {child.status}"
            f", broker_order_id={child.broker_order_id or '-'}"
            f", client_order_id={child.client_order_id or '-'}"
        )
        if child.message:
            lines.append(f"    message: {child.message}")


def _append_trace_orders(
    lines: list[str], heading: str, records: list[Any], *, show_message: bool = False
) -> None:
    lines.append(f"- {heading}: {len(records)}")
    for record in records:
        lines.append(
            "  * "
            f"{record.broker_order_id}: {record.status}, "
            f"filled {float(record.filled_quantity or 0.0):g} / "
            f"remaining {float(record.remaining_quantity or 0.0):g}, "
            f"updated {record.updated_at}"
        )
        if show_message and getattr(record, "message", None):
            lines.append(f"    message: {record.message}")


def _append_trace_fills(lines: list[str], heading: str, records: list[Any]) -> None:
    lines.append(f"- {heading}: {len(records)}")
    for record in records:
        lines.append(
            f"  * {record.fill_id}: {record.quantity:g} @ {record.price:g} on {record.filled_at}"
        )


def _append_warning_lines(lines: list[str], warnings: list[str]) -> None:
    if not warnings:
        return
    lines.append("- Warnings:")
    for warning in warnings:
        diagnostic = diagnose_warning_message(warning)
        lines.append(f"  * [{diagnostic.code}] {diagnostic.summary}")
        if diagnostic.action_hint:
            lines.append(f"    next: {diagnostic.action_hint}")


def render_retry_summary(
    *,
    broker_name: str,
    account_label: str,
    order_ref: str,
    new_child_order_id: str,
    broker_order_id: str | None,
    broker_status: str | None,
    state_path: str,
    warnings: list[str],
) -> str:
    """Render tracked-order retry summary."""

    lines = [
        "Retry summary:",
        f"- Broker / Account: {broker_name} / {account_label}",
        f"- Requested Ref: {order_ref}",
        f"- New Child Order ID: {new_child_order_id}",
        f"- Broker Order ID: {broker_order_id or '-'}",
        f"- Broker Status: {broker_status or '-'}",
        f"- State file: {state_path}",
    ]
    if warnings:
        lines.append("- Warnings:")
        for warning in warnings:
            diagnostic = diagnose_warning_message(warning)
            lines.append(f"  * [{diagnostic.code}] {diagnostic.summary}")
            if diagnostic.action_hint:
                lines.append(f"    next: {diagnostic.action_hint}")
    return "\n".join(lines)


def render_reprice_summary(outcome: ExecutionRepriceResult) -> str:
    """Render tracked-order reprice summary."""

    old_limit_price = outcome.old_limit_price if outcome.old_limit_price is not None else "-"
    lines = [
        "Reprice summary:",
        f"- Broker / Account: {outcome.broker_name} / {outcome.account_label}",
        f"- Requested Ref: {outcome.order_ref}",
        f"- Old Broker Order ID: {outcome.old_broker_order_id}",
        f"- Cancel Status: {outcome.cancel_status}",
        f"- Old Limit Price: {old_limit_price}",
        f"- New Limit Price: {outcome.new_limit_price}",
        f"- New Child Order ID: {outcome.new_child_order_id or '-'}",
        f"- New Broker Order ID: {outcome.broker_order_id or '-'}",
        f"- New Broker Status: {outcome.broker_status or '-'}",
        f"- State file: {outcome.state_path}",
    ]
    if outcome.warnings:
        lines.append("- Warnings:")
        for warning in outcome.warnings:
            diagnostic = diagnose_warning_message(warning)
            lines.append(f"  * [{diagnostic.code}] {diagnostic.summary}")
            if diagnostic.action_hint:
                lines.append(f"    next: {diagnostic.action_hint}")
    return "\n".join(lines)


def render_stale_retry_summary(outcome: ExecutionStaleRetryResult) -> str:
    """Render stale tracked-order retry summary."""

    lines = [
        "Stale retry summary:",
        f"- Broker / Account: {outcome.broker_name} / {outcome.account_label}",
        f"- Older Than (minutes): {outcome.older_than_minutes}",
        f"- Targeted stale tracked orders: {outcome.targeted_orders}",
        f"- Cancel attempts completed: {len(outcome.cancel_results)}",
        f"- Retry attempts completed: {len(outcome.retry_results)}",
        f"- State file: {outcome.state_path}",
    ]
    _append_stale_cancel_results(lines, outcome)
    _append_stale_retry_results(lines, outcome)
    _append_warning_lines(lines, outcome.warnings)
    if not outcome.cancel_results and not outcome.retry_results and not outcome.warnings:
        lines.append("- No stale tracked open orders were eligible for retry")
    return "\n".join(lines)


def _append_stale_cancel_results(lines: list[str], outcome: ExecutionStaleRetryResult) -> None:
    if not outcome.cancel_results:
        return
    lines.append("- Cancel results:")
    for result in outcome.cancel_results:
        lines.append(f"  * {result.broker_order_id} -> {result.status}")
        _append_indented_warning_lines(lines, result.warnings)


def _append_stale_retry_results(lines: list[str], outcome: ExecutionStaleRetryResult) -> None:
    if not outcome.retry_results:
        return
    lines.append("- Retry results:")
    for result in outcome.retry_results:
        lines.append(
            f"  * {result.order_ref} -> "
            f"child {result.new_child_order_id} / "
            f"broker {result.broker_order_id or '-'} / "
            f"status {result.broker_status or '-'}"
        )
        _append_indented_warning_lines(lines, result.warnings)


def _append_indented_warning_lines(lines: list[str], warnings: list[str]) -> None:
    for warning in warnings:
        diagnostic = diagnose_warning_message(warning)
        lines.append(f"    warning: [{diagnostic.code}] {diagnostic.summary}")
        if diagnostic.action_hint:
            lines.append(f"    next: {diagnostic.action_hint}")


def render_resume_remaining_summary(outcome: ExecutionResumeRemainingResult) -> str:
    """Render resume-remaining summary."""

    lines = [
        "Resume remaining summary:",
        f"- Broker / Account: {outcome.broker_name} / {outcome.account_label}",
        f"- Requested Ref: {outcome.order_ref}",
        f"- Submitted Remaining Quantity: {outcome.submitted_quantity:g}",
        f"- New Child Order ID: {outcome.new_child_order_id}",
        f"- Broker Order ID: {outcome.broker_order_id or '-'}",
        f"- Broker Status: {outcome.broker_status or '-'}",
        f"- State file: {outcome.state_path}",
    ]
    if outcome.warnings:
        lines.append("- Warnings:")
        for warning in outcome.warnings:
            diagnostic = diagnose_warning_message(warning)
            lines.append(f"  * [{diagnostic.code}] {diagnostic.summary}")
            if diagnostic.action_hint:
                lines.append(f"    next: {diagnostic.action_hint}")
    return "\n".join(lines)


def render_accept_partial_summary(outcome: ExecutionAcceptPartialResult) -> str:
    """Render accept-partial summary."""

    lines = [
        "Accept partial summary:",
        f"- Broker / Account: {outcome.broker_name} / {outcome.account_label}",
        f"- Requested Ref: {outcome.order_ref}",
        f"- Parent Order ID: {outcome.parent_order_id}",
        f"- Accepted Filled Quantity: {outcome.accepted_filled_quantity:g}",
        f"- Abandoned Remaining Quantity: {outcome.abandoned_remaining_quantity:g}",
        f"- State file: {outcome.state_path}",
    ]
    if outcome.warnings:
        lines.append("- Warnings:")
        for warning in outcome.warnings:
            diagnostic = diagnose_warning_message(warning)
            lines.append(f"  * [{diagnostic.code}] {diagnostic.summary}")
            if diagnostic.action_hint:
                lines.append(f"    next: {diagnostic.action_hint}")
    return "\n".join(lines)
