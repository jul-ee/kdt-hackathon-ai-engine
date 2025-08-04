"""
app/schemas.py
==============

Pydantic 데이터 모델(Pydantic Schemas) 정의 모듈
FastAPI 엔드포인트 Request/Response 바디 검증 및 문서화를 담당합니다.

섹션별 역할
------------
1. 슬롯 추출 관련 모델
   * `SlotQuery`      : 자연어 입력 파싱 요청 바디
   * `JobPreview`     : 일거리 카드 미리보기(단건)
   * `TourPreview`    : 관광지 카드 미리보기(단건)
   * `SlotsResponse`  : 슬롯 + 카드 10개 미리보기 응답

2. 추천(일정 생성) 관련 모델
   * `RecommendationRequest` : 공통 필드(query, user_id, budget)
   * `RecommendRequest`      : 선택한 카드 ID 리스트를 추가한 최종 요청

3. 일정(Itinerary) 모델
   * `ScheduleItem` : 하루 단위 일정 항목
   * `Itinerary`    : 향후 확장 가능성을 위해 ScheduleItem 을 그대로 상속

주의사항
~~~~~~~~
• 이 모듈은 비즈니스 로직이 없는 순수 데이터 클래스만 포함해야 합니다.
• 필드 순서나 타입을 변경하면 FastAPI 스펙 및 클라이언트와의 계약이 깨질 수 있으므로, 기존 필드는 그대로 유지해야 합니다.
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

# ─────────────────────────────────────────────────────────────────
# 1) 슬롯 추출용 스키마
# ─────────────────────────────────────────────────────────────────

class SlotQuery(BaseModel):
    """사용자 자연어 쿼리 하나를 감싸는 Request Body 모델."""
    query: str = Field(
        ...,  # 필수값
        example="9월 첫째 주 고창에서 조개잡이 + 해변 관광하고 싶어요",
        description="일·여행 조건이 포함된 자연어 문장",
    )


# ─────────────────────────────────────────────────────────────────
# 2) 카드 미리보기 응답 모델
# ─────────────────────────────────────────────────────────────────

class JobPreview(BaseModel):
    """벡터 유사도 상위 Job(일거리) 카드 메타데이터."""
    job_id: int
    farm_name: str
    region: str
    tags: List[str]


class TourPreview(BaseModel):
    """벡터 유사도 상위 Tour(관광지) 카드 메타데이터."""
    content_id: int
    title: str
    region: str
    overview: str
    image_url: Optional[str] = None  # 🔥 NEW: 이미지 URL 필드 추가


class SlotsResponse(BaseModel):
    """/slots 엔드포인트 응답 모델."""
    slots: dict  # GPT Slot Extraction 결과(JSON)
    jobs_preview: List[JobPreview]
    tours_preview: List[TourPreview]


# ─────────────────────────────────────────────────────────────────
# 3) 추천 요청 스키마
# ─────────────────────────────────────────────────────────────────

class RecommendationRequest(BaseModel):
    """추천(일정 생성) 요청 공통 필드."""
    query: str
    user_id: Optional[UUID] = None  # 로그인 사용자 식별자(옵션)
    budget: int  # 전체 여행 예산(₩)


class RecommendRequest(RecommendationRequest):
    """/recommend 엔드포인트 최종 Request Body."""
    selected_jobs: List[int] = Field(default_factory=list)
    selected_tours: List[int] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────
# 4) 일정(Itinerary) 모델
# ─────────────────────────────────────────────────────────────────

class ScheduleItem(BaseModel):
    """하루 단위 여행·일거리 Schedule."""
    day: int
    date: str
    plan_items: List[str]
    total_distance_km: Optional[float]
    total_cost_krw: Optional[int]


class Itinerary(ScheduleItem):
    """현재는 ScheduleItem과 동일하지만 향후 다중 일정을 위한 래퍼."""

    pass  # 확장을 위해 비워둠
