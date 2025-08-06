from transformers import pipeline
import argostranslate.package, argostranslate.translate

argostranslate.package.update_package_index()
installed_packages = argostranslate.package.get_installed_packages()
if not installed_packages:
    available_packages = argostranslate.package.get_available_packages()

    for pkg in available_packages:
        if (pkg.from_code == "en" and pkg.to_code == "ur") or (pkg.from_code == "ur" and pkg.to_code == "en"):
            argostranslate.package.install_from_path(pkg.download())

def detect_language(text):
    pipe = pipeline("text-classification", model="papluca/xlm-roberta-base-language-detection")
    result = pipe(text[:100])[0]
    return result["label"]

def translate_text(text, from_lang, to_lang):
    available_translations = argostranslate.translate.get_installed_languages()
    from_lang_obj = next((lang for lang in available_translations if lang.code == from_lang), None)
    to_lang_obj = next((lang for lang in available_translations if lang.code == to_lang), None)
    if from_lang_obj and to_lang_obj:
        translation = from_lang_obj.get_translation(to_lang_obj)
        return translation.translate(text)
    return text 
