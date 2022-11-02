# Wordee
Wordee is a random word picker with dictionary and news attached. Help you memorize vocabularies using CLI.
Useful for english test preparations like TOEFL or GRE.

![](/imgs/screenshot_6.png)

## Pick a word
``python3 wordee.py --hide -i gre_vocabularies.txt`` picking from a words list file.

``python3 wordee.py --hide --translate ja -i gre_vocabularies.txt`` with translation

``python3 wordee.py --news -i gre_vocabularies.txt`` always show the news related to the word

``python3 wordee.py -h`` for help

## More informations

[Google translate languages code](https://cloud.google.com/translate/docs/languages)

[dictionaryapi.dev](https://dictionaryapi.dev/)