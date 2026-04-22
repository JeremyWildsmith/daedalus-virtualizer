int add(int a, int b)
{
    return a + b + 10;
}

int add(int a, int b)
{ // Not cool!
    return a + b + 20;
}

void main(void) {
    add(10, 20);
}