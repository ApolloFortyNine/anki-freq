from pprint import pprint
import re
import requests
import yaml
from tqdm import tqdm
from argparse import ArgumentParser

URL = 'http://localhost:8765'

def load():
    res = requests.get(URL)
    print(res.content)
    res = requests.post(URL, json={
        'action': 'findNotes',
        'version': 6,
        'params': {
            'query': 'deck:current',
        },
    }).json()
    if res.get('error', None):
        print('error:', res['error'])
        return
    detail_res = requests.post(URL, json={
        'action': 'notesInfo',
        'version': 6,
        'params': {
            'notes': res['result']
        },
    }).json()
    with open('notes.yml', 'w') as fp:
        yaml.dump(detail_res, fp)

def handle_note(note):
    found = False
    for field, value in note['fields'].items():
        if '#000000' in value['value']:
            print('old', field, value)
            value['value'] = re.sub(r'color: #000000; ', '', value['value'])
            print('new', field, value)
            found = True
    if found:
        print('updated note:')
        print(note)
        payload = {
            'action': 'updateNoteFields',
            'version': 6,
            'params': {
                'note': {
                    'id': note['noteId'],
                    'fields': {}
                },
            },
        }
        for field, value in note['fields'].items():
            payload['params']['note']['fields'][field] = value['value']
        pprint(payload)
        if True:
            res = requests.post(URL, json=payload).json()
            print(res)

    return False

def fix():
    print('loading')
    with open('notes.yml', 'r') as fp:
        notes = yaml.load(fp)
    print('loaded')
    notes = notes['result']
    print(f'notes: {len(notes)}')
    for note in notes:
        res = handle_note(note)
        if res:
            return

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--fix', action='store_true')
    parser.add_argument('--load', action='store_true')
    args = parser.parse_args()
    if args.load:
        load()
    if args.fix:
        fix()