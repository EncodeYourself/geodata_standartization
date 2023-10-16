from enchant.utils import levenshtein
import re
import numpy as np

clean_mutations = {
    'C': ['Россия'],
    'R1': ['область','обл.'],
    'R2': ['республика', 'респ.'],
    'R3': ['край'],
    'R4': ['автономный округ'],
    'D1': ['район', 'р-н'],
    'D2': ['городской округ'],
    'G': ['город ', 'г.'],
    'V1': ['деревня'],
    'V2': ['село', 'с.'],
    'V3': ['станица', 'ст-ца'],
    'V4': ['п.г.т.', 'посёлок городского типа'],
    'V5': ['рабочий посёлок', 'р.п.'],
    'V6': ['посёлок', 'п.'],
    'V7': ['аул'],
    'V8': ['починок', 'поч.'],
    'V9': ['хутор', 'х.'],
    'VV': ['слобода', 'сл.'],
    'S1': ['проспект', 'пр-кт'],
    'S2' : ['ул.', 'улица'],
    'S3': ['переулок', 'пер.', 'пр.'],
    'S4': ['площадь', 'пл.'],
    'S5': ['бульвар', 'б.'],
    'B': ['дом', 'стр.'],
    'Z': ['помещение', ''],
    }

def reverse(dictionary):
    result = {}

    for key, values in dictionary.items():
        for value in values:
            result.update({value:key})

    return result


def clean_X(string):
    regex_pattern = re.compile(f'X(?=\s\w+)')
    string = re.sub(regex_pattern, 'V1', string)

    return string.replace('X', 'B')


def clean_S(string):
    pattern = re.compile(' ул(?![ауь])(?=\w+)')
    string = re.sub(pattern, ' S2 ', string)

    return string


def remove_par(string):
    string = re.sub(r'\([^)]*\)', '', string)
    string = re.sub(r'[()]', '', string)

    return string


def preprocess(string, values, rev_dictionary):
    string = string.lower().replace('.', '')
    if '(' in string:
        string = remove_par(string)

    for value in values:
        pattern = r'\b{}\b'.format(value)
        string = re.sub(pattern, rev_dictionary[value], string)

    cleaning_func = [clean_X, clean_S]
    for idx, symbol in enumerate(['X', 'ул']):
        if symbol in string:
            string = cleaning_func[idx](string)

    return string.title()

def assess(df, name, idx, sample=500):
    assert idx < (len(df) - sample), 'number is too big'
    string = df.loc[idx]
    cost_func = lambda x: levenshtein(x, string[name])
    subset = df.loc[idx+1:idx+sample+1]
    new_score = subset[name].apply(cost_func).sum()
    return new_score 


########################################


class GA:
    def __init__(self, df, mutations=clean_mutations, pop_size = 4):
        self.df = df.copy()
        self.current_settings = None
        self.population = None
        self.pop_size = pop_size
        self.results = []

        self.muts = mutations.copy()

        self.possibilities = {}
        for key in self.muts.keys():
            self.possibilities.update({key: len(self.muts[key])})
        self.possibilities.update({'restriction': 4})

        self.create_population()

        self.restrictions = ['D', 'R', 'C']
    
    def pop_restirctions(self, string):
        restriction_lvl = self.current_settings['restriction']
        vector = string.split(',')
        indices = []
        for element in self.restrictions[:restriction_lvl]:
            for idx, part in enumerate(vector):
                if element in part:
                    indices.append(idx)
                    break
        indices = sorted(indices, reverse=True)
        for idx in indices:
            try:
                del vector[idx]
            except IndexError:
                pass
    
        return vector

    def apply_mut(self, vector):
        for idx, part in enumerate(vector):
            for key in self.current_settings.keys():
                if key in part:
                    replacement = self.muts[key][self.current_settings[key]]
                    vector[idx] = part.replace(key, replacement)

        return ','.join(vector).strip()
    

    def create_sample(self):
        sample = {}
        for key, value in self.possibilities.items():
            sample.update({key : np.random.randint(0,value)})

        return sample
    

    def create_population(self):
        self.population = [self.create_sample()]

        while len(self.population) != self.pop_size:
            sample = self.create_sample()
            unique = True

            for element in self.population:
                if list(element.values()) == list(sample.values()):
                    unique == False
                    break

            if unique:
                self.population.append(sample)

    
    def forward(self):
        for idx, sample in enumerate(self.population):
            self.current_settings = sample
            name = 'result' + str(idx)
            self.df[name] = self.df['raw'].apply(
                lambda x: self.apply_mut(self.pop_restirctions(x)))
    
    def get_scores(self):
        for name in self.df.columns[3:]:
            score = assess(self.df, name, 100)
            self.results.append(score)

    def mix(self, parent1, parent2):
        child = self.create_sample()
        for key in self.population[0].keys():
            var = np.random.randint(0,100)
            if var < 85:
                continue
            elif var < 90:
                child[key] = parent1[key]
                break
            elif var < 95:
                child[key] = parent2[key]
                break
            elif var < 101:
                child[key] = np.random.randint(0, self.possibilities[key])
                break
        
        return child
    
    
    def select_parents(self):
        parents_num = self.pop_size // 2
        sorted_res = sorted(self.results)
        indices = [self.results.index(value) for value in sorted_res[:parents_num]]
        new_population = [self.population[indices[0]]]
        for _ in range(self.pop_size - 1):
            parents = np.random.choice(indices, 2, replace=False)
            parent1 = min(parents)
            parent2 = max(parents)
            child = self.mix(self.population[parent1], self.population[parent2])

            new_population.append(child)
        
        self.population = new_population
        self.results = []














            






