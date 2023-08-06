"""add: columns(created_at, edited) in comments table

Revision ID: 4895101e7d57
Revises: 0d4f8619c270
Create Date: 2023-08-06 14:51:36.090901

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4895101e7d57'
down_revision = '0d4f8619c270'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_comments_id', table_name='comments')
    op.drop_table('comments')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comments',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('content', sa.VARCHAR(), nullable=True),
    sa.Column('owner_id', sa.INTEGER(), nullable=True),
    sa.Column('ad_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['ad_id'], ['advertisements.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_comments_id', 'comments', ['id'], unique=False)
    # ### end Alembic commands ###
