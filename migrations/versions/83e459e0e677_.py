"""empty message

Revision ID: 83e459e0e677
Revises: a8c861ea0380
Create Date: 2020-04-26 20:03:53.658275

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83e459e0e677'
down_revision = 'a8c861ea0380'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('thumbnail_file', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'thumbnail_file')
    # ### end Alembic commands ###
