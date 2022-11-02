import argparse, os, random, requests, json, os, signal, sys, textwrap
from googletrans import Translator
from rich.console import Console
from rich.prompt import Prompt
from GoogleNews import GoogleNews

googlenews = GoogleNews(lang="en")
console = Console()
bookmarked_surfix = "_bookmarked"

textWrapper = textwrap.TextWrapper(initial_indent=" ", subsequent_indent=" ")
textWrapperDoubleIndents = textwrap.TextWrapper(initial_indent="    ", subsequent_indent="    ")

parser = argparse.ArgumentParser(description='Wordee, a random word picker with with dictionary and news attached.')

parser.add_argument("-i", dest="filename", required=True,
                    help="Specify input text file.", metavar="FILE",
                    type=lambda x: is_valid_file(parser, x))

parser.add_argument("--hide", dest="hideDictionary", action='store_true',
                    help="Hide dictionary result. Until enter pressed.")

# parser.add_argument("--phonetic", dest="phonetic", action='store_true',
#                     help="Play phonetic sound.")

parser.add_argument("--translate", dest="translateDestination", metavar="LANG",
        help="Translate destination language. For example \"ja\", \"ko\", \"zh-tw\".")

# parser.add_argument("--news-api-key", dest="newsApiApiKey", metavar="LANG",
#         help="API key for https://newsapi.org.")

parser.add_argument("--news", dest="alwaysShowNews", action='store_true',
        help="Always show the news related to the word. Can be a little bit slower.")

wordResponseJSONCache = {}
wordNewsResultsCache = {}

def asynchronous(func):
    async def wrapper(*args, **kwargs):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(func, *args, **kwargs)
            return future.result()

    return wrapper

def signal_handler(sig, frame):
    print('\nYou pressed Ctrl+C!')
    sys.exit(0)

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle

def get_news_for_the_word(word):
    if word in wordNewsResultsCache:
        return wordNewsResultsCache[word]
    else:
        googlenews.clear()
        googlenews.search(word)
        newsResults = googlenews.results()
        wordNewsResultsCache[word] = newsResults
        return newsResults

def print_news_for_the_word(word):
    newsResults = get_news_for_the_word(word)
    console.print("Related news:", style="bold")
    for i, newsResult in enumerate(newsResults[:5]):
        title = newsResult["title"].replace(word.capitalize(), "[bold]"+word.capitalize()+"[/bold]")
        title = title.replace(word.lower(), "[bold]"+word+"[/bold]")
        console.print(" %s. "%(i+1)+"[link="+newsResult["link"]+"]"+title)
    console.print("")

