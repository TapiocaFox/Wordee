import argparse, os, random, requests, json, os, signal, sys, textwrap
from googletrans import Translator
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def signal_handler(sig, frame):
    print('\nYou pressed Ctrl+C!')
    sys.exit(0)

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle

def print_word_with_dictionary(word, wordDescription="", hideDictionary=False, translator=None, translateDestination=None):
        if translator!=None:
            wordTranslated = translator.translate(word, dest=translateDestination).text

        response = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/"+word)
    
        responseJSON = json.loads(response.text)

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

        if response.ok:
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

        else:
            if(hideDictionary):
                input("Press enter to show dictionary results...")
            os.system('clear')
            
            if args.translateDestination:
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

def start():
    args = parser.parse_args()

    words = args.filename.read().splitlines()
    words = list(word for word in words if word)
    # console.print(lines)

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
    while True:
        pickNextWord = Prompt.ask("Pick next word?", default="Y")
        if pickNextWord != "Y" and pickNextWord != "y":
            break
        os.system('clear')
        wordIndex = random.choice(range(len(words)))
        word = words[wordIndex]

        console.print(word.capitalize(), style="markdown.h1")

        print_word_with_dictionary(word, "("+str(wordIndex+1)+" of "+str(len(words))+")", args.hideDictionary, translator, args.translateDestination)


textWrapper = textwrap.TextWrapper(initial_indent=" ", subsequent_indent=" ")
textWrapperDoubleIndents = textwrap.TextWrapper(initial_indent="    ", subsequent_indent="    ")

parser = argparse.ArgumentParser(description='Wordee, a word picker with dictionary api attached.')

parser.add_argument("-i", dest="filename", required=True,
                    help="Specify input text file.", metavar="FILE",
                    type=lambda x: is_valid_file(parser, x))

parser.add_argument("--hide", dest="hideDictionary", action='store_true',
                    help="Hide dictionary result. Until enter pressed.")

# parser.add_argument("--phonetic", dest="phonetic", action='store_true',
#                     help="Play phonetic sound.")

parser.add_argument("--translate", dest="translateDestination", metavar="LANG",
        help="Translate destination language. For example \"ja\", \"ko\", \"zh-tw\".")

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    start()