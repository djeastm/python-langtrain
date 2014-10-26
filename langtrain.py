import sqlite3
#import time

buffer = '\n'

def language_sel():
    print("What language?")
    print("1. German")
    print("2. Japanese")
    print("3. Syrian")
    language = input(":")
    selection(language)

def selection(language):
    print("Enter 1 to input sentences.")
    print("Enter 2 to create sentences.")
    print("Enter 3 to browse sentences. (not functioning)")
    print("Enter 4 to look at dictionary.")
    print("Enter 5 to search through dictionary and edit.")
    print("Enter 6 to import sentences from import.txt")
    print("Enter $$ to go back to language selection.")
    answer = input(":")
    if answer == '$$':
        language_sel()
    elif answer == '1':
        get_string(buffer, language)
    elif answer == '2':
        print("Write the first word.")
        print("Press Enter if you want suggestions.")
        print("Enter '$$' if you want to go back to the main menu.")
        prevword = ''
        writing_mode(prevword, language)
    elif answer == '3':
        pass
    elif answer == '4':
        look_dictionary(language)
    elif answer == '5':
        search_dictionary(language)
    elif answer == '6':
        import_sentences(language)
    else:
        print("Invalid choice")
        selection(language)

def get_string(buffer, language):                                     
    
    string = input("Enter sentence: ")
    if string == '$$':
        if buffer != '\n':
            into_database(buffer, language, 'manual')       #DONE allows user to look at input before committing
        else:
            selection(language)
    elif string == '!':
        if buffer != '\n':
            into_database(buffer, language, 'continual')       #DONE allows user to look at input before committing
        else:
            get_string(buffer, language)        
    elif string == 'X':                                     #DONE allows user to delete last sentence (for mistakes)
        import re
        buffer = re.sub('\n.*.\n$', '\n', buffer)
        print(buffer)
        get_string(buffer, language)
    else:    
        buffer += (string+'\n')
        print(buffer)                                       
        get_string(buffer, language)
        
def into_database(buffer, language, mode):
    if language == '1':
        conn = sqlite3.connect('germandictionary.db')
        sentence_file = 'germansentences.txt'
    elif language == '2':
        conn = sqlite3.connect('japanesedictionary.db')
        sentence_file = 'japanesesentences.txt'
    elif language == '3':
        conn = sqlite3.connect('syriandictionary.db')
        sentence_file = 'syriansentences.txt'
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    #c.execute('drop table if exists dictionary')
    #c.execute('drop table if exists count')
    #c.execute('create table count (count int, k2 int)')
    #c.execute('create table dictionary (position int, prevword text, word text, nextword text)')    
    with open(sentence_file, 'a') as textfile:
        buffer = buffer.splitlines()
        for line in buffer:
            textfile.write(line)
            textfile.write('\n')
            string = line
            string = string.split()
            i = 0
            for word in string:
                while i == 0 and i < len(string)-1:
                    c.execute('insert into dictionary (position, prevword, word, nextword) values (?, ?, ?, ?)', (i, '', string[i], string[i+1]))
                    i += 1
                while i < len(string)-1:
                    c.execute('insert into dictionary (position, prevword, word, nextword) values (?, ?, ?, ?)', (i, string[i-1], string[i], string[i+1]))
                    i += 1
            c.execute('insert into count (count, k2) values (?, ?)', (i, 0))
            conn.commit()
    if mode == 'manual':
        selection(language)
    elif mode == 'continual':
        buffer = '\n'
        print('Input saved.')
        get_string(buffer, language)      

def import_sentences(language):                                      #DONE add way to 'auto-add' sentences (for new databases, etc)
    with open('import.txt', 'r') as import_text:
        print('This might take a minute')
        imported_list = list(import_text)
        for line in imported_list:
            buffer = line
            into_database(buffer, language, 'auto')
        #localtime = time.asctime( time.localtime(time.time()) )
        #if language == '1':
        #    sentence_file = 'germansentences.txt'
        #elif language == '2':
        #    sentence_file = 'japanesesentences.txt'
        #elif language == '3':
        #    sentence_file = 'syriansentences.txt'
        #with open(sentence_file, 'a') as textfile:
        #    textfile.write('------------------------')
        #    textfile.write('\n')
        #    textfile.write('Imported at {0}'.format(localtime))                                     #DONE put in a date-time stamp for every push from buffer to database in the sentences file
        #    textfile.write('\n')
        #    textfile.write('------------------------')
        #    textfile.write('\n')
        print('Done')  
    with open('import.txt', 'w') as new_line:
        new_line.write('\n')
    selection(language) 