def print_word_with_dictionary(word, wordDescription="", hideDictionary=False, translator=None, translateDestination=None, alwaysShowNews=None):
        if translator!=None:
            wordTranslation = translator.translate(word, dest=translateDestination)
            wordTranslated = wordTranslation.text

        if word in wordResponseJSONCache:
            responseJSON = wordResponseJSONCache[word]
            ok = True
        else:
            response = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/"+word)
            ok = response.ok
            responseJSON = json.loads(response.text)
            wordResponseJSONCache[word] = responseJSON

        if alwaysShowNews:
            newsResults = get_news_for_the_word(word)

        # console.print(type(responseJSON) is list)

        # if args.phonetic and "phonetics" in responseJSON:
        #     phonetics = responseJSON["phonetics"]
        #     console.print("phonetics")
        #     # sourceUrl = None
        #     for phonetic in phonetics:
        #         if "audio" in phonetic:
        #             audio = phonetic["audio"]
        #             if audio == "":
        #                 continue
        #             mediaPlayer = vlc.MediaPlayer(audio)
        #             mediaPlayer.play()
        #             break

        if ok:
            if type(responseJSON) is list and len(responseJSON) > 0:
                responseJSON = responseJSON[0]
            if(hideDictionary):
                input("Press enter to show dictionary results...")
            os.system('clear')

            if translator!=None:
                console.print(word.capitalize()+" [magenta]"+wordTranslated+"[/magenta] "+wordDescription, style="markdown.h1")
            else:
                console.print(word.capitalize()+" "+wordDescription, style="markdown.h1")

            
            if "phonetic" in responseJSON:
                console.print(responseJSON["phonetic"], style="bright_magenta")
            else:
                console.print("phonetic not found", style="bright_magenta")

            if "meanings" in responseJSON:
                meanings = responseJSON["meanings"]
                for meaning in meanings:
                    if "partOfSpeech" in meaning:
                        console.print(textWrapper.fill(meaning["partOfSpeech"]), style="italic")
                    if "synonyms" in meaning:
                        synonyms = meaning["synonyms"]
                        if len(synonyms) > 0:
                            console.print(textWrapperDoubleIndents.fill(", ".join(synonyms)), style="green")
                    if "antonyms" in meaning:   
                        antonyms = meaning["antonyms"]
                        if len(antonyms) > 0:
                            console.print(textWrapperDoubleIndents.fill(", ".join(antonyms)), style="red")
                    if "definitions" in meaning:
                        definitions = meaning["definitions"]
                        for i, definition in enumerate(definitions):
                            if i >= 8:
                                break
                            console.print(textWrapperDoubleIndents.fill("%s. "%(i+1)+definition["definition"]))
                            if "example" in definition:
                                console.print(textWrapperDoubleIndents.fill("> "+definition["example"]), style="markdown.block_quote")
                    console.print("")
                console.print("> [link=https://www.google.com/search?q=define+"+word+"]Show the definition on google.[/link]\n")

            if alwaysShowNews:
                print_news_for_the_word(word)

        else:
            if(hideDictionary):
                input("Press enter to show dictionary results...")
            os.system('clear')
            
            if translator!=None:
                console.print(word.capitalize()+" [magenta]"+wordTranslated+"[magenta] "+wordDescription, style="markdown.h1")
            else:
                console.print(word.capitalize()+" "+wordDescription, style="markdown.h1")

            console.print("Status code: "+str(response.status_code), style="red")
            if "title" in responseJSON:
                console.print(textWrapper.fill(responseJSON["title"]), style="bold")
            if "message" in responseJSON:
                console.print(textWrapper.fill(responseJSON["message"]))
            if "resolution" in responseJSON:
                console.print(textWrapper.fill(responseJSON["resolution"]), style="bright_magenta")
            console.print("")
            console.print("> [link=https://www.google.com/search?q=define+"+word+"]Show the definition on google.[/link]\n")

            if alwaysShowNews:
                print_news_for_the_word(word)
        # console.print(responseJSON)
        # console.print(wordTranslation.extra_data)

