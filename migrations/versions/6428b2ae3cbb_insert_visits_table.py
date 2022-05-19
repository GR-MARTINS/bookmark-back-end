"""insert visits table

Revision ID: 6428b2ae3cbb
Revises: a76dd2820a15
Create Date: 2022-05-17 14:54:53.139165

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6428b2ae3cbb'
down_revision = 'a76dd2820a15'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('visits',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bookmark_id', sa.Integer(), nullable=True),
    sa.Column('visiting_hours', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['bookmark_id'], ['bookmarks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('visits')
    # ### end Alembic commands ###