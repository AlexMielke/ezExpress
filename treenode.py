# ----------------------------------------------------------------------------------------------------------------- #
# ---  ezExpress v1.0.6                                                                                         --- #
# ---                                                                                                           --- #
# ---  Modul : treenode                                                                                         --- #
# ---                                                                                                           --- #
# ---  Ausgelagerte Methode zur Erstellung eines Produktkataloges mit Hilfe einer Baumstruktur                  --- #
# ---                                                                                                           --- #
# ---                                                                                                           --- #
# ---  Beispiel:                                                                                                --- #
# ---                                                                                                           --- #
# ---  Produkte  |-->  Getränke                                                                                 --- #
# ---            |       |                                                                                      --- #
# ---            |       |-->     Soft Drinks (mit Artikelliste)                                                --- #
# ---            |       |                                                                                      --- #
# ---            |       |-->     Kaffee/Tee (mit Artikelliste)                                                 --- #
# ---            |                                                                                              --- #
# ---            |                                                                                              --- #
# ---            |-->  Tiefkühl                                                                                 --- #
# ---            |       |                                                                                      --- #
# ---            |       |-->     Gemüse (mit Artikelliste)                                                     --- #
# ---            |                                                                                              --- #
# ---            |                                                                                              --- #
# ---            |-->  Pflege (mit Artikelliste)                                                                --- #
# ---                                                                                                           --- #
# ---                                                                                                           --- #
# ---  Das Modul wurde in Python (Version 3.8.6) geschrieben.                                                   --- #
# ---                                                                                                           --- #
# ---  Lizenzinformation:                                                                                       --- #
# ---                                                                                                           --- #
# ---  Das Programm ezExpress wird under der Apache License, Version 2.0 veröffentlicht.                        --- #
# ---  (http://www.apache.org/licenses/LICENSE-2.0.html)                                                        --- #
# ---                                                                                                           --- #
# ---  Bei Fragen, gefundenen Fehlern oder Verbesserungsvorschlägen bitte eine Email schreiben.                 --- #
# ---                                                                                                           --- #
# ---  mailto: alexandermielke@t-online.de                                                                      --- #
# ---                                                                                                           --- #
# ---  Alexander Mielke, November 2020                                                                          --- #
# ---                                                                                                           --- #
# ----------------------------------------------------------------------------------------------------------------- #

############################### Global Variable ############################
anzliste = []

############################### Class: TreeNode ############################


