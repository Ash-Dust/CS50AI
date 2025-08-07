import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines

    
class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells       #if all cells are mines, return all cells
        return set()                #return if no mines are known
        raise NotImplementedError   

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells       #if count is 0, all cells are safe
        return set()                #return if no safe cells are known
        raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:          #if the cell is in the set of cells
            self.cells.remove(cell)     #remove the cell from the set of cells
            self.count -= 1             #decrease the count of mines by 1
        if self.count < 0:              #if the count is negative, raise an error
            raise ValueError("Count cannot be negative after marking a mine.")          
      

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)  #if the cell is in the set of cells, remove it
        # No need to change count, as it only counts mines

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)                # Add the cell to the set of mines
        for sentence in self.knowledge:     # Iterate through all sentences in knowledge to mark the cell as a mine
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)                # Add the cell to the set of safes
        for sentence in self.knowledge:     # Iterate through all sentences in knowledge to mark the cell as safe
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        
        # 1) Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) Mark the cell as safe
        self.mark_safe(cell)

        # 3) Add a new sentence to the AI's knowledge base
        # based on the value of `cell` and `count`
        neighbors = set()
        for i in range(cell[0] - 1, cell[0] + 2):   # Loop through all neighboring cells
            for j in range(cell[1] - 1, cell[1] + 2):   
                if (i, j) != cell and 0 <= i < self.height and 0 <= j < self.width: # Ensure the cell is not the one clicked and is within bounds
                    neighbors.add((i, j))   # Collect all neighboring cells
        new_sentence = Sentence(neighbors, count)  
        self.knowledge.append(new_sentence)  # Add the new sentence to the knowledge base   
        
        # 4) Mark any additional cells as safe or mines if it can be concluded
        #If, based on any of the sentences in self.knowledge, new cells can be marked as safe or as mines, then the function should do so.
        for sentence in self.knowledge.copy():  # Use copy to avoid modifying the list while iterating
            # Mark known mines
            for mine in sentence.known_mines().copy():
                self.mark_mine(mine)
            
            # Mark known safes
            for safe in sentence.known_safes().copy():
                self.mark_safe(safe)
        #[print the mine and safe cells for debugging purposes red color]
        # Red for mines
        print(f"\033[91mMines: {self.mines}\033[0m")

        # Remaining safe moves (not yet played)
        remaining_safes = self.safes - self.moves_made

        # Print only the remaining safe moves in green
        print(f"\033[92mSafe moves left: {remaining_safes}\033[0m")


        
        # After marking known mines and safes, we should also check if any sentences can be simplified
        self.knowledge = [s for s in self.knowledge if s.cells]  # Remove empty sentences
        # This line ensures that we only keep sentences that still have cells left in them
        # If a sentence has no cells left, it is no longer useful and can be removed
        # Also, we can remove sentences that have a count of 0 and no cells left
        self.knowledge = [s for s in self.knowledge if s.count > 0
                        or (s.count == 0 and s.cells)]  
        # 5) Add any new sentences to the AI's knowledge base if they can be inferred
        # Note that any time that you make any change to your AI’s knowledge, it may be possible to draw new inferences that weren’t possible before. Be sure that those new inferences are added to the knowledge base if it is possible to do so.
        new_knowledge = []
        for sentence in self.knowledge:
            if sentence not in new_knowledge:
                new_knowledge.append(sentence)  # Add the sentence to new_knowledge if it is not already present
        self.knowledge = new_knowledge  
        # Check for new sentences that can be inferred from existing knowledge
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 != sentence2:
                    # If sentence1 is a subset of sentence2, create a new sentence
                    if sentence1.cells.issubset(sentence2.cells):
                        inferred_cells = sentence2.cells - sentence1.cells
                        inferred_count = sentence2.count - sentence1.count
                        if inferred_cells and inferred_count >= 0:
                            new_sentence = Sentence(inferred_cells, inferred_count)
                            if new_sentence not in self.knowledge:
                                self.knowledge.append(new_sentence)

    
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
            
        return None  # No safe moves available
        raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        choices = [
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
            if (i, j) not in self.moves_made and (i, j) not in self.mines
        ]
        if choices:
            return random.choice(choices)
        return None
