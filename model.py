from sqlalchemy import Column, String, create_engine, Integer, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()


# 大分类标签
class Tag(Base):
    # 表名
    __tablename__ = 'tag'
    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String(1024), unique=True)
    link = Column(String(1024))
    tag = relationship('Type')


class Type(Base):
    # 表名
    __tablename__ = 'type'
    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String(1024), unique=True)
    link = Column(String(1024))
    tag = Column(String(1024), ForeignKey('tag.name'))
    course = relationship('Course')


class Course(Base):
    # 表名
    __tablename__ = 'course'
    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String(1024), unique=True)
    types = Column(String(1024), ForeignKey('type.name'))
    image = Column(String(1024))  # 封面图
    info = Column(Text)  # 简介
    num = Column(String(1024))  # 学习人数
    vip = Column(Integer)  # 是否VIP课程 1=是 0=不是
    status = Column(Integer)  # 是否更新完 1=是 0 = 不是
    link = Column(String(1024))  # 课程详情链接
    chapter_num = Column(String(64))  # 章节数量
    play_num = Column(String(64))  # 播放次数
    lession = relationship('Lessions')


class Lessions(Base):
    # 表名
    __tablename__ = 'lessions'
    id = Column(Integer, unique=True, primary_key=True)
    course_name = Column(String(1024), ForeignKey('course.name'))
    name = Column(String(1024))  # 章节名称
    long = Column(String(1024))  # 章节时长
    chapter_link = Column(String(256))  # 章节链接
    play_link = Column(String(256))  # 播放连接


# 数据库连接信息
db_host = '*********'
db_user = 'root'
db_pawd = 'roottoor'
db_name = 'maizi'
db_port = 3306

if __name__ == "__main__":
    engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'
                           .format(db_user, db_pawd, db_host, db_port, db_name), max_overflow=500)
    Base.metadata.create_all(engine)
