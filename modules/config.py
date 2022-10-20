# Copyright (c) 2022 Adriano Angelone
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the
# Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import os




# subclass of Exception associated to errors in config loading
class ConfigError(Exception):
    pass




class config:
    def __init__(self, config_file: str):
        self.tstr = ''
        self.tdict = {}

        if (os.path.exists(config_file)):
            self.load_config(config_file)
        else:
            self.create_config(config_file)


    def add_category(self, letter: str, description: str):
        if (letter in self.tstr):
            raise ConfigError('duplicate type {}'.format(letter))

        tlist = sorted(self.tstr + letter)
        self.tstr = ''.join(tlist)
        self.tdict[letter] = description


    def remove_category(self, letter: str):
        self.tstr = self.tstr.replace(letter, '')
        self.tdict.pop(letter)


    def create_config(self, config_file: str):
        self.path = 'data/expenses.sqlite'
        self.tstr = 'EHINR'
        self.tdict = {
                'E': 'Extra (voluptuary)',
                'H': 'House expenses (rent...)',
                'I': 'Income',
                'N': 'Necessary',
                'R': 'Refundable'
        }

        self.save_config(config_file)


    def load_config(self, config_file: str):
        with open(config_file, 'r') as f:
            self.path = f.readline().replace('\n', '')

            for line in f:
                letter = line[0]
                description = line[3:].replace('\n', '')
                self.add_category(letter, description)
        
            f.close()


    def save_config(self, config_file: str):
        with open(config_file, 'w') as f:
            f.write(self.path + '\n')

            for (l,d) in self.tdict.items():
                f.write('{}: {}\n'.format(l,d))
        
            f.flush()
            f.close()
