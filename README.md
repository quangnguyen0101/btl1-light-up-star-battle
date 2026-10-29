# Tổng hợp BTL1: Light Up và Star Battle

Dự án mô hình hoá và giải hai bài toán logic **Light Up (Akari)** và **Star Battle** bằng Python. Các thuật toán tìm kiếm dùng chung một hợp đồng kết quả, một CLI thống nhất, và so sánh được trên cùng bộ 48 đề.

## 1. Bài toán

- **Light Up**: đặt bóng đèn vào ô trắng sao cho mọi ô trắng được chiếu sáng, không có hai bóng nhìn thấy nhau theo hàng hoặc cột, và mỗi tường số có đúng số bóng liền kề.
- **Star Battle**: đặt sao sao cho mỗi hàng, cột và vùng có đúng `stars_per_unit` sao; hai sao không chạm nhau (kể cả chéo); không đặt sao trên ô bị khoá. Biến thể `shapeless` không có vùng.

## 2. Thuật toán

| Thuật toán | Họ | Mô tả |
|---|---|---|
| `dfs` | `blind_search` | Tìm kiếm theo chiều sâu, không dùng heuristic. Duyệt theo từng hàng (Star Battle) hoặc từng ô trắng (Light Up). |
| `greedy` | `heuristic` | Greedy Best-First. Chỉ dùng `h(n)` để chọn nút tiếp theo. `h` là số cột và số vùng còn thiếu sao (Star Battle), hoặc số ô trắng chưa được chiếu sáng (Light Up). Light Up có lan truyền ràng buộc (các bước bắt buộc) và chọn ô theo MRV. |

Greedy không đảm bảo tối ưu. DFS đầy đủ hơn, Greedy nhanh hơn trên các đề vừa và nhỏ.

Các thuật toán đã thử và bỏ: A\* (commit `35603f3`), Simulated Annealing (commit `67b247e`, không giải được đề lớn nào trong 120s). Lịch sử đầy đủ nằm trong git.

## 3. Hợp đồng kết quả

Mọi thuật toán trả về dict với các trường (định nghĩa trong `src/model/result.py`):

| Trường | Ý nghĩa |
|---|---|
| `solution` | Danh sách toạ độ `[row, col]`, `[]` nếu không giải được |
| `state` | Bitmask, luôn được suy ra từ `solution` bởi `build_result` |
| `path` | Các trạng thái bitmask từ bàn trống (`path[0]`) tới lời giải (`path[-1]`) |
| `expanded` | Số nút lấy ra khỏi frontier và xử lý, kể cả nút đích |
| `generated` | Số nút đưa vào frontier |
| `frontier_peak` | Kích thước lớn nhất của frontier (DFS: stack) |

Runner thêm `status` (`xong`, `timeout`, `vo nghiem`) và `time_s`. Khi timeout, `expanded`, `generated`, `frontier_peak` đặt là `-1` và `known_solution` là `[]`.

## 4. Cấu trúc thư mục

```text
tong-hop/
├── data/                  48 đề JSON, chia theo loại (light_up, star_battle)
├── src/
│   ├── model/             Mô hình bài toán và hợp đồng kết quả
│   │   ├── light_up.py
│   │   ├── star_battle.py
│   │   ├── result.py      build_result, validate_result, path_from_came_from
│   │   └── solver.py
│   ├── blind_search/      DFS
│   ├── heuristic/greedy/  Greedy Best-First (theo loại đề)
│   ├── utils/             Đọc/ghi JSON, bảng markdown, giới hạn thời gian
│   └── registry.py        Tên thuật toán -> (họ, hàm chạy)
├── scripts/
│   ├── run.py             Chạy một thuật toán trên bộ đề
│   ├── verify.py          Kiểm tra dữ liệu, hợp đồng, is_goal, toàn vẹn file
│   ├── compare.py         Tổng hợp các lượt chạy vào output/so-sanh/diff.md
│   ├── demo.py            In từng bước của một đề theo path
│   └── figures.py         Sinh toàn bộ ảnh trong figs/
├── viz/                   Vẽ bàn cờ bằng Pillow (đề, lời giải)
├── output/                Kết quả chạy: bang.md, manifest.json, lời giải JSON
├── figs/                  Ảnh PNG (sinh bằng scripts.figures)
├── tests/                 Unit test, theo họ thuật toán và mô hình
└── requirements.txt       Chỉ cần pillow (cho viz)
```

## 5. Cài đặt

Yêu cầu Python 3.10 trở lên. Chỉ cần Pillow để vẽ ảnh:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Mô hình, các thuật toán và test không cần thư viện ngoài.

## 6. Chạy

Các lệnh chạy từ thư mục gốc của repo.

### Chạy một thuật toán trên bộ đề

```bash
python -m scripts.run --algo dfs --timeout 300
python -m scripts.run --algo greedy --timeout 300 --kind light_up
```

Tham số:

