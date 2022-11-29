from pytest_alembic import MigrationContext

from sqlalchemy_declarative_extensions.dialects import get_roles
from sqlalchemy_declarative_extensions.dialects.postgresql import Role


def test_apply_autogenerated_revision(alembic_runner: MigrationContext, alembic_engine):
    result = alembic_runner.generate_revision(
        autogenerate=True, prevent_file_generation=False
    )
    alembic_runner.migrate_up_one()

    result = get_roles(
        alembic_engine, exclude=[alembic_engine.pmr_credentials.username]
    )

    expected_result = [
        Role(
            "admin",
            superuser=True,
            createdb=True,
            createrole=True,
            login=False,
            replication=True,
            bypass_rls=True,
            in_roles=["read", "write"],
        ),
        Role(
            "app",
            login=True,
            in_roles=["read", "write"],
        ),
        Role("read"),
        Role("write"),
    ]
    assert expected_result == result
