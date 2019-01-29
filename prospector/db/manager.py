import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.orm import scoping
from prospector.db import models


class DBManager(object):
    """
    DB Connection Class
    :return db connection/session
    """

    def __init__(self, connection=None):
        self.connection = connection
        self.engine = sqlalchemy.create_engine(
            self.connection,
            pool_pre_ping=True
        )
        self.DBSession = scoping.scoped_session(
            orm.sessionmaker(
                bind=self.engine,
                autocommit=True,
                autoflush=True
            )
        )

    @property
    def session(self):
        return self.DBSession()

    def setup(self):
        """
        Database setup code here
        :return:
        """

        try:
            models.SAModel.metadata.create_all(self.engine)
        except Exception as e:
            print('Unable to connect to database: {}'.format(str(e)))
