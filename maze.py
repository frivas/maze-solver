from tkinter import Tk, BOTH, Canvas
import time
import random
import sys
from typing import Optional


class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y


class Line:
    def __init__(self, point1: Point, point2: Point) -> None:
        self.point1 = point1
        self.point2 = point2

    def draw(self, canvas: Canvas, fill_color: str) -> None:
        canvas.create_line(self.point1.x, self.point1.y,
                           self.point2.x, self.point2.y, fill=fill_color, width=2)
        canvas.pack(fill=BOTH, expand=1)


class Window:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.__root_widget = Tk('Maze Solver', 'Maze')
        self.__root_widget.title('Maze Solver - Boot.dev')
        self.__root_widget.protocol('WM_DELETE_WINDOW', self.close)
        self.__canvas = Canvas(
            self.__root_widget, bg='white', height=height, width=width)
        self.__canvas.pack(fill=BOTH, expand=1)
        self.__isRunning = False

    def redraw(self) -> None:
        self.__root_widget.update_idletasks()
        self.__root_widget.update()

    def wait_for_close(self) -> None:
        self.__isRunning = True
        while self.__isRunning:
            self.redraw()

    def draw_line(self, line: Line, fill_color: str) -> None:
        line.draw(self.__canvas, fill_color)

    def close(self) -> None:
        self.__isRunning = False


class Cell:
    def __init__(self, win: Optional[Window] = None) -> None:
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self.top_left_corner = Point(0.0, 0.0)
        self.bottom_right_corner = Point(0.0, 0.0)
        self._win = win
        self.visited = False

    def draw(self, top_left_corner: Point, bottom_right_corner: Point) -> None:
        if self._win is None:
            return
        x1 = top_left_corner.x
        y1 = top_left_corner.y
        x2 = bottom_right_corner.x
        y2 = bottom_right_corner.y

        if self.has_left_wall:
            left_wall = Line(Point(x1, y1), Point(x1, y2))
            self._win.draw_line(left_wall, 'black')
        else:
            left_wall = Line(Point(x1, y1), Point(x1, y2))
            self._win.draw_line(left_wall, 'white')

        if self.has_right_wall:
            right_wall = Line(Point(x2, y1), Point(x2, y2))
            self._win.draw_line(right_wall, 'black')
        else:
            right_wall = Line(Point(x2, y1), Point(x2, y2))
            self._win.draw_line(right_wall, 'white')

        if self.has_top_wall:
            top_wall = Line(Point(x1, y1), Point(x2, y1))
            self._win.draw_line(top_wall, 'black')
        else:
            top_wall = Line(Point(x1, y1), Point(x2, y1))
            self._win.draw_line(top_wall, 'white')

        if self.has_bottom_wall:
            bottom_wall = Line(Point(x1, y2), Point(x2, y2))
            self._win.draw_line(bottom_wall, 'black')
        else:
            bottom_wall = Line(Point(x1, y2), Point(x2, y2))
            self._win.draw_line(bottom_wall, 'white')

    def draw_move(self, to_cell, undo=False):
        if self._win is None:
            return
        x1 = self.top_left_corner.x
        y1 = self.top_left_corner.y

        x2 = self.bottom_right_corner.x
        y2 = self.bottom_right_corner.y

        to_cell_x1 = to_cell.top_left_corner.x
        to_cell_y1 = to_cell.top_left_corner.y

        to_cell_x2 = to_cell.bottom_right_corner.x
        to_cell_y2 = to_cell.bottom_right_corner.y

        x_center = (x1 + x2) / 2
        y_center = (y1 + y2) / 2

        to_cell_x_center = (to_cell_x1 + to_cell_x2) / 2
        to_cell_y_center = (to_cell_y1 + to_cell_y2) / 2

        fill_color = 'red' if undo else 'gray'

        # Apply when moving left
        if x1 > to_cell_x1:
            line = Line(Point(x1, y_center), Point(x_center, y_center))
            self._win.draw_line(line, fill_color)
            line = Line(Point(to_cell_x_center, to_cell_y_center),
                        Point(to_cell_x2, to_cell_y_center))
            self._win.draw_line(line, fill_color)

        # Apply when moving right
        if x1 < to_cell_x1:
            line = Line(Point(x_center, y_center), Point(x2, y_center))
            self._win.draw_line(line, fill_color)
            line = Line(Point(to_cell_x1, to_cell_y_center),
                        Point(to_cell_x_center, to_cell_y_center))
            self._win.draw_line(line, fill_color)

        # Apply when moving up
        if y1 > to_cell_y1:
            line = Line(Point(x_center, y_center), Point(x_center, y1))
            self._win.draw_line(line, fill_color)
            line = Line(Point(to_cell_x_center, to_cell_y2),
                        Point(to_cell_x_center, to_cell_y_center))
            self._win.draw_line(line, fill_color)

        # Apply when moving down
        if y1 < to_cell_y1:
            line = Line(Point(x_center, y_center), Point(x_center, y2))
            self._win.draw_line(line, fill_color)
            line = Line(Point(to_cell_x_center, to_cell_y_center),
                        Point(to_cell_x_center, to_cell_y1))
            self._win.draw_line(line, fill_color)


