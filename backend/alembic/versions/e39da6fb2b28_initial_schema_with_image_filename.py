"""initial schema with image_filename

Revision ID: e39da6fb2b28
Revises: 
Create Date: 2025-10-18 01:25:56.267208

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e39da6fb2b28'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Crear tabla base: users
    op.create_table('users',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('username', sa.VARCHAR(length=50), nullable=False),
        sa.Column('email', sa.VARCHAR(length=100), nullable=False),
        sa.Column('password', sa.VARCHAR(length=255), nullable=False),
        sa.Column('role', sa.VARCHAR(length=20), server_default=sa.text("'user'::character varying"), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('users_pkey'))
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Crear tabla base: products
    op.create_table('products',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.VARCHAR(length=100), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('price', sa.INTEGER(), nullable=False),
        sa.Column('image_filename', sa.VARCHAR(), nullable=True),  # ← corregido aquí
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('products_pkey'))
    )
    op.create_index(op.f('ix_products_name'), 'products', ['name'], unique=True)
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)

    # Crear tabla base: carts
    op.create_table('carts',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.INTEGER(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('carts_user_id_fkey'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('carts_pkey'))
    )
    op.create_index(op.f('ix_carts_id'), 'carts', ['id'], unique=False)

    # Crear tabla dependiente: payments
    op.create_table('payments',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.INTEGER(), nullable=False),
        sa.Column('amount', sa.INTEGER(), nullable=False),
        sa.Column('status', sa.VARCHAR(length=20), server_default=sa.text("'pending'::character varying"), nullable=False),
        sa.Column('stripe_session_id', sa.VARCHAR(length=255), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('payments_user_id_fkey'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('payments_pkey'))
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)

    # Crear tabla dependiente: cart_items
    op.create_table('cart_items',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('cart_id', sa.INTEGER(), nullable=False),
        sa.Column('product_id', sa.INTEGER(), nullable=False),
        sa.Column('quantity', sa.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(['cart_id'], ['carts.id'], name=op.f('cart_items_cart_id_fkey'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], name=op.f('cart_items_product_id_fkey'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('cart_items_pkey'))
    )
    op.create_index(op.f('ix_cart_items_id'), 'cart_items', ['id'], unique=False)
