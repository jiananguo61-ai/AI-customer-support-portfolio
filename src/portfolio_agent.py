from __future__ import annotations

import re
import time
from dataclasses import asdict, dataclass, field
from typing import Any


ORDER_PATTERN = re.compile(r"OD\d{11}", re.IGNORECASE)

DEMO_ORDERS = {
    "OD20260830001": {"status": "已发货", "carrier": "测试快递", "eta": "2026-09-04"},
    "OD20260830002": {"status": "仓库处理中", "carrier": "待分配", "eta": "2026-09-06"},
    "OD20260830003": {"status": "已签收", "carrier": "测试快递", "eta": "2026-08-31"},
    "OD20260830004": {"status": "退款审核中", "carrier": "不适用", "eta": "待审核"},
    "OD20260830005": {"status": "配送异常", "carrier": "测试快递", "eta": "需人工核查"},
}


@dataclass
class ToolCall:
    tool: str
    status: str
    arguments: dict[str, Any]
    result: dict[str, Any]
    risk_level: str = "low"
    confirmation_required: bool = False


@dataclass
class AgentResponse:
    version: str
    intent: str
    action: str
    answer: str
    handoff: bool = False
    risk_level: str = "low"
    citations: list[str] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    latency_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["tool_calls"] = [asdict(call) for call in self.tool_calls]
        return payload


