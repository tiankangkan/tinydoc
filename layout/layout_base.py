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
    TO_RIGHT = 'TO_RIGHT'
    TO_LEFT = 'TO_LEFT'
    TO_TOP = 'TO_TOP'
    TO_BOTTOM = 'TO_BOTTOM'

    def __init__(self, direction):
        self.direction = direction

    def __neg__(self):
        if self.direction == self.TO_BOTTOM:
            direction = self.TO_TOP
        elif self.direction == self.TO_TOP:
            direction = self.TO_BOTTOM
        elif self.direction == self.TO_LEFT:
            direction = self.TO_RIGHT
        elif self.direction == self.TO_RIGHT:
            direction = self.TO_LEFT
        else:
            raise ValueError('Wrong direction: %s' % self.direction)
        return Direction(direction=direction)

    @property
    def is_horizontal(self):
        return self.direction in (self.TO_LEFT, self.TO_RIGHT)

    @property
    def is_vertical(self):
        return self.direction in (self.TO_BOTTOM, self.TO_TOP)


class Area(object):
    def __init__(self, rect=None):
        self.rect = rect

    def __str__(self):
        return str(self.rect)

    def copy(self):
        return copy.deepcopy(self)
