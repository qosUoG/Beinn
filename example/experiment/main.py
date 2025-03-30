import os
import pickle
import pprint


if __name__ == "__main__":
    # filename = "./data/ExampleSqlSaver.pickle"

    # with open(filename, "rb") as f:
    #     pprint.pprint(pickle.load(f))

    # Exec mode for multiple statements
    exec_code = compile('name = "Alice"\nprint(name)', "example.py", "exec")
    exec(exec_code)

    # Eval mode for expressions
    eval_code = compile("3 + 4", "expr.py", "eval")
    result = eval(eval_code)
    print("Result of eval:", result)

    # Single mode for single interactive statement
    single_code = compile("name\n\n", "single_stmt.py", "eval")
    print(eval(single_code))
