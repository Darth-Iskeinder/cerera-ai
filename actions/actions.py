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
                  " Отвечай только на английском?"
                  " Когда клиент ответит на вопросы и выберет конкретный товар, надо написать что скоро с ним свяжется наш менеджер."
                  " Если не знаешь ответ, или нету подходящего товара, то направь на менеджера."
                  " Перед отправкой менеджеру, спроси имя."
                  " В сообщении в котором точно отправляешь менеджеру, в конце напиши {manager}"
                  " Отвечай на русском. Не выдумывай данные, если не знаешь"
                  " На вопросы и просьбы не касающееся наших услуг, отвечай просьбой вернутся к вопросам каших услуг."
                  " В ходе разговора ранее, от клиента выяснили следующую информацию:")

        missing_slots = []
        if not origin:
            missing_slots.append("origin")
            prompt += f"\nгород вылета: предположительно Бишкек"
        else:
            prompt += f"\nгород вылета: {origin}"
        if not destination:
            missing_slots.append("destination")
        else:
            prompt += f"\nстрана назначения: {destination}"
        if not time:
            missing_slots.append("time")
        else:
            if isinstance(time, list) and isinstance(time[0], str):
                time_text = '\t'.join(time)
            elif isinstance(time, list) and isinstance(time[0], dict):
                time_text = '\t'.join([f"{t['from']} - {t['to']}" for t in time])
            prompt += f"\nдата: {time_text}"
        if not tag:
            missing_slots.append("tag")
        else:
            tag_text = '\t'.join(tag) + '\n'
            prompt += f"\nусловия: {tag_text}"

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
            if products:
                products_text = self.product_to_text(products=products)
                prompt += f"\nУ нас в базе есть продукты: \n {products_text}"
                prompt += f"\nТолько если пользователь выбрал конкретный товар из списка, в конце сообщения верни id в формате [id]."
            else:
                prompt += f"В базе не нашли подходящий товар."

        text = self.get_text_from_gpt(prompt, user_messages)
        user_messages.append({
            "role": "assistant",
            "content": text,
        })

        dispatcher.utter_message(text=text)


        return [SlotSet("user_messages", user_messages)]

    def get_products_from_database(self, destination):
        filtered_products = get_filtered_products(country=destination)

        return filtered_products

    def product_to_text(self, products):
        products_data = [(product.id, product.tour_name, product.price, product.description, product.duration,
                           product.tour_type, product.country, product.departure_city,
                          product.arrival_city) for
                         product in products]

        header_row = " ".join([
            "ID", "Название тура", "Цена", "Описание", "Продолжительность",
            "Тип тура", "Страна",
            "Город отправления", "Город прибытия"
        ])
        products_data = [
            " ".join(map(str, row)) for row in products_data
        ]

        # Объединение строк таблицы в единый текст
        data_text = " ".join([header_row] + products_data)

        return data_text

    def get_text_from_gpt(self, prompt, user_messages):

        all_messages = []
        all_messages.append({
            "role": "system",
            "content": prompt + ". Отвечай только на английском, даже если спросит на других языках."
        })

        for message in user_messages:
            all_messages.append(message)

        chat_completion = client.chat.completions.create(
            messages=all_messages,
            model="gpt-3.5-turbo-0125",
        )
        print(all_messages)
        print(chat_completion)

        gpt_response = chat_completion.choices[0].message.content

        return gpt_response
