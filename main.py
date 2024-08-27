import docx2txt
import re
import csv
import os

def exception_found(line):
    if 'METEOROLOGIA [entrada actualitzada] huracà 1.' in line:
        return True

    if 'NÚVOLS [entrada original] fracto-.' in line:
        return True

    if 'ALTRES ÀREES [entrada actualitzada] iso-.' in line:
        return True

    if 'ALTRES ÀREES [entrada original] quasi-.' in line:
        return True

    if 'ALTRES ÀREES [entrada original] turbo-.' in line:
        return True


def treat_exceptions(data):
    if 'METEOROLOGIA [entrada actualitzada] huracà 1.' in line:
        word = 'huracà'
        data[word] = {}
        data[word]['definition'] = []
        data[word]['definition'].append('Vent violent produït pels ciclons tropicals; més especialment pels del mar de les Antilles.')
        data[word]['definition'].append('El conjunt del cicló.')
        data[word]['definition'].append('En l’escala de Beaufort, vent de força 12, amb una velocitat mitjana de més de 32,7 metres per segon.')

        data[word]['lemma'] = lemmatize(word)
        data[word]['def_lem'] = []
        data[word]['def_lem'].append(lemmatize(data[word]['definition'][0]))
        data[word]['def_lem'].append(lemmatize(data[word]['definition'][1]))
        data[word]['def_lem'].append(lemmatize(data[word]['definition'][2]))

        return word

    if 'NÚVOLS [entrada original] fracto-.' in line:
        word = 'fracto-'
        data[word] = {}
        data[word]['definition'] = 'Prefix que es posa al nom d’alguns núvols per a indicar que són de formes esqueixades.'

    if 'ALTRES ÀREES [entrada actualitzada] iso-.' in line:
        word = 'iso-'
        data[word] = {}
        data[word]['definition'] = 'Prefix que significa ‘igual’ i s’usa, unit a altres mots, per a designar les línies o superfícies en les quals alguna variable meteorològica té el mateix valor.'

    if 'ALTRES ÀREES [entrada original] quasi-.' in line:
        word = 'quasi-'
        data[word] = {}
        data[word]['definition'] = 'Prefix freqüentment usat davant un adjectiu, per a indicar que la condició expressada per a aquest es compleix aproximadament, però no exactament (depressió quasiestacionària; oscil·lació quasiperiòdica).'

    if 'ALTRES ÀREES [entrada original] turbo-.' in line:
        word = 'turbo-'
        data[word] = {}
        data[word]['definition'] = 'Prefix que s’anteposa al nom d’alguna propietat de l’aire per a indicar que és deguda o inherent a la turbulència (turbodifusivitat, turboviscositat, etc.).'

    data[word]['lemma'] = lemmatize(word)
    data[word]['def_lem'] = lemmatize(data[word]['definition'])

    return word


def lemmatize(text):
    output = os.popen('echo "' + text + '" | analyze -f /usr/share/freeling/config/ca.cfg --numb --noquant --nodate --outlv morfo').read().splitlines()
    final_lemma = ''
    for i, lema_line in enumerate(output):
        if not lema_line:
            continue

        lemma = re.findall(r'(\S*)', output[i])[2]
        if lemma == '|':
            break
        final_lemma += ' ' + lemma

    print(final_lemma)

    return final_lemma.strip()


# Load the document
doc_path = "/home/vboxuser/script_diccionari-main/Vocabulari_meteo_DEFINITIU_11març(2).docx"

# Convertim docx en text pla
text = docx2txt.process(doc_path)

# Eliminem linies innecessàries
lines = text.splitlines()
lines = lines[63:]
lines = [line.strip() for line in lines]
lines = list(filter(lambda line: line != '' and line != ' ', lines))
lletres = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
lines = list(filter(lambda line: line not in lletres, lines))
lines = list(filter(lambda line: not (line.startswith('Sin. compl') or line.startswith('Sin compl') or line.startswith('Símbol:') or line.startswith('Sinònim compl.') or line.startswith('Sigla:') or line.startswith('V. t.') or line.startswith('V.t.:') or line.startswith('V.t:') or line.startswith('V. t:')), lines))
lines.pop()

