from inspect import signature
from typing import Callable
import math

from plover.formatting import RetroFormatter, _Context, _Action


RPN_STACK = "rpn_stack"
RPN_BASE = "rpn_base"
RPN_CALC = "rpn_calc"
RPN_BUFFER = "rpn_buffer"
RPN_IS_FLOAT = "rpn_is_float"

PARSE_ERROR = "parse error"
OP_ERROR = "op error"
PARAM_ERROR = "param error"

EXT_BUFFER_LIMIT = 50


def to_bin(num: int) -> str:
    return str(bin(num))[2:]


def to_hex(num: int) -> str:
    return str(hex(num))[2:]


def print_stack_action(
    ctx: _Context,
    prev_action: _Action,
    stack: list, 
    buffer: str, 
    is_float: bool,
    base: int = 0, 
    is_end: bool = False,
    force_del: str = ""
) -> _Action:
    if prev_action is None:
        # Using lambda as a generic object
        prev_action = lambda: None

    action = ctx.new_action()
    action.rpn_calc = not is_end

    if is_float:
        base = 10
    elif base == 0:
        base = getattr(prev_action, RPN_BASE, 10)
    
    if base == 2:    num_to_str = to_bin
    elif base == 16: num_to_str = to_hex
    else:            num_to_str = str

    stack_str = " | ".join(
        num_to_str(num)
        for num in stack
    )

    if force_del:
        action.prev_replace = force_del
        action.prev_attach = True
    elif getattr(prev_action, RPN_CALC, False):
        action.prev_replace = prev_action.text
        action.prev_attach = True
    
    if len(stack) == 1 and not buffer:
        action.text = stack_str
    else: 
        buffer_spacer = " > " if stack else "> "
        buffer_str = buffer_spacer + buffer if buffer else ""
        action.text = f"[ {stack_str}{buffer_str} ]"
    
    action.rpn_stack = stack
    action.rpn_buffer = buffer
    action.rpn_is_float = is_float
    action.rpn_base = base
    return action


def push_buffer_to_stack(
    stack: list, 
    is_float: bool, 
    buffer: str, 
    base: int
):
    if buffer:
        try:
            if "." in buffer:
                is_float = True
                stack.append(float(buffer))
            else:
                stack.append(int(buffer, base))
            
            buffer = ""
        except ValueError:
            buffer = PARSE_ERROR

    return is_float, buffer


def gen_mod_buffer(modify: Callable) -> Callable:
    def mod_func(ctx: _Context, arg: str) -> _Action:
        prev_action = ctx.last_action

        new_buffer = modify(
            getattr(prev_action, RPN_BUFFER, ""), arg
        ).strip()

        return print_stack_action(
            ctx,
            prev_action,
            getattr(prev_action, RPN_STACK, []).copy(),
            new_buffer,
            getattr(prev_action, RPN_IS_FLOAT, False)
        )
    
    return mod_func


rpn_put = gen_mod_buffer(lambda b, a: b + a)
rpn_del_buff = gen_mod_buffer(lambda b, a: b[:-1])
rpn_clear_buff = gen_mod_buffer(lambda b, a: "")


def rpn_put_ext(ctx: _Context, _: str) -> _Action:
    prev_rpn_action = None
    buff_stack = []

    accumulated_chars = 0
    for tln in reversed(ctx.previous_translations):
        is_calc = False
        for action in reversed(tln.formatting):
            if hasattr(action, RPN_CALC):
                is_calc = True
                prev_rpn_action = action
                break
            else:
                action_text = getattr(action, "text", "")
                accumulated_chars += len(action_text) if action_text else 0
        
        if not is_calc:
            buff_stack.insert(0, tln)
        
        if (
            accumulated_chars > EXT_BUFFER_LIMIT or
            prev_rpn_action is not None
        ):
            break
    
    if prev_rpn_action is None:
        new_stack = []
        new_buffer = "".join(ctx.last_words())
        new_is_float = False
        force_del = new_buffer

    else:
        new_stack = getattr(prev_rpn_action, RPN_STACK, [])
        last_text = RetroFormatter(buff_stack).last_text(EXT_BUFFER_LIMIT)
        new_buffer = (
            getattr(prev_rpn_action, RPN_BUFFER) +
            RetroFormatter(buff_stack).last_text(EXT_BUFFER_LIMIT)
        )
        new_is_float = getattr(prev_rpn_action, RPN_IS_FLOAT, False)
        buffer_spacer = ""

        if buff_stack:
            head_tln = buff_stack[0]
            if head_tln.formatting and not head_tln.formatting[0].prev_attach:
                buffer_spacer = " "
        
        force_del = prev_rpn_action.text + buffer_spacer + last_text
    
    return print_stack_action(
        ctx,
        prev_rpn_action,
        new_stack,
        new_buffer,
        new_is_float,
        force_del=force_del,
    )


