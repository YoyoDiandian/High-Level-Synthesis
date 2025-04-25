define int sumArray(int arr[], int n)
    i = 0;
    total = 0;

start:
    cond = i >= n;
    br cond return_sum add;

add:
    ai = load(arr, i);
    total = total + ai;
    i = i + 1;
    br start;

return_sum:
    return total;