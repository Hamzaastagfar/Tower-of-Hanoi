from flask import Flask, render_template, request, jsonify, session
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

class TowerOfHanoi:
    def __init__(self, num_disks=3):
        self.num_disks = num_disks
        self.towers = [list(range(num_disks, 0, -1)), [], []]
        self.moves = 0
        self.start_time = datetime.now()
        self.game_won = False
    
    def is_valid_move(self, from_tower, to_tower):
        if not self.towers[from_tower]:
            return False
        if not self.towers[to_tower]:
            return True
        return self.towers[from_tower][-1] < self.towers[to_tower][-1]
    
    def make_move(self, from_tower, to_tower):
        if self.is_valid_move(from_tower, to_tower):
            disk = self.towers[from_tower].pop()
            self.towers[to_tower].append(disk)
            self.moves += 1
            
            # Check win condition
            if len(self.towers[2]) == self.num_disks:
                self.game_won = True
            
            return True
        return False
    
    def get_state(self):
        return {
            'towers': self.towers,
            'moves': self.moves,
            'game_won': self.game_won,
            'num_disks': self.num_disks,
            'min_moves': (2 ** self.num_disks) - 1
        }
    
    def reset(self, num_disks=None):
        if num_disks:
            self.num_disks = num_disks
        self.towers = [list(range(self.num_disks, 0, -1)), [], []]
        self.moves = 0
        self.start_time = datetime.now()
        self.game_won = False
    
    def to_dict(self):
        """Convert game state to dictionary for session storage"""
        return {
            'num_disks': self.num_disks,
            'towers': self.towers,
            'moves': self.moves,
            'game_won': self.game_won
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create game instance from dictionary"""
        game = cls(data['num_disks'])
        game.towers = data['towers']
        game.moves = data['moves']
        game.game_won = data['game_won']
        return game

# Store games using simple dictionary storage instead of objects in session
def get_game():
    if 'game_data' not in session:
        game = TowerOfHanoi(3)
        session['game_data'] = game.to_dict()
        return game
    else:
        return TowerOfHanoi.from_dict(session['game_data'])

def save_game(game):
    """Save game state to session"""
    session['game_data'] = game.to_dict()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game_state')
def game_state():
    game = get_game()
    return jsonify(game.get_state())

@app.route('/api/move', methods=['POST'])
def make_move():
    data = request.get_json()
    from_tower = data.get('from')
    to_tower = data.get('to')
    
    game = get_game()
    success = game.make_move(from_tower, to_tower)
    
    if success:
        save_game(game)
    
    return jsonify({
        'success': success,
        'state': game.get_state()
    })

@app.route('/api/reset', methods=['POST'])
def reset_game():
    data = request.get_json()
    num_disks = data.get('num_disks', 3)
    
    game = TowerOfHanoi(num_disks)
    save_game(game)
    
    return jsonify(game.get_state())

@app.route('/api/solve', methods=['POST'])
def solve_game():
    game = get_game()
    moves = solve_hanoi(game.num_disks, 0, 2, 1)
    return jsonify({'moves': moves})

def solve_hanoi(n, source, destination, auxiliary):
    if n == 1:
        return [{'from': source, 'to': destination}]
    
    moves = []
    moves.extend(solve_hanoi(n-1, source, auxiliary, destination))
    moves.append({'from': source, 'to': destination})
    moves.extend(solve_hanoi(n-1, auxiliary, destination, source))
    
    return moves

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)