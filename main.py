import docx2txt
import re
import csv


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
        data[word] = []
        data[word].append('Vent violent produït pels ciclons tropicals; més especialment pels del mar de les Antilles.')
        data[word].append('El conjunt del cicló.')
        data[word].append('En l’escala de Beaufort, vent de força 12, amb una velocitat mitjana de més de 32,7 metres per segon.')

    if 'NÚVOLS [entrada original] fracto-.' in line:
        word = 'fracto-'
        data[word] = 'Prefix que es posa al nom d’alguns núvols per a indicar que són de formes esqueixades.'

    if 'ALTRES ÀREES [entrada actualitzada] iso-.' in line:
        word = 'iso-'
        data[word] = 'Prefix que significa ‘igual’ i s’usa, unit a altres mots, per a designar les línies o superfícies en les quals alguna variable meteorològica té el mateix valor.'

    if 'ALTRES ÀREES [entrada original] quasi-.' in line:
        word = 'quasi-'
        data[word] = 'Prefix freqüentment usat davant un adjectiu, per a indicar que la condició expressada per a aquest es compleix aproximadament, però no exactament (depressió quasiestacionària; oscil·lació quasiperiòdica).'

    if 'ALTRES ÀREES [entrada original] turbo-.' in line:
        word = 'turbo-'
        data[word] = 'Prefix que s’anteposa al nom d’alguna propietat de l’aire per a indicar que és deguda o inherent a la turbulència (turbodifusivitat, turboviscositat, etc.).'

    return word


# Load the document
doc_path = "/Users/oriol/Downloads/Vocabulari_meteo_DEFINITIU_11març(2).docx"

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
data2 = {}
for line in lines:
    # Search definition
    for pattern in definition_regexs:
        definition_found = re.search('(?<=' + pattern + ').*', line)
        if definition_found:
            break

    definition_pattern = pattern

    if not definition_found:
        # Check exceptions
        if exception_found(line):
            word = treat_exceptions(data)
            continue

        if isinstance(data[word], str):
            data[word] += ' ' + line
        else:
            data[word].append(line)

        continue

    definition = definition_found.group().strip()

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
        data[word] = definition

        if has_many_definitions:
            data[word] = []
            data[word].append(def1)
            data[word].append(def2)
            if def3:
                data[word].append(def3)
            if def4:
                data[word].append(def4)

with open('diccionari.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['Paraula', 'Definició'])
    for word in data:
        if isinstance(data[word], str):
            writer.writerow([word] + ["['" + data[word] + "']"])
        else:
            writer.writerow([word] + [str(data[word])])
