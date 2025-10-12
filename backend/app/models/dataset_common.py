"""Common dataset models."""
from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class DatasetTides(Base, TimestampMixin):
    """Tides and water levels dataset."""

    __tablename__ = "datasets_tides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    station_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    water_level_m: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        Index("idx_tides_station_time", "station_id", "time"),
    )


class DatasetSST(Base, TimestampMixin):
    """Sea surface temperature dataset."""

    __tablename__ = "datasets_sst"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    lon: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    sst_c: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        Index("idx_sst_lat_lon_time", "lat", "lon", "time"),
    )


class DatasetCurrents(Base, TimestampMixin):
    """Ocean currents dataset."""

    __tablename__ = "datasets_currents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    lon: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    u: Mapped[float] = mapped_column(Float, nullable=False)  # eastward velocity
    v: Mapped[float] = mapped_column(Float, nullable=False)  # northward velocity

    __table_args__ = (
        Index("idx_currents_lat_lon_time", "lat", "lon", "time"),
    )


class DatasetTurbidity(Base, TimestampMixin):
    """Water turbidity dataset."""

    __tablename__ = "datasets_turbidity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    lon: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ntu: Mapped[float] = mapped_column(Float, nullable=False)  # Nephelometric Turbidity Units

    __table_args__ = (
        Index("idx_turbidity_lat_lon_time", "lat", "lon", "time"),
    )


class DatasetBathyTiles(Base, TimestampMixin):
    """Bathymetry tiles dataset."""

    __tablename__ = "datasets_bathy_tiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tile_z: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    tile_x: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    tile_y: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    blob: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    __table_args__ = (
        Index("idx_bathy_tiles_zxy", "tile_z", "tile_x", "tile_y", unique=True),
    )

