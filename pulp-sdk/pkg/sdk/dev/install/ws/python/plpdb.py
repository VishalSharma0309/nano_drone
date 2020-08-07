#!/usr/bin/env python3

import os
import sys
from sqlalchemy import Table, Column, ForeignKey, Integer, String, DateTime, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import plpobjects

Base = declarative_base()


class Db_Build(Base):
    __tablename__ = 'builds'
    id = Column(Integer, primary_key=True)
    package = Column(String(50))
    config = Column(String(1024))
    status = Column(String(50))
    version = Column(String(50))
    branch = Column(String(50))
    commit = Column(String(50))
    artifact = Column(String(256))
    deps = Column(String(1024))
    env = Column(String(1024))
    tests = Column(Integer)
    testrun = Column(Integer)
    passed = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    def get(self):
        env_list = []
        if self.env is not None:
            env_list = self.env.split(' ')
        return plpobjects.Package_Build(
            pobj=None, id=self.id,
            package=self.package, status=self.status,
            start_date=self.start_date, end_date=self.end_date,
            version=self.version, artifact=self.artifact,
            deps=self.deps, passed=self.passed, tests=self.tests,
            testrun=self.testrun, config=self.config, branch=self.branch,
            commit_version=self.commit, env=env_list
        )


class Db_Test(Base):
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    config = Column(String(256))
    build = Column(Integer)
    status = Column(String(50))
    time = Column(DateTime)
    metrics = Column(String(256))

    def get(self, pobj):
        return plpobjects.TestRun(
            pobj=pobj, test=None,
            success=self.status == 'success',
            duration=self.time.timestamp(),
            log=None,
            name=self.name,
            metrics=self.metrics,
            config=self.config,
            build=self.build
        )


class BuildsTable(object):

    def __init__(self, session):
        self.session = session

    def delete(self, **kwargs):
        return self.session.query(Db_Build).filter_by(**kwargs).delete()    

    def get(self, **kwargs):
        return self.session.query(Db_Build).filter_by(**kwargs).all()    

    def findOrReg(self, status, package, **kwargs):
        dbBuild = self.get(status=status, package=package, **kwargs)
        if len(dbBuild) != 0: return dbBuild[0]
        else: return self.reg(status=status, package=package, **kwargs)

    def reg(self, status, package, **kwargs):
        newBuild = Build(author=os.environ.get('USER'), date=datetime.datetime.today(), status=status, package=package, **kwargs)
        self.session.add(newBuild)
        self.session.commit()

        return newBuild

    def update(self):
        self.session.commit()

    def dump(self, packages=None, **kwargs):
        builds = self.get(**kwargs)

        x = PrettyTable(['package', 'tag', 'date', 'status'])
        for build in builds:
            if packages != None and not build.package.package in packages: continue
            x.add_row([build.package.package, build.package.tag, build.date, build.status])

        print(x)

class TestsTable(object):

    def __init__(self, session):
        self.session = session

    def get(self, **kwargs):
        return self.session.query(Db_Test).filter_by(**kwargs).all()    




class PulpDb(object):

    def __init__(self, local_file=None):

        local_file = os.environ.get('PULP_DB_FILE')
        db_host = os.environ.get('PULP_DB_MYSQL')
        self.engine = None

        if db_host is not None:
            self.engine = create_engine('mysql://%s' % db_host)

        if local_file is not None:
            self.engine = create_engine('sqlite:///%s' % (local_file))

        if self.engine is not None:

            self.local_file = local_file
            Base.metadata.bind = self.engine
            DBSession = sessionmaker()
            DBSession.bind = self.engine
            self.session = DBSession()

            self.builds_table = BuildsTable(self.session)

            self.tests_table = TestsTable(self.session)

            self.create_tables()

    def get_builds_table(self):
        return self.buildsTable

    def drop_all(self):
        Base.metadata.drop_all(self.engine)

    def get_builds_table(self):
        return self.buildsTable

    def get_tests_table(self):
        return self.testsTable

    def create_tables(self):
        #Base.metadata.drop_all(self.engine)
        if self.engine is not None:
            Base.metadata.create_all(self.engine)

    def reg_build(self, package, config, status, start_date, end_date, version,
                  artifact, deps, passed, tests, testrun, branch, commit, env):
        if self.engine is not None:
            build = Db_Build(package=package, config=config, status=status,
                             start_date=start_date, end_date=end_date,
                             version=version, artifact=artifact, deps=deps,
                            passed=passed, tests=tests, testrun=testrun,
                            branch=branch, commit=commit, env=' '.join(env))
            self.session.add(build)
            self.session.commit()
            return build
        return None

    def reg_run(self, *kargs, **kwargs):
        if self.engine is not None:
            run = Db_Test(*kargs, **kwargs)
            self.session.add(run)
            self.session.commit()

    def get_builds(self):
        if self.engine is None:
            return []
        builds = []
        for db_build in self.builds_table.get():
            builds.append(db_build.get())
        return builds


    def get_tests(self, pobj):
        if self.engine is None:
            return []
        tests = []
        for db_test in self.tests_table.get():
            tests.append(db_test.get(pobj))
        return tests



