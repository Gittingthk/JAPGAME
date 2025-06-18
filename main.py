"""
FastAPI + WebSocket + SQLite
(워치 v2.1 프로토콜 대응 — DB 저장과 브로드캐스트를 한 파일에 통합)

  • GET  /time      : epoch µs 반환 → 워치 NTP 동기화
  • POST /collect   : 패킷 저장 + 모든 대시보드로 실시간 push
  • WS   /ws        : JSON 스트림 구독

DB = SQLite(`wearboxing.db`) – 파일이 없으면 앱 기동 시 자동 생성
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Optional
import time, asyncio

# ────────────────────────────────────
# SQLAlchemy ― 한 파일 내 셋업
# ────────────────────────────────────
from sqlalchemy import (
    create_engine, Column, Integer, Float, String
)
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DB_URL = "sqlite:///./wearboxing.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class PacketORM(Base):
    __tablename__ = "packets"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(String,  index=True)
    session_id = Column(String,  index=True)
    label      = Column(String,  index=True)
    ts         = Column(Integer)              # epoch µs
    ax = Column(Float); ay = Column(Float); az = Column(Float)
    gx = Column(Float); gy = Column(Float); gz = Column(Float)
    batt = Column(Integer, nullable=True)
    rssi = Column(Integer, nullable=True)


# 테이블이 없으면 생성 (앱 기동 시 1회)
Base.metadata.create_all(bind=engine)

# ────────────────────────────────────
# Pydantic ― 워치 JSON 스키마
# ────────────────────────────────────
class Packet(BaseModel):
    user_id: str      = Field(..., example="u001")
    session_id: str   = Field(..., example="s001")
    label: str        = Field(..., example="strong_jab")
    ts: int           # epoch µs
    ax: float; ay: float; az: float
    gx: float; gy: float; gz: float
    batt: Optional[int] = None
    rssi: Optional[int] = None


# ────────────────────────────────────
# FastAPI & WebSocket
# ────────────────────────────────────
app = FastAPI()
clients: set[WebSocket] = set()     # 활성 대시보드
latest_packet: dict | None = None   # 마지막 패킷(신규 접속 시 즉시 전송)


@app.get("/time")
async def time_sync():
    """워치용 1-shot 시간 동기화 (µs)."""
    return {"epoch_us": int(time.time() * 1_000_000)}


@app.post("/collect")
async def collect(pkt: Packet):
    """센서 패킷 1개 수신 → DB 저장 + 브로드캐스트."""
    global latest_packet
    latest_packet = pkt.dict()

    # 1) 콘솔 로그
    print(f"▶ {pkt.session_id} | {pkt.label:<12} | "
          f"ax={pkt.ax:6.2f} ay={pkt.ay:6.2f} az={pkt.az:6.2f}")

    # 2) DB INSERT
    with SessionLocal() as db:       # commit & close 자동
        db.add(PacketORM(**latest_packet))
        db.commit()

    # 3) WebSocket push
    for ws in clients.copy():
        try:
            await ws.send_json(latest_packet)
        except WebSocketDisconnect:
            clients.discard(ws)

    return {"ok": True}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """대시보드 실시간 스트림."""
    await ws.accept()
    clients.add(ws)

    # 첫 접속 시 직전에 온 패킷 한번 보여주기
    if latest_packet:
        await ws.send_json(latest_packet)

    try:
        while True:
            await asyncio.sleep(60)   # keep-alive (인바운드 메시지는 무시)
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(ws)