def rpn_clear_stack(ctx: _Context, _: str) -> _Action:
    prev_action = ctx.last_action
    return print_stack_action(
        ctx,
        prev_action,
        [],
        getattr(prev_action, RPN_BUFFER, "").strip(),
        getattr(prev_action, RPN_IS_FLOAT, False)
    )


def rpn_clear_all(ctx: _Context, _: str) -> _Action:
    action = ctx.new_action()
    prev_action = ctx.last_action
    action.prev_replace = prev_action.text
    action.prev_attach = True
    action.text = ""
    return action


def rpn_end(ctx: _Context, _: str) -> _Action:
    prev_action = ctx.last_action
    return print_stack_action(
        ctx,
        prev_action,
        getattr(prev_action, RPN_STACK, []),
        getattr(prev_action, RPN_BUFFER, "").strip(),
        getattr(prev_action, RPN_IS_FLOAT, False),
        is_end=True
    )
    

def gen_rpn_push(base: int) -> Callable:
    def push_func(ctx: _Context, arg: str) -> _Action:
        prev_action = ctx.last_action
        new_stack = getattr(prev_action, RPN_STACK, []).copy()
        new_is_float = getattr(prev_action, RPN_IS_FLOAT, False)
        new_is_float, new_buffer = push_buffer_to_stack(
            new_stack,
            new_is_float, 
            (getattr(prev_action, RPN_BUFFER, "") + arg).strip(),
            base
        )

        return print_stack_action(
            ctx,
            prev_action,
            new_stack,
            new_buffer,
            new_is_float,
            base
        )
    
    return push_func


rpn_push = gen_rpn_push(10)
rpn_push_bin = gen_rpn_push(2)
rpn_push_hex = gen_rpn_push(16)


def gen_mod_stack(stack_op: Callable, parse_arg: bool = False) -> Callable:
    def mod_func(ctx: _Context, arg: str) -> _Action:
        if parse_arg:
            op_func = stack_op(arg)
        else:
            op_func = stack_op
        
        prev_action = ctx.last_action
        new_stack = getattr(prev_action, RPN_STACK, []).copy()
        new_is_float, new_buffer = push_buffer_to_stack(
            new_stack,
            getattr(prev_action, RPN_IS_FLOAT, False), 
            getattr(prev_action, RPN_BUFFER, "").strip(),
            getattr(prev_action, RPN_BASE, 10)
        )

        param_count = len(signature(op_func).parameters)
        if len(new_stack) >= param_count:
            op_params = new_stack[-param_count:]
            leftover_stack = new_stack[:-param_count]
            try:
                results = op_func(*op_params)
                if isinstance(results, tuple):
                    new_is_float = new_is_float or any(
                        isinstance(num, float)
                        for num in results
                    )

                    for num in results:
                        leftover_stack.append(num)
                else:
                    new_is_float = new_is_float or isinstance(results, float)
                    leftover_stack.append(results)
                
                new_stack = leftover_stack
            except:
                new_buffer = OP_ERROR
        else:
            new_buffer = PARAM_ERROR
        
        prev_action = ctx.last_action
        return print_stack_action(
            ctx,
            prev_action,
            new_stack,
            new_buffer,
            new_is_float
        )
    
    return mod_func


rpn_add = gen_mod_stack(lambda x, y: x + y)
rpn_sub = gen_mod_stack(lambda x, y: x - y)
rpn_mul = gen_mod_stack(lambda x, y: x * y)
rpn_div = gen_mod_stack(lambda x, y: x / y)
rpn_intdiv = gen_mod_stack(lambda x, y: x // y)
rpn_mod = gen_mod_stack(lambda x, y: x % y)
rpn_pow = gen_mod_stack(lambda x, y: x ** y)
rpn_and = gen_mod_stack(lambda x, y: int(x) & int(y))
rpn_or = gen_mod_stack(lambda x, y: int(x) | int(y))
rpn_xor = gen_mod_stack(lambda x, y: int(x) ^ int(y))
rpn_not = gen_mod_stack(lambda x: ~ int(x))
rpn_lsl = gen_mod_stack(lambda x, y: int(x) << int(y))
rpn_lsr = gen_mod_stack(lambda x, y: int(x) >> int(y))
rpn_swap = gen_mod_stack(lambda x, y: (y, x))
rpn_pop = gen_mod_stack(lambda _: tuple())
rpn_dup = gen_mod_stack(lambda x: (x, x))
rpn_neg = gen_mod_stack(lambda x: -x)
rpn_func = gen_mod_stack(lambda s: eval(f"lambda {s}"), True)
