import pygame
import sys
import copy
import math
import random
import time

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 550
FPS = 30
MAX_DEPTH = 4 

PLAYER_1 = 1 
PLAYER_2 = -1 # MIN

BG_COLOR = (20, 20, 20)
WOOD_BROWN = (139, 69, 19)
PIT_COLOR = (70, 35, 10)
SCORE_BOX_COLOR = (255, 255, 255)
SEED_COLORS = [(50, 50, 200), (200, 50, 50), (50, 200, 50), (200, 200, 200)]
HIGHLIGHT_COLOR = (255, 215, 0) 
LABEL_COLOR = (255, 255, 255)
MENU_COLOR = (40, 40, 40)
BTN_COLOR = (100, 100, 255)
BTN_HOVER = (150, 150, 255)


class MancalaBoard:
    def __init__(self):
        self.board = {
            'A': 4, 'B': 4, 'C': 4, 'D': 4, 'E': 4, 'F': 4,
            'G': 4, 'H': 4, 'I': 4, 'J': 4, 'K': 4, 'L': 4,
            '1': 0, '2': 0
        }
        self.p1_pits = ['A', 'B', 'C', 'D', 'E', 'F']
        self.p2_pits = ['G', 'H', 'I', 'J', 'K', 'L']
        
        self.next_pit = {
            'A': 'B', 'B': 'C', 'C': 'D', 'D': 'E', 'E': 'F', 'F': '1',
            '1': 'L', 
            'L': 'K', 'K': 'J', 'J': 'I', 'I': 'H', 'H': 'G', 'G': '2',
            '2': 'A' 
        }
        self.opposite_pit = {
            'A': 'G', 'G': 'A', 'B': 'H', 'H': 'B', 'C': 'I', 'I': 'C',
            'D': 'J', 'J': 'D', 'E': 'K', 'K': 'E', 'F': 'L', 'L': 'F'
        }

    def possibleMoves(self, player_idx):
        pits = self.p1_pits if player_idx == 1 else self.p2_pits
        return [p for p in pits if self.board[p] > 0]

    def doMove(self, player_idx, pit):
        seeds = self.board[pit]
        self.board[pit] = 0
        current_pit = pit
        
        opponent_store = '2' if player_idx == 1 else '1'
        own_store = '1' if player_idx == 1 else '2'
        
        while seeds > 0:
            current_pit = self.next_pit[current_pit]
            if current_pit == opponent_store: continue
            
            self.board[current_pit] += 1
            seeds -= 1

        extra_turn = (current_pit == own_store)

        is_own_pit = (current_pit in self.p1_pits if player_idx == 1 else current_pit in self.p2_pits)
        
        if not extra_turn and self.board[current_pit] == 1 and is_own_pit:
            opposite = self.opposite_pit.get(current_pit)
            if opposite:
                captured = self.board[opposite]
                if captured > 0:
                    self.board[own_store] += captured + 1 
                    self.board[opposite] = 0
                    self.board[current_pit] = 0
                
        return extra_turn

class Game:
    def __init__(self, mode="HvC"):
        self.state = MancalaBoard()
        self.mode = mode 
        
    def gameOver(self):
        p1_empty = all(self.state.board[p] == 0 for p in self.state.p1_pits)
        p2_empty = all(self.state.board[p] == 0 for p in self.state.p2_pits)

        if p1_empty or p2_empty:
            remaining_p1 = sum(self.state.board[p] for p in self.state.p1_pits)
            remaining_p2 = sum(self.state.board[p] for p in self.state.p2_pits)
            
            self.state.board['1'] += remaining_p1
            self.state.board['2'] += remaining_p2
            
            for p in self.state.p1_pits + self.state.p2_pits:
                self.state.board[p] = 0
            return True
        return False

    def findWinner(self):
        s1, s2 = self.state.board['1'], self.state.board['2']
        p1_name = "Human (P1)" if self.mode == "HvC" else "Comp 1 (P1)"
        p2_name = "Comp (P2)" if self.mode == "HvC" else "Comp 2 (P2)"
        
        if s1 > s2: return p1_name, s1
        if s2 > s1: return p2_name, s2
        return "Draw", s1

    #HEURISTICS
    def evaluate(self, player_perspective, heuristic_type=1):
        s1 = self.state.board['1']
        s2 = self.state.board['2']
        score = (s1 - s2) if player_perspective == 1 else (s2 - s1)

        if heuristic_type == 1:
            return score
            
        elif heuristic_type == 2:
            score_diff = score
            my_pits = self.state.p1_pits if player_perspective == 1 else self.state.p2_pits
            my_seeds = sum(self.state.board[p] for p in my_pits)
            
            control_score = 0.5 * my_seeds 
            
            return score_diff + control_score