class Maze:
    def __init__(self, x1, y1, num_rows, num_cols, cell_size_x, cell_size_y, win: Optional[Window] = None, seed: Optional[int] = None) -> None:
        self._x1 = x1
        self._y1 = y1
        self._num_rows = num_rows
        self._num_cols = num_cols
        self._cell_size_x = cell_size_x
        self._cell_size_y = cell_size_y
        self._win = win
        self._cells = []
        self.seed = seed

        if seed:
            random.seed(seed)

        self._create_cells()
        self._break_entrance_and_exit()
        self._break_walls_r(0, 0)
        self._reset_cell_visited()

    def _create_cells(self):
        for i in range(self._num_cols):
            col_cells = []
            for j in range(self._num_rows):
                col_cells.append(Cell(self._win))
            self._cells.append(col_cells)

        for i in range(self._num_cols):
            for j in range(self._num_rows):
                self._draw_cell(i, j)

    def _draw_cell(self, i, j):
        if self._win is None:
            return
        x1 = self._x1 + i * self._cell_size_x
        y1 = self._y1 + j * self._cell_size_y
        x2 = x1 + self._cell_size_x
        y2 = y1 + self._cell_size_y
        self._cells[i][j].draw(Point(x1, y1), Point(x2, y2))
        self._animate()

    def _animate(self):
        if self._win is None:
            return
        self._win.redraw()
        time.sleep(0.01)

    def _break_entrance_and_exit(self):
        self._cells[0][0].has_top_wall = False
        self._draw_cell(0, 0)
        self._cells[self._num_cols - 1][self._num_rows -
                                        1].has_bottom_wall = False
        self._draw_cell(self._num_cols - 1, self._num_rows - 1)

    def _break_walls_r(self, i, j):
        self._cells[i][j].visited = True
        while True:
            next_index_list = []
            if i > 0 and not self._cells[i-1][j].visited:
                next_index_list.append((i-1, j))
            if i < self._num_cols - 1 and not self._cells[i+1][j].visited:
                next_index_list.append((i+1, j))
            if j > 0 and not self._cells[i][j-1].visited:
                next_index_list.append((i, j-1))
            if j < self._num_rows - 1 and not self._cells[i][j+1].visited:
                next_index_list.append((i, j+1))
            if len(next_index_list) == 0:
                self._draw_cell(i, j)
                return
            direction_index = random.randrange(len(next_index_list))
            next_index = next_index_list[direction_index]

            if next_index[0] == i + 1:
                self._cells[i][j].has_right_wall = False
                self._cells[i+1][j].has_left_wall = False
            if next_index[0] == i - 1:
                self._cells[i][j].has_left_wall = False
                self._cells[i-1][j].has_right_wall = False
            if next_index[1] == j + 1:
                self._cells[i][j].has_bottom_wall = False
                self._cells[i][j+1].has_top_wall = False
            if next_index[1] == j - 1:
                self._cells[i][j].has_top_wall = False
                self._cells[i][j-1].has_bottom_wall = False

            self._break_walls_r(next_index[0], next_index[1])

    def _reset_cell_visited(self):
        for col in self._cells:
            for cell in col:
                cell.visited = False

    def _solve_r(self, i, j):
        self._animate()

        self._cells[i][j].visited = True

        if i == self._num_cols - 1 and j == self._num_rows - 1:
            return True

        if (
            i > 0
            and not self._cells[i][j].has_left_wall
            and not self._cells[i - 1][j].visited
        ):
            self._cells[i][j].draw_move(self._cells[i - 1][j])
            if self._solve_r(i - 1, j):
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i - 1][j], True)

        if (
            i < self._num_cols - 1
            and not self._cells[i][j].has_right_wall
            and not self._cells[i + 1][j].visited
        ):
            self._cells[i][j].draw_move(self._cells[i + 1][j])
            if self._solve_r(i + 1, j):
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i + 1][j], True)

        # move up if there is no wall and it hasn't been visited
        if (
            j > 0
            and not self._cells[i][j].has_top_wall
            and not self._cells[i][j - 1].visited
        ):
            self._cells[i][j].draw_move(self._cells[i][j - 1])
            if self._solve_r(i, j - 1):
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i][j - 1], True)

        # move down if there is no wall and it hasn't been visited
        if (
            j < self._num_rows - 1
            and not self._cells[i][j].has_bottom_wall
            and not self._cells[i][j + 1].visited
        ):
            self._cells[i][j].draw_move(self._cells[i][j + 1])
            if self._solve_r(i, j + 1):
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i][j + 1], True)

        # we went the wrong way let the previous cell know by returning False
        return False

    def solve(self):
        return self._solve_r(0, 0)


def main():
    num_rows = 14
    num_cols = 20
    margin = 50
    screen_x = 800
    screen_y = 600
    cell_size_x = (screen_x - 2 * margin) / num_cols
    cell_size_y = (screen_y - 2 * margin) / num_rows

    sys.setrecursionlimit(10000)
    win = Window(screen_x, screen_y)

    maze = Maze(margin, margin, num_rows, num_cols,
                cell_size_x, cell_size_y, win, 10)
    is_solvable = maze.solve()
    if not is_solvable:
        print('Maze cannot be solved!')
    else:
        print("Maze Solved")
    win.wait_for_close()


main()
