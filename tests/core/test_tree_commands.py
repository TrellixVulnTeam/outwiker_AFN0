'''
Test for the outwiker.test.commands.getAlternativeTitle
'''

import pytest

import outwiker.core.tree_commands as tc


@pytest.mark.parametrize('title, siblings, expected', [
    ('', [], '(1)'),
    ('         ', [], '(1)'),
    ('', ['(1)'], '(2)'),
    ('Проверка', [], 'Проверка'),
    ('Проверка тест', [], 'Проверка тест'),
    ('    Проверка тест     ', [], 'Проверка тест'),
    ('Проверка', ['Проверка'], 'Проверка (1)'),
    ('Проверка', ['Test', 'Проверка'], 'Проверка (1)'),
    ('Проверка     ', ['Test', 'Проверка'], 'Проверка (1)'),
    ('     Проверка', ['Test', 'Проверка'], 'Проверка (1)'),
    ('     Проверка     ', ['Test', 'Проверка'], 'Проверка (1)'),
    ('Проверка', ['Test', 'Проверка', 'Проверка (1)',
                  'Проверка (2)'], 'Проверка (3)'),
    ('Проверка', ['Test', 'проверка'], 'Проверка (1)'),
    ('проверка', ['Test', 'Проверка'], 'проверка (1)'),
    ('Проверка', ['Test', 'проверка', 'проверка (1)'], 'Проверка (2)'),
    ('проверка', ['Test', 'Проверка', 'Проверка (1)'], 'проверка (2)'),
    ('Проверка:', ['Проверка_'], 'Проверка_ (1)'),
    ('Проверка:', ['Проверка_', 'Проверка_ (1)'], 'Проверка_ (2)'),
    ('Проверка:', [], 'Проверка_'),
    ('Проверка ><|?*:"\\/#%', [], 'Проверка ___________'),
    ('Проверка ><|?*:"\\/#% test', [], 'Проверка ___________ test'),
    ('Проверка.', [], 'Проверка_'),
    ('Проверка...', [], 'Проверка___'),
    ('Проверка...', ['Проверка___'], 'Проверка___ (1)'),
])
def test_getAlternativeTitle(title, siblings, expected):
    newtitle = tc.getAlternativeTitle(title, siblings)
    assert newtitle == expected
