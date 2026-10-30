import os
import time
import tracemalloc
import json
import multiprocessing
import pygame
from pathlib import Path

# --- IMPORT DỰA TRÊN MÃ NGUỒN THỰC TẾ ---
from src.model.light_up import LightUpProblem
from src.model.star_battle import StarBattleProblem
from src.blind_search.dfs import dfs
from src.heuristic.greedy.light_up import greedy as greedy_lu
from src.heuristic.greedy.star_battle import greedy as greedy_sb

# Lưu ý: Import thuật toán Heuristic từ Việc 3 (Vui lòng điền đúng tên hàm thực tế)
# Ví dụ giả định:
# from src.heuristic.greedy.light_up import greedy_light_up
# from src.heuristic.greedy.star_battle import greedy_star_battle

# --- PHẦN 1: BENCHMARK (ĐO THỜI GIAN & BỘ NHỚ) ---

def run_solver_process(problem_class, file_path, algo_name, return_dict):
    """
    Chạy thuật toán trong một tiến trình riêng biệt để đo bộ nhớ chính xác.
    """
    tracemalloc.start()
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    problem = problem_class.from_dict(data)
    
    start_time = time.perf_counter()
    
    if algo_name == "DFS":
        solution = dfs(problem)
    elif algo_name == "Heuristic":
        if problem_class.__name__ == "LightUpProblem":
            solution = greedy_lu(problem)
        else:
            solution = greedy_sb(problem)
    else:
        solution = {} 
        
    end_time = time.perf_counter()
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    time_taken = end_time - start_time
    
    expanded_nodes = solution.get("expanded", 0) if solution else 0
    is_solved = "solution" in solution if solution else False
    
    return_dict['time'] = time_taken
    return_dict['peak_memory'] = peak / (1024 * 1024) # Đổi sang MB
    return_dict['expanded_nodes'] = expanded_nodes
    return_dict['is_solved'] = is_solved

def benchmark_algorithm(problem_class, file_path, algo_name, num_runs=5, timeout=60):
    """
    Chạy lặp N lần để lấy trung bình thời gian và bộ nhớ.
    """
    total_time = 0
    peak_memories = []
    expanded_nodes = 0
    is_solved = False
    
    for i in range(num_runs):
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        p = multiprocessing.Process(target=run_solver_process, args=(problem_class, file_path, algo_name, return_dict))
        
        p.start()
        p.join(timeout)
        
        if p.is_alive():
            p.terminate()
            p.join()
            return f"Timeout (> {timeout}s)", "N/A", "N/A", False
            
        if 'time' in return_dict:
            total_time += return_dict['time']
            peak_memories.append(return_dict['peak_memory'])
            expanded_nodes = return_dict['expanded_nodes']
            is_solved = return_dict['is_solved']
        else:
             return "Error", "N/A", "N/A", False

    avg_time = total_time / num_runs
    avg_memory = sum(peak_memories) / len(peak_memories)
    
    return f"{avg_time:.4f}", f"{avg_memory:.2f}", expanded_nodes, is_solved

def generate_markdown_table(results, puzzle_name):
    """
    Sinh bảng Markdown để paste vào báo cáo.
    """
    md = f"### Bảng số liệu: {puzzle_name}\n\n"
    md += "| Test case | Thuật toán | Số Node mở rộng | Bộ nhớ đỉnh (MB) | Thời gian TB (s) | Trạng thái |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for r in results:
        status = "Thành công" if r['is_solved'] else "Thất bại/Timeout"
        md += f"| {r['file']} | {r['algo']} | {r['nodes']} | {r['mem']} | {r['time']} | {status} |\n"
    return md

# --- PHẦN 2: GIAO DIỆN DEMO (DÙNG PYGAME) ---

def draw_grid(screen, width, height, rows, cols, tile_size):
    for x in range(0, width + 1, tile_size):
        pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, height))
    for y in range(0, height + 1, tile_size):
        pygame.draw.line(screen, (200, 200, 200), (0, y), (width, y))

