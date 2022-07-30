# RPN Calculator for Plover
[![PyPI](https://img.shields.io/pypi/v/plover-rpn-calculator)](https://pypi.org/project/plover-rpn-calculator/)
![GitHub](https://img.shields.io/github/license/Kaoffie/plover_rpn_calculator)

**RPN Calculator** is a stack-based calculator that you can use to calculate equations directly in-line while writing. It uses reverse polish notation, where operations are written after their arguments, rather than in-between.

## Commands

| Definition | Explanation |
|---:|:---|
| `{:rpn_put:<characters>}` | Put characters into buffer. <br> For example: `{:rpn_put:1}` |
| `{:rpn_put_ext}` | Put all characters after the most recent calculator command into buffer. This allows you to use regular number entry strokes rather than `rpn_put` strokes to put characters into buffer. |
| `{:rpn_del_buff}` | Delete rightmost character in buffer. |
| `{:rpn_clear_buff}` | Clear buffer. |
| `{:rpn_clear_all}` | Clear and delete everything. |
| `{:rpn_push}` | Parse and push buffer into stack. |
| `{:rpn_push_bin}` | Parse and push buffer into stack as binary. |
| `{:rpn_push_hex}` | Parse and push buffer into stack as hexadecimal. |
| `{:rpn_add}` | Pop `(x, y)` from stack (where `y` is at the top) and push `x + y`. |
| `{:rpn_sub}` | Subtraction: Pop `(x, y)`, push `x - y`. |
| `{:rpn_mul}` | Multiplication: Pop `(x, y)`, push `x * y`. |
| `{:rpn_div}` | Division: Pop `(x, y)`, push `x / y`. |
| `{:rpn_intdiv}` | Floor division: Pop `(x, y)`, push `floor(x, y)`. |
| `{:rpn_mod}` | Modulo: Pop `(x, y)`, push `x mod y`. |
| `{:rpn_pow}` | Exponent: Pop `(x, y)`, push `pow(x, y)`. |
| `{:rpn_neg}` | Negation: Pop `x`, push `-x`. |
| `{:rpn_and}` | Bitwise AND: Pop `(x, y)`, push `x & y`. |
| `{:rpn_or}` | Bitwise OR: Pop `(x, y)`, push `x | y`. |
| `{:rpn_xor}` | Bitwise XOR: Pop `(x, y)`, push `x ^ y`. |
| `{:rpn_not}` | Bitwise NOT: Pop `x`, push `~x`. |
| `{:rpn_lsl}` | Logical Shift Left: Pop `(x, y)`, push `x << y`. |
| `{:rpn_lsr}` | Logical Shift Right: Pop `(x, y)`, push `x >> y`. |
| `{:rpn_swap}` | Swap top two stack items. |
| `{:rpn_pop}` | Remove the topmost item. |
| `{:rpn_dup}` | Duplicate top stack item. |
| `{:rpn_func:<params>:<return>}` | Define custom function; parameters are separated by commas, and the return value is written using python syntax. <br> For example: `{:rpn_func:x,y:3*x+2*y}` |
| `{:rpn_end}` | Mark the end of the calculation. |

Here are a few things to note when using the plugin:
- You can chain these definitions in a single stroke. For instance, `"{:rpn_clear_buff}{:rpn_dup}{:rpn_put:2}{:rpn_mul}"` will let you repeatedly add double the topmost item onto the stack.
- When the stack has exactly one item, it will be formatted as a bare number, allowing you to quickly move on after calculation.
- You can use the undo stroke (Typically `*`) to undo all RPN commands. This is helpful whenever you encounter an error during calculation.
