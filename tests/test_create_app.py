import subprocess
import sys
import textwrap


def test_create_app_creates_every_table(tmp_path):
    # run in a fresh interpreter: the test fixtures import every model and call
    # create_all themselves, which would hide tables create_app fails to make
    script = textwrap.dedent(f"""
        from statsapp import datastore_config
        datastore_config.DB_CONFIG['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{tmp_path}/fresh.db'
        import sqlalchemy
        import statsapp
        app = statsapp.create_app({{'DEFAULT_USER_EMAIL': 'x'}})
        with app.app_context():
            print(','.join(sorted(sqlalchemy.inspect(statsapp.db.engine).get_table_names())))
    """)
    result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, check=True)

    tables = set(result.stdout.strip().split(','))
    assert {'user', 'strava_activity', 'withings_data', 'google_fit_data', 'google_fit_yoga'} <= tables
