# db_session.global_init("db/mars.db")
# db_sess = db_session.create_session()
# user = User()
# user.surname = "Scott"
# user.name = "Ridley"
# user.age = 21
# user.position = "captain"
# user.speciality = "research engineer"
# user.address = "module_1"
# user.email = "scott_chief@mars.org"
# db_sess.add(user)
#
# user = User()
# user.surname = "Pupkin"
# user.name = "Vasiliy"
# user.age = 26
# user.position = "ship worker"
# user.speciality = "windows cleaner"
# user.address = "module_3"
# user.email = "Vasek_Pupkin@mars.org"
# db_sess.add(user)
#
# user = User()
# user.surname = "Salieri"
# user.name = "Ennio"
# user.age = 57
# user.position = "mafia leader"
# user.speciality = "don"
# user.address = "module_2"
# user.email = "Mr_Salieri@mars.org"
# db_sess.add(user)
#
# user = User()
# user.surname = "Johnson"
# user.name = "Carl"
# user.age = 32
# user.position = "ex-captain"
# user.speciality = "Mars explorer"
# user.address = "module_4"
# user.email = "Carl_Johnson@mars.org"
# db_sess.add(user)
# db_sess.commit()

# jobs = Jobs(team_leader=1, job="deployment of residential modules 1 and 2", work_size=15, collaborators="2, 3",
#             start_date=datetime.datetime.now(), is_finished=False)
# db_sess = db_session.create_session()
# db_sess.add(jobs)
# db_sess.commit()

# user = db_sess.query(User).first()
# print(user)
# for user in db_sess.query(User).all():
#     print(user)
# for user in db_sess.query(User).filter(User.id > 1, User.email.notilike("%1%")):
#     print(user)
# db_sess.query(User).filter(User.id >= 2).delete()
# db_sess.commit()
