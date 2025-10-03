void print(int x)
{
    x += 12;
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

    // simple function call (assuming print is defined elsewhere)
    print(z);
    print(sum);
    print(max);

    return 0;
}