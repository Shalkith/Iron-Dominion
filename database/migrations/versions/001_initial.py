"""Initial migration - create all tables

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create players table
    op.create_table(
        'players',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('gold', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('army_size', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_attack_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_index('ix_players_id', 'players', ['id'])
    op.create_index('ix_players_username', 'players', ['username'])

    # Create tiles table
    op.create_table(
        'tiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('x', sa.Integer(), nullable=False),
        sa.Column('y', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('resource_value', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['owner_id'], ['players.id']),
        sa.UniqueConstraint('x', 'y', name='uix_tile_coords')
    )
    op.create_index('ix_tiles_id', 'tiles', ['id'])
    op.create_index('ix_tiles_x', 'tiles', ['x'])
    op.create_index('ix_tiles_y', 'tiles', ['y'])
    op.create_index('ix_tiles_owner_id', 'tiles', ['owner_id'])

    # Create alliances table
    op.create_table(
        'alliances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player1_id', sa.Integer(), nullable=False),
        sa.Column('player2_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['player1_id'], ['players.id']),
        sa.ForeignKeyConstraint(['player2_id'], ['players.id']),
        sa.UniqueConstraint('player1_id', 'player2_id', name='uix_alliance_pair')
    )
    op.create_index('ix_alliances_id', 'alliances', ['id'])
    op.create_index('ix_alliances_player1_id', 'alliances', ['player1_id'])
    op.create_index('ix_alliances_player2_id', 'alliances', ['player2_id'])

    # Create alliance_requests table
    op.create_table(
        'alliance_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('from_player_id', sa.Integer(), nullable=False),
        sa.Column('to_player_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('responded_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['from_player_id'], ['players.id']),
        sa.ForeignKeyConstraint(['to_player_id'], ['players.id'])
    )
    op.create_index('ix_alliance_requests_id', 'alliance_requests', ['id'])
    op.create_index('ix_alliance_requests_from_player_id', 'alliance_requests', ['from_player_id'])
    op.create_index('ix_alliance_requests_to_player_id', 'alliance_requests', ['to_player_id'])

    # Create attack_logs table
    op.create_table(
        'attack_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('attacker_id', sa.Integer(), nullable=False),
        sa.Column('defender_id', sa.Integer(), nullable=False),
        sa.Column('tile_id', sa.Integer(), nullable=False),
        sa.Column('attacker_army', sa.Integer(), nullable=False),
        sa.Column('defender_army', sa.Integer(), nullable=False),
        sa.Column('attacker_won', sa.Boolean(), nullable=False),
        sa.Column('tile_captured', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['attacker_id'], ['players.id']),
        sa.ForeignKeyConstraint(['defender_id'], ['players.id']),
        sa.ForeignKeyConstraint(['tile_id'], ['tiles.id'])
    )
    op.create_index('ix_attack_logs_id', 'attack_logs', ['id'])
    op.create_index('ix_attack_logs_attacker_id', 'attack_logs', ['attacker_id'])
    op.create_index('ix_attack_logs_defender_id', 'attack_logs', ['defender_id'])


def downgrade() -> None:
    op.drop_table('attack_logs')
    op.drop_table('alliance_requests')
    op.drop_table('alliances')
    op.drop_table('tiles')
    op.drop_table('players')
