# Logic Puzzles Starter

Dự án xây dựng nền tảng để mô hình hóa, kiểm tra và giải hai bài toán logic: **Light Up (Akari)** và **Star Battle** bằng Python.

Repo cung cấp cấu trúc dữ liệu cho bài toán, `Parser` đọc dữ liệu từ file JSON, cơ chế biểu diễn `State` bằng `Bitmask`, các hàm kiểm tra luật chơi, hiển thị bàn cờ và `Interface` chung để tích hợp các thuật toán tìm kiếm do các thành viên trong nhóm phát triển.

## 1. Tổng quan dự án

### Các bài toán được hỗ trợ

- **Light Up (Akari):** Đặt các bóng đèn vào ô trắng sao cho mọi ô trắng đều được chiếu sáng, không có hai bóng đèn nhìn thấy nhau theo hàng hoặc cột, và các ô tường có số thỏa mãn số bóng đèn liền kề.
- **Star Battle:** Đặt các ngôi sao sao cho mỗi hàng, mỗi cột và mỗi vùng (đối với biến thể `normal`) có đúng số sao yêu cầu. Hai ngôi sao không được nằm cạnh nhau theo chiều ngang, chiều dọc hoặc đường chéo.

### Các chức năng chính

- Đọc dữ liệu bài toán từ file JSON.
- Biểu diễn `State` bằng `Bitmask` để tiết kiệm bộ nhớ và hỗ trợ thao tác bit.
- Chuyển đổi giữa danh sách tọa độ và `State`.
- Kiểm tra tính hợp lệ của trạng thái bằng `Validation`.
- Kiểm tra trạng thái đích bằng `Goal State`.
- Hiển thị bàn cờ dưới dạng văn bản.
- Cung cấp `Interface` chung để tích hợp các `Search Algorithm`.
- Sử dụng `Unit Test` để kiểm tra mô hình và luật chơi.

## 2. Yêu cầu hệ thống

- Python 3.10 trở lên.
- Git để tải repo.
- Các thư viện chuẩn có sẵn của Python.

Hiện tại, phần mô hình bài toán và kiểm thử không yêu cầu cài thêm thư viện bên ngoài.

## 3. Cấu trúc thư mục

```text
logic_puzzles_starter/
├── data/
│   ├── light_up/
│   │   ├── light_up_7x7.json
│   │   └── light_up_10x10.json
│   └── star_battle/
│       ├── normal_1star_5x5.json
│       ├── normal_2star_10x10.json
│       ├── shapeless_1star_6x6.json
│       └── shapeless_2star_10x10.json
├── src/
│   ├── __init__.py
│   ├── light_up.py
│   ├── star_battle.py
│   └── solver.py
├── tests/
│   ├── test_light_up.py
│   └── test_star_battle.py
├── .gitignore
└── README.md
```

Ý nghĩa các thư mục và file:

- `data/`: Chứa các bộ dữ liệu bài toán dưới định dạng JSON.
- `src/light_up.py`: Mô hình bài toán Light Up, xử lý ánh sáng, kiểm tra luật chơi và hiển thị bàn cờ.
- `src/star_battle.py`: Mô hình bài toán Star Battle, kiểm tra luật chơi và hiển thị bàn cờ.
- `src/solver.py`: Cung cấp `Interface` chung để gọi thuật toán giải.
- `tests/`: Chứa các `Unit Test` để kiểm tra mô hình và luật chơi.
- `README.md`: Hướng dẫn cài đặt và sử dụng dự án.

## 4. Cài đặt

### Bước 1: Clone repository

```bash
git clone https://github.com/tiennd2k5/logic_puzzles_starter.git
cd logic_puzzles_starter
```


### Bước 2: Tạo môi trường ảo (khuyến nghị)

Trên Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Trên Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Bước 3: Chạy kiểm thử

Từ thư mục gốc của dự án, chạy:

```bash
python -m unittest discover -s tests -v
```

Lệnh này chạy toàn bộ `Unit Test` hiện có để kiểm tra việc đọc dữ liệu, chuyển đổi `State` và xác thực luật chơi.

## 5. Định dạng dữ liệu đầu vào

Các bài toán được lưu trong thư mục `data/` dưới định dạng JSON.

### 5.1. Light Up

Ví dụ cấu trúc dữ liệu:

```json
{
  "name": "light_up_example",
  "type": "light_up",
  "rows": 3,
  "cols": 3,
  "grid": [
    [".", ".", "#"],
    [".", "2", "."],
    [".", ".", "."]
  ],
  "known_solution": []
}
```

