#!/usr/bin/env python3
from pathlib import Path

base = Path("tests/semantic")

# Создаем директории
dirs = [
    "valid/basic",
    "valid/functions",
    "valid/expressions",
    "invalid/type_errors",
    "invalid/declaration_errors",
    "invalid/scope_errors",
    "invalid/argument_errors",
    "invalid/return_errors"
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

# Valid tests
tests = {
    "valid/basic/test_return.src": '''fn main() -> int {
    return 42;
}''',
    "valid/basic/test_variable.src": '''fn main() -> int {
    int x = 10;
    int y = 20;
    int z = x + y;
    return z;
}''',
    "valid/basic/test_if.src": '''fn main() -> int {
    int x = 10;
    if (x > 5) {
        return 1;
    } else {
        return 0;
    }
}''',
    "valid/basic/test_while.src": '''fn main() -> int {
    int i = 0;
    int sum = 0;
    while (i < 10) {
        sum = sum + i;
        i = i + 1;
    }
    return sum;
}''',
    "valid/basic/test_for.src": '''fn main() -> int {
    int sum = 0;
    int i = 0;
    for (i = 0; i < 10; i = i + 1) {
        sum = sum + i;
    }
    return sum;
}''',
    "valid/basic/test_block_scope.src": '''fn main() -> int {
    int x = 10;
    {
        int x = 20;
        int y = 30;
    }
    int z = x + 5;
    return z;
}''',
    "valid/functions/test_simple_function.src": '''fn add(int a, int b) -> int {
    return a + b;
}

fn main() -> int {
    int result = add(5, 3);
    return result;
}''',
    "valid/functions/test_multiple_functions.src": '''fn add(int a, int b) -> int {
    return a + b;
}

fn sub(int a, int b) -> int {
    return a - b;
}

fn mul(int a, int b) -> int {
    return a * b;
}

fn main() -> int {
    int x = add(10, 5);
    int y = sub(10, 5);
    int z = mul(10, 5);
    return x + y + z;
}''',
    "valid/functions/test_recursive.src": '''fn factorial(int n) -> int {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}

fn main() -> int {
    return factorial(5);
}''',
    "valid/expressions/test_arithmetic.src": '''fn main() -> int {
    int a = 10;
    int b = 20;
    int c = 5;
    int d = (a + b) * c - 10;
    return d;
}''',
    "valid/expressions/test_comparison.src": '''fn main() -> int {
    int x = 10;
    int y = 20;
    bool b1 = x < y;
    bool b2 = x > y;
    bool b3 = x == 10;
    bool b4 = x != 5;
    if (b1 && !b2) {
        return 1;
    }
    return 0;
}''',
    "valid/expressions/test_type_conversion.src": '''fn main() -> int {
    int a = 10;
    float b = 3.14;
    float c = a + b;
    int d = a + 5;
    return d;
}''',
}

# Invalid tests
invalid_tests = {
    "invalid/type_errors/test_wrong_return_type.src": '''fn main() -> int {
    return true;
}''',
    "invalid/type_errors/test_wrong_assign.src": '''fn main() -> int {
    int x = 10;
    x = true;
    return x;
}''',
    "invalid/type_errors/test_condition_not_bool.src": '''fn main() -> int {
    int x = 10;
    if (x) {
        return 1;
    }
    return 0;
}''',
    "invalid/type_errors/test_binary_op_mismatch.src": '''fn main() -> int {
    int x = 10;
    bool y = true;
    int z = x + y;
    return z;
}''',
    "invalid/declaration_errors/test_duplicate_var.src": '''fn main() -> int {
    int x = 10;
    int x = 20;
    return x;
}''',
    "invalid/declaration_errors/test_duplicate_function.src": '''fn foo() -> int {
    return 1;
}

fn foo() -> int {
    return 2;
}

fn main() -> int {
    return foo();
}''',
    "invalid/declaration_errors/test_duplicate_param.src": '''fn add(int a, int a) -> int {
    return a + a;
}

fn main() -> int {
    return add(5, 3);
}''',
    "invalid/scope_errors/test_undeclared_variable.src": '''fn main() -> int {
    int x = y;
    return x;
}''',
    "invalid/scope_errors/test_out_of_scope.src": '''fn main() -> int {
    {
        int x = 10;
    }
    int y = x;
    return y;
}''',
    "invalid/scope_errors/test_parameter_scope.src": '''fn add(int a, int b) -> int {
    int a = 10;
    return a + b;
}

fn main() -> int {
    return add(5, 3);
}''',
    "invalid/argument_errors/test_argument_count.src": '''fn add(int a, int b) -> int {
    return a + b;
}

fn main() -> int {
    return add(5);
}''',
    "invalid/argument_errors/test_argument_type.src": '''fn add(int a, int b) -> int {
    return a + b;
}

fn main() -> int {
    return add(5, true);
}''',
    "invalid/return_errors/test_missing_return.src": '''fn foo() -> int {
    int x = 10;
}

fn main() -> int {
    return foo();
}''',
    "invalid/return_errors/test_void_return.src": '''fn foo() -> void {
    return 42;
}

fn main() -> void {
    foo();
}''',
}

# Создаем файлы
for path, content in tests.items():
    file_path = base / path
    file_path.write_text(content, encoding='utf-8')
    print(f"Created: {path}")

for path, content in invalid_tests.items():
    file_path = base / path
    file_path.write_text(content, encoding='utf-8')
    print(f"Created: {path}")

print("\nAll tests created!")