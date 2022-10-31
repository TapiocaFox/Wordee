import argparse, os, random, requests, json, os, signal, sys, vlc, textwrap
from rich.console import Console
from rich.prompt import Prompt

def signal_handler(sig, frame):
    print('\nYou pressed Ctrl+C!')
    sys.exit(0)

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle

textWrapper = textwrap.TextWrapper(initial_indent=" ", subsequent_indent=" ")
textWrapperDoubleIndents = textwrap.TextWrapper(initial_indent="    ", subsequent_indent="    ")

parser = argparse.ArgumentParser(description='Wordee, a word picker with dictionary api attached.')

parser.add_argument("-i", dest="filename", required=True,
                    help="Specify input text file.", metavar="FILE",
                    type=lambda x: is_valid_file(parser, x))

parser.add_argument("--hide", dest="hideDictionary", action='store_true',
                    help="Hide dictionary result. Until enter pressed.")

parser.add_argument("--phonetic", dest="phonetic", action='store_true',
                    help="Play phonetic sound.")

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    console = Console()
    args = parser.parse_args()
    words = args.filename.read().splitlines()
    words = list(word for word in words if word)
    # console.print(lines)

    console.print("Total", len(words), "words in the file.")
    console.print(">", args.filename.name, style="markdown.h1")
    console.print("")
    while True:
        pickNextWord = Prompt.ask("Pick next word?", default="Y")
        if pickNextWord != "Y" and pickNextWord != "y":
            break
        os.system('clear')
        wordIndex = random.choice(range(len(words)))
        word = words[wordIndex]

        console.print(word.capitalize(), style="markdown.h1")

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
            if(args.hideDictionary):
                input("Press Enter to show dictionary results...")
            os.system('clear')
            console.print(word.capitalize(), style="markdown.h1")

            
            if "phonetic" in responseJSON:
                console.print(responseJSON["phonetic"], style="markdown.block_quote")
            else:
                console.print("phonetic not found", style="markdown.block_quote")

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
                console.print("[link=https://www.google.com/search?q=define+"+word+"]Show definition on google.[/link]\n")

        else:
            if(args.hideDictionary):
                input("Press Enter to show dictionary results...")
            os.system('clear')
            console.print(word.capitalize(), style="markdown.h1")
            console.print("Status code: "+str(response.status_code), style="red")
            console.print(responseJSON)

