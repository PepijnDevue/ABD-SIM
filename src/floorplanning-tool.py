"""
This is a first concept for the GUI, in this concept the next steps of the simulation isnt't tested.
In this concept you can build a grid in which the simulation will take place, this grid can display the simulation(though not tested)
And the grid is saved so the simulation can also run in the console when the "go" butoon is pressed.
This concept can only run X*X gridsizes, so 10x10 or 30x30. To compensate for the growing gridsizes the user can choose the cell size.
"""
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QPushButton, QWidget, QTextEdit, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout
from PyQt6.QtCore import QSize

# Initialize constants
GRID_SIZE_X = 10  # Define gridsize length
GRID_SIZE_Y = 10  # Define gridsize width
CELL_SIZE = 40  # Define cell size in pixels

TILES = ['.', 'W', 'E']  # Possible tile states
"""
. = Empty
W = Wall
E = Entrance/Exit
"""
COLORS = {'.': 'white', 'W': 'black', 'E': 'green'} # Color of each state

class SimulationUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.GRID_SIZE_X = GRID_SIZE_X  # Set standard grid size
        self.GRID_SIZE_Y = GRID_SIZE_Y
        self.CELL_SIZE = CELL_SIZE

        # Initialize the grid with empty/white cells
        self.grid_data = [['.'] * self.GRID_SIZE_Y for _ in range(self.GRID_SIZE_X)]
        
        # Set outer tiles to 'W' (Wall) (black color)
        for i in range(self.GRID_SIZE_X):
            self.grid_data[i][0] = 'W'  # Left column
            self.grid_data[i][self.GRID_SIZE_Y - 1] = 'W'  # Right column
        for j in range(self.GRID_SIZE_Y):
            self.grid_data[0][j] = 'W'  # Top row
            self.grid_data[self.GRID_SIZE_X - 1][j] = 'W'  # Bottom row

        self.init_ui()

    def adjust_window_size(self):
        """
        To make it possible to input other numbers than the default 10 the window is dynamic,
        To accommodate the "go" button and to have some "pazass" there is a padding built in.
        """
        grid_width = self.GRID_SIZE_Y * self.CELL_SIZE
        grid_height = self.GRID_SIZE_X * self.CELL_SIZE
        self.setFixedSize(QSize(grid_width + 50, grid_height + 200)) # Addes extra pixels for some "pazass"

    def init_ui(self):
        """
        Initialize GUI, including the grid, console-preview and Go button
        """
        self.setWindowTitle("Mesa Simulation Editor") # Window titel
        self.adjust_window_size()

        # Initialize the window
        central_widget = QWidget() # Main container for the UI-elements
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        input_layout = QHBoxLayout()

        # Create labels and inputboxes for the grid parameters
        self.grid_size_x_label = QLabel("Length:")
        self.grid_size_y_label = QLabel("Width:")
        self.cell_size_label = QLabel("Tile Size In Px:")

        # Convert input to string because QLineEdit needs that
        self.grid_size_x_input = QLineEdit(str(self.GRID_SIZE_X))
        self.grid_size_y_input = QLineEdit(str(self.GRID_SIZE_Y))
        self.cell_size_input = QLineEdit(str(self.CELL_SIZE))

        # Connect inputdata with update_grid function
        self.grid_size_x_input.returnPressed.connect(self.update_grid)
        self.grid_size_y_input.returnPressed.connect(self.update_grid)
        self.cell_size_input.returnPressed.connect(self.update_grid)

        # Add the widgets to the window
        input_layout.addWidget(self.grid_size_x_label)
        input_layout.addWidget(self.grid_size_x_input)
        input_layout.addWidget(self.grid_size_y_label)
        input_layout.addWidget(self.grid_size_y_input)
        input_layout.addWidget(self.cell_size_label)
        input_layout.addWidget(self.cell_size_input)

        main_layout.addLayout(input_layout)

        # Add the update grid button
        self.update_grid_button = QPushButton("Update Grid")
        self.update_grid_button.clicked.connect(self.update_grid)
        main_layout.addWidget(self.update_grid_button)

        # Add text line to give the grid a name....like Fred
        self.grid_name_input = QLineEdit()
        self.grid_name_input.setPlaceholderText("Enter grid name...")
        main_layout.addWidget(self.grid_name_input)

        # Create the gridlayout with the tiles
        grid_layout = QGridLayout()
        self.buttons = []

        # Go through every row in the grid
        for row in range(self.GRID_SIZE_X):
            row_buttons = [] # Create empty list to store the tiles in the list
            
            # Go through every colomn corrisponding to that row
            for col in range(self.GRID_SIZE_Y):
                btn = QPushButton() # Create a tile for this cel
                
                # Set standard value for the cell, 
                # If it's an outer wall its a "w" or black, 
                # otherwise its a "." or white.
                btn.setFixedSize(self.CELL_SIZE, self.CELL_SIZE)
                btn.setStyleSheet(f"background-color: {COLORS[self.grid_data[row][col]]}")
                btn.clicked.connect(lambda checked, r=row, c=col: self.toggle_tile(r, c)) # Connect the press of the button with the "Toggle_title" function
                grid_layout.addWidget(btn, row, col)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

        main_layout.addLayout(grid_layout)

        # Add the console preview
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True) # Read only because you can't change it by using text, you have to use the buttons
        main_layout.addWidget(self.console_output)

        # Add the save button that outputs the current grid
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.start_simulation)
        main_layout.addWidget(self.save_button)

    # If the update grid button is pressed this function will activate and update the grid
    def update_grid(self):
        try:
            # Recieve the new grid values from the input boxes
            new_grid_size_x = int(self.grid_size_x_input.text())
            new_grid_size_y = int(self.grid_size_y_input.text())
            new_cell_size = int(self.cell_size_input.text())

            # If the values are different then the original ones, update the grid
            if new_grid_size_x != self.GRID_SIZE_X or new_grid_size_y != self.GRID_SIZE_Y or new_cell_size != self.CELL_SIZE:
                self.GRID_SIZE_X = new_grid_size_x
                self.GRID_SIZE_Y = new_grid_size_y
                self.CELL_SIZE = new_cell_size

                # Initialize the new grid
                self.grid_data = [['.'] * self.GRID_SIZE_Y for _ in range(self.GRID_SIZE_X)]
                
                # Recalculate the wall grids and set values to "W" or black
                for i in range(self.GRID_SIZE_X):
                    self.grid_data[i][0] = 'W'
                    self.grid_data[i][self.GRID_SIZE_Y - 1] = 'W'
                for j in range(self.GRID_SIZE_Y):
                    self.grid_data[0][j] = 'W'
                    self.grid_data[self.GRID_SIZE_X - 1][j] = 'W'

                # Delete and recreate the tiles in the grid
                self.buttons.clear()
                self.clearLayout(self.layout())
                self.init_ui()
        except ValueError:
            pass

    # When the update_grid calculations are done,
    # This function will delete the old tiles in the window and add the now ones.
    def clearLayout(self, layout):
        # Delete all widgets from the layout
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                else:
                    self.clearLayout(child.layout())

    def toggle_tile(self, row, col):
        """
        This function switches the tile position (row, col) to the next state in TILES.
        Also applies the color.
        """
        current_type = self.grid_data[row][col] # Gets current tilestate
        next_type = TILES[(TILES.index(current_type) + 1) % len(TILES)]  # Calculates next state from the list
        self.grid_data[row][col] = next_type  # Updates grid

        # Applies color of the tile
        self.buttons[row][col].setStyleSheet(f"background-color: {COLORS[next_type]}")  # Update de kleur
        self.update_console()

    def update_console(self):
        # Generate the JSON-style grid text
        grid_text = ',\n'.join([f"'{''.join(row)}'" for row in self.grid_data])  # Each row as a string
        json_output = f"{{'Unnamed_Grid': [\n{grid_text}\n]}}"
        
        # Display the JSON-style representation in the QTextEdit (console output)
        self.console_output.setText(json_output)

    def start_simulation(self):
        """
        Start the simulation, this function prints the grid state at the beginning
        and then runs the simulation, updating the grid accordingly.
        """
        # Generate the JSON-style grid text
        grid_text = ',\n'.join([f"'{''.join(row)}'" for row in self.grid_data])  # Each row as a string
        json_output = f"{{'Unnamed_Grid': [\n{grid_text}\n]}}"
        
        # Print the JSON-style representation in the console (QTextEdit)
        print(json_output)  # This prints to the real console
        

if __name__ == "__main__":
    app = QApplication([]) # Start the QT-window
    window = SimulationUI() # Create a simulation UI-instance
    window.show() # Show the window
    app.exec() # Start the event loop of the window
