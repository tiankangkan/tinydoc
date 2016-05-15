import copy


class LayoutLabel(object):
    CHAR = 'CHAR'
    CHAR_ATOM = 'CHAR_ATOM'
    SPACING = 'SPACING'
    CHAR_SPACING = 'CHAR_SPACING'
    TEXT_LINE = 'TEXT_LINE'
    TEXT_LINE_SPACING = 'TEXT_LINE_SPACING'
    TEXT = 'TEXT'
    LAYOUT_LINEAR = 'LAYOUT_LINEAR'
    LAYOUT = 'LAYOUT'

    @property
    def spacing_label_list(self):
        return [self.CHAR_SPACING, self.TEXT_LINE_SPACING, self.SPACING]

    @property
    def atom_label_list(self):
        return [self.CHAR_ATOM]

    @property
    def frame_label_list(self):
        return [self.LAYOUT, self.LAYOUT_LINEAR, self.TEXT, self.TEXT_LINE, self.CHAR]


class LayoutSignal(object):
    NORMAL = 'NORMAL'
    OUT_OF_SPACE = 'OUT_OF_SPACE'


class LayoutAlign(object):
    H_CENTER = 'H_CENTER'
    H_LEFT = 'H_LEFT'
    H_RIGHT = 'H_RIGHT'
    V_CENTER = 'V_CENTER'
    V_LEFT = 'V_LEFT'
    V_RIGHT = 'V_RIGHT'

    def __init__(self, h_align=H_CENTER, v_align=V_CENTER):
        self.h_align = h_align
        self.v_align = v_align


class Direction(object):
    TO_TOP = 0
    TO_RIGHT = 1
    TO_BOTTOM = 2
    TO_LEFT = 3

    name_mapping = {
        0: 'TO_TOP',
        1: 'TO_RIGHT',
        2: 'TO_BOTTOM',
        3: 'TO_LEFT',
    }

    def __init__(self, direction):
        if direction not in (0, 1, 2, 3):
            raise
        self.direction = direction

    def __str__(self):
        return self.name_mapping[self.direction]

    def __neg__(self):
        dire = (self.direction + 2) % 4
        return Direction(direction=dire)

    @property
    def is_horizontal(self):
        return self.direction in (self.TO_LEFT, self.TO_RIGHT)

    @property
    def is_vertical(self):
        return self.direction in (self.TO_BOTTOM, self.TO_TOP)

    def same(self):
        return copy.deepcopy(self)

    def reversed(self):
        return -self

    def add(self):
        dire = (self.direction + 1) % 4
        return Direction(direction=dire)

    def sub(self):
        dire = (self.direction - 1) % 4
        return Direction(direction=dire)

    def parallel_with(self, direction):
        return direction in (self.reversed(), self.same())

    def vertically_with(self, direction):
        return direction in (self.add(), self.sub())


class Area(object):
    def __init__(self, rect=None):
        self.rect = rect

    def __str__(self):
        return str(self.rect)

    def copy(self):
        return copy.deepcopy(self)