def demo_gui(problem_class, file_path, algo_name):
    """
    Hiển thị giao diện Pygame và chạy step-by-step.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    problem = problem_class.from_dict(data)
    
    if algo_name == "DFS":
        solution = dfs(problem)
    elif algo_name == "Heuristic":
        if problem_class.__name__ == "LightUpProblem":
            solution = greedy_lu(problem)
        else:
            solution = greedy_sb(problem)
    else:
        solution = {}
    
    steps_log = solution.get("path", []) if solution else []
    
    if not steps_log:
         print(f"[{algo_name}] Không có lịch sử bước đi (path) để demo UI.")
         return
    
    rows = problem.rows
    cols = problem.cols
    tile_size = 50
    width = cols * tile_size
    height = rows * tile_size
    
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(f"Demo {problem_class.__name__} - {algo_name}")
    
    clock = pygame.time.Clock()
    running = True
    step_index = 0
    font = pygame.font.Font(None, 36)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if step_index < len(steps_log) - 1:
                    step_index += 1

        screen.fill((255, 255, 255))
        draw_grid(screen, width, height, rows, cols, tile_size)
        
        current_state = steps_log[step_index]
        for r in range(rows):
            for c in range(cols):
                 val = current_state[r]
                 rect = pygame.Rect(c * tile_size, r * tile_size, tile_size, tile_size)
                 
                 # Kiểm tra bitmask xem ô đó có đèn/sao hay không
                 if (val >> c) & 1:
                     pygame.draw.circle(screen, (255, 215, 0), rect.center, tile_size // 3)
                     
                 # Vẽ tường nếu là bài toán Light Up
                 elif problem_class.__name__ == 'LightUpProblem' and problem.grid[r][c] != '.':
                     pygame.draw.rect(screen, (0, 0, 0), rect)
                     # In số lên tường nếu có
                     if problem.grid[r][c] in "01234":
                         num_text = font.render(problem.grid[r][c], True, (255, 255, 255))
                         screen.blit(num_text, num_text.get_rect(center=rect.center))
                 
                 # Vẽ ô bị khóa (blocked) nếu là bài toán Star Battle
                 elif problem_class.__name__ == 'StarBattleProblem' and (r, c) in problem.blocked_cells:
                     pygame.draw.rect(screen, (100, 100, 100), rect)
                     
        text = font.render(f"Step {step_index + 1}/{len(steps_log)} (Press SPACE)", True, (255, 0, 0))
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(30)
        
# --- PHẦN 3: MAIN EXECUTION ---
if __name__ == '__main__':
    # Tự động thu thập toàn bộ testcases để benchmark (không hard-code)
    light_up_files = [str(p) for p in Path("data/light_up").glob("*.json") if not any(n in p.name for n in ("daily","weekly","monthly"))]
    star_battle_files = [str(p) for p in Path("data/star_battle").glob("*.json") if not any(n in p.name for n in ("daily","weekly","monthly"))]
    
    print("=== ĐANG CHẠY BENCHMARK ===")
    
    # 1. Benchmark Light Up
    lu_results = []
    for f in light_up_files:
        if os.path.exists(f):
            # Tạm thời chỉ chạy DFS để test, hãy thêm "Heuristic" vào danh sách khi code team xong
            for algo in ["DFS","Heuristic"]: 
                print(f"Đang benchmark {f} bằng {algo}...")
                time_val, mem_val, nodes, solved = benchmark_algorithm(LightUpProblem, f, algo, num_runs=5)
                lu_results.append({
                    'file': os.path.basename(f), 'algo': algo, 
                    'time': time_val, 'mem': mem_val, 'nodes': nodes, 'is_solved': solved
                })
    
    # 2. Benchmark Star Battle
    sb_results = []
    for f in star_battle_files:
         if os.path.exists(f):
            for algo in ["DFS","Heuristic"]:
                print(f"Đang benchmark {f} bằng {algo}...")
                time_val, mem_val, nodes, solved = benchmark_algorithm(StarBattleProblem, f, algo, num_runs=5)
                sb_results.append({
                    'file': os.path.basename(f), 'algo': algo, 
                    'time': time_val, 'mem': mem_val, 'nodes': nodes, 'is_solved': solved
                })
                
    # In Markdown Table
    if lu_results:
        print("\n" + generate_markdown_table(lu_results, "Light Up"))
    if sb_results:
        print("\n" + generate_markdown_table(sb_results, "Star Battle"))
    
    # --- CHẠY GIAO DIỆN DEMO ---
    print("\n=== KHỞI ĐỘNG DEMO GUI ===")
    print("Nhấn phím SPACE để xem từng bước của thuật toán.")
    
    pygame.init()
    
    # 1. Mở demo Light Up trước
    if os.path.exists(light_up_files[0]):
        print("\nĐang hiển thị demo Light Up (DFS)...")
        demo_gui(LightUpProblem, light_up_files[0], "DFS")
        
    # 2. Sau khi bạn đóng cửa sổ Light Up, demo Star Battle sẽ hiện lên
    if os.path.exists(star_battle_files[0]):
        print("\nĐang hiển thị demo Star Battle (DFS)...")
        demo_gui(StarBattleProblem, star_battle_files[0], "DFS")
        
    pygame.quit()
