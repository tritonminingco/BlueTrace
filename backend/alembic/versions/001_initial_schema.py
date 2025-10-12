"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # API Keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('key_hash', sa.Text(), nullable=False),
        sa.Column('prefix', sa.String(length=20), nullable=False),
        sa.Column('owner_email', sa.String(length=255), nullable=False),
        sa.Column('plan', sa.String(length=50), nullable=False),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash')
    )
    op.create_index('idx_api_keys_owner_plan', 'api_keys', ['owner_email', 'plan'])
    op.create_index('idx_api_keys_prefix_revoked', 'api_keys', ['prefix', 'revoked_at'])
    op.create_index(op.f('ix_api_keys_owner_email'), 'api_keys', ['owner_email'])
    op.create_index(op.f('ix_api_keys_plan'), 'api_keys', ['plan'])
    op.create_index(op.f('ix_api_keys_prefix'), 'api_keys', ['prefix'])

    # Usage Events table
    op.create_table(
        'usage_events',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('api_key_id', sa.Integer(), nullable=False),
        sa.Column('route', sa.String(length=255), nullable=False),
        sa.Column('bytes_sent', sa.Integer(), nullable=False),
        sa.Column('bytes_received', sa.Integer(), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['api_key_id'], ['api_keys.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_usage_events_api_key_created', 'usage_events', ['api_key_id', 'created_at'])
    op.create_index('idx_usage_events_route_created', 'usage_events', ['route', 'created_at'])
    op.create_index(op.f('ix_usage_events_api_key_id'), 'usage_events', ['api_key_id'])
    op.create_index(op.f('ix_usage_events_route'), 'usage_events', ['route'])

    # Datasets - Tides
    op.create_table(
        'datasets_tides',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('station_id', sa.String(length=50), nullable=False),
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('water_level_m', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tides_station_time', 'datasets_tides', ['station_id', 'time'])
    op.create_index(op.f('ix_datasets_tides_station_id'), 'datasets_tides', ['station_id'])
    op.create_index(op.f('ix_datasets_tides_time'), 'datasets_tides', ['time'])

    # Datasets - SST
    op.create_table(
        'datasets_sst',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lon', sa.Float(), nullable=False),
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sst_c', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sst_lat_lon_time', 'datasets_sst', ['lat', 'lon', 'time'])
    op.create_index(op.f('ix_datasets_sst_lat'), 'datasets_sst', ['lat'])
    op.create_index(op.f('ix_datasets_sst_lon'), 'datasets_sst', ['lon'])
    op.create_index(op.f('ix_datasets_sst_time'), 'datasets_sst', ['time'])

    # Datasets - Currents
    op.create_table(
        'datasets_currents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lon', sa.Float(), nullable=False),
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('u', sa.Float(), nullable=False),
        sa.Column('v', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_currents_lat_lon_time', 'datasets_currents', ['lat', 'lon', 'time'])
    op.create_index(op.f('ix_datasets_currents_lat'), 'datasets_currents', ['lat'])
    op.create_index(op.f('ix_datasets_currents_lon'), 'datasets_currents', ['lon'])
    op.create_index(op.f('ix_datasets_currents_time'), 'datasets_currents', ['time'])

    # Datasets - Turbidity
    op.create_table(
        'datasets_turbidity',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lon', sa.Float(), nullable=False),
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ntu', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_turbidity_lat_lon_time', 'datasets_turbidity', ['lat', 'lon', 'time'])
    op.create_index(op.f('ix_datasets_turbidity_lat'), 'datasets_turbidity', ['lat'])
    op.create_index(op.f('ix_datasets_turbidity_lon'), 'datasets_turbidity', ['lon'])
    op.create_index(op.f('ix_datasets_turbidity_time'), 'datasets_turbidity', ['time'])

    # Datasets - Bathymetry Tiles
    op.create_table(
        'datasets_bathy_tiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('tile_z', sa.Integer(), nullable=False),
        sa.Column('tile_x', sa.Integer(), nullable=False),
        sa.Column('tile_y', sa.Integer(), nullable=False),
        sa.Column('blob', sa.LargeBinary(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_bathy_tiles_zxy', 'datasets_bathy_tiles', ['tile_z', 'tile_x', 'tile_y'], unique=True)
    op.create_index(op.f('ix_datasets_bathy_tiles_tile_x'), 'datasets_bathy_tiles', ['tile_x'])
    op.create_index(op.f('ix_datasets_bathy_tiles_tile_y'), 'datasets_bathy_tiles', ['tile_y'])
    op.create_index(op.f('ix_datasets_bathy_tiles_tile_z'), 'datasets_bathy_tiles', ['tile_z'])


def downgrade() -> None:
    op.drop_table('datasets_bathy_tiles')
    op.drop_table('datasets_turbidity')
    op.drop_table('datasets_currents')
    op.drop_table('datasets_sst')
    op.drop_table('datasets_tides')
    op.drop_table('usage_events')
    op.drop_table('api_keys')

