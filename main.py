#!/usr/bin/python3

from PyQt5 import QtCore, QtWidgets, QtGui
from typing import List, Dict, Tuple
from Simplex import Simplex
from fractions import Fraction

def float2fraction(number):
    if type(number) == float:
        decimal: float = number % 1
        multiplier: int = 10 ** (len(str(decimal)) - 2)
        return Fraction(int(number * multiplier), multiplier)

    if type(number) == int:
        return Fraction(number, 1)

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.window_height, self.window_width = 400, 600
        font = QtGui.QFont()
        font.setPointSize(20)
        self.number_of_variables: int = 0
        self.number_of_constraints: int = 0
        self.child_window: Inputwidget = None

        # window style
        # self.resize(self.window_width, self.window_height)
        self.setWindowTitle("Simplex Algorithm")

        # header styling
        self.title = QtWidgets.QLabel("Simplex Algorithm", self)
        self.title.setFont(font)

        # style number of vars widgets
        self.var_number_lable = QtWidgets.QLabel("Number of Variables:", self)
        self.var_number_input = QtWidgets.QSpinBox(self)

        # style number of constraint widget
        self.var_constraint_label = QtWidgets.QLabel("Number of Constraints: ", self)
        self.var_constraint_input = QtWidgets.QSpinBox(self)

        # buttons
        self.generate_button = QtWidgets.QPushButton("Genereate", self)
        self.exit_button = QtWidgets.QPushButton("Exit", self)
        self.exit_button.clicked.connect(self.exit_app)
        self.generate_button.clicked.connect(self.get_user_input)

        # layout management
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.title)

        formgrid = QtWidgets.QFormLayout()
        formgrid.addRow(self.var_number_lable, self.var_number_input)
        formgrid.addRow(self.var_constraint_label, self.var_constraint_input)
        vbox.addLayout(formgrid)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.exit_button)
        hbox.addWidget(self.generate_button)

        vbox.addLayout(hbox)

        self.setLayout(vbox)

    # slot: exit app
    def exit_app(self):
        self.close()
        exit()

    # slot: get input
    def get_user_input(self):
        self.number_of_variables = int(self.var_number_input.text())
        self.number_of_constraints = int(self.var_constraint_input.text())

        self.child_window: Inputwidget = Inputwidget(self.number_of_variables, self.number_of_constraints)
        self.child_window.show()

class Inputwidget(QtWidgets.QWidget):
    def __init__(self, n: int, m: int):
        super().__init__()
        self.n: int = n  # Number of vars
        self.m: int = m  # Number of constraints
        self.nature: bool = False  # False for minimisation and true for maximisation
        self.a: List[List[float]] = list()  # matrix of constraints and coefficient
        self.boundry: List[float] = list()  # second memeber variables
        self.constraints: List[str] = list()  # constraints of the matrix
        self.objective_function = list()
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.solution_window: SolvingWidget = None
        self.setWindowTitle("Simplex Input")
        
        # Objective function layout
        func_layout = QtWidgets.QHBoxLayout()
        func_layout.addWidget(QtWidgets.QLabel("Objective Function: ", self))
        var_names: List[str] = ['x'+str(i) for i in range(1, n+1)]
        self.var_inputs: List[QtWidgets.QLineEdit] = list()
        for _ in range(self.n):
            input_box = QtWidgets.QLineEdit("0", self)
            input_box.setValidator(QtGui.QDoubleValidator())
            self.var_inputs.append(input_box)

        for name, input_box in zip(var_names, self.var_inputs):
            func_layout.addWidget(input_box)
            func_layout.addWidget(QtWidgets.QLabel(name, self), 1)

        # grid layout for matrix
        matrix_layout = QtWidgets.QGridLayout()
        self.input_matrix: List[List[QtWidgets.QLineEdit]] = list()
        self.b: List[QtWidgets.QLineEdit] = list()
        self.constraints_inputs: List[QtWidgets.QComboBox] = list()
        for i in range(self.m):
            input_line: List[QtWidgets.QLineEdit] = list()
            for j in range(self.n):
                var_input = QtWidgets.QLineEdit("0", self)
                var_input.setValidator(QtGui.QDoubleValidator())
                input_line.append(var_input)
            else:
                self.input_matrix.append(input_line)

            # add boundries input
            tmp_input: QtWidgets.QLineEdit = QtWidgets.QLineEdit("0", self)
            tmp_input.setValidator(QtGui.QDoubleValidator())
            self.b.append(tmp_input)

            # add constraint input
            tmp_combo = QtWidgets.QComboBox(self)
            tmp_combo.addItems(['<', '>', '='])
            self.constraints_inputs.append(tmp_combo)


        for i in range(self.m):
            for j in range(0, self.n):
                matrix_layout.addWidget(self.input_matrix[i][j], i, j)
            else:
                matrix_layout.addWidget(self.constraints_inputs[i], i, self.n + 1)
                matrix_layout.addWidget(self.b[i], i, self.n + 2)

        # probleme type
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(QtWidgets.QLabel("Problem Nature: ", self))
        self.problem_nature: QtWidgets.QComboBox = QtWidgets.QComboBox(self)
        self.problem_nature.addItems(['Minmisation', 'Maximisation'])
        hbox.addWidget(self.problem_nature)
        hbox.addStretch()

        # buttons: exit and solve
        button_layout = QtWidgets.QHBoxLayout()
        exit_button = QtWidgets.QPushButton("Exit", self)
        solve_button = QtWidgets.QPushButton("Solve", self)
        button_layout.addStretch()
        button_layout.addWidget(exit_button)
        button_layout.addWidget(solve_button)
        exit_button.clicked.connect(self.exit_app)
        solve_button.clicked.connect(self.solve_problem)

        self.main_layout.addLayout(func_layout)
        self.main_layout.stretch(1)
        self.main_layout.addLayout(hbox)
        self.main_layout.addWidget(QtWidgets.QLabel("Matrix"))
        self.main_layout.addLayout(matrix_layout)
        self.main_layout.addLayout(button_layout)
        self.setLayout(self.main_layout)

    # Slot: exit button
    def exit_app(self):
        self.close()

    # Slot: Solve problem
    def solve_problem(self):
        """Get input from user"""
        # reset all variables
        self.a = list()
        self.objective_function = list()
        self.boundry = list()
        self.constraints = list()

        # get matrix input
        for i in range(self.m):
            tmp_line: List[float] = []
            for j in range(self.n):
                inp: float = float(self.input_matrix[i][j].text())
                tmp_line.append(float2fraction(inp))
            else:
                # store line and get boundries values and constraints
                self.a.append(tmp_line)
                self.boundry.append(float2fraction(float(self.b[i].text())))
                constraint: str = str(self.constraints_inputs[i].currentText())
                if constraint == '>':
                    self.constraints.append('gt')
                elif constraint == '<':
                    self.constraints.append('lt')
                else:
                    self.constraints.append('eq')

        # get objective function value and problem nature
        for i in range(self.n):
            self.objective_function.append(float2fraction(float(self.var_inputs[i].text())))
        nature = int(self.problem_nature.currentIndex())
        self.nature = True if nature else False

        if self.verification():
            self.solution_window = SolvingWidget(
                self.n,
                self.m,
                self.a,
                self.boundry,
                self.constraints,
                self.objective_function,
                self.nature
            )
            self.solution_window.show()


    def verification(self):
        """Verfiey user input"""
        alert = QtWidgets.QMessageBox()
        alert.setIcon(QtWidgets.QMessageBox.Critical)
        alert.setWindowTitle("Error")


        if not any(self.objective_function):
            alert.setText("Objective function")
            alert.setInformativeText("Objective Function is empty!!!")
            alert.exec_()
            return False

        if any(list(filter(lambda x: True if x < 0 else False, self.boundry))):
            alert.setText("Boundries Error")
            alert.setInformativeText("All boundry should be positive.\nYou may wanna multiply be -1")
            alert.exec_()
            return False
        return True


