import pytest
from pytest_alembic import MigrationContext
from pytest_mock_resources import PostgresConfig, create_postgres_fixture
from sqlalchemy import text

alembic_engine = create_postgres_fixture(scope="function", engine_kwargs={"echo": True})


@pytest.fixture(scope="session")
def pmr_postgres_config():
    return PostgresConfig(port=None, ci_port=None)


def test_apply_autogenerated_revision(alembic_runner: MigrationContext, alembic_engine):
    with alembic_engine.connect() as conn:
        with conn.begin() as trans:
            conn.execute(
                text(
                    """
                    CREATE FUNCTION gimme() RETURNS trigger LANGUAGE plpgsql AS $$
                    BEGIN
                    INSERT INTO foo (id) select NEW.id + 1;
                    RETURN NULL;
                    END
                    $$;
                    """
                )
            )
            trans.commit()

    alembic_runner.migrate_up_one()
    result = alembic_runner.generate_revision(
        autogenerate=True, prevent_file_generation=False
    )
    alembic_runner.migrate_up_one()

    with alembic_engine.connect() as conn:
        conn.execute(text("insert into foo (id) values (1)"))
        result = conn.execute(text("select id from foo")).scalars().all()

    assert result == [1, 2]