#ALGORITHM

def Minimax(game_node, max_player_idx, current_player, depth, alpha, beta, heuristic_id):
    if depth == 1 or game_node.gameOver():
        return game_node.evaluate(max_player_idx, heuristic_id), None 

    possible_moves = game_node.state.possibleMoves(current_player)
    if not possible_moves:
        return game_node.evaluate(max_player_idx, heuristic_id), None

    bestPit = None

    if current_player == max_player_idx: 
        bestValue = -math.inf 
        for pit in possible_moves: 
            child = copy.deepcopy(game_node) 
            extra = child.state.doMove(current_player, pit) 
            
            next_p = current_player if extra else (-1 if current_player == 1 else 1)
            
            value, _ = Minimax(child, max_player_idx, next_p, depth - 1, alpha, beta, heuristic_id) 
            
            if value > bestValue: 
                bestValue = value 
                bestPit = pit 
            alpha = max(alpha, bestValue) 
            if bestValue >= beta: break 
        return bestValue, bestPit

    else: 
        bestValue = math.inf 
        for pit in possible_moves: 
            child = copy.deepcopy(game_node) 
            extra = child.state.doMove(current_player, pit) 
            
            next_p = current_player if extra else (-1 if current_player == 1 else 1)
            
            value, _ = Minimax(child, max_player_idx, next_p, depth - 1, alpha, beta, heuristic_id) 
            
            if value < bestValue: 
                bestValue = value 
                bestPit = pit 
            beta = min(beta, bestValue) 
            if bestValue <= alpha: break 
        return bestValue, bestPit

# --- GUI ---

class MancalaGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mancala: AI Analysis Tool")
        self.clock = pygame.time.Clock()
        
        self.font_large = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_med = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 16)

        self.state = "MENU" 
        self.game = None
        self.turn = PLAYER_1
        self.status_msg = ""
        self.ai_thinking = False
        self.ai_selected_pit = None 
        
        self.pit_rects = {}
        self.setup_layout()
        
        self.btn_hvc = pygame.Rect(350, 200, 300, 60)
        self.btn_cvc = pygame.Rect(350, 300, 300, 60)
        self.btn_menu = pygame.Rect(SCREEN_WIDTH-120, 10, 100, 40)

    def setup_layout(self):
        bx, by, bw, bh = 50, 100, 900, 340
        self.board_rect = pygame.Rect(bx, by, bw, bh)
        
        start_x = bx + 120
        spacing = 100
        
      
        for i, k in enumerate(['G','H','I','J','K','L']):
            self.pit_rects[k] = pygame.Rect(start_x + i*spacing, by + 40, 80, 80)
        for i, k in enumerate(['A','B','C','D','E','F']):
            self.pit_rects[k] = pygame.Rect(start_x + i*spacing, by + 220, 80, 80)
            
        self.pit_rects['2'] = pygame.Rect(bx + 10, by + 40, 100, 280)
        self.pit_rects['1'] = pygame.Rect(bx + bw - 110, by + 40, 100, 280)

    def draw_seeds(self, rect, count, pit_name):
        if count == 0: return
        cx, cy = rect.center
        random.seed(ord(pit_name) + count * 555) 
        for i in range(count):
            angle = random.uniform(0, 6.28)
            dist = random.uniform(0, 28)
            x = cx + dist * math.cos(angle)
            y = cy + dist * math.sin(angle)
            col = SEED_COLORS[i % 4]
            pygame.draw.circle(self.screen, col, (int(x), int(y)), 8)
            pygame.draw.circle(self.screen, (0,0,0), (int(x), int(y)), 8, 1)

    def draw_menu(self):
        self.screen.fill(MENU_COLOR)
        title = self.font_large.render("MANCALA AI SOLVER", True, LABEL_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
        
        mx, my = pygame.mouse.get_pos()
        c1 = BTN_HOVER if self.btn_hvc.collidepoint((mx,my)) else BTN_COLOR
        c2 = BTN_HOVER if self.btn_cvc.collidepoint((mx,my)) else BTN_COLOR
        
        pygame.draw.rect(self.screen, c1, self.btn_hvc, border_radius=10)
        pygame.draw.rect(self.screen, c2, self.btn_cvc, border_radius=10)
        
        t1 = self.font_med.render("Human vs Computer ", True, (255,255,255))
        t2 = self.font_med.render("Computer vs Computer (P2)", True, (255,255,255))
        
        self.screen.blit(t1, (self.btn_hvc.centerx - t1.get_width()//2, self.btn_hvc.centery - 12))
        self.screen.blit(t2, (self.btn_cvc.centerx - t2.get_width()//2, self.btn_cvc.centery - 12))
        
        sub = self.font_small.render("HvC (P2): Heuristic 1 | CvC (P2): Heuristic 2 ", True, (150,150,150))
        self.screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, 380))

    def draw_game(self):
        self.screen.fill(BG_COLOR)
        
        mode_txt = "HvC Mode: Human vs (H1)" if self.game.mode == "HvC" else "CvC Mode: Simple AI (P1/H1) vs Strategic AI (P2/H2)"
        h_s = self.font_med.render(mode_txt, True, (100, 200, 100))
        self.screen.blit(h_s, (30, 20))
        
        pygame.draw.rect(self.screen, BTN_COLOR, self.btn_menu, border_radius=5)
        m_txt = self.font_small.render("MENU", True, (255,255,255))
        self.screen.blit(m_txt, (self.btn_menu.centerx-m_txt.get_width()//2, self.btn_menu.centery-8))
        
        stat = self.font_med.render(self.status_msg, True, HIGHLIGHT_COLOR)
        self.screen.blit(stat, (SCREEN_WIDTH//2 - stat.get_width()//2, 60))

        pygame.draw.rect(self.screen, WOOD_BROWN, self.board_rect, border_radius=20)
        
        mx, my = pygame.mouse.get_pos()
        
        for k, r in self.pit_rects.items():
            color = PIT_COLOR
            
            # 1. Human Hover Logic
            if not self.ai_thinking and not self.game.gameOver():
                if self.game.mode == "HvC" and self.turn == PLAYER_1:
                    if k in self.game.state.p1_pits and r.collidepoint((mx,my)):
                        color = HIGHLIGHT_COLOR
            
            # 2. AI Selection Logic (S'allume quand l'IA choisit)
            if k == self.ai_selected_pit:
                color = HIGHLIGHT_COLOR

            if k in ['1','2']: pygame.draw.rect(self.screen, color, r, border_radius=15)
            else: pygame.draw.ellipse(self.screen, color, r)
            
            self.draw_seeds(r, self.game.state.board[k], k)
            
            if k not in ['1','2']:
                lbl = self.font_small.render(k, True, LABEL_COLOR)
                off = 60 if k in self.game.state.p1_pits else -60
                self.screen.blit(lbl, (r.centerx-5, r.centery+off))

        s1 = self.game.state.board['1']
        s2 = self.game.state.board['2']
        lbl1 = "Human" if self.game.mode == "HvC" else "Comp 1 (Simple)"
        lbl2 = "Comp " if self.game.mode == "HvC" else "Comp 2 " 
        
        t1 = self.font_large.render(f"{lbl1}: {s1}", True, SCORE_BOX_COLOR)
        t2 = self.font_large.render(f"{lbl2}: {s2}", True, SCORE_BOX_COLOR)
        
        self.screen.blit(t2, (50, 480))
        self.screen.blit(t1, (SCREEN_WIDTH-280, 480))

    def run(self):
        while True:
            self.clock.tick(FPS)
            
            if self.state == "MENU":
                self.draw_menu()
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: sys.exit()
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = e.pos
                        if self.btn_hvc.collidepoint((mx,my)):
                            self.game = Game("HvC")
                            self.turn = PLAYER_1
                            self.status_msg = "Human Turn (A-F)"
                            self.state = "GAME"
                        elif self.btn_cvc.collidepoint((mx,my)):
                            self.game = Game("CvC")
                            self.turn = PLAYER_1
                            self.status_msg = "Comp 1 Thinking..."
                            self.state = "GAME"
                            self.ai_thinking = True

            elif self.state == "GAME":
                self.draw_game()
                
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: sys.exit()
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        if self.btn_menu.collidepoint(e.pos):
                            self.state = "MENU"
                        
                        if self.game.mode == "HvC" and self.turn == PLAYER_1 and not self.ai_thinking:
                            for k in self.game.state.p1_pits:
                                if self.pit_rects[k].collidepoint(e.pos) and self.game.state.board[k] > 0:
                                    self.handle_move(PLAYER_1, k)
                                    break

                if self.ai_thinking and not self.game.gameOver():
                    pygame.display.flip() 
                    time.sleep(1.5) 
                    
                    if self.turn == PLAYER_1: 
                        heuristic_to_use = 1
                        _, move = Minimax(self.game, PLAYER_1, PLAYER_1, MAX_DEPTH, -math.inf, math.inf, heuristic_to_use)
                        
                        if move:
                            self.ai_selected_pit = move
                            self.status_msg = f"Comp 1 Chooses Pit: {move}"
                            self.draw_game()
                            pygame.display.flip()
                            
                            time.sleep(1.3)
                            
                            self.ai_selected_pit = None
                            self.handle_move(PLAYER_1, move)
                        else: self.pass_turn()
                        
                    elif self.turn == PLAYER_2:
                        if self.game.mode == "HvC":
                            heuristic_to_use = 1
                            comp_name = "Comp "
                        else:
                            heuristic_to_use = 2
                            comp_name = "Comp 2 "
                            
                        self.status_msg = f"{comp_name} Thinking..."
                        _, move = Minimax(self.game, PLAYER_2, PLAYER_2, MAX_DEPTH, -math.inf, math.inf, heuristic_to_use)
                        
                        if move:
                            self.ai_selected_pit = move
                            self.status_msg = f"{comp_name} Chooses Pit: {move}"
                            self.draw_game()
                            pygame.display.flip()
                            
                            time.sleep(1.3)
                            
                            self.ai_selected_pit = None
                            self.handle_move(PLAYER_2, move)
                        else: self.pass_turn()
                    
                if self.game.gameOver():
                    w, s = self.game.findWinner()
                    self.status_msg = f"GAME OVER! {w} Wins ({s})"
                    self.ai_thinking = False

            pygame.display.flip()

    def handle_move(self, player, pit):
        extra = self.game.state.doMove(player, pit)
        
        if extra:
            self.status_msg = f"Player {'1' if player == 1 else '2'} gets an Extra Turn!"
        else:
            self.status_msg = "Move Done."

        self.draw_game()       
        pygame.display.flip() 
        
        time.sleep(1.2) 

        if not extra:
            self.pass_turn()

    def pass_turn(self):
        self.turn = -1 if self.turn == 1 else 1
        
        if self.game.mode == "HvC":
            if self.turn == PLAYER_1:
                self.status_msg = "Human Turn"
                self.ai_thinking = False
            else:
                self.status_msg = "Comp  Thinking..." 
                self.ai_thinking = True
        else: 
            p_name = "Comp 1 (P1)" if self.turn == 1 else "Comp 2 (P2)"
            self.status_msg = f"{p_name} Thinking..."
            self.ai_thinking = True

if __name__ == "__main__":
    MancalaGUI().run()