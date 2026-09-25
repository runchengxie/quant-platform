"""RebalanceService planning layer.

Builds on :class:`RebalancePricingMixin`: per-symbol order construction and the
top-level ``plan_rebalance`` entry point.
"""

from __future__ import annotations

import math
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from ._rebalance_pricing import RebalancePricingMixin
from .config import load_cfg
from .fees import FeeSchedule, estimate_fees
from .logging import get_logger
from .models import AccountSnapshot, Order, Position, RebalanceResult
from .targets import TargetEntry

logger = get_logger(__name__)


class RebalancePlanMixin(RebalancePricingMixin):
    """Per-symbol order construction + plan_rebalance (planning layer)."""

    def _build_order(
        self,
        lb_symbol: str,
        price: float,
        current_qty: int,
        target_qty_raw: float,
        allow_fractional: bool,
        client: Any,
        fs: FeeSchedule,
        frac_enable: bool,
        frac_step: Decimal,
    ) -> tuple[Position, Order | None]:
        """Build target position and corresponding order for a symbol."""
        lot_size = client.lot_size(lb_symbol)
        target_qty_int = math.floor(float(target_qty_raw) + 1e-9)
        target_qty = (target_qty_int // lot_size) * lot_size
        target_qty_frac = Decimal(0)
        if price > 0 and frac_enable:
            target_qty_frac = Decimal(str(target_qty_raw)).quantize(
                frac_step, rounding=ROUND_HALF_UP
            )
        target_position = Position(
            symbol=lb_symbol,
            quantity=target_qty,
            last_price=price,
            estimated_value=target_qty * price,
            env=self.env,
        )

        delta_qty = target_qty - current_qty
        if abs(delta_qty) < lot_size:
            logger.info(f"跳过 {lb_symbol}：差额 {delta_qty} 小于最小交易单位 {lot_size}")
            return target_position, None

        side = "BUY" if delta_qty > 0 else "SELL"
        qty_to_trade = abs(delta_qty)
        order = Order(
            symbol=lb_symbol,
            quantity=qty_to_trade,
            side=side,
            price=price,
            order_type="MARKET",
        )
        est_fee, frac_hint = estimate_fees(
            side=side,
            qty_int=qty_to_trade,
            price=price,
            any_fractional_lt1=(target_qty_frac > 0 and target_qty_frac < 1),
            fs=fs,
        )
        order.est_fees = est_fee
        order.est_frac_hint = frac_hint
        if frac_enable:
            order.target_qty_frac = float(target_qty_frac)
            order.rounded_target_qty = int(target_qty)
            order.rounding_loss = float(target_qty_frac - Decimal(int(target_qty)))

        return target_position, order

    def plan_rebalance(
        self,
        targets: list[TargetEntry],
        account_snapshot: AccountSnapshot,
        quotes: dict[str, float] | None = None,
        allow_fractional: bool = False,
        target_gross_exposure: float = 1.0,
    ) -> RebalanceResult:
        """Create rebalancing plan

        Args:
            targets: Canonical target entries
            account_snapshot: Current account snapshot

        Returns:
            RebalanceResult: Rebalancing plan result
        """
        if not targets:
            raise ValueError("目标列表不能为空")

        if quotes is None:
            try:
                quotes = self._fetch_quotes(targets)
            except Exception as e:
                logger.error(f"获取报价失败: {e}")
                raise
        quotes = self._normalize_quotes_to_usd(quotes)
        self._refresh_positions_from_usd_quotes(account_snapshot, quotes)

        weighted_targets = [target for target in targets if target.target_weight is not None]

        effective_total = self._compute_effective_total(
            account_snapshot, quotes, target_gross_exposure
        )
        target_value_per_stock = (
            effective_total / len(weighted_targets) if weighted_targets else 0.0
        )

        # Build current position mapping
        current_positions_map = {pos.symbol: pos for pos in account_snapshot.positions}

        client = self._get_client()
        cfg = load_cfg() or {}
        fees_cfg = (cfg.get("fees") or {}) if isinstance(cfg, dict) else {}
        fs = FeeSchedule(
            commission=float(fees_cfg.get("commission", 0.0) or 0.0),
            platform_per_share=float(fees_cfg.get("platform_per_share", 0.005) or 0.0),
            fractional_pct_lt1=float(fees_cfg.get("fractional_pct_lt1", 0.012) or 0.0),
            fractional_cap_lt1=float(fees_cfg.get("fractional_cap_lt1", 0.99) or 0.0),
            sell_reg_fees_bps=float(fees_cfg.get("sell_reg_fees_bps", 0.0) or 0.0),
        )
        frac_cfg = (cfg.get("fractional_preview") or {}) if isinstance(cfg, dict) else {}
        frac_enable = bool(frac_cfg.get("enable", True))
        frac_step = Decimal(str(frac_cfg.get("default_step", 0.001)))

        target_positions, orders = self._plan_target_entries(
            targets,
            current_positions_map=current_positions_map,
            quotes=quotes,
            effective_total=effective_total,
            allow_fractional=allow_fractional,
            client=client,
            fee_schedule=fs,
            frac_enable=frac_enable,
            frac_step=frac_step,
        )
        target_set = {self._coerce_lb_symbol(target) for target in targets}
        liquidations = self._plan_unrequested_liquidations(
            current_positions_map,
            target_set=target_set,
            quotes=quotes,
            client=client,
            fee_schedule=fs,
        )
        target_positions.extend(position for position, _ in liquidations)
        orders.extend(order for _, order in liquidations)

        return RebalanceResult(
            target_positions=target_positions,
            current_positions=account_snapshot.positions,
            orders=orders,
            total_portfolio_value=effective_total,
            target_value_per_stock=target_value_per_stock,
            env=self.env,
            broker_name=self.broker_name,
            account_label=self.account_label,
        )

    def _plan_target_entries(
        self,
        targets: list[TargetEntry],
        *,
        current_positions_map: dict[str, Position],
        quotes: dict[str, float],
        effective_total: float,
        allow_fractional: bool,
        client: Any,
        fee_schedule: FeeSchedule,
        frac_enable: bool,
        frac_step: Decimal,
    ) -> tuple[list[Position], list[Order]]:
        target_positions: list[Position] = []
        orders: list[Order] = []
        for target in targets:
            symbol = self._coerce_lb_symbol(target)
            price_value = quotes.get(symbol)
            if not price_value or price_value <= 0:
                logger.warning(f"跳过 {target.symbol}：无有效价格")
                continue
            price = float(price_value)
            current = current_positions_map.get(symbol)
            current_qty = current.quantity if current else 0
            target_qty = (
                float(target.target_quantity)
                if target.target_quantity is not None
                else effective_total * float(target.target_weight or 0.0) / price
            )
            position, order = self._build_order(
                symbol,
                price,
                current_qty,
                target_qty,
                allow_fractional,
                client,
                fee_schedule,
                frac_enable,
                frac_step,
            )
            target_positions.append(position)
            if order is not None:
                orders.append(order)
        return target_positions, orders

    def _plan_unrequested_liquidations(
        self,
        current_positions: dict[str, Position],
        *,
        target_set: set[str],
        quotes: dict[str, float],
        client: Any,
        fee_schedule: FeeSchedule,
    ) -> list[tuple[Position, Order]]:
        liquidations: list[tuple[Position, Order]] = []
        for symbol, current in current_positions.items():
            if symbol in target_set or current.quantity <= 0:
                continue
            lot_size = client.lot_size(symbol)
            quantity = (int(current.quantity) // lot_size) * lot_size
            if quantity <= 0:
                continue
            price = float(quotes.get(symbol, current.last_price or 0.0))
            position = Position(
                symbol=symbol,
                quantity=0,
                last_price=price,
                estimated_value=0.0,
                env=self.env,
            )
            order = Order(
                symbol=symbol,
                quantity=quantity,
                side="SELL",
                price=price if price > 0 else None,
                order_type="MARKET",
            )
            order.est_fees, order.est_frac_hint = estimate_fees(
                side="SELL",
                qty_int=quantity,
                price=price or 0.0,
                any_fractional_lt1=False,
                fs=fee_schedule,
            )
            liquidations.append((position, order))
        return liquidations