Đây là ví dụ minh họa cấu trúc JSON, không phải một lời giải đã được xác nhận.

Ý nghĩa các ký hiệu:

| Ký hiệu | Ý nghĩa |
|---|---|
| `.` | Ô trắng, có thể đặt bóng đèn |
| `#` | Ô tường không có ràng buộc số |
| `0`–`4` | Ô tường quy định số bóng đèn cần có ở các ô liền kề |

Các trường bắt buộc:

- `name`: Tên bài toán.
- `type`: Phải là `light_up`.
- `rows`, `cols`: Số hàng và số cột.
- `grid`: Lưới biểu diễn bàn cờ.

Trường tùy chọn:

- `known_solution`: Đáp án có sẵn : danh sách tọa độ đặt bóng đèn, sử dụng chỉ số bắt đầu từ `0`.

Ví dụ tọa độ `[1, 2]` có nghĩa là hàng `1`, cột `2`.

### 5.2. Star Battle

Ví dụ cấu trúc dữ liệu:

```json
{
  "name": "shapeless_example",
  "type": "star_battle",
  "variant": "shapeless",
  "rows": 3,
  "cols": 3,
  "stars_per_unit": 1,
  "blocked_cells": [],
  "known_solution": []
}
```

Các trường dữ liệu:

| Trường | Ý nghĩa |
|---|---|
| `name` | Tên bài toán |
| `type` | Phải là `star_battle` |
| `variant` | Biến thể `normal` hoặc `shapeless` |
| `rows`, `cols` | Số hàng và số cột |
| `stars_per_unit` | Số sao yêu cầu trong mỗi hàng, cột và vùng nếu có |
| `regions` | Lưới xác định vùng, bắt buộc với biến thể `normal` |
| `blocked_cells` | Danh sách ô không được đặt sao |
| `known_solution` | Danh sách tọa độ đặt sao |

Đối với `normal`, bàn cờ phải có lưới `regions` với đúng số vùng khác nhau bằng số hàng. Đối với `shapeless`, không sử dụng `regions`.

Phiên bản hiện tại yêu cầu bàn cờ hình vuông.

Tọa độ sử dụng chỉ số bắt đầu từ `0`, theo định dạng `[row, col]`.

## 6. Biểu diễn State bằng Bitmask

Cả hai bài toán đều sử dụng một `tuple` chứa các số nguyên, mỗi số nguyên đại diện cho một hàng của bàn cờ.

Ví dụ:

```python
state = (
    0b00101,
    0b01000,
    0b10010,
)
```

Mỗi bit đại diện cho một cột:

- Bit bằng `1`: Ô tương ứng có bóng đèn hoặc ngôi sao.
- Bit bằng `0`: Ô tương ứng không có bóng đèn hoặc ngôi sao.
- Bit thấp nhất đại diện cho cột `0`.

Ví dụ:

```python
mask = 0b00101
```

Với bàn cờ có ít nhất 3 cột, `mask` này biểu diễn hai ô được chọn tại cột `0` và cột `2`.

### Chuyển đổi State

Cả hai lớp bài toán đều cung cấp các hàm chuyển đổi giữa tọa độ và `State`:

```python
state = problem.state_from_coords([
    (0, 0),
    (1, 2)
])

coords = problem.coords_from_state(state)

print(state)
print(coords)
```

Cách biểu diễn này giúp tiết kiệm bộ nhớ và hỗ trợ thao tác bằng toán tử bit trong các thuật toán tìm kiếm.

Lưu ý: Hai bài toán sử dụng cùng định dạng `State`, nhưng có luật chơi khác nhau. Cần dùng đúng lớp bài toán để kiểm tra trạng thái.

## 7. Đọc và kiểm tra bài toán

### 7.1. Light Up

```python
from src.light_up import LightUpProblem

problem = LightUpProblem.from_json(
    "data/light_up/light_up_7x7.json"
)

print(problem.name)
print(problem.rows, problem.cols)

state = problem.state_from_coords(
    problem.known_solution
)

print(problem.render(state))
print(problem.is_valid_state(state))
print(problem.is_goal(state))
```

Các phương thức chính:

