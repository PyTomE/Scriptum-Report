"""Task definitions for RDF report parsing."""

from ..values import Value

count_string = '_c%03d'


class ReportTask:
    """A task is mostly one line in a rdf file with an instruction what to do."""

    # get a list of all already existing tasks to be able to get
    # a serial and new naming in case of duplicates
    _serial = 0
    _tree = {}  # list of dicts of dicts of dicts...
    _allPaths = {}
    _newPaths = {}
    _debug = False

    @classmethod
    def set_debug(cls, enabled: bool) -> None:
        """Enable or disable debug output for inspections."""

        cls._debug = bool(enabled)

    def __init__(self, root=[], line: str = '', settings={}, **modifier):
        """Create a new task.

        Args:
            root: list of strings from _currentroot in ReportDataFile.
            line: string with the line always as 'key=value'.
            settings: dict with configuration options.
            modifier: optional modifiers like what/where/actions.
        """

        # just a counter for each element
        ReportTask._serial += 1
        self.serial = ReportTask._serial
        
        #self.newPath = None
        path, value = line.split('=', 1)
        path = path.lower().strip().split('.')  # creates a list of strings to be appended to root

        # target is the last element before the '='
        # never more than one target with same name in the same section!
        self.target = path[-1]
        # path is usually empty or the rest between root and target
        path = path[:-1]
        value = value.strip()  # value is everything behind the '='

        self.path = root[:]  # copy
        if path:
            self.path += path

        # required for TaskGroup class only
        self.length = 1

        # further evaluate value
        self.value = Value(value, settings, target=self.target.split(':')[0])

        self.what = ''
        self.where = ''
        self.actions = {}
        self.copyifrequired = False

        # mods on that object
        if modifier:
            self.modified = True
            self.what = modifier.get('what', '')
            self.where = modifier.get('where', '')
            self.actions = modifier.get('actions', {})
            self.copyifrequired = modifier.get('ifrequired', False)
            if self.actions:
                # can be used, e.g. in tables
                self.value.applyActions(self.actions)
        else:
            self.modified = False

        # this can be either a section (namespace) == copy or a + == add
        # thus chance is high to have multiple of these inside and a
        # numbering is required. Mostly for docx

        targetPath = self.path
        if self.target:
            targetPath += [self.target]

        self.checkPath(targetPath)

        #if self.path[-1] != self.myAddress[-1]:
        # define rewritten, new target
        if self.target:
            self.finaltarget = self.myAddress[-1]

    def checkPath(self, targetPath):
        """Check if that path exists already in Class._tree."""

        subtree = ReportTask._tree
        rootname = []  # root
        subcount = 0
        for tp in targetPath[:-1]:
            if tp in subtree:
                subname, _, subtree = subtree[tp]
            else:
                subtree[tp] = [tp, 1, {}]
                subname, _, subtree = subtree[tp]
            rootname += [subname]
        # last element
        tp = targetPath[-1]
        if tp in subtree:
            subname, subcount, _ = subtree[tp]
            subcount += 1
            subname = f'{tp}_c{subcount:03d}'
            subtree[tp] = [subname, subcount, {}]
        else:
            subtree[tp] = [tp, 1, {}]
            subname, _, _ = subtree[tp]
        rootname += [subname]

        self.myAddress = rootname

        # record duplicate paths
        fullpath = '.'.join(targetPath)
        if fullpath in ReportTask._allPaths:
            ReportTask._newPaths.setdefault(fullpath, []).append('.'.join(rootname))
        else:
            ReportTask._allPaths[fullpath] = '.'.join(rootname)

        if self.copyifrequired:
            # remove the copy attribute from self.what when myAdress and path are the same
            # this will not work with PPTX but is required for DOCX!!!
            #print('difference', self.myAddress, self.path)
            # we have to check only the last element as the intermediate element should have been added anyhow?
            # @TODO verify that nothing is lost in complex structures
            if self.myAddress[-1] == self.path[-1]:
                if self.what == 'copy':
                    self.what = 'apply'

    def __repr__(self) -> str:
        rval = '   ' + '.'.join(self.path) + ' = ' + self.value.__repr__()
        if self.modified:
            rval += f"\n     +-> modified: what = {self.what}; where = {self.where}; actions = {self.actions}"

        if self.myAddress != self.path:
            rval += f"\n     +-> new (full) path: {'.'.join(self.myAddress)}"
        return rval

    def _inspect(self):
        r = {
            'number': self.serial,
            'path': self.path,
            'value': self.value,
            'address': self.myAddress,
        }
        if self.target:
            r['target'] = self.target
        if ReportTask._debug:
            r['modified'] = self.modified
        if self.modified:
            r['what'] = self.what
            if self.where:
                r['where'] = self.where
            if self.actions:
                r['actions'] = self.actions
        #if self.newPath:
        #    r['newPath'] = self.newPath

        return r

    @property
    def getPath(self):
        #if self.newPath:
        #    return self.newPath
        #else:
        return self.path
