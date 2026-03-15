# Формальная грамматика языка MiniCompiler

## 1. Общие сведения

Данный документ описывает синтаксис языка MiniCompiler в нотации EBNF (Extended Backus-Naur Form). Грамматика разработана для парсинга методом рекурсивного спуска с одним символом предпросмотра (LL(1)).

### Условные обозначения:
- `::=` - определяет нетерминал
- `{ ... }` - повторение 0 или более раз
- `[ ... ]` - опционально (0 или 1 раз)
- `|` - альтернатива
- Терминалы в кавычках: `"if"`, `"int"`, `";"`
- Нетерминалы с большой буквы: `Program`, `Expression`

---

## 2. Иерархия грамматики
Program
└── Declaration
├── FunctionDecl
├── StructDecl
└── VarDecl
└── Statement
├── Block
├── IfStmt
├── WhileStmt
├── ForStmt
├── ReturnStmt
├── ExprStmt
└── VarDecl
└── Expression
└── Assignment
└── LogicalOr
└── LogicalAnd
└── Equality
└── Relational
└── Additive
└── Multiplicative
└── Unary
└── Primary
├── Literal
├── Identifier
├── (Expression)
└── Call


---

## 3. Полная грамматика

### 3.1 Программа
```ebnf
Program ::= { Declaration }
```
### 3.2 Объявления
```ebnf
Declaration ::= FunctionDecl | StructDecl | VarDecl
```
#### Объявление функции
```ebnf
FunctionDecl ::= "fn" Identifier "(" [ Parameters ] ")" [ "->" Type ] Block
```
#### Объявление структуры
```ebnf
StructDecl ::= "struct" Identifier "{" { VarDecl } "}"
```

#### Объявление переменной
```ebnf
VarDecl ::= Type Identifier [ "=" Expression ] ";"
```
### Параметры функции
```ebnf
Parameters ::= Parameter { "," Parameter }
Parameter  ::= Type Identifier
``` 
### Типы
```ebnf
Type ::= "int" | "float" | "bool" | "void" | Identifier
```
 - int - целое число (32-bit)

 - float - число с плавающей точкой

 - bool - булевый тип

 - void - отсутствие типа (для функций)

 - Identifier - пользовательский тип (структура)

### 3.3 Инструкции
```ebnf
Statement ::= Block 
            | IfStmt 
            | WhileStmt 
            | ForStmt 
            | ReturnStmt 
            | ExprStmt 
            | VarDecl 
            | ";"
```

### Блок
```ebnf
Block ::= "{" { Statement } "}"
```

### Условная инструкция
``` ebnf
IfStmt ::= "if" "(" Expression ")" Statement [ "else" Statement ]
```
### Цикл while
```ebnf
WhileStmt ::= "while" "(" Expression ")" Statement
```

### Цикл for
```ebnf
ForStmt ::= "for" "(" [ ExprStmt ] ";" [ Expression ] ";" [ Expression ] ")" Statement
```
### 3.4 Выражения (с учетом приоритетов)
```ebnf
Expression ::= Assignment
```
Уровень 9: Присваивание (самый низкий приоритет)
```ebnf
Assignment ::= LogicalOr { ("=" | "+=" | "-=" | "*=" | "/=") Assignment }
```

### Уровень 8: Логическое ИЛИ
``` ebnf
LogicalOr ::= LogicalAnd { "||" LogicalAnd }
```
### Уровень 7: Логическое И
```ebnf
LogicalAnd ::= Equality { "&&" Equality }
```
### Уровень 6: Равенство
``` ebnf
Equality ::= Relational { ("==" | "!=") Relational }
```

### Уровень 5: Сравнение
```ebnf
Relational ::= Additive { ("<" | "<=" | ">" | ">=") Additive }
```

### Уровень 4: Сложение/Вычитание
```ebnf
Additive ::= Multiplicative { ("+" | "-") Multiplicative }
```
### Уровень 3: Умножение/Деление
```ebnf
Multiplicative ::= Unary { ("*" | "/" | "%") Unary }
```

### Уровень 2: Унарные операторы
```ebnf
Unary ::= ("-" | "!") Unary | Primary
```

### Уровень 1: Первичные выражения (самый высокий приоритет)
```ebnf
Primary ::= Literal 
          | Identifier 
          | "(" Expression ")" 
          | Call
``` 
### Вызов функции
``` ebnf
Call ::= Identifier "(" [ Arguments ] ")"
Arguments ::= Expression { "," Expression }
```

### 3.5 Литералы
```ebnf
Literal ::= Integer | Float | String | Boolean | "null"

Integer ::= digit { digit }
Float   ::= digit { digit } "." digit { digit }
String  ::= '"' { character } '"'
Boolean ::= "true" | "false"
```
### 3.6 Идентификаторы
```ebnf
Identifier ::= letter { letter | digit | "_" }
letter     ::= "a".."z" | "A".."Z"
digit      ::= "0".."9"
``` 

