from __future__ import annotations

from datetime import datetime

from .base import Broker, Fill


class RestBrokerAdapter(Broker):
    """외부 시장데이터·주문 인터페이스 연동을 위한 어댑터 경계.

    현재 저장소는 특정 사업자의 인증정보나 주문 엔드포인트에 의존하지 않는다.
    실제 외부 인터페이스를 연결할 때 이 계층에서 시세 조회, 포지션 조회,
    주문 기능을 구현하고 전략·포트폴리오·리스크 관리 코드는 그대로 재사용한다.
    """

    def get_price(self, symbol: str) -> float:
        raise NotImplementedError("외부 시세 조회 구현 필요")

    def get_position(self, symbol: str) -> int:
        raise NotImplementedError("외부 포지션 조회 구현 필요")

    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        timestamp: datetime,
    ) -> Fill:
        raise NotImplementedError("외부 주문 구현 필요")
