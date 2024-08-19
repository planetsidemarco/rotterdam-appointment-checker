"""Simple dict file"""

XPATHS = {
    "appointment": {
        "xpath": "//a[@class='styles_button__BEjUn' and @title='Afspraak maken']",
        "action": "button",
        "query": "",
        "screenshot": False,
        "textfile": False,
        "end_condition": False,
    },
    "overseas": {
        "xpath": "//input[@class='form-control' and @id='id6']",
        "action": "textbox",
        "query": "Eerste vestiging buiten Europa",
        "screenshot": False,
        "textfile": False,
        "end_condition": False,
    },
    "subject": {
        "xpath": "//button[@class='btn btn-link btn-block text-left' and @id='id5']",
        "action": "button",
        "query": "",
        "screenshot": False,
        "textfile": False,
        "end_condition": False,
    },
    "rental": {
        "xpath": "//select[@class='form-control' and @aria-required='true' and "
        "@name='matches:form:keuzes:0:button:form:in-focus:hvv:form:huurOfKoop:field']",
        "action": "dropdown",
        "query": "HUUR",
        "screenshot": False,
        "textfile": False,
        "end_condition": False,
    },
    "postcode": {
        "xpath": "//input[@type='text' and @class='form-control' and @maxlength='6' and"
        "@name='matches:form:keuzes:0:button:form:in-focus:hvv:form:postcodeContainer:postcode']",
        "action": "textbox",
        "query": "3039RL",
        "screenshot": False,
        "textfile": False,
        "end_condition": False,
    },
    "postcode_input": {
        "xpath": "//button[@class='btn btn-secondary' and @type='submit' and"
        "@name='matches:form:keuzes:0:button:form:in-focus:hvv:form:afspraak']",
        "action": "button",
        "query": "",
        "screenshot": False,
        "textfile": False,
        "end_condition": False,
    },
    "quantity_input": {
        "xpath": "//button[@class='btn btn-secondary' and @type='submit' and"
        "@value='button' and @name='verder']",
        "action": "button",
        "query": "",
        "screenshot": False,
        "textfile": False,
        "end_condition": False,
    },
    "options": {
        "xpath": "//button[@class='list-group-item list-group-item-action flex-column "
        "align-items-start' and @name='keuzes:0:give-focus']",
        "action": "button",
        "query": "",
        "screenshot": True,
        "textfile": True,
        "end_condition": True,
    },
    "options_input": {
        "xpath": "//button[@class='btn btn-secondary' and @type='submit' and @value='button'"
        "and @name='keuzes:0:in-focus:button']",
        "action": "button",
        "query": "",
        "screenshot": False,
        "textfile": False,
        "end_condition": False,
    },
    "calendar": {
        "xpath": "//span[@class='input-group-text' and @title='Kies datum ...']",
        "action": "button",
        "query": "",
        "screenshot": True,
        "textfile": False,
        "end_condition": False,
    },
}
