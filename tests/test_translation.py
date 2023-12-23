def test_translation(module_name):
    translations = module_name.translations('ru')
    print(translations)
    assert translations