class TreeNode:
    def __init__(self, index, data):
        self.index = index
        self.data = data
        self.aufgeklappt = True
        self.liste = []
        self.children = []
        self.parent = None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def get_level(self):
        level = 0
        p = self.parent
        while p:
            level += 1
            p = p.parent
        return level

    def is_empty(self):
        yo = False if self.parent or self.children else True
        return yo

    def is_index(self, index):
        Node = self.find_indexnode(index)
        if Node:
            return True
        else:
            return False

    def make_list(self):
        global anzliste
        spaces = ' ' * (self.get_level()-1) * 8
        if self.children:
            pfeil = '□  ' if self.aufgeklappt else '■  '
        else:
            pfeil = '    '
        if self.parent:
            prefix = (spaces + pfeil)
        else:
            prefix = ''
        if (type(self.data) == str) and self.parent:
            zeile = prefix + self.data
            anzliste.append([self.index, zeile])
        if self.children and self.aufgeklappt:
            for child in self.children:
                child.make_list()

    def get_list(self):
        global anzliste
        self.make_list()
        catalog = anzliste
        anzliste = []
        return catalog

    def find_indexnode(self, index):
        if self.index == index:
            return self
        else:
            for child in self.children:
                node = child.find_indexnode(index)
                if node:
                    if node.index == index:
                        return node

    def delete_node(self, node):
        if self == node:
            if self.parent:
                self.parent.children.remove(node)
        else:
            for child in self.children:
                node2 = child.delete_node(node)
                if node2:
                    if node2 == node:
                        return node2

    def delete_index(self, index):
        self.delete_node(self.find_indexnode(index))

    def add_sibling(self, sibling):
        if self.parent:
            self.parent.add_child(sibling)
        else:
            self.add_child(sibling)

    def is_leaf(self):
        return (self.children == [])

    def sort_Tree(self, Node):
        if Node.children:
            Node.children.sort(key=lambda element: element.data.upper())
            for child in Node.children:
                child.sort_Tree(child)

    def sort_list(self):
        # Entferne leere Zeilen ohne Artikelbezeichnung
        neue_liste = []
        for i in range(len(self.liste)):
            if self.liste[i][0] != '':
                neue_liste.append(self.liste[i])

        neue_liste.sort(key=lambda element: element[0].upper())
        self.liste = neue_liste

    def move_node(self, node, direction):
        if direction == 'DOWN':
            index = node.parent.children.index(node)
            laenge = len(node.parent.children)
            if (laenge > 1) and (index < laenge-1):
                temp = node.parent.children[index]
                node.parent.children[index] = node.parent.children[index+1]
                node.parent.children[index+1] = temp

        elif direction == 'UP':
            index = node.parent.children.index(node)
            laenge = len(node.parent.children)
            if (laenge > 1) and (index > 0):
                temp = node.parent.children[index]
                node.parent.children[index] = node.parent.children[index-1]
                node.parent.children[index-1] = temp

    def print_tree(self):
        spaces = ' ' * (self.get_level()-1) * 6
        if self.children:
            pfeil = ' • '
        else:
            pfeil = ' ‣ '
        if self.parent:
            prefix = (spaces + pfeil)
        else:
            prefix = '• '
        if (type(self.data) == str) and self.parent:
            print(prefix + self.data + '  (' + str(self.index) + ')(Level = '+str(self.get_level())+')')
        if self.children:
            for child in self.children:
                child.print_tree()

############################## Internal Methods ############################


def build_tree():
    Kategorie = [['Getränke', ['Softdrinks', 'Wasser', 'Säfte', 'Kaffee, Tee & Kakao']],
                 ['Frische & Kühlung', ['Wurst', 'Käse',
                                        'Fleisch', 'Milchprodukte', 'Sonstiges']],
                 ['Tiefkühl', ['Fertiggerichte', 'Gemüse',
                               'Fisch & Fleisch', 'Eiscreme']],
                 ['Obst & Gemüse', ['Obst', 'Gemüse', 'Kräuter']],
                 ['Nahrungsmittel', ['Fertiggerichte', 'Nudeln, Reis', 'Backen',
                                     'Brot & Backwaren', 'Öl, Essig, Saucen', 'Frühstück', 'Sonstiges']],
                 ['Drogerie', ['Papierartikel', 'Gesundheit',
                               'Körperpflege', 'Sonstiges']],
                 ['Küche & Haushalt', ['Putzen & Reinigen', 'Waschen', 'Sonstiges']],
                 ['Sonstiges', ['Food', 'Non-Food']]]

    root = TreeNode(0, 'Produkte')
    for i in range(len(Kategorie)):
        gruppe = Kategorie[i][0]
        untergruppe = Kategorie[i][1]
        Node = TreeNode(i+1, gruppe)
        for j in range(len(untergruppe)):
            kid = TreeNode((i+1)*100+j+1, untergruppe[j])
            Node.add_child(kid)
        root.add_child(Node)
    return root


def save_tree(data):
    afile = open(r'Produktkatalog.epk', 'wb')
    pickle.dump(data, afile)
    afile.close()


def load_tree():
    afile = open(r'Produktkatalog.epk', 'rb')
    data = pickle.load(afile)
    afile.close()
    return data

#################################### Main ##################################


if __name__ == '__main__':
    pass
    # import pickle
    root = build_tree()
    # save_tree(root)
    root.print_tree()
    # print('Leeren Produktkatalog erstellt...')
