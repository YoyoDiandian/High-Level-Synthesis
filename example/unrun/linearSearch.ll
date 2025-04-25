define int linearSearch(int arr[], int target, int n)
    i = 0;

start:
    cond = i >= n;
    br cond ret check;

check:
    ai = load(arr, i);
    found = ai == target;
    br found ret next;

next:
    i = i + 1;
    br start;

ret:
    return i;