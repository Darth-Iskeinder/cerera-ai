from database_connector import get_all_destinations, get_all_origins, get_all_products
import random

def generate_destinations(intent_examples, entities, name):
    generated_texts = {}

    for intent, examples in intent_examples.items():
        for entity in entities:
            if ' ' in entity.value:
                values = entity.value.split(' ')
                entity_value = values[0] + " [" + values[1] + "]{\"entity\":\"" + name + "\"}"
            else:
                entity_value = "[" + entity.value + "]{\"entity\":\"" + name + "\"}"

            example = random.choice(examples)

            generated_text = example.replace("[entity]", entity_value)

            if intent in generated_texts:
                generated_texts[intent].append(generated_text)
            else:
                generated_texts[intent] = [generated_text]

    return generated_texts


def create_file(generated_texts_intents, name):
    filename = f"../data/intents/generated_{name}.yml"
    with open(filename, "w") as file:
        file.write("version: \"3.1\"\n")
        file.write("nlu:\n")
        for intent, generated_texts in generated_texts_intents.items():
            file.write(f"  - intent: {intent}\n")
            file.write("    examples: |\n")
            for text in generated_texts:
                file.write(f"      - {text}\n")


def generate_for_destinations():
    name = 'destination'
    examples = {
        'info': [
            "[entity]"
        ],
        'availability': [
            "есть туры [entity]",
            "самые дорогие туры [entity] какие",
            "какие самые дешевые туры [entity]",
            "какие самые дешевые туры из Бишкека [entity]",
            "какие самые дешевые туры из Оша [entity]",
            "есть  у вас туры [entity]",
            "какие горящие туры у вас есть [entity]",
            "[entity] тоже отправляете?"
        ],
        'price': [
            "цена тура [entity]?",
            "сколько стоит тур [entity]",
            "во сколько обойдется туры [entity]",
            "за сколько можно купить туры с питанием [entity]",
            "можете сказать стоимость туров [entity]",
            "ценники на отдых [entity]",
            "[entity] цена",
            "цена [entity]"
        ]
    }

    entities = get_all_destinations()
    generated_texts = generate_destinations(examples, entities, name)
    create_file(generated_texts, name)
    print("File created successfully!")

def generate_for_origins():
    name = 'origin'
    examples = {
        'info': [
            "[entity]",
        ],
        'availability': [
            "у вас есть билеты [entity]",
            "какие самые дорогие туры [entity] в Турцию какие",
            "напиши дешевые авиабилеты [entity] на Сейшелские острова",
            "есть у вас билеты на самолет [entity] в Европу",
            "горящие туры у вас есть [entity]",
            "[entity] тоже можете отправить?"
        ],
        'price': [
            "цена [entity] в Филиппины?",
            "цена [entity]?",
            "у вас сколько стоит авиабилет [entity] на Бали",
            "во сколько обойдется билет [entity]",
            "за сколько могу купить билеты [entity]",
            "можете сказать стоимость туров с питанием [entity]",
            "ценники на отдых [entity] в",
            "[entity] цена",
            "цена [entity]"
        ]
    }

    entities = get_all_origins()
    generated_texts = generate_destinations(examples, entities, name)
    create_file(generated_texts, name)
    print("File created successfully!")

def generate_for_products():
    name = 'product'
    examples = {
        'info': [
            "[entity]"
        ],
        'availability': [
            "у вас есть [entity]",
            "какие самые дорогие [entity] в Турцию какие",
            "напиши дешевые [entity] на Сейшелские острова",
            "есть у вас [entity] в Европу",
            "горящие [entity] у вас есть",
        ],
        'price': [
            "сколько стоит [entity]",
            "цена [entity] в турцию",
            "[entity] в турцию почем",
            "стоимость [entity] из Бишкека в Гаваи",
            "за сколько могу купить [entity]",
            "цена [entity]"
        ]
    }

    entities = get_all_products()
    generated_texts = generate_destinations(examples, entities, name)
    create_file(generated_texts, name)
    print("File created successfully!")

generate_for_destinations()
generate_for_origins()
generate_for_products()