definition_regexs = [
    r'c. nom. m. \| c. nom. f.',
    r'c. nom. m. o c. nom. f.',
    r'c\. nom\. f\. pl\.',
    r'c\. nom\. m\. pl\.',
    r'v\. intr\. pron\.',
    r'conc\. nom\.m\.',
    r'c\. nom\. \.f',
    r'c\. nom\. f\.',
    r'c\. nom\. m\.',
    r'conc. nom m.',
    r'n\. pr\. f\.',
    r'n\. pr\. m\.',
    r'c\. nom\. f',
    r'c\. nom\. m',
    r'v\. intr\.',
    r'c\. nom\.',
    r'm\. \| f\.',
    r'm\.\| f\.',
    r'm\. o f\.',
    r'm\. pl\.',
    r'f\. pl\.',
    r'adj\.',
    r' m\.',
    r' f\.',
    r' v\.'
]

word_regexs = [
    '(?<=.entrada original. ).*(?=%%)',
    '(?<=.entrada original obsoleta. ).*(?=%%)',
    '(?<=.entrada actualitzada. ).*(?=%%)',
    '(?<=.entrada nova. ).*(?=%%)',
]

data = {}
for line in lines:
    # Search definition
    for pattern in definition_regexs:
        definition_pattern_found = re.search('(?<=' + pattern + ').*', line)
        if definition_pattern_found:
            break

    definition_pattern = pattern

    # If we don't find a normal definition pattern it means it is one of those extra definitions of a word that is not specified as 1., 2., 3., etc. So we have to treat it.
    if not definition_pattern_found:
        # Check exceptions
        if exception_found(line):
            word = treat_exceptions(data)
            continue

        # If we only hava one definition, we add the extra definition line
        if isinstance(data[word]['definition'], str):
            data[word]['definition'] += ' ' + line
            data[word]['def_lem'] += ' ' + lemmatize(line)
        else:
            # If we have actual different definitions (1., 2., etc.) we append the extra definition in the list of definitions
            data[word]['definition'].append(line)
            data[word]['def_lem'].append(lemmatize(line))

        continue
    else:
        # We found a normal definition
        definition = definition_pattern_found.group().strip()

    # Check whether it has more than one definition
    has_many_definitions = re.search(r'\| 2', definition)
    if has_many_definitions:
        def1 = def2 = def3 = def4 = None
        try:
            def1 = re.search(r'(?<=1\.).*(?=\| 2)', definition).group().strip()
        except:
            def1 = re.search(r'.*(?=\| 2)', definition).group().strip()
        def2 = re.search(r'(?<=\| 2\.).*(?=\| 3\.)', definition)
        if def2:
            def2 = def2.group().strip()
            def3 = re.search(r'(?<=\| 3\.).*(?=\| 4\.)', definition)
            if def3:
                def3 = def3.group().strip()
                def4 = re.search(r'(?<=\| 4\.).*', definition)
                if def4:
                    def4 = def4.group().strip()
            else:
                def3 = re.search(r'(?<=\| 3\.).*', definition).group().strip()
        else:
            def2 = re.search(r'(?<=\| 2\.).*', definition).group().strip()

    # Search word
    for pattern in word_regexs:
        pattern = pattern.replace('%%', definition_pattern)
        word_found = re.search(pattern, line)
        if word_found:
            break
    
    # Generate data
    if word_found:
        word = word_found.group().strip()
        data[word] = {}
        data[word]['lemma'] = lemmatize(word)
        data[word]['definition'] = definition
        data[word]['def_lem'] = lemmatize(definition)

        if has_many_definitions:
            data[word]['definition'] = []
            data[word]['definition'].append(def1)
            data[word]['definition'].append(def2)

            data[word]['def_lem'] = []
            data[word]['def_lem'].append(lemmatize(def1))
            data[word]['def_lem'].append(lemmatize(def2))

            if def3:
                data[word]['definition'].append(def3)
                data[word]['def_lem'].append(lemmatize(def3))
            if def4:
                data[word]['definition'].append(def4)
                data[word]['def_lem'].append(lemmatize(def4))


with open('diccionari.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['Paraula', 'Lema', 'Definició', 'Def_lema'])
    for word in data:
        if isinstance(data[word]['definition'], str):
            writer.writerow([word, data[word]['lemma']] + ["['" + data[word]['definition'] + "']", "['" + data[word]['def_lem'] + "']"])
        else:
            writer.writerow([word, data[word]['lemma']] + [str(data[word]['definition']), str(data[word]['def_lem'])])
