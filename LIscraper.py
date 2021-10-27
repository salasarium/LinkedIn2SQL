import linkedin_scrapper
import time
from linkedin_scrapper import Person, Account
import sqlite3


with open('links.txt', 'r') as f:
    profiles = f.read().splitlines()
print('Будут обработаны профили: ', profiles)

#парсим имя
def get_name():
    full_names = driver.find_elements_by_xpath('//li[@class="inline t-24 t-black t-normal break-words"]')
    time.sleep(1)
    names = []
    for i in full_names:
        names.append(i.text)
    return names

#парсим статус
def get_status():
    statuses = driver.find_elements_by_xpath('//h2[@class="mt1 t-18 t-black t-normal break-words"]')
    time.sleep(1)
    status = []
    for i in statuses:
        status.append(i.text)
    return status

#парсим образование
def get_education():
    #собираем названия ВУЗов
    educations = driver.find_elements_by_xpath('//h3[@class="pv-entity__school-name t-16 t-black t-bold"]')
    #собираем годы обучения
    edu_dates = driver.find_elements_by_xpath('//p[@class="pv-entity__dates t-14 t-black--light t-normal"]')
    time.sleep(1)
    list_of_education = []
    index = 1
    for educations, edu_dates in zip(educations, edu_dates):
        globals()["training" + str(index)]={}
        globals()["training" + str(index)]["School Name"] = educations.text
        globals()["training" + str(index)]["Duration"] = edu_dates.text.split("\n")[1]
        list_of_education.append(globals()["training" + str(index)])
        index += 1
    return list_of_education

#парсим карьеру
def get_career():
    # get all job_titles datas
    job_titles = driver.find_elements_by_xpath('//h3[@class="t-16 t-black t-bold"]')
    # get all company_names
    company_names = driver.find_elements_by_xpath('//p[@class="pv-entity__secondary-title t-14 t-black t-normal"]')
    # get all employements dates
    employements_dates = driver.find_elements_by_class_name('pv-entity__date-range')
    # get all duration of employements
    duration_of_employements = driver.find_elements_by_class_name('pv-entity__bullet-item-v2')
    # get all locations
    #locations = driver.find_elements_by_class_name('pv-entity__location')
    list_of_experiences = []
    index = 1
    # browse all company name and job titles in same times
    for job_title, company_name, employement_date, duration_of_employement in zip(job_titles, company_names, employements_dates, duration_of_employements):
        globals()["experiences" + str(index)] = {}
        globals()["experiences" + str(index)]["Job title"] = job_title.text
        globals()["experiences" + str(index)]["Company"] = company_name.text
        globals()["experiences" + str(index)]["Employement date"] = employement_date.text.split("\n")[1]
        globals()["experiences" + str(index)]["Duration of employement"] = duration_of_employement.text
        list_of_experiences.append(globals()["experiences" + str(index)])
        index += 1
    return list_of_experiences

#логинимся
for profile in profiles:
    myAccount = Account("YOUR_LOGIN", "YOUR_PASSWORD", "chrome")  # change login & pass
    driver = myAccount.login()
    person = Person(driver)
    person.search_by_account_link(profile)
    name = get_name()
    print("Name: ", name)

    status = get_status()
    print("Status: ", status)

    career = get_career()
    print("Career: ", career)

    education = get_education()
    print("Education: ", education)

    skills = person.get_skills()
    print("skills: ", skills)

    #закрываем окно браузера
    driver.quit()

    # начинаем работать с БД
    # подключение к базе данных
    connection = sqlite3.connect('Linkedin.db')
    # создаем курсор
    crsr = connection.cursor()

    # команда SQL для создания таблицы в базе данных (выполняется один раз)
    sql_command = '''CREATE TABLE IF NOT EXISTS Linkedin_table (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    profile VARCHAR,
    status VARCHAR,
    career VARCHAR,
    education VARCHAR,
    skills VARCHAR);'''
    crsr.execute(sql_command)

    #переводим кортежи в строки
    name1 = ', '.join(map(str, name))
    status1 = ', '.join(map(str, status))
    career1 = ', '.join(map(str, career))
    education1 = ', '.join(map(str, education))
    skills1 = ', '.join(map(str, skills))

    #Определяем количество строк в таблице
    id_count = crsr.execute("select * from Linkedin_table")
    id_count = len(crsr.fetchall())
    print('Сохраняем в базу. Количество строк: ', id_count)

    # команда SQL для вставки данных в таблицу
    sql_command = '''INSERT INTO Linkedin_table VALUES (:id, :name1, :profile, :status1, :career1, :education1, :skills1);'''
    crsr.execute(sql_command, {'id':id_count+1, 'name1': name1, 'profile': profile, 'status1': status1, 'career1': career1, 'education1': education1, 'skills1':skills1})

    # Сохранить изменения
    connection.commit()
    # закрыть соединение
    connection.close()