def writing_mode(prevword, language):
    from operator import itemgetter
    if language == '1':
        conn = sqlite3.connect('germandictionary.db')
    elif language == '2':
        conn = sqlite3.connect('japanesedictionary.db')
    elif language == '3':
        conn = sqlite3.connect('syriandictionary.db')
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    word = input(":")
    if word == '$$':
        selection(language)
    elif word == '.':
        prevword = ''
        writing_mode(prevword, language)
    else:       
        temp = []
        temp_count = []
        c.execute('select * from dictionary where word=:word and prevword=:prevword', {'word' : word, 'prevword' : prevword})
        for row in c:                                                   #DONE also make it so that the database will look back two words (for when db gets big and lots of results are possible)
            if row[3] not in temp:                                      #DONE needs prevword column in db that saves string[i-1] (except for first word, which gets '')
                temp.append(row[3])                                     #DONE when selecting word from db, first word will look for word AND prevword = '', then each word after
                temp_count.append(dict(nextword=row[3], count=1))       #DONE will look for word and prevword for a match. this should improve results (give more relevant results)
            else:
                for item in temp_count:
                    if item['nextword'] == row[3]:
                        item['count'] += 1
        sorted_temp_count = sorted(temp_count, key=itemgetter('count'), reverse=True)
        for item in sorted_temp_count:
            print(item['nextword'])
        prevword = word
        c.close()
        writing_mode(prevword, language)
        
#TODO create a good gui
    #TODO make it so that you can enter more than one word at a time in writing_mode (gui might help that)
    #TODO instead of timestamping each entry into database, have it timestamp a 'session'
        #TODO perhaps use a different key than '$$' for each entry, but keep $$ as a session marker
        #TODO or perhaps the 'crowding' problem wouldn't be as noticeable in a proper gui
    #TODO have a tooltip-type popup when you hover over a word that gives definitions and/or grammar
#TODO dictionary is somewhat unusable because of duplicate entries, can hide position count (I think)
#TODO have the website autocomplete words, if possible, so to reinforce spelling.
#TODO set it up so that case doesn't matter except Sie and sie (Actually, I think case is okay to leave important)
#TODO make it judge where in the sentence the word is (beginning, middle, end) and prioritize results   
#TODO save sentences for browsing later (partially done, need easy way to browse other than textfile)
#TODO consider adding a game/competitive element to it
#TODO get more than just previous and next word, and have a game-type drill that gives you sections of sentences and you have to make a
    #TODO complete thought with it
#TODO as a game, when creating sentences from previous ones, (option 2), save all entered words, and have the program check to see if you've used the
    #TODO correct words in each sentence. IE, it gives you choices, but some of them are from sentences that have different beginnings.
#TODO show the last couple of entries (5-10), and instead of having to feed the lines a little at a time, make it autosave
    #TODO should be easier on the web?
#TODO have a way for, when you press X to undo what you've written, it will automatically copy the line back to be edited.
#TODO maybe have graphs allowing user to analyze what words/phrases are used most, what gaps are there in coverage, etc
#TODO would be really effective using speech-recognition software, since the software would only need to pick from the files
    #TODO of the smaller list
#TODO have a visualization that first shows all possibilities, but removes possibilities from the list as you add more words to the filter.
#TODO if on web, consider having a way for people to collaborate on inputting sentences (like classmates putting in a chapter each, for example).
     
def look_dictionary(language):
    if language == '1':
        conn = sqlite3.connect('germandictionary.db')
    elif language == '2':
        conn = sqlite3.connect('japanesedictionary.db')
    elif language == '3':
        conn = sqlite3.connect('syriandictionary.db')
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    print('   Position     Word                Next Word     ')
    print('-------------------------------------------------')
    c.execute('select * from dictionary order by lower(word)')          #DONE sort ignoring case
    for row in c:
        print('{:^16}{:<20}{:<20}'.format(row['position'], row['word'], row['nextword']))
    c.execute('select * from count')
    w_count = 0
    for row in c:
        w_count += row['count'] + 1
    print('Total word count equals {}'.format(w_count)) 
    print()
    c.close()
    selection(language)

def search_dictionary(language):                                        #DONE edit mode where you can browse through the dictionary and edit entries (for mistakes) 
    if language == '1':
        conn = sqlite3.connect('germandictionary.db')
    elif language == '2':
        conn = sqlite3.connect('japanesedictionary.db')
    elif language == '3':
        conn = sqlite3.connect('syriandictionary.db')
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    search_term = input('Enter word to change: ')
    c.execute('select * from dictionary where word=:search_term', {'search_term' : search_term})
    print('Index   Position     Word                Next Word     ')
    print('------------------------------------------------------')
    i = 1
    for row in c:
        print('{:^5}{:^16}{:<20}{:<20}'.format(i, row['position'], row['word'], row['nextword']))
        i += 1
    #print('What Index do you want to edit?')
    #index_num = input(':')
    print('To what do you want the word changed?')
    print("Enter '$$' to cancel")
    word_sel = input(':')
    if word_sel != '$$':
        c.execute('update dictionary set word=:word_sel where word=:search_term', {'word_sel' : word_sel, 'search_term' : search_term})
        conn.commit()
        print('Edit done.')
    selection(language)
    
def main():
    
    language_sel()
  
    def get_partSpeech(s):
        ''' has to ask the user the part of speech and store it'''
        pass 
       
if __name__ == "__main__": main()
