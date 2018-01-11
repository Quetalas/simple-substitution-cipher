import random
import pprint
import copy
import re
import wordPatterns
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
nonLettersOrSpacePattern = re.compile('[^A-Z\s]')

def encryptMessage(key, message):
    return translateMessage(key, message, 'encrypt')


def decryptMessage(key, message):
    return translateMessage(key, message, 'decrypt')


def translateMessage(key, message, mode):
    translated = ''
    charsA = LETTERS
    charsB = key
    if mode == 'decrypt':
        charsA, charsB = charsB, charsA
    for symbol in message:
        if symbol.upper() in charsA:
            symIndex = charsA.find(symbol.upper())
            if symbol.isupper():
                translated += charsB[symIndex].upper()
            else:
                translated += charsB[symIndex].lower()
        else:
            translated += symbol
    return translated


def getRandomKey():
    key = list(LETTERS)
    random.shuffle(key)
    return ''.join(key)


def getWordPattern(word):
    """
    Return a string of the pattern from of the given word.
    :param word:
    :return:
    """
    word = word.upper()
    nextNum = 0
    letterNums = {}
    wordPattern = []

    for letter in word:
        if letter not in letterNums:
            letterNums[letter] = str(nextNum)
            nextNum += 1
        wordPattern.append(letterNums[letter])
    return '.'.join(wordPattern)


def getPatterns():
    allPatterns = {}
    wordList = []
    for word in open('dictionary.txt', 'r'):
        wordList.append(word[:-1]) #cut \n
    print(wordList[:5])

    for word in wordList:
        pattern = getWordPattern(word)
        if pattern not in allPatterns:
            allPatterns[pattern] = [word]
        else:
            allPatterns[pattern].append(word)
    fo = open('wordPatterns.py', 'w')
    fo.write('allPatterns = ')
    fo.write(pprint.pformat(allPatterns))
    fo.close()


def hack(message):
    #Determine the possible valid ciphertext translations
    print('Hacking...')
    letterMapping = hackSimpleSub(message)
    #Display the results to user
    print('Mapping:')
    pprint.pprint(letterMapping)
    print('Original ciphertext:')
    print(message, '\n')
    print('Copying hacked message to clipboard:')
    hackedMessage = decryptWithCipherletterMapping(message, letterMapping)
    #pyperclip.copy(hackedMessage)
    print(hackedMessage)


def getBlanlCipherletterMapping():
    return { chr(x): [] for x in range(65, 91)}


def addLettersToMapping(letterMapping, cipherword, candidate):
    letterMapping = copy.deepcopy(letterMapping)
    for i in range(len(cipherword)):
        if candidate[i] not in letterMapping[cipherword[i]]:
            letterMapping[cipherword[i]].append(candidate[i])
    return letterMapping


def intersectMapping(mapA, mapB):
    """
    Return map which consist letters which exist in BOTH maps
    :param mapA:
    :param mapB:
    :return:
    """
    intersectedMapping = getBlanlCipherletterMapping()
    for letter in LETTERS:
        #An empty list means "any letter is possible". In this case
        # just copy the othe map entirely.
        if mapA[letter] == []:
            intersectedMapping[letter] = copy.deepcopy(mapB[letter])
        elif mapB[letter] == []:
            intersectedMapping[letter] = copy.deepcopy(mapA[letter])
        else:
            for mappedLetter in mapA[letter]:
                if mappedLetter in mapB[letter]:
                    intersectedMapping[letter].append(mappedLetter)
    return intersectedMapping


def removeSolvedLettersFromMapping(letterMapping):
    """
    Cipher letters in the mapping that map to only one letter are
    solved and can be removed from theother letters.
    :param letterMapping:
    :return:
    """
    letterMapping = copy.deepcopy(letterMapping)
    loopAgain = True
    while loopAgain:

        loopAgain = False
        solvedLettes = []

        for cipherletter in LETTERS:
            if len(letterMapping[cipherletter]) == 1:
                solvedLettes.append(letterMapping[cipherletter][0])

        for cipherletter in LETTERS:
            for s in solvedLettes:
                if len(letterMapping[cipherletter]) != 1 and s in letterMapping[cipherletter]:
                    letterMapping[cipherletter].remove(s)
                    if len(letterMapping[cipherletter]) == 1:
                        loopAgain = True
    return letterMapping


def hackSimpleSub(message):
    intersectedMap = getBlanlCipherletterMapping()
    cipherwordList = nonLettersOrSpacePattern.sub('', message.upper()).split()
    for cipherword in cipherwordList:
        newMap = getBlanlCipherletterMapping()

        wordPattern = getWordPattern(cipherword)
        if wordPattern not in wordPatterns.allPatterns:
            # there aren't in the dictionary
            continue

        for candidate in wordPatterns.allPatterns[wordPattern]:
            newMap = addLettersToMapping(newMap, cipherword, candidate)

        intersectedMap = intersectMapping(intersectedMap, newMap)
    return removeSolvedLettersFromMapping(intersectedMap)


def decryptWithCipherletterMapping(ciphertext, lettermapping):
    """
    Return a string of the ciphertext decrypted with the letter mapping,
    with any ambiguous leters replaced with an _ underscore.
    :param ciphertext:
    :param lettermapping:
    :return:
    """
    key = ['x'] * len(LETTERS)
    for cipherletter in LETTERS:
        if len(lettermapping[cipherletter]) == 1:
            keyIndex = LETTERS.find(lettermapping[cipherletter][0])
            key[keyIndex] = cipherletter
        else:
            ciphertext = ciphertext.replace(cipherletter.lower(), '_')
            ciphertext = ciphertext.replace(cipherletter.upper(), '_')
    key = ''.join(key)
    return decryptMessage(key, ciphertext)





if __name__ == '__main__':
    key = getRandomKey()
    mes = """If a man is offered a fact which goes against his 
          instincts, he will scrutinize it closely, and unless the evidence is
          overwhelming, he will refuse to believe it. If, on the other hand, he is
          offered something which affords a reason for acting in accordance to his instincts, he
          will accept it even on the slightest evidence. The origin of myths is
          explained in this way. -Bertrand Russel"""
    encmes = encryptMessage(key, mes)

    print('encrypted message:')
    print(encmes, '\n')
    print('decrypted message: ')
    print(decryptMessage(key, encmes), '\n')

    print('word pattern for "Hello"', getWordPattern('Hello'))
    getPatterns()
    print(getBlanlCipherletterMapping())
    print(hack(encmes))