| Phương thức | Chức năng |
|---|---|
| `from_json(path)` | Đọc bài toán từ file JSON |
| `from_dict(data)` | Tạo bài toán từ Python dictionary |
| `state_from_coords(coords)` | Chuyển tọa độ bóng đèn thành `State` |
| `coords_from_state(state)` | Chuyển `State` thành danh sách tọa độ |
| `illuminated_cells(state)` | Trả về tập hợp các ô được chiếu sáng |
| `is_valid_state(state)` | Kiểm tra xung đột bóng đèn và ràng buộc của tường số |
| `is_goal(state)` | Kiểm tra trạng thái đã giải xong hay chưa |
| `render(state)` | Hiển thị bàn cờ dưới dạng văn bản |

`is_valid_state(state)` kiểm tra các ràng buộc áp dụng cho cách đặt bóng đèn hiện tại. Khi cần xác nhận lời giải hoàn chỉnh, sử dụng `is_goal(state)`.

### 7.2. Star Battle

```python
from src.star_battle import StarBattleProblem

problem = StarBattleProblem.from_json(
    "data/star_battle/normal_1star_5x5.json"
)

print(problem.name)
print(problem.variant)

state = problem.state_from_coords(
    problem.known_solution
)

print(problem.render(state))
print(problem.is_goal(state))
```

Các phương thức chính:

| Phương thức | Chức năng |
|---|---|
| `from_json(path)` | Đọc bài toán từ file JSON |
| `from_dict(data)` | Tạo bài toán từ Python dictionary |
| `state_from_coords(coords)` | Chuyển tọa độ sao thành `State` |
| `coords_from_state(state)` | Chuyển `State` thành danh sách tọa độ |
| `is_valid_state(state, partial=True)` | Kiểm tra trạng thái đang xây dựng |
| `is_goal(state)` | Kiểm tra lời giải hoàn chỉnh |
| `render(state)` | Hiển thị bàn cờ dưới dạng văn bản |

Với Star Battle, `partial=True` cho phép một hàng, cột hoặc vùng chưa đủ số sao yêu cầu trong quá trình tìm kiếm. Tuy nhiên, trạng thái vẫn không được vượt quá số sao quy định hoặc vi phạm các luật còn lại.

## 8. Chạy chương trình

Các lệnh sau được chạy từ thư mục gốc của repo.

### Light Up

```bash
python -m src.light_up data/light_up/light_up_7x7.json
```

Chạy với bộ dữ liệu lớn hơn:

```bash
python -m src.light_up data/light_up/light_up_10x10.json
```

### Star Battle

```bash
python -m src.star_battle data/star_battle/normal_1star_5x5.json
```

Chạy biến thể `normal` với bàn cờ lớn hơn:

```bash
python -m src.star_battle data/star_battle/normal_2star_10x10.json
```

Chạy biến thể `shapeless`:

```bash
python -m src.star_battle data/star_battle/shapeless_1star_6x6.json
```

```bash
python -m src.star_battle data/star_battle/shapeless_2star_10x10.json
```

Các lệnh này dùng để đọc dữ liệu, hiển thị bài toán và kiểm tra `known_solution` nếu file có cung cấp lời giải.

**Lưu ý:** Các lệnh trên chưa tự động tìm lời giải. Việc tìm kiếm cần được triển khai trong các `Search Algorithm` và tích hợp qua `solver.py`.

## 9. Interface chung cho Search Algorithm

File `src/solver.py` cung cấp hàm:

```python
def solve(problem, algo):
    if not callable(algo):
        raise TypeError(
            "algo must be callable and accept one problem argument"
        )
    return algo(problem)
```

Hàm `solve(problem, algo)` đóng vai trò adapter, giúp các thành viên gọi thuật toán thông qua cùng một `Interface`.

### Ví dụ tích hợp thuật toán

Giả sử một thành viên triển khai thuật toán trong `src/my_algorithm.py`:

```python
def my_algorithm(problem):
    # Triển khai thuật toán tìm kiếm tại đây.
    # Trả về kết quả nếu tìm được lời giải.
    # Trả về None nếu không tìm được lời giải.
    ...
```

Có thể gọi thuật toán như sau:

```python
from src.light_up import LightUpProblem
from src.solver import solve
from src.my_algorithm import my_algorithm

problem = LightUpProblem.from_json(
    "data/light_up/light_up_7x7.json"
)

result = solve(problem, my_algorithm)
```

Đối với Star Battle, chỉ cần thay lớp bài toán và file JSON tương ứng:

