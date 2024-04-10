from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction, SlotSet
import sys
import os
from openai import OpenAI

current_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_directory)

from crmdb_connector import get_filtered_products

client = OpenAI(
    api_key='',
)
class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Возвращаемое действие action_for_price_availability
        return [FollowupAction("action_for_price_availability")]

class ForPriceAvailability(Action):
    def name(self) -> Text:
        return "action_for_price_availability"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        origin = tracker.get_slot("origin")
        destination = tracker.get_slot("destination")
        time = tracker.get_slot("time")
        product = tracker.get_slot("product")
        tag = tracker.get_slot("tag")

        prompt = ("Ты ассистент туристической фирмы Церера. У фирмы есть туры, авиабилеты, а также"
                  " предоставляют услуги по получению визы."
                  " Твоя задача ответить на вопрос и разузнать страну назначения, желаемую дату, бюджет и в конце страну вылета."
                  " Когда клиент ответит на вопросы, надо написать что скоро с ним свяжется наш менеджер."
                  " Отвечай на русском. Не выдумывай данные, если не знаешь"
                  " Если клиент задает вопрос вне твоей компетенции, надо сказать об этом."
                  " В ходе разговора ранее, от клиента выяснили следующую информацию:")

        missing_slots = []
        if not origin:
            missing_slots.append("origin")
        else:
            prompt += f"\nгород вылета: {origin}"
        if not destination:
            missing_slots.append("destination")
        else:
            prompt += f"\nстрана назначения: {destination}"
        if not time:
            missing_slots.append("time")
        else:
            time_text = '\t'.join(time) + '\n'
            prompt += f"\nдата: {time_text}"
        if not tag:
            missing_slots.append("tag")
        else:
            tag_text = '\t'.join(tag) + '\n'
            prompt += f"\nусловия или вид: {tag_text}"

        intent = tracker.latest_message['intent'].get('name')
        user_message = tracker.latest_message['text']
        user_messages = tracker.get_slot("user_messages") or []
        user_messages.append({
            "role": "user",
            "content": user_message,
        })

        if len(user_messages) > 4:
            user_messages = user_messages[-4:]

        if destination:
            products = self.get_products_from_database(destination)
            products_text = self.product_to_text(products=products)
            prompt += f"\nУ нас в базе есть продукты: \n {products_text}"
            prompt += f"\nЕсли пользователь выбрал товар, в конце сообщения верни id в формате [id]."

        text = self.get_text_from_gpt(prompt, user_messages)
        user_messages.append({
            "role": "assistant",
            "content": text,
        })

        if product:
            dispatcher.utter_message(text=text)
        else:
            dispatcher.utter_message(
                text="У нас есть несколько типов продуктов. Какой именно вас интересует: авиабилеты, туры или визы?")

        return [SlotSet("user_messages", user_messages)]

    def get_products_from_database(self, destination):
        filtered_products = get_filtered_products(country=destination)

        return filtered_products

    def product_to_text(self, products):
        products_data = [(product.id, product.tour_name, product.price, product.description, product.duration, product.start_date,
                          product.end_date, product.tour_type, product.country, product.departure_city,
                          product.arrival_city) for
                         product in products]

        header_row = "\t".join([
            "ID", "Название тура", "Цена", "Описание", "Продолжительность",
            "Дата начала", "Дата окончания", "Тип тура", "Страна",
            "Город отправления", "Город прибытия"
        ])
        products_data = [
            "\t".join(map(str, row)) for row in products_data
        ]

        # Объединение строк таблицы в единый текст
        data_text = "\n".join([header_row] + products_data)
        print(data_text)

        return data_text

    def get_text_from_gpt(self, prompt, user_messages):

        all_messages = []
        all_messages.append({
            "role": "system",
            "content": prompt
        })

        for message in user_messages:
            all_messages.append(message)

        print(all_messages)
        chat_completion = client.chat.completions.create(
            messages=all_messages,
            model="gpt-4",
        )

        print(chat_completion)

        gpt_response = chat_completion.choices[0].message.content

        return gpt_response
