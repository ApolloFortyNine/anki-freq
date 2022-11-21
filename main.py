import requests
import json
import sqlite3
from tqdm import tqdm


# Search is:new -is:suspended deck:Personal
# Search is:new deck:Personal

URL = 'http://localhost:8765'
con = sqlite3.connect('anki-freq.db3')
cur = con.cursor()


def main():
    res = requests.get(URL)
    print(res.content)
    res = requests.post(URL, json={
        'action': 'findNotes',
        'version': 6,
        'params': {
            'query': 'deck:Personal is:new',
        },
    }).json()
    print(len(res['result']))
    # print(res['result'])
    # other one 1631151275263
    # note_id = 1621926249452
    detail_res = requests.post(URL, json={
        'action': 'notesInfo',
        'version': 6,
        'params': {
            'notes': res['result']
        },
    }).json()
    # Could also use pprint
    # print(json.dumps(detail_res, indent=2, ensure_ascii=False))
    for x in tqdm(detail_res['result']):
        word_in_kanji = x['fields']['Vocabulary-Kanji']['value']
        # print(word_in_kanji)
        word_count = get_word_frequency(word_in_kanji)
        # print(word_count)
        update_freq_count_field(x['noteId'], word_count)

def get_word_frequency(word):
    cur.execute(f"SELECT count FROM word_freq_report WHERE word='{word}';")
    result = cur.fetchone()
    if result is None:
        return 0
    else:
        return result[0]

def update_freq_count_field(note_id, word_count):
    payload = {
            'action': 'updateNoteFields',
            'version': 6,
            'params': {
                'note': {
                    'id': note_id,
                    'fields': {}
                },
            },
        }
    payload['params']['note']['fields']['Frequency-Count'] = str(word_count)
    # print(payload)
    res = requests.post(URL, json=payload).json()
    # print(res)

main()