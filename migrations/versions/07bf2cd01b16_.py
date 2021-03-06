"""empty message

Revision ID: 07bf2cd01b16
Revises: 
Create Date: 2020-04-26 00:35:57.269886

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "07bf2cd01b16"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "scenes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_index("ix_test_timestamp", table_name="test")
    op.drop_table("test")
    op.drop_table("follow")
    op.create_foreign_key(None, "posts", "scenes", ["scene"], ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "posts", type_="foreignkey")
    op.create_table(
        "follow",
        sa.Column("follower_id", sa.INTEGER(), nullable=False),
        sa.Column("followed_id", sa.INTEGER(), nullable=False),
        sa.Column("timestamp", sa.DATETIME(), nullable=True),
        sa.ForeignKeyConstraint(["followed_id"], ["users.id"],),
        sa.ForeignKeyConstraint(["follower_id"], ["users.id"],),
        sa.PrimaryKeyConstraint("follower_id", "followed_id"),
    )
    op.create_table(
        "test",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("title", sa.VARCHAR(length=128), nullable=True),
        sa.Column("body", sa.TEXT(), nullable=True),
        sa.Column("timestamp", sa.DATETIME(), nullable=True),
        sa.Column("author_id", sa.INTEGER(), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_test_timestamp", "test", ["timestamp"], unique=False)
    op.drop_table("scenes")
    # ### end Alembic commands ###
