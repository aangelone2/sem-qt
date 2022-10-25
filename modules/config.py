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



# configuration settings class: contains
# + database path (path)
# + expense type keys joined in a sorted string (tstr)
# + dictionary with type keys and explanations (tdict)
class config:

    # multiple constructors
    def __init__(self, filename: str = '', dic: dict[str] = {}):
        self.tstr = ''
        self.tdict = {}

        # loads config from file,
        # sets default and saves it to file if not existent
        # file should be in the format 'key: explanation'
        if (filename != ''):
            if (os.path.exists(filename)):
                self.load(filename)
            else:
                self.path = 'data/expenses.sqlite'
                self.set_default()

                self.save(filename)

        # dictionary constructor
        elif (dic != {}):
            self.path = 'data/expenses.sqlite'
            for k in dic:
                self.add(k, dic[k])


    # sets default values for the configuration class
    def set_default(self):
        self.tstr = 'EHINR'
        self.tdict = {
                'E': 'Extra (voluptuary)',
                'H': 'House expenses (rent...)',
                'I': 'Income',
                'N': 'Necessary',
                'R': 'Refundable'
        }


    # creates a new category from key and description:
    # keys must be of length 1 and non-repeating
    def add(self, key: str, description: str):
        if (len(key) != 1):
            raise ConfigError('invalid type {}'.format(k))

        if (key in self.tstr):
            raise ConfigError('duplicate type {}'.format(key))

        tlist = sorted(self.tstr + key)
        self.tstr = ''.join(tlist)
        self.tdict[key] = description


#    # removes a category defined by its key
#    def remove(self, key: str):
#        self.tstr = self.tstr.replace(key, '')
#        self.tdict.pop(key)


    # loads the configuration from the given file
    # file should be in the format 'key: explanation'
    def load(self, config_file: str):
        with open(config_file, 'r') as f:
            self.path = f.readline().replace('\n', '')

            for line in f:
                key = line[0]
                description = line[3:].replace('\n', '')
                self.add(key, description)

            f.close()


    # saves to file as 'key: explanation'
    def save(self, config_file: str):
        with open(config_file, 'w') as f:
            f.write(self.path + '\n')

            for (l,d) in self.tdict.items():
                f.write('{}: {}\n'.format(l,d))
        
            f.flush()
            f.close()
