# coding:utf-8
import re
import time
import requests
from lxml import etree
# 使用sqlachemy操作数据表
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Tag, Type, Course, Lessions

# 数据库连接信息
db_host = '*****'
db_user = 'root'
db_pawd = 'roottoor'
db_name = 'maizi'
db_port = 3306



# 获取HTML代码
def get_response(url):
    while True:
        try:
            response = requests.get(url)
            return response
        except Exception as e:
            print("Connect Error :{}".format(e))
            time.sleep(2)


# 获取分类
def get_tag_list(url):
    tags = []
    response = get_response(url)
    tree = etree.HTML(response.text)
    li_list = tree.xpath('/html/body/div[3]/div/div[2]/ul/li')
    for li in li_list[1:]:
        tag = "".join(li.xpath('a/text()'))
        tag_link = "http://www.maiziedu.com" + "".join(li.xpath('a/@href'))
        details = li.xpath('div/a')
        for detail in details:
            name = "".join(detail.xpath('text()'))
            link = "http://www.maiziedu.com" + "".join(detail.xpath('@href'))
            tags.append([tag, tag_link, name, link])
    return tags


# 获取该分类下的课程列表
def get_course_list(url):
    course_s = []
    response = get_response(url)
    tree = etree.HTML(response.text)
    course_list = tree.xpath('/html/body/div[3]/div/div[3]/ul/li')
    for course in course_list:
        course_name = "".join(course.xpath('a/div/p[1]/text()'))
        course_image = "http://www.maiziedu.com/" + "".join(course.xpath('a/p[1]/img/@src'))
        course_info = "".join(course.xpath('a/div/p[2]/text()'))
        course_num = "".join(course.xpath('a/div/p[3]/text()'))
        course_link = "http://www.maiziedu.com/" + "".join(course.xpath('a/@href'))
        vip_type = "".join(course.xpath('a/p[1]/i[1]/@class'))
        if "vip_user" in vip_type.lower():
            vip_type = True
        else:
            vip_type = False
        status_type = "".join(course.xpath('a/p[1]/i[2]/@class'))
        if "status_end" in status_type.lower():
            status_type = True
        else:
            status_type = False
        course_s.append([course_name, course_image, course_info, course_num, course_link, vip_type, status_type])
    return course_s


# 获取课程详情以及播放信息
def get_course_detail(url):
    response = get_response(url)
    tree = etree.HTML(response.text)
    chapter_num = tree.xpath('/html/body/div[4]/div[2]/p[3]/span[1]/text()')
    play_num = tree.xpath('/html/body/div[4]/div[2]/p[3]/span[2]/text()')
    lession_list = tree.xpath('/html/body/div[5]/div[1]/div/div[1]/ul/li')
    details = []
    for num, lession in enumerate(lession_list):
        name = "".join(lession.xpath('a/span[1]/text()'))
        long = "".join(lession.xpath('a/span[2]/text()'))
        chapter_link = "http://www.maiziedu.com" + "".join(lession.xpath('a/@href'))
        play_page = get_response(chapter_link)
        com = re.compile(r'lessonUrl = "(http://newoss\.maiziedu\.com.*?)"')
        play_link = "".join(re.findall(com, play_page.text))
        details.append([chapter_link, name, long, play_link])
    return chapter_num, play_num, details


if __name__ == "__main__":
    start_url = "http://www.maiziedu.com/course/all-all/0-2/"

    # 初始化数据库连接,:
    engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'
                           .format(db_user, db_pawd, db_host, db_port, db_name), max_overflow=500)
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    tag_list = get_tag_list(start_url)
    a = ""
    for tags in tag_list:
        tag = tags[0]  # 主分类
        tag_link = tags[1]
        name = tags[2]  # 二级分类名
        link = tags[3]  # 二级分类链接
        if a != tag:
            info = Tag(
                name=tag,
                link=tag_link
            )
            try:
                session.add(info)
                session.commit()
            except Exception as e:
                session.rollback()
                print("Error:{}".format(e))
            a = tag

        info = Type(
            name=name,
            link=link,
            tag=tag
        )
        try:
            session.add(info)
            session.commit()
        except Exception as e:
            session.rollback()
            print("Error:{}".format(e))

        print(tag, tag_link, name, link)

        course_list = get_course_list(link)
        for course in course_list:
            course_name = course[0]
            course_image = course[1]
            course_info = course[2]
            course_num = course[3]
            course_link = course[4]
            if course[5] == True:
                vip_type = 1
            else:
                vip_type = 0
            if course[6] == True:
                status_type = 1
            else:
                status_type = 0
            chapter_num, play_num, details = get_course_detail(course_link)

            info = Course(
                name=course_name,
                types=name,
                image=course_image,
                info=course_info,
                num=course_num,
                vip=vip_type,
                status=status_type,
                link=course_link,
                chapter_num=chapter_num,
                play_num=play_num
            )
            try:
                session.add(info)
                session.commit()
            except Exception as e:
                session.rollback()
                print("Error:{}".format(e))
            for lession in details:
                info = Lessions(
                    course_name=course_name,
                    name=lession[1],
                    long=lession[2],
                    chapter_link=lession[0],
                    play_link=lession[3],
                )
                try:
                    session.add(info)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    print("Error:{}".format(e))
            print(chapter_num, play_num, details)
