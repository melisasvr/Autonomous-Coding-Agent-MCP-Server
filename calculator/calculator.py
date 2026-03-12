import argparse
import operator

def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return x / y

def main():
    parser = argparse.ArgumentParser(description="CLI Calculator")
    parser.add_argument("-o", "--operation", choices=["add", "subtract", "multiply", "divide"], required=True)
    parser.add_argument("-n1", "--num1", type=float, required=True)
    parser.add_argument("-n2", "--num2", type=float, required=True)
    args = parser.parse_args()

    operations = {
        "add": add,
        "subtract": subtract,
        "multiply": multiply,
        "divide": divide
    }

    try:
        result = operations[args.operation](args.num1, args.num2)
        print(f"{args.num1} {get_operator(args.operation)} {args.num2} = {result}")
    except ZeroDivisionError as e:
        print(str(e))

def get_operator(operation):
    operators = {
        "add": "+",
        "subtract": "-",
        "multiply": "*",
        "divide": "/"
    }
    return operators[operation]

if __name__ == "__main__":
    main()