```python
from src.star_battle import StarBattleProblem
from src.solver import solve
from src.my_algorithm import my_algorithm

problem = StarBattleProblem.from_json(
    "data/star_battle/normal_1star_5x5.json"
)

result = solve(problem, my_algorithm)
```

### Quy ước khi triển khai thuật toán

Mỗi thuật toán nên:

1. Nhận một đối tượng `LightUpProblem` hoặc `StarBattleProblem`.
2. Sử dụng `State` dạng `Bitmask` để biểu diễn trạng thái.
3. Sinh các trạng thái ứng viên và loại bỏ trạng thái không hợp lệ.
4. Sử dụng `problem.is_goal(state)` để kiểm tra lời giải.
5. Trả về kết quả theo định dạng mà nhóm đã thống nhất, hoặc `None` nếu không tìm được lời giải.

**Lưu ý:** `solver.py` hiện không tự triển khai thuật toán tìm kiếm và cũng không quy định kết quả bắt buộc phải là `State` hay đường đi. Nhóm cần thống nhất định dạng đầu ra trước khi tích hợp các thuật toán.

## 10. Chạy Unit Test

Chạy toàn bộ test:

```bash
python -m unittest discover -s tests -v
```

Chỉ chạy test Light Up:

```bash
python -m unittest discover -s tests -p "test_light_up.py" -v
```

Chỉ chạy test Star Battle:

```bash
python -m unittest discover -s tests -p "test_star_battle.py" -v
```

Các test hiện có kiểm tra:

- Đọc file JSON và xác nhận kích thước bàn cờ.
- Đọc và xác thực `known_solution`.
- Chuyển đổi giữa tọa độ và `Bitmask`.
- Từ chối tọa độ nằm ngoài bàn cờ và `State` có định dạng sai.
- Kiểm tra chiếu sáng, xung đột bóng đèn và tác dụng chắn sáng của tường trong Light Up.
- Kiểm tra số sao theo hàng, cột, vùng, luật không tiếp xúc và ô bị chặn trong Star Battle.

Khi bổ sung thuật toán, nên viết thêm `Unit Test` để kiểm tra lời giải trả về, trường hợp không có lời giải và các chức năng riêng của thuật toán.

## 11. Thêm bài toán mới

Để bổ sung một puzzle:

1. Tạo file JSON trong thư mục tương ứng dưới `data/`.
2. Khai báo các trường dữ liệu theo đúng định dạng của bài toán.
3. Kiểm tra kích thước bàn cờ và các tọa độ.
4. Nếu có lời giải mẫu, thêm danh sách tọa độ vào `known_solution`.
5. Đọc file bằng phương thức `from_json()`.
6. Chuyển lời giải thành `State` và kiểm tra bằng `problem.is_goal(state)`.

`known_solution` phải chứa lời giải hợp lệ cho đúng bộ dữ liệu tương ứng. Danh sách rỗng không có nghĩa là puzzle đã được giải.

## 12. Quy ước làm việc nhóm

Để các thành viên có thể phát triển độc lập và tích hợp thuận lợi:

- Giữ nguyên định dạng `State` dạng `Bitmask`.
- Sử dụng các lớp bài toán hiện có để kiểm tra luật, tránh viết lại logic trùng lặp.
- Tách phần triển khai `Search Algorithm` khỏi phần đọc dữ liệu và kiểm tra luật chơi.
- Thống nhất định dạng kết quả trả về của `solve(problem, algo)`.
- Bổ sung test khi thêm tính năng hoặc thay đổi `Interface`.
- Chạy toàn bộ test trước khi commit code.
- Cập nhật README nếu có thay đổi đối với cấu trúc dữ liệu hoặc `Interface` chung.

## 13. Phạm vi hiện tại

Repo cung cấp nền tảng dùng chung gồm:

- Mô hình dữ liệu cho Light Up và Star Battle.
- Đọc và kiểm tra file JSON.
- Biểu diễn `State` bằng `Bitmask`.
- Kiểm tra luật chơi và trạng thái đích.
- Hiển thị bàn cờ.
- `Interface` chung để tích hợp thuật toán.
- Các `Unit Test` cơ bản.

Các `Search Algorithm` sẽ được phát triển riêng và tích hợp qua `solve(problem, algo)`.

---

**Mục tiêu:** Xây dựng nền tảng chung, dễ kiểm thử và dễ mở rộng để các thành viên có thể triển khai, tích hợp và so sánh các thuật toán tìm kiếm cho Light Up và Star Battle.
