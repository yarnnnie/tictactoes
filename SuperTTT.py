from IPython.display import clear_output

class SuperTTT:
  def __init__(self):
    """Initializes the game board
       -1 is an empty space
        0 is an X
        1 is an O
        2 is a tie
    """

    self.board = [[-1 for i in range(9)] for j in range(9)]
    self.megaboard = [-1 for i in range(9)]
    self.icons=["x","◯","□"]
    self.in_notebook=True
    self.num_moves = 0

    # Bitboard looks like this
    # 0  1  2  9  10 11 18 19 20
    # 3  4  5  12 13 14 21 22 23
    # 6  7  8  15 16 17 24 25 26
    # 27 28 29 36 37 38 45 46 47
    # 30 31 32 39 40 41 48 49 50
    # 33 34 35 42 43 44 51 52 53
    # 54 55 56 63 64 65 72 73 74
    # 57 58 59 66 67 68 75 76 77
    # 60 61 62 69 70 71 78 79 80

    # Mega bitboard looks like this
    # 0  1  2
    # 3  4  5
    # 6  7  8


    #TODO: Add bitboards for player 1 and player 2
    self.player1_bitboard = 0
    self.player2_bitboard = 0

    self.player1_mega_bitboard = 0 # For player 1 wins
    self.player2_mega_bitboard = 0 # For player 2 wins
    self.tie_mega_bitboard = 0     # For ties

    self.player_1_turn = True

  def get_move(self):
    """Gets a move from the user
        Args:
            None
  
          Returns:
            move: (x: int, y: int) where x is the board number and y is the space number
            concede_flag: bool: True if the user wants to concede, False otherwise
    """
    move = None
    while self.check_valid_move(move) == False:
      move = input("Enter a move (or 9000 to concede): ")
      if move == "9000":
        return None, True
      move = move.split(" ")
      move = (int(move[0]), int(move[1]))
    
    return move, False
    


  def check_valid_move(self, move):
    """Checks if a move is valid or not
       Args:
          (x: int, y: int) where x is the board number and y is the space number

        Returns:
          bool: True if the move is valid, False otherwise
    """
    if move == None: # For starting
      return False
    
    board_num, position = move

    if (board_num < 0 or board_num > 8) or (position < 0 or position > 8): # Making sure move is actually on the board
      return False
    
    if self.megaboard[board_num] != -1: # Making sure the board is not already won
      return False
    
    # Bitboard implementation
    all_finished_boards = self.player1_mega_bitboard | self.player2_mega_bitboard | self.tie_mega_bitboard

    if (1 << board_num) & all_finished_boards != 0: # Checking if the board is already won
      return False
    
    if self.board[board_num][position] != -1: # Making sure the space is empty
      return False
    
    # Bitboard implementation
    all_moves = self.player1_bitboard | self.player2_bitboard # Bitwise OR of both bitboards to get all filled positions

    if (1 << (board_num * 9 + position)) & all_moves != 0: # Checking if the space is already filled
      return False
    
  def check_win(self, board):
        """Checks if the board is in a winning state
            Args:
                board: a 1D list of ints representing the board
  
              Returns:
                bool: True if the board is in a winning state, False otherwise
                int: 0 if player 1 won, 1 if player 2 won, 2 if tie

            For bitboard implementation:
            Args:
                board: An int with the board number or a "Mega"
            
            Returns:
                bool: True if the board is in a winning state, False otherwise
                int: 0 if player 1 won, 1 if player 2 won, 2 if tie

        
        """
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]]             # Diagonals
       
        for condition in win_conditions:
            if board[condition[0]] == board[condition[1]] == board[condition[2]] and board[condition[0]] != -1 and board[condition[0]] != 2:
                return True, board[condition[0]]
            if -1 not in board: #no empty cells & no win => draw
                return False, 2
        return False, None
  

        # TODO: Add bitboard implementation  
        # Bitboard implementation
        board_mask = 0b111111111 #Mask to get specific board

        horizontal_win = 0b000000111
        vertical_win = 0b1001001001
        tl_br_diagonal_win = 0b100010001
        tr_bl_diagonal_win = 0b001010100

        if board == "Mega":
          bitboard = self.player1_mega_bitboard if self.player_1_turn else self.player2_mega_bitboard

        else:
           bitboard = self.player1_bitboard if self.player_1_turn else self.player2_bitboard
           bitboard = bitboard & (board_mask << (board * 9)) # Masking to get specific board

           print(bitboard)
        
        # Win conditions
        for offset in range(3):
          if (bitboard & (horizontal_win << (offset * 3))) == horizontal_win << (offset * 3):
            return True, 0 if self.player_1_turn else 1
          if (bitboard & (vertical_win << offset)) == vertical_win << offset:
            return True, 0 if self.player_1_turn else 1
        
        if (bitboard & tl_br_diagonal_win) == tl_br_diagonal_win:
          return True, 0 if self.player_1_turn else 1
        
        if (bitboard & tr_bl_diagonal_win) == tr_bl_diagonal_win:
          return True, 0 if self.player_1_turn else 1
        
        # Tie condition
        if board == "Mega":
          all_bitboards = self.player1_mega_bitboard | self.player2_mega_bitboard | self.tie_mega_bitboard
        else:
          all_bitboards = self.player1_bitboard | self.player2_bitboard

          all_bitboards = all_bitboards & (board_mask << (board * 9)) # Masking to get specific board

        if all_bitboards == 0b111111111: # If all boards are filled
          return False, 2
        
        return False, None
        
  
  def update_mega_board(self, move):
    """Updates the mega board to reflect the current state of the game
       Args:
          move: a tuple (x: int, y: int) where x is the board number and y is the space number

        Returns:
          None
    """

    board_num, position = move

    win_bool, winner = self.check_board_win(board_num)
    if win_bool:
      self.megaboard[board_num] = winner
  
    # Bitboard implementation
    win_bool, winner = self.check_board_win_bitboard(board_num)
    if win_bool:
      if winner == 0:
        self.player1_mega_bitboard |= (1 << board_num)
      else:
        self.player2_mega_bitboard |= (1 << board_num)


  def check_board_win(self, board_num):
    return self.check_win(self.board[board_num])
  
  def check_board_win_bitboard(self, board_num):
    return self.check_win(board_num)
  
  def check_mega_win(self):
    return self.check_win(self.megaboard)
  
  def check_mega_win_bitboard(self):
    return self.check_win("Mega")
      
  def play_move(self, move):
    # TODO: Finish this function
    """Plays a move on the board move is a tuple 
       Args:
          (x: int, y: int) where x is the board number and y is the space number

        Returns:
          bool: True if the move was completed, False otherwise
    """

    board_num, position = move

    if self.check_valid_move(move):
      self.board[board_num][position] = 0 if self.player_1_turn else 1

      # Bitboard implementation
      if self.player_1_turn:
        self.player1_bitboard |= (1 << (board_num * 9 + position))
      else:
        self.player2_bitboard |= (1 << (board_num * 9 + position))
    else:
      return False

    self.player_1_turn = not self.player_1_turn

    return True
  
  def print_board(self):
    """Prints the board
       Args:
          None

        Returns:
          megaboard: string
    """
    if self.in_notebook:
      clear_output(wait=True)
    megaboard=f"you are {self.icons[self.player]}\nmove: {self.moves}\nnext board: {self.previousmove}\n"
    for i in range(3): # large horizontal rows
        for j in range(3): # small horizontal rows
            for k in range(3): # large vertical columns
                if k != 0: #horizontal spacing between boards
                    megaboard=megaboard+" "
                for l in range(3): # small horizontal columns
                    cell_value = self.board[i * 3 + k][j * 3 + l]
                    if cell_value==-1:
                        megaboard=megaboard+(f"[{'-':^1}]") #cell is blank
                    else:
                        megaboard=megaboard+(f"[{self.icons[cell_value]:^1}]")
            if j != 2:
                megaboard=megaboard+"\n" # new line-ing between small rows
        if i != 2:
            megaboard=megaboard+"\n\n" # new line-ing between big rows
    megaboard=megaboard+(f"\n{self.megaboard}")
    return megaboard

    # Bitboard implementation
    if self.in_notebook:
      clear_output(wait=True)
    megaboard=f"you are {self.icons[self.player]}\nmove: {self.moves}\nnext board: {self.previousmove}\n"
    for i in range(3): # large horizontal rows
        for j in range(3): # small horizontal rows
            for k in range(3): # large vertical columns
                if k != 0: #horizontal spacing between boards
                    megaboard=megaboard+" "
                for l in range(3): # small horizontal columns
                    index = i * 9 + j + k*27 + l*3
                    if self.player1_bitboard & (1 << index):
                      megaboard=megaboard+(f"[{self.icons[0]:^1}]")
                    
                    elif self.player2_bitboard & (1 << index):
                      megaboard=megaboard+(f"[{self.icons[1]:^1}]")
                    
                    else:
                      megaboard=megaboard+(f"[{'-':^1}]")
            if j != 2:
                megaboard=megaboard+"\n" # new line-ing between small rows
        if i != 2:
            megaboard=megaboard+"\n\n" # new line-ing between big rows
    megaboard + megaboard + (f"\n{"Mega Board:"}")
    for i in range(3):
      for j in range(3):
        index = i*3 + j
        if self.player1_mega_bitboard & (1 << index):
          megaboard=megaboard+(f"[{self.icons[0]:^1}]")
        elif self.player2_mega_bitboard & (1 << index):
          megaboard=megaboard+(f"[{self.icons[1]:^1}]")
        elif self.tie_mega_bitboard & (1 << index):
          megaboard=megaboard+(f"[{self.icons[2]:^1}]")
        else:
          megaboard=megaboard+(f"[{'-':^1}]")
      megaboard=megaboard+"\n"
        
        
          

    def play(self):
        """Plays the game
           Args:
              None

            Returns:
              None
        """
        while True:
            print(self.print_board())
            player_move, concede_bool = self.get_move()
            if concede_bool:
                print("Player conceded")
                print(f"Player {1 if self.player_1_turn == False else 2} won!")
                print(f"Number of moves: {self.num_moves}")
                break
            self.play_move(player_move)
            self.update_mega_board(player_move)
            win_bool, winner = self.check_mega_win()
            self.num_moves += 1
            if win_bool:
                print(self.print_board())
                print(f"Player {winner} won!")
                print(f"Number of moves: {self.num_moves}")
                break
    
  



    