def start():
    args = parser.parse_args()

    bookmarkedWordsFilename = args.filename.name+bookmarked_surfix+".txt"

    words = args.filename.read().splitlines()
    words = list(word for word in words if word)

    wordsHistory = []

    console.print("[bold]📖 Wordee[/bold]\nA word picker with dictionary api attached.\ncopyright©2022 magneticchen. GPLv3 License.\n")
    console.print(textWrapper.fill("Total "+str(len(words))+" words in the file."))
    console.print(textWrapper.fill("> "+args.filename.name), style="markdown.h1")
    console.print("")

    translator = None
    if args.translateDestination:
        translator = Translator()
        console.print(textWrapper.fill(translator.translate("You have enabled the Translation.", dest=args.translateDestination).text))
        console.print(textWrapper.fill(translator.translate("Translation destionation: ", dest=args.translateDestination).text+"\""+args.translateDestination+"\""))
        # console.print("Translation destionation: \""+args.translateDestination+"\"")
        console.print("")
    # console.print(lines)

    if os.path.isfile(bookmarkedWordsFilename):
        with open(bookmarkedWordsFilename, 'r+') as bookmarkedFile:
            bookmarkedWords = bookmarkedFile.read().splitlines()
            bookmarkedWords = list(word.lower() for word in bookmarkedWords if word)
    else:
        bookmarkedWords = []
    word = None
    wordIndex = -1
    while True:
        dictionary_bookmarked_surfix = ""
        if word == None:
            code = Prompt.ask("Actions: [[bold]N[/bold]]ext word, [[bold]I[/bold]]nput a word, [[bold]H[/bold]]istory, [[bold]Q[/bold]]uit\n", default="N")
            dictionary_bookmarked_surfix = ""
        elif wordIndex == -1:
            code = Prompt.ask("Actions: [[bold]N[/bold]]ext word, [[bold]I[/bold]]nput a word, [[bold]H[/bold]]istory, [[bold]S[/bold]]how news, [[bold]Q[/bold]]uit\n", default="N")
            dictionary_bookmarked_surfix = ""
        elif word.lower() not in bookmarkedWords:
            code = Prompt.ask("Actions: [[bold]N[/bold]]ext word, [[bold]I[/bold]]nput a word, [[bold]H[/bold]]istory, [[bold]S[/bold]]how news, [[bold]B[/bold]]ookmark, [[bold]Q[/bold]]uit\n", default="N")
            dictionary_bookmarked_surfix = ""
        else:
            code = Prompt.ask("Actions: [[bold]N[/bold]]ext word, [[bold]I[/bold]]nput a word, [[bold]H[/bold]]istory, [[bold]S[/bold]]how news, Un[[bold]b[/bold]]ookmark, [[bold]Q[/bold]]uit\n", default="N")
            dictionary_bookmarked_surfix = " [green bold]•[/green bold]"

        if code.lower() == "q":
            break

        elif code.lower() == "i":
            word = Prompt.ask("Word: ")
            wordsHistory.append(word)
            os.system('clear')
            console.print(word.capitalize(), style="markdown.h1")
            print_word_with_dictionary(word, "(Inputted manually)", args.hideDictionary, translator, args.translateDestination, args.alwaysShowNews)
            wordIndex = -1

        elif code.lower() == "h":
            console.print(wordsHistory[-5:])      
            
        elif code.lower() == "s":
            console.print("")
            print_news_for_the_word(word)

        elif code.lower() == "b":
            if word == None:
                console.print("Word not selected.", style="red")
            elif word.lower() not in bookmarkedWords:
                with open(bookmarkedWordsFilename, 'w+') as bookmarkedFile:
                    bookmarkedWords.append(word.lower())
                    bookmarkedFile.write("\n".join(bookmarkedWords))
                    console.print(bookmarkedWords)
                    dictionary_bookmarked_surfix = " [green bold]•[/green bold]" if word.lower() in bookmarkedWords else ""
                    print_word_with_dictionary(word, "("+str(wordIndex+1)+" of "+str(len(words))+")"+dictionary_bookmarked_surfix, False, translator, args.translateDestination, args.alwaysShowNews)
            else:
                with open(bookmarkedWordsFilename, 'w+') as bookmarkedFile:
                    bookmarkedWords.remove(word.lower())
                    bookmarkedFile.write("\n".join(bookmarkedWords))
                    dictionary_bookmarked_surfix = " [green bold]•[/green bold]" if word.lower() in bookmarkedWords else ""
                    print_word_with_dictionary(word, "("+str(wordIndex+1)+" of "+str(len(words))+")"+dictionary_bookmarked_surfix, False, translator, args.translateDestination, args.alwaysShowNews)

        else:
            os.system('clear')
            wordIndex = random.choice(range(len(words)))
            word = words[wordIndex]
            wordsHistory.append(word)
            console.print(word.capitalize(), style="markdown.h1")
            print_word_with_dictionary(word, "("+str(wordIndex+1)+" of "+str(len(words))+")"+dictionary_bookmarked_surfix, args.hideDictionary, translator, args.translateDestination, args.alwaysShowNews)


signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    start()