- `--algo`: `dfs` hoặc `greedy`.
- `--kind`: chỉ chạy một loại (`light_up` hoặc `star_battle`).
- `--timeout`: giới hạn thời gian mỗi đề, tính bằng giây (mặc định 60).
- `--data`, `--out`: thư mục đề và thư mục output (mặc định `data/` và `output/`).

Mỗi lần chạy ghi, với mỗi loại đề:

- `output/<họ>/<algo>/<kind>/<tên đề>.json`: đề kèm `known_solution` do thuật toán tìm ra.
- `output/<họ>/<algo>/<kind>/bang.md`: bảng 7 cột (đề, kích thước, mở rộng, thời gian, kết quả, sinh ra, stack max).
- `output/<họ>/<algo>/<kind>/manifest.json`: số liệu máy đọc, dùng cho `compare` và `verify`.

### So sánh và kiểm tra

```bash
python -m scripts.compare
python -m scripts.verify
```

`compare` đọc các `manifest.json` và ghi `output/so-sanh/diff.md`, một bảng gộp các thuật toán trên cùng từng đề, kèm cột "nhanh hơn". `verify` kiểm tra dữ liệu, hợp đồng kết quả, `is_goal` của mọi lời giải và tính toàn vẹn của file output; thoát với mã 0 nếu không có lỗi.

### Xem từng bước của một đề

```bash
python -m scripts.demo --algo greedy --puzzle data/light_up/lu-7x7-normal-01.json --timeout 10
```

### Vẽ bàn cờ

```bash
python -m scripts.figures                                  # toàn bộ ảnh
python -m viz.puzzle data/star_battle/sb-5x5-normal-01.json  # một đề
python -m viz.solution output/blind_search/dfs/light_up/lu-7x7-normal-01.json
```

`figs/` chưa có ảnh; chạy `scripts.figures` để sinh.

## 7. Unit test

```bash
python3 -m unittest discover -s tests -t .
```

Các test hiện có:

- `tests/test_model/`: mô hình và khoá hành vi của `is_goal`. Các ca "gần đúng nhưng sai" (ví dụ tường số đủ bóng nhưng còn ô tối, hai sao kề chéo) để đảm bảo `is_goal` kiểm tra đủ luật.
- `tests/test_blind_search/`: DFS trên đề nhỏ, vô nghiệm, và hợp đồng kết quả.
- `tests/test_heuristic/`: Greedy trên đề nhỏ, hợp đồng, path bắt đầu từ bàn trống, vô nghiệm, và đối chiếu với DFS.

Test kiểm tra `is_goal(state)` chứ không so tập toạ độ với `known_solution`, vì một đề có thể có nhiều lời giải đúng.

## 8. Kết quả hiện tại

Bộ 48 đề, timeout 300 giây mỗi đề.

| Thuật toán | Giải được | Timeout | Ghi chú |
|---|---:|---:|---|
| DFS | 42/48 | 6 | Giải được nhiều đề lớn nhất trong các thuật toán đã thử |
| Greedy | 25/48 | 23 | Nhanh nhất trên Star Battle đến 10×10 |

Chi tiết theo nhóm đề (Greedy):

| Nhóm | Giải được |
|---|---|
| Star Battle 5×5 đến 10×10 | 18/18 |
| Star Battle 14×14 đến 25×25 | 0/7 |
| Light Up 7×7 | 7/7 |
| Light Up 10×10 | 0/7 |
| Light Up 14×14 trở lên | 0/9 |

Greedy được chạy trên 8 tiến trình song song để rút ngắn thời gian. Khi chạy đơn lẻ trước đó, `lu-10x10-normal-01` giải được sau 232s; trong lần chạy song song này đề đó timeout. Vì vậy với các đề gần ngưỡng 300s, kết quả có thể thay đổi theo mức tải của máy.

Dữ liệu đầy đủ: `output/so-sanh/diff.md` và `output/<họ>/<algo>/<kind>/bang.md`.

## 9. Thêm thuật toán

1. Viết hàm nhận một `StarBattleProblem` hoặc `LightUpProblem` và trả về kết quả qua `build_result`.
2. Đăng ký trong `src/<họ>/registry.py` và thêm dòng tương ứng vào `src/registry.py`.
3. Thêm test trong `tests/`.
4. Chạy `scripts.run`, `scripts.compare`, `scripts.verify`.

`scripts.run`, `compare` và `verify` tự nhận thuật toán mới qua `src/registry.py`.

## 10. Thêm đề mới

1. Tạo file JSON trong `data/light_up/` hoặc `data/star_battle/`.
2. Đọc bằng `from_json()` và kiểm tra kích thước, toạ độ.
3. Nếu có lời giải mẫu, ghi vào `known_solution`. Danh sách rỗng nghĩa là chưa có lời giải, không phải là đề vô nghiệm.

## 11. Ghi chú

- `known_solution` trong file output là lời giải do thuật toán tìm ra, không phải đáp án gốc của đề.
- `path` của Greedy và DFS là các trạng thái theo từng bước quyết định. Với Light Up, bước đầu có thể đặt nhiều bóng do lan truyền ràng buộc.
- Thời gian đo bằng `time.perf_counter()` và có thể dao động giữa các lần chạy.
