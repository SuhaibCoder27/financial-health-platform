from googletrans import Translator

translator = Translator()

def translate_text(text, lang):
    if lang == "en":
        return text
    return translator.translate(text, dest=lang).text


def translate_list(items, lang):
    if lang == "en":
        return items
    return [translator.translate(i, dest=lang).text for i in items]
