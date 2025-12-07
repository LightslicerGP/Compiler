void print(int x)
{
    x += 12;
}

// Additional function to test parameters + return
int add(int a, int b)
{
    return a + b;
}

// Function to test unary ops, precedence, and logical ops
int compute(int x, int y)
{
    int r;

    // Unary operators
    r = -x;
    r = +y;
    r = !x;
    r = ~y;
    r = ++x;
    r = y--;

    // Logical operators (short-circuit tests)
    if (x > 0 && y > 0)
    {
        r = 1;
    }
    else if (x > 0 || y > 0)
    {
        r = 2;
    }
    else
    {
        r = 3;
    }

    // Operator precedence
    r = x + y * 2 - (y / 2 + 3);

    return r;
}

int main()
{
    int x = 10, y = 5, z;

    // if-else
    if (x > y)
    {
        z = x - y;
    }
    else
    {
        z = y - x;
    }

    // nested if
    if (z > 0)
    {
        if (x == 10)
        {
            z += 1;
        }
    }

    // while loop
    int i = 0;
    while (i < 3)
    {
        z += i;
        i = i + 1;
    }

    // do-while loop
    int j = 0;
    do
    {
        z -= j;
        j = j + 1;
    } while (j < 2);

    // for loop
    int sum = 0;
    for (int k = 0; k < 4; k = k + 1)
    {
        sum = sum + k;
    }

    // switch-case
    int val = 2;
    switch (val)
    {
    case 1:
        z = z + 10;
        break;
    case 2:
        z = z + 20;
        break;
    default:
        z = z + 30;
    }

    // compound statement
    {
        int temp = z * 2;
        z = temp / 2;
    }

    // ternary operator
    int max = (x > y) ? x : y;

    // ARRAY TESTS
    int arr[5];
    arr[0] = x;
    arr[1] = y + 1;
    arr[2] = arr[0] + arr[1];
    arr[3] = 3;
    arr[4] = arr[2] * 2;

    // More array indexing expressions
    int arr_sum = arr[0] + arr[1] + arr[2] + arr[3] + arr[4];

    // FUNCTION CALL + RETURN TEST
    int result = add(x, y);

    // UNARY + PRECEDENCE + LOGICAL OPS TEST
    int c = compute(x, y);

    // Nested compound blocks (scope test)
    {
        int x = 99; // shadowing
        {
            int x = 123; // nested shadow
            z += x;
        }
        z += x;
    }

    // Simple function calls
    print(z);
    print(sum);
    print(max);
    print(arr_sum);
    print(result);
    print(c);

    return 0;
}