class SolvingWidget(QtWidgets.QScrollArea):
    def __init__(self, n, m, a, b, constraints, objective_function, nature=False):
        super(SolvingWidget, self).__init__()
        self.solution = Simplex(n, m, a, b, constraints, [objective_function, 0], not nature)
        self.setWindowTitle("Simplex Solution")

        self.widget = QtWidgets.QWidget()  # main widget that contains content
        main_layout = QtWidgets.QVBoxLayout(self.widget)
        main_layout.addWidget(QtWidgets.QLabel("Solution"))

        phase1: List = self.solution.phase1_steps if self.solution.phase1_steps else False
        iteration: int = 1
        if phase1:
            for iteration_table in phase1:
                main_layout.addWidget(QtWidgets.QLabel(str(iteration)))
                iteration += 1
                main_layout.addWidget(self._construct_table(iteration_table))
        else:
            main_layout.addWidget(QtWidgets.QLabel("Phase One not needed !!!"))


        main_layout.addWidget(QtWidgets.QLabel("Phase Two"))
        iteration = 1
        phase2 = self.solution.phase2_steps if self.solution.phase2_steps else False
        if phase2:
            for iteration_table in phase2:
                main_layout.addWidget(QtWidgets.QLabel(str(iteration)))
                iteration += 1
                main_layout.addWidget(self._construct_table(iteration_table))
        else:
            main_layout.addWidget(QtWidgets.QLabel("No need for phase, you already on the optimal solution"))

        if len(self.solution.error_message):
            main_layout.addWidget(QtWidgets.QLabel(self.solution.error_message))
            print(self.solution.error_message)


        self.setWidget(self.widget)
        self.setWidgetResizable(True)
        self.showMaximized()

    def _construct_table(self, iteration_table):
        """Create table widget for solution"""
        n: int = len(iteration_table[0])
        m: int = len(iteration_table[1])

        table_widget = QtWidgets.QTableWidget(m + 1, n + 1, self.widget)
        table_widget.setHorizontalHeaderLabels(list( iteration_table[0] + ['Constraints']))
        table_widget.setVerticalHeaderLabels(iteration_table[1]+ ['costs'])

        for i in range(m):
            for j in range(n):
                table_widget.setItem(i, j, QtWidgets.QTableWidgetItem(str(iteration_table[2][i][j])))
            else:
                # Add constraints
                table_widget.setItem(i, n, QtWidgets.QTableWidgetItem(str(iteration_table[3][i])))
        else:
            # Add objective function coefficient
            for i in range(n):
                table_widget.setItem(m, i, QtWidgets.QTableWidgetItem(str(iteration_table[4][i])))
            else:
                table_widget.setItem(m, n, QtWidgets.QTableWidgetItem(str(iteration_table[5])))

        table_widget.setMinimumHeight(m * 50)
        return table_widget
    
    def close_window(self):
        self.solution = None
        self.close()

def main():
    app = QtWidgets.QApplication([])
    mainwindow = MainWindow()
    mainwindow.show()
    app.exec_()


if __name__ == '__main__':
    main()
