define int maxArray(int arr[], int n)
    i = 0;
    max = load(arr, 0);

start:
    cond = i >= n;
    br cond return_max check;

check:
    ai = load(arr, i);
    cond_max = ai > max;
    br cond_max update_max next;

update_max:
    max = ai;

next:
    i = i + 1;
    br start;

return_max:
    return max;