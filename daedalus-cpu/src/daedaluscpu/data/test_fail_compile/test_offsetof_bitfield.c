
struct z
{
    int foo : 23;
};
void main()
{
    __builtin_offsetof(struct z, foo);
}