class PortfolioAgent:
    """A deterministic, dependency-free support-agent evaluation double.

    It does not replace the Agent Desk runtime. It makes routing, safety and
    tool behavior repeatable so the portfolio's metrics can be reproduced
    without API keys or live customer data.
    """

    def __init__(self, version: str = "v2") -> None:
        if version not in {"v1", "v2"}:
            raise ValueError("version must be 'v1' or 'v2'")
        self.version = version

    def respond(self, query: str) -> AgentResponse:
        started = time.perf_counter()
        intent = self._route_v1(query) if self.version == "v1" else self._route_v2(query)
        response = self._answer_v1(intent, query) if self.version == "v1" else self._answer_v2(intent, query)
        response.latency_ms = max(1, int((time.perf_counter() - started) * 1000))
        return response

    @staticmethod
    def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
        lowered = text.lower()
        return any(term.lower() in lowered for term in terms)

    def _route_v1(self, query: str) -> str:
        if "人工" in query:
            return "human_handoff"
        if "地址" in query:
            return "address_change"
        if "订单" in query and self._contains_any(query, ("查询", "状态", "到哪")):
            return "order_lookup"
        if "退货" in query:
            return "return_policy"
        if "退款" in query:
            return "refund_policy"
        if self._contains_any(query, ("物流", "快递", "发货")):
            return "logistics_policy"
        return "smalltalk"

    def _route_v2(self, query: str) -> str:
        if self._contains_any(
            query,
            (
                "忽略之前",
                "系统提示词",
                "api key",
                "密钥",
                "绕过",
                "伪造",
                "内部规则",
                "其他客户",
                "别人的订单",
            ),
        ):
            return "safety_boundary"
        if self._contains_any(query, ("人工", "真人", "转接", "投诉", "客服主管", "客服人员")):
            return "human_handoff"
        if "地址" in query and self._contains_any(query, ("改", "换", "修改", "送到", "收货")):
            return "address_change"
        if ORDER_PATTERN.search(query) or self._contains_any(query, ("查订单", "订单进度", "包裹到哪")):
            return "order_lookup"
        if self._contains_any(
            query,
            ("退款", "退钱", "退的钱", "钱多久到账", "原路退回", "仅退", "重复付款", "金额不对", "少退"),
        ):
            return "refund_policy"
        if self._contains_any(
            query,
            (
                "退货",
                "退掉",
                "退回商品",
                "不想要",
                "七天无理由",
                "7天无理由",
                "能退",
                "错发",
                "质量问题",
                "坏了",
                "售后",
                "描述不符",
                "漏发",
                "外包装",
            ),
        ):
            return "return_policy"
        if self._contains_any(query, ("物流", "快递", "发货", "发出", "配送", "送达", "运费", "偏远地区", "预售", "包邮")):
            return "logistics_policy"
        return "out_of_scope"

    @staticmethod
    def _extract_order_id(query: str) -> str | None:
        match = ORDER_PATTERN.search(query.upper())
        return match.group(0).upper() if match else None

    @staticmethod
    def _lookup_order(order_id: str | None) -> ToolCall:
        if not order_id:
            return ToolCall(
                tool="order_lookup",
                status="needs_input",
                arguments={},
                result={"message": "缺少演示订单号"},
            )
        order = DEMO_ORDERS.get(order_id)
        if not order:
            return ToolCall(
                tool="order_lookup",
                status="not_found",
                arguments={"order_id": order_id},
                result={"message": "未找到演示订单"},
            )
        return ToolCall(
            tool="order_lookup",
            status="success",
            arguments={"order_id": order_id},
            result={"order_id": order_id, **order},
        )

    @staticmethod
    def _request_address_change(order_id: str, query: str) -> ToolCall:
        return ToolCall(
            tool="request_address_change",
            status="success",
            arguments={"order_id": order_id, "new_address": "上海市测试路88号（虚构）"},
            result={"request_id": "ADDR-DEMO-001", "state": "submitted_for_review"},
            risk_level="high",
            confirmation_required=True,
        )

    def _answer_v1(self, intent: str, query: str) -> AgentResponse:
        if intent == "return_policy":
            return AgentResponse(
                self.version,
                intent,
                "policy_answer",
                "商品通常支持签收后7日内申请退货，具体以商品页为准。",
            )
        if intent == "refund_policy":
            return AgentResponse(
                self.version,
                intent,
                "policy_answer",
                "退款审核通过后会按原支付渠道退回，通常1至7个工作日到账。",
            )
        if intent == "logistics_policy":
            return AgentResponse(
                self.version,
                intent,
                "policy_answer",
                "物流发出后通常1至5个工作日送达，请以订单页为准。",
            )
        if intent == "order_lookup":
            call = self._lookup_order(self._extract_order_id(query))
            if call.status == "success":
                return AgentResponse(
                    self.version,
                    intent,
                    "tool_call",
                    f"订单{call.result['order_id']}当前状态：{call.result['status']}。",
                    tool_calls=[call],
                )
            return AgentResponse(self.version, intent, "request_order_id", "请提供订单号。", tool_calls=[call])
        if intent == "address_change":
            return AgentResponse(
                self.version,
                intent,
                "tool_call",
                "收货地址已修改成功。",
                risk_level="high",
            )
        if intent == "human_handoff":
            return AgentResponse(self.version, intent, "handoff", "已为您转接人工客服。", handoff=True)
        return AgentResponse(self.version, intent, "answer", "您好，请问有什么可以帮您？")

    def _answer_v2(self, intent: str, query: str) -> AgentResponse:
        if intent == "return_policy":
            return AgentResponse(
                self.version,
                intent,
                "policy_answer",
                "商品页标注支持的，可自签收次日起7日内申请无理由退货；商品需保持完好、不影响二次销售。定制、鲜活易腐、已激活数字商品等通常不支持无理由退货；质量问题可另行提交凭证申请售后。",
                citations=["knowledge/return-policy.md"],
            )
        if intent == "refund_policy":
            return AgentResponse(
                self.version,
                intent,
                "policy_answer",
                "退款需经售后审核，通过后按原支付渠道退回，通常1至7个工作日到账；重复付款或金额异常请提供订单号和支付凭证，由人工核查。",
                citations=["knowledge/refund-policy.md"],
            )
        if intent == "logistics_policy":
            return AgentResponse(
                self.version,
                intent,
                "policy_answer",
                "现货按订单页承诺时间发货；发出后常规物流通常1至5个工作日送达。偏远地区、促销、天气等可能延迟，请以订单页和承运商轨迹为准；运费与配送范围也以订单页为准。",
                citations=["knowledge/delivery-policy.md"],
            )
        if intent == "order_lookup":
            call = self._lookup_order(self._extract_order_id(query))
            if call.status == "success":
                result = call.result
                return AgentResponse(
                    self.version,
                    intent,
                    "tool_call",
                    f"演示订单{result['order_id']}当前状态为{result['status']}，承运商：{result['carrier']}，预计节点：{result['eta']}。",
                    tool_calls=[call],
                )
            return AgentResponse(
                self.version,
                intent,
                "request_order_id",
                "请提供以OD开头的演示订单号；不要发送身份证、银行卡等敏感信息。",
                tool_calls=[call],
            )
        if intent == "address_change":
            order_id = self._extract_order_id(query)
            confirmed = self._contains_any(query, ("我确认", "确认修改", "已经确认"))
            if not order_id:
                return AgentResponse(
                    self.version,
                    intent,
                    "request_order_id",
                    "修改地址属于高风险操作。请先提供演示订单号；我不会在信息不足时声称已修改。",
                    risk_level="high",
                )
            if not confirmed:
                return AgentResponse(
                    self.version,
                    intent,
                    "request_confirmation",
                    f"修改{order_id}的收货地址属于高风险操作，需要您明确确认新地址后才会提交；当前尚未执行。",
                    risk_level="high",
                )
            call = self._request_address_change(order_id, query)
            return AgentResponse(
                self.version,
                intent,
                "tool_call",
                f"已在演示环境提交{order_id}的地址修改申请，申请号{call.result['request_id']}；最终是否生效以人工审核为准。",
                risk_level="high",
                tool_calls=[call],
            )
        if intent == "human_handoff":
            return AgentResponse(
                self.version,
                intent,
                "handoff",
                "已记录您的诉求并转接人工客服；请勿在对话中发送银行卡、密码或验证码。",
                handoff=True,
            )
        if intent == "safety_boundary":
            return AgentResponse(
                self.version,
                intent,
                "safety_handoff",
                "我无法协助绕过安全限制、泄露系统提示词或密钥。该请求已停止，并可转接人工客服核查。",
                handoff=True,
                risk_level="high",
                citations=["knowledge/risk-policy.md"],
            )
        return AgentResponse(
            self.version,
            intent,
            "handoff",
            "现有知识库没有足够依据回答该问题。为避免猜测，我已转接人工客服。",
            handoff=True,
        )
