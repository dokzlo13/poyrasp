from jinja2 import Template
from emoji import emojize

def emoj(string: str) -> str:
    return emojize(string, use_aliases=True)

kind_mapper = {'Бакалавриат': 0, 'Магистратура': 1, 'Специалитет': 2}
type_mapper = {'Очная': 'common', 'Заочная': 'distance', 'Очно-Заочная': 'evening'}
level_mapper = {'1 Курс': 1, '2 Курс': 2, '3 Курс': 3, '4 Курс': 4, '5 Курс': 5, '6 Курс': 6}
group_checkout_mapper = {emoj(':white_check_mark: Сохранить группу'): 1}
main_menu = {'nearset': emoj(':mega: Ближайшие пары'),
             'plan': emoj(':notebook_with_decorative_cover: Расписание'),
             'settings': emoj(':wrench: Настройки'),
             'subs': emoj(':books: Мои группы'),
             'renew': emoj(':arrows_counterclockwise: Обновить расписания'),
             'add': emoj(':pencil: Добавить группу'),
             'week': emoj(':calendar: Неделя')}

search_menu = {'teacher': emoj(':ok_woman: Поиск по преподавателю'),
               'calendar': emoj(':calendar: Календарь')}


main_menu_button = emoj(':house: Главное меню')
back_button = emoj(':arrow_backward: Назад')
group_setting_button = emoj(':wrench: Настроить группы')


class Messages:
    no_schedule_on_date = "Извините, расписаний для этого дня не найдено!"
    select_date = "Пожалуста, выберите день:"
    no_schedule =  "Извините, активных расписаний для Вас не найдено!\n Попробуйте добавить группу /add"
    faculties_unaviable = "Извините, на данный момент нет информации о расписаниях, попробуйте позже!"
    schedule_will_be_updated = '*Информация о вашем расписании будет обновлена!*'
    welcome = "Добро пожаловать!"
    what_to_do = "*Что необходимо сделать?*"
    hello = "Привет! Проверь список своих подписок. Для изменения настроек используй /subs"
    settings = "Настройки групп"
    please_select_group = "Пожалуйста, выберите группу"

    @staticmethod
    def schedule_for(date):
        return "*Расписание на {0}:*".format(date.strftime("%Y-%m-%d"))

class ParseMode(object):
    """This object represents a Telegram Message Parse Modes."""

    MARKDOWN = 'Markdown'
    """:obj:`str`: 'Markdown'"""
    HTML = 'HTML'
    """:obj:`str`: 'HTML'"""


def get_teacher_short(teacher_data):
    if teacher_data:
        return "{first_name} {middle_name[0]}. {last_name[0]}.".format(**teacher_data)
    else:
        return ''

def lessons_template(data, markup=True):
    text = ""

    text += "{% if data[0] %}{% if data[0]['groups'] %}\n:two_men_holding_hands: {% endif %}"
    text += "{% for group in data[0]['groups']%}"
    text += "{% if group['name'] %}"
    text += "*{{ group['name'] }}*, " if markup else "{{ group['name'] }}, "
    text += "{% endif %}"
    text += "{% endfor %}"
    text += "{% endif %}"
    text += "\n:calendar: {{  data[0]['time_start'].strftime('%A, %d %B') }} \n"

    text += "{% for lesson in data %}"
    text += "{% if lesson['additional_info'] %}\n:information_source: {{lesson['additional_info']}}{% endif %}"
    text += "\n:pencil: *{{ lesson['subject']}}*" if markup else "\n:pencil: {{ lesson['subject']}}"
    text += "\n:mag_right: _{{ lesson['typeObj']['name'] }}_ " if markup else "\n:mag_right: {{ lesson['typeObj']['name'] }} "
    text+= ":clock10: {{ lesson['time_start'].strftime('%H:%M') }}-{{lesson['time_end'].strftime('%H:%M')}}"
    text += "\n:school: {{ lesson['auditories'][0]['building']['abbr'] }}, {{ lesson['auditories'][0]['name'] }}"
    text+= "{% if lesson['teachers'] %}({{ short_fio(lesson['teachers'][0]) }}){% endif %}"
    # text +=  "{{ day['addr'] }}, {{ day['room'] }} ({{ day['teacher'] }})\n\n"
    text += "\n{% endfor %}"
    t = Template(text)
    t.globals['short_fio'] = get_teacher_short
    message = emoj(t.render(data=data))
    return message

def short_group(sub):
    data = sub.copy()
    km = dict((v, k) for k, v in kind_mapper.items())
    tm = dict((v, k) for k, v in type_mapper.items())
    data['type'] = tm.get(data['type'])
    data['kind'] = km.get(data['kind'])
    text = ""
    text += "{% if data['kind'] %}:mortar_board: {{ data['kind'] }} {% endif %}"
    text += "{% if data['type'] %}:pencil2:{{ data['type'] }} {% endif %}"
    text += ":books: {{ data['level']}} "
    text += ":school_satchel: {{ data['name'] }}"

    t = Template(text)
    message = emojize(t.render(data=data), use_aliases=True)
    return message




def selected_group_message(data, facult=None, use_intro=True):
    data = data.copy()
    if facult:
        facult = facult.copy()

    km = dict((v, k) for k, v in kind_mapper.items())
    tm = dict((v, k) for k, v in type_mapper.items())

    data['type'] = tm.get(data['type'])
    data['kind'] = km.get(data['kind'])

    if use_intro:
        text = "*Вы выбрали* :mag:\n"
    else:
        text = '\n'

    text += "{% if facult['name'] %}:school: *Институт :*{{facult['name']}} ({{ facult['abbr']}})\n{% endif %}"
    text += "{% if data['spec'] %}:telescope: *Специальность :*\n{{ data['spec'] }}\n{% endif %}"
    text += "{% if data['kind'] %}:mortar_board: *Квалификация :* {{ data['kind'] }}\n{% endif %}"
    text += "{% if data['type'] %}:pencil2: *Форма обучения :* {{ data['type'] }}\n{% endif %}"
    text += ":books: *Курс:* {{ data['level']}}\n"
    text += ":school_satchel: *Группа:* {{ data['name'] }}"

    t = Template(text)

    message = emojize(t.render(data=data, facult=facult), use_aliases=True)